from datetime import datetime, timedelta
import random
from typing import Iterator

from superego.game.game import\
    Clock,\
    GameObserver,\
    GameState,\
    Lobby,\
    LobbyMember,\
    GameSettings,\
    Answer,\
    Guess
from tests.test_deck import test_deck


class ArtificialClock(Clock):
    def __init__(self):
        self._time = datetime(2022, 1, 1, 12)

    def now(self) -> datetime:
        self._time += timedelta(minutes=1)
        return self._time


class ObserverStub(GameObserver):
    def notify_game_state_changed(self, game_state: GameState) -> None:
        pass


def generate_lobby_member() -> Iterator[LobbyMember]:
    names = ('Bob', 'Alice', 'Andrew', 'Lily', 'Michael',
             'Drew', 'Kate', 'Anne', 'Zack')
    for name in names:
        yield LobbyMember(name)


def create_test_lobby(players_count: int, rounds_per_player: int) -> Lobby:
    player_generator = generate_lobby_member()
    host = next(player_generator)
    settings = GameSettings(deck=test_deck, max_rounds_factor=rounds_per_player)
    lobby = Lobby(host=host, settings=settings)
    for i in range(players_count - 1):
        lobby.add_member(next(player_generator))
    return lobby


def random_answer() -> Answer:
    answers = (Answer.ANSWER_A, Answer.ANSWER_B, Answer.ANSWER_C)
    return random.choice(answers)


def random_guess() -> Guess:
    answer = random_answer()
    bet = random.choice((1, 2))
    return Guess(answer=answer, bet=bet)
