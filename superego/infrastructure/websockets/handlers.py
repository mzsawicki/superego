from abc import ABCMeta, abstractmethod
from typing import List

from websockets import WebSocketServerProtocol

from superego.application.usecases import AnswerUseCase, GuessUseCase, \
    ChangeCardUseCase, GetGameStateUseCase, ReadyUseCase
from superego.infrastructure.websockets.broadcast import Broadcast
from superego.infrastructure.websockets.events import Event
from superego.infrastructure.websockets.serialization import \
    serialize_confirmation, serialize_game_state


class EventHandlingError(RuntimeError):
    pass


class EventParametersMissing(EventHandlingError):
    def __init__(self, parameter_names: List[str]):
        message = f'Event is missing parameters: {parameter_names}'
        super().__init__(message)


class EventHandler(metaclass=ABCMeta):
    @abstractmethod
    async def handle(self, event: Event,
                     websocket: WebSocketServerProtocol) -> None:
        raise NotImplemented


class AnswerEventHandler(EventHandler):
    def __init__(self, use_case: AnswerUseCase):
        self._answer = use_case

    async def handle(self, event: Event,
                     websocket: WebSocketServerProtocol) -> None:
        self._ensure_params_present(event)
        answer_text = event.params[0]
        self._answer(answer_text, event.issuer)
        await _send_confirmation(websocket)

    @staticmethod
    def _ensure_params_present(event: Event) -> None:
        if not event.params:
            raise EventParametersMissing(['answer'])


class GuessEventHandler(EventHandler):
    def __init__(self, use_case: GuessUseCase):
        self._guess = use_case

    async def handle(self, event: Event,
                     websocket: WebSocketServerProtocol) -> None:
        self._ensure_params_present(event)
        answer_text, bet = event.params
        self._guess(answer_text, bet, event.issuer)
        await _send_confirmation(websocket)

    @staticmethod
    def _ensure_params_present(event: Event) -> None:
        if not event.params:
            raise EventParametersMissing(['answer', 'bet'])
        elif len(event.params) == 1:
            raise EventParametersMissing(['bet'])


class ChangeCardEventHandler(EventHandler):
    def __init__(self, use_case: ChangeCardUseCase):
        self._change_card: ChangeCardUseCase = use_case

    async def handle(self, event: Event,
                     websocket: WebSocketServerProtocol) -> None:
        self._change_card(event.issuer)
        message = serialize_confirmation()
        await websocket.send(message)


class ReadyEventHandler(EventHandler):
    def __init__(self, use_case: ReadyUseCase):
        self._mark_ready: ReadyUseCase = use_case

    async def handle(self, event: Event,
                     websocket: WebSocketServerProtocol) -> None:
        self._mark_ready(event.issuer)
        message = serialize_confirmation()
        await websocket.send(message)


class SubscribeGameBroadcastEventHandler(EventHandler):
    def __init__(self, game_broadcast: Broadcast):
        self._broadcast = game_broadcast

    async def handle(self, event: Event,
                     websocket: WebSocketServerProtocol) -> None:
        await self._broadcast.add_listener(websocket)
        message = serialize_confirmation()
        await websocket.send(message)


class ReadGameStateEventHandler(EventHandler):
    def __init__(self, use_case: GetGameStateUseCase):
        self._get_game_state = use_case

    async def handle(self, event: Event,
                     websocket: WebSocketServerProtocol) -> None:
        game_state = self._get_game_state()
        read = serialize_game_state(game_state)
        await websocket.send(read)


async def _send_confirmation(websocket: WebSocketServerProtocol) -> None:
    message = serialize_confirmation()
    await websocket.send(message)
