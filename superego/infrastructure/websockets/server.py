import asyncio
import signal
from dataclasses import dataclass
from uuid import UUID
from abc import ABCMeta, abstractmethod
from typing import Dict

from websockets import WebSocketServerProtocol, serve

from superego.infrastructure.websockets.broadcast import Broadcast
from superego.infrastructure.websockets.events import\
    Event, \
    EventAction
from superego.infrastructure.websockets.handlers import EventHandler
from superego.game.game import GameObserver, GameState
from superego.infrastructure.time import TimeProvider
from superego.infrastructure.websockets.serialization import \
    serialize_game_state, deserialize_json, deserialize_event


class WebsocketsServerError(RuntimeError):
    pass


class DataEncodingInvalid(WebsocketsServerError):
    def __init__(self, encoding: str):
        super().__init__(f'Incoming data is not encoded properly ({encoding})')


class MissingEventAction(WebsocketsServerError):
    pass


class MissingEventIssuer(WebsocketsServerError):
    pass


class UnknownEventAction(WebsocketsServerError):
    def __init__(self, action_name: str):
        message = f'Event action unknown: {action_name}'
        super().__init__(message)


class InvalidPlayerGUIDSubscriptionAttempt(WebsocketsServerError):
    def __init__(self, guid: UUID):
        message = f'Attempted to subscribe as player but GUID not found: {guid}'
        super().__init__(message)


class SocketReadUnsuccessful(WebsocketsServerError):
    pass


@dataclass(init=True, frozen=True)
class WebsocketsServerConfig:
    host: str
    port: int
    encoding: str


class Server(metaclass=ABCMeta):
    @abstractmethod
    def run(self) -> None:
        raise NotImplemented

    @abstractmethod
    def stop(self) -> None:
        raise NotImplemented


class ConnectionHandler(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, websocket: WebSocketServerProtocol) -> None:
        raise NotImplemented


class EventRouter(metaclass=ABCMeta):
    @abstractmethod
    async def route(self, event: Event, websocket: WebSocketServerProtocol) -> None:
        raise NotImplemented

    @abstractmethod
    def register_handler(self, action: EventAction,
                         handler: EventHandler) -> 'EventRouter':
        raise NotImplemented


class WebSocketsGameObserver(GameObserver):
    def __init__(self, broadcast: Broadcast):
        self._broadcast: Broadcast = broadcast

    def notify_game_state_changed(self, game_state: GameState) -> None:
        message = serialize_game_state(game_state)
        self._broadcast.broadcast(message)


class WebSocketsEventRouter(EventRouter):
    def __init__(self):
        self._handlers: Dict[str, EventHandler] = dict()

    async def route(self, event: Event,
                    websocket: WebSocketServerProtocol) -> None:
        action_name = event.action.value
        if action_name not in self._handlers:
            raise UnknownEventAction(action_name)
        handler = self._handlers[action_name]
        await handler.handle(event, websocket)

    def register_handler(self, action: EventAction,
                         handler: EventHandler) -> EventRouter:
        self._handlers[action.value] = handler
        return self


class WebSocketsConnectionHandler(ConnectionHandler):
    def __init__(
            self,
            encoding: str,
            time_provider: TimeProvider,
            router: EventRouter,
            broadcast: Broadcast
    ):
        self._encoding: str = encoding
        self._time_provider: TimeProvider = time_provider
        self._router: EventRouter = router
        self._broadcast: Broadcast = broadcast

    async def __call__(self, websocket: WebSocketServerProtocol) -> None:
        async for message in websocket:
            event = await self._receive_event(message)
            await self._process_event(event, websocket)

    async def _receive_event(self, message: str):
        event_dict = deserialize_json(message)
        event = self._read_event(event_dict)
        return event

    async def _process_event(self, event: Event,
                             websocket: WebSocketServerProtocol) -> None:
        await self._router.route(event, websocket)

    def _decode_incoming_data(self, data: bytes) -> str:
        try:
            decoded = data.decode(self._encoding)
            return decoded
        except UnicodeDecodeError:
            raise DataEncodingInvalid

    def _read_event(self, event_dict: Dict) -> Event:
        if 'action' not in event_dict:
            raise MissingEventAction
        if 'issuer' not in event_dict:
            raise MissingEventIssuer

        event = deserialize_event(event_dict, self._time_provider)

        return event


class WebSocketsServer(Server):
    def __init__(
            self,
            config: WebsocketsServerConfig,
            connection_handler: ConnectionHandler
    ):
        self._host: str = config.host
        self._port: int = config.port
        self._handler: ConnectionHandler = connection_handler

        self._loop = asyncio.get_event_loop()
        self._stopped: asyncio.Future = self._loop.create_future()
        self._loop.add_signal_handler(signal.SIGTERM, self.stop)
        self._loop.add_signal_handler(signal.SIGINT, self.stop)

    def run(self) -> None:
        self._loop.run_until_complete(self._serve())

    def stop(self) -> None:
        self._stopped.set_result(True)

    async def _serve(self) -> None:
        async with serve(self._handler, self._host, self._port):
            await self._stopped
