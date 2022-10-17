from superego.infrastructure.websockets.events import \
    EventAction
from superego.infrastructure.websockets.handlers import AnswerEventHandler, \
    GuessEventHandler, ChangeCardEventHandler, \
    SubscribeGameBroadcastEventHandler, ReadGameStateEventHandler, \
    ReadyEventHandler
from superego.infrastructure.websockets.server import\
    WebsocketsServerConfig, \
    WebSocketsGameObserver,\
    WebSocketsEventRouter,\
    WebSocketsConnectionHandler,\
    WebSocketsServer,\
    Server
from superego.infrastructure.websockets.broadcast import WebSocketsBroadcast
from superego.infrastructure.time import\
    SimpleLocalTimeProvider,\
    TimeProviderClock
from superego.game.game import Lobby, Game
from superego.application.usecases import\
    GuessUseCase,\
    AnswerUseCase,\
    ChangeCardUseCase,\
    GetGameStateUseCase,\
    ReadyUseCase


def assemble_websockets_server(
        server_config: WebsocketsServerConfig,
        lobby: Lobby
) -> Server:
    broadcast = WebSocketsBroadcast()
    game_observer = WebSocketsGameObserver(broadcast)

    time_provider = SimpleLocalTimeProvider()
    game_clock = TimeProviderClock(time_provider)
    game = Game(lobby, game_clock, game_observer)

    guess = GuessUseCase(game)
    answer = AnswerUseCase(game)
    change_card = ChangeCardUseCase(game)
    get_game_state = GetGameStateUseCase(game)
    ready = ReadyUseCase(game)

    answer_event_handler = AnswerEventHandler(answer)
    guess_event_handler = GuessEventHandler(guess)
    change_card_event_handler = ChangeCardEventHandler(change_card)
    subscribe_game_event_handler = SubscribeGameBroadcastEventHandler(broadcast)
    read_game_state_event_handler = ReadGameStateEventHandler(get_game_state)
    ready_event_handler = ReadyEventHandler(ready)
    event_router = WebSocketsEventRouter()\
        .register_handler(EventAction.ANSWER, answer_event_handler)\
        .register_handler(EventAction.GUESS, guess_event_handler)\
        .register_handler(EventAction.CHANGE_CARD, change_card_event_handler)\
        .register_handler(EventAction.SUBSCRIBE, subscribe_game_event_handler)\
        .register_handler(EventAction.READ, read_game_state_event_handler)\
        .register_handler(EventAction.READY, ready_event_handler)

    connection_handler = WebSocketsConnectionHandler(
            server_config.encoding,
            time_provider,
            event_router,
            broadcast
        )

    server = WebSocketsServer(server_config, connection_handler)

    return server







