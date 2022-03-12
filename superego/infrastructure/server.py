import asyncio
import json
from json import JSONDecodeError
from abc import ABCMeta, abstractmethod

from websockets import WebSocketServerProtocol, serve

from superego.application.app import Server
from superego.application.routing import\
    Event,\
    configure_event_router,\
    EVENT_TYPE_KEY,\
    RouterResponse,\
    Notice


ENCODING = 'utf-8'


class ServerLayerError(RuntimeError):
    pass


class DataEncodingInvalid(ServerLayerError):
    def __init__(self):
        super().__init__(f'Incoming data is not encoded properly ({ENCODING})')


class IncomingMessageInvalid(ServerLayerError):
    def __init__(self, message: str):
        error_message = f'Received invalid message: {message}'
        super().__init__(error_message)


class MissingEventType(ServerLayerError):
    def __init__(self, event: Event):
        event_string = str(event)
        message = f'Missing event type value: {event_string}'
        super().__init__(message)


def _validate_data(data: bytes):
    try:
        data.decode(ENCODING)
    except UnicodeDecodeError:
        raise DataEncodingInvalid


def _validate_message(message: str) -> None:
    try:
        json.loads(message)
    except JSONDecodeError:
        raise IncomingMessageInvalid(message)


def _validate_event_format(event: Event) -> None:
    if EVENT_TYPE_KEY not in event.keys():
        raise MissingEventType(event)


class ConnectionHandler(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, websocket: WebSocketServerProtocol) -> None:
        raise NotImplemented


class DefaultConnectionHandler:
    def __init__(self):
        self._router = configure_event_router()

    async def __call__(self, websocket: WebSocketServerProtocol) -> None:
        event = await self._receive_event(websocket)
        response = self._route_incoming_event(event)
        for notice in response:
            await self._send_notice(websocket, notice)

    def _route_incoming_event(self, event: Event) -> RouterResponse:
        response = self._router.route(event)
        return response

    @staticmethod
    async def _receive_event(websocket: WebSocketServerProtocol) -> Event:
        data = await websocket.recv()
        _validate_data(data)
        message = data.decode(ENCODING)
        _validate_message(message)
        event = json.loads(message)
        _validate_event_format(event)
        return event

    @staticmethod
    async def _send_notice(websocket: WebSocketServerProtocol,
                           notice: Notice) -> None:
        json_ = json.dumps(notice)
        message = str(json_)
        data = message.encode(ENCODING)
        await websocket.send(data)


class WebSocketsServer(Server):
    def __init__(self, host: str, port: int,
                 handler: ConnectionHandler = DefaultConnectionHandler()):
        self._host: str = host
        self._port: int = port
        self._handler: ConnectionHandler = handler

    def run(self) -> None:
        asyncio.run(self._serve())

    async def _serve(self) -> None:
        async with serve(self._handler, self._host, self._port):
            await asyncio.Future()
