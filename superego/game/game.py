import uuid
import random
from typing import Dict, List
from uuid import UUID
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
from abc import ABCMeta, abstractmethod
from datetime import datetime

from superego.game.datatypes import Carousel


INITIAL_PLAYER_POINTS_COUNT = 10


class GameError(RuntimeError):
    pass


@dataclass(init=True, frozen=True)
class Card:
    question: str
    answer_A: str
    answer_B: str
    answer_C: str

    def __repr__(self) -> str:
        return self.question


class Deck:
    def __init__(self, name: str, cards: List[Card]):
        self._guid: UUID = uuid.uuid4()
        self._name: str = name
        self._cards = cards
        self._cards_carousel: Carousel = Carousel(self._cards)

    def __repr__(self) -> str:
        return self._name

    def shuffle(self) -> None:
        random.shuffle(self._cards)
        self._cards_carousel = Carousel(self._cards)

    def advance_card(self) -> None:
        self._cards_carousel.pop_push()

    @property
    def current_card(self) -> Card:
        return self._cards_carousel.front


class LobbyMember:
    def __init__(self, name: str):
        self._name: str = name
        self._guid: UUID = uuid.uuid4()

    def __repr__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def guid(self) -> UUID:
        return self._guid


@dataclass(frozen=True, init=True)
class GameSettings:
    deck: Deck
    max_rounds_factor: int


class Lobby:
    def __init__(self, host: LobbyMember, settings: GameSettings):
        self._guid: UUID = uuid.uuid4()
        self._host: LobbyMember = host
        self._members: Dict[UUID, LobbyMember] = {host.guid: host, }
        self._deck = settings.deck
        self._max_rounds_factor = settings.max_rounds_factor

    def __repr__(self) -> str:
        return str(self._guid)

    def add_member(self, player: LobbyMember) -> None:
        self._members[player.guid] = player

    def remove_member(self, guid: UUID) -> None:
        if guid not in self._members.keys():
            raise Exception('Invalid UUID when removing member from lobby')
        del self._members[guid]

    def change_deck(self, deck: Deck) -> None:
        self._deck = deck

    @property
    def guid(self) -> UUID:
        return self._guid

    @property
    def members(self) -> List[LobbyMember]:
        return [member for guid, member in self._members.items()]

    @property
    def members_count(self) -> int:
        return len(self._members)

    @property
    def deck(self) -> Deck:
        return self._deck

    @property
    def max_rounds(self) -> int:
        return self._max_rounds_factor * self.members_count


class Player:
    def __init__(self, lobby_member: LobbyMember):
        self._name = lobby_member.name
        self._guid = lobby_member.guid
        self._points = INITIAL_PLAYER_POINTS_COUNT

    def __repr__(self) -> str:
        return self._name

    def take_points(self, count: int) -> None:
        if self._points - count < 0:
            raise ValueError(f'Tried to take {count} points'
                             f' from player {self._guid}'
                             f' having {self._points} points')
        self._points -= count

    def give_points(self, count: int) -> None:
        self._points += count

    def can_bet(self, count: int) -> bool:
        return self._points - count >= 0

    def __eq__(self, other) -> bool:
        return self.guid == other.guid

    @property
    def name(self) -> str:
        return self._name

    @property
    def guid(self) -> UUID:
        return self._guid

    @property
    def points(self) -> int:
        return self._points

    @property
    def has_points(self) -> bool:
        return self._points > 0


class PlayersPool:
    def __init__(self, players: List[Player]):
        self._players: Dict[UUID, Player] =\
            {player.guid: player for player in players}
        self._players_carousel: Carousel = Carousel(players)

    def advance_player(self) -> None:
        self._players_carousel.pop_push()

    def kick_player(self, player: Player) -> None:
        del self._players[player.guid]
        self._players_carousel.find_remove(lambda x: x.guid == player.guid)

    def __len__(self):
        return len(self._players_carousel)

    @property
    def current_player(self) -> Player:
        return self._players_carousel.front

    @property
    def all_players(self) -> List[Player]:
        return self._players_carousel.items


class Answer(Enum):
    ANSWER_A = 'A'
    ANSWER_B = 'B'
    ANSWER_C = 'C'
    NO_ANSWER = 'NO_ANSWER'


class PlayerAlreadyAnswered(GameError):
    def __init__(self, player: Player):
        message = f'Player {player.guid} already answered'
        super().__init__(message)


class AnswersPool:
    def __init__(self, players_pool: PlayersPool):
        self._players_pool = players_pool
        self._players_answered: int = 0
        self._player_answers: defaultdict[UUID, Answer]\
            = defaultdict(lambda: Answer.NO_ANSWER)

    def flush(self) -> None:
        self._players_answered = 0
        self._player_answers = defaultdict(lambda: Answer.NO_ANSWER)

    def add_answer(self, player: Player, answer: Answer) -> None:
        if self._player_answers[player.guid] != Answer.NO_ANSWER:
            raise PlayerAlreadyAnswered(player)
        self._player_answers[player.guid] = answer
        self._players_answered += 1

    def get_player_answer(self, player: Player) -> Answer:
        return self._player_answers[player.guid]

    @property
    def all_players_answered(self) -> bool:
        return self._players_answered == len(self._players_pool)


class InvalidBetValue(GameError):
    def __init__(self, bet: int):
        message = f'Invalid bet: {bet}'
        super().__init__(message)


class PlayerAlreadyBet(GameError):
    def __init__(self, player: Player):
        message = f'Player {player.guid} already bet'
        super().__init__(message)


class BetPool:
    MAX_BET = 2
    MIN_BET = 1

    def __init__(self, players_pool: PlayersPool):
        self._players_pool = players_pool
        self._players_bet: int = 0
        self._bets: defaultdict[UUID, int] = defaultdict(int)

    def flush(self) -> None:
        self._players_bet = 0
        self._bets = defaultdict(int)

    def get_player_bet(self, player: Player) -> int:
        return self._bets[player.guid]

    def add_bet(self, player: Player, bet: int) -> None:
        self._ensure_player_has_not_bet(player)
        self._ensure_bet_value_valid(bet)
        self._place_bet(player, bet)

    def _ensure_player_has_not_bet(self, player: Player) -> None:
        if self._bets[player.guid] != 0:
            raise PlayerAlreadyBet(player)

    def _ensure_bet_value_valid(self, bet: int) -> None:
        if bet < self.MIN_BET or bet > self.MAX_BET:
            raise InvalidBetValue(bet)

    def _place_bet(self, player: Player, bet: int) -> None:
        self._bets[player.guid] = bet
        self._players_bet += 1

    @property
    def all_players_bet(self) -> bool:
        return self._players_bet == len(self._players_pool)


class PointsBank:
    def __init__(self, players_pool: PlayersPool):
        self._points_in_bank = INITIAL_PLAYER_POINTS_COUNT * len(players_pool)
        self._players_pool = players_pool

    def give_points(self, player: Player, amount: int) -> None:
        self._points_in_bank -= amount
        player.give_points(amount)

    def take_points(self, player: Player, amount: int) -> None:
        player.take_points(amount)
        self._points_in_bank += amount

    @property
    def points_left_in_bank(self):
        return self._points_in_bank


class GameTable:
    def __init__(self, players_pool: PlayersPool, deck: Deck):
        self._guid = uuid.uuid4()
        self._players_pool = players_pool
        self._answers_pool: AnswersPool = AnswersPool(self._players_pool)
        self._bet_pool: BetPool = BetPool(self._players_pool)
        self._deck: Deck = deck
        self._points_bank = PointsBank(players_pool)

    def change_card(self) -> None:
        self._deck.advance_card()

    def place_bet(self, player: Player, points: int) -> None:
        self._bet_pool.add_bet(player, points)

    def add_answer(self, player: Player, answer: Answer) -> None:
        self._answers_pool.add_answer(player, answer)

    def flush(self) -> None:
        self._answers_pool.flush()
        self._bet_pool.flush()

    def get_player_bet(self, player: Player) -> int:
        return self._bet_pool.get_player_bet(player)

    def get_player_answer(self, player: Player) -> Answer:
        return self._answers_pool.get_player_answer(player)

    def execute_win(self, player: Player) -> None:
        bet = self._bet_pool.get_player_bet(player)
        amount_to_give = bet
        self._points_bank.give_points(player, amount_to_give)

    def execute_loss(self, player: Player) -> None:
        bet = self._bet_pool.get_player_bet(player)
        self._points_bank.take_points(player, bet)
        if not player.has_points:
            self._players_pool.kick_player(player)

    def player_answered(self, player: Player) -> bool:
        return self._answers_pool.get_player_answer(player) != Answer.NO_ANSWER

    def player_bet(self, player: Player) -> bool:
        bet = self._bet_pool.get_player_bet(player)
        return bet != 0

    def player_can_bet(self, player: Player, bet: int) -> bool:
        if self.player_bet(player):
            return False
        return player.points >= bet

    def advance_player(self) -> None:
        self._players_pool.advance_player()

    def shuffle_deck(self) -> None:
        self._deck.shuffle()

    @property
    def current_card(self) -> Card:
        return self._deck.current_card

    @property
    def all_players_answered(self) -> bool:
        return self._answers_pool.all_players_answered

    @property
    def points_in_bank(self) -> int:
        return self._points_bank.points_left_in_bank

    @property
    def current_player(self) -> Player:
        return self._players_pool.current_player

    @property
    def players(self) -> List[Player]:
        return self._players_pool.all_players

    @property
    def guessing_players(self) -> List[Player]:
        return self._players_pool.all_players[1:]

    @property
    def in_game_players_count(self) -> int:
        return len(self.players)

    @property
    def ready_players(self) -> List[Player]:
        ready_players = sel


class ActionName(Enum):
    ANSWER_ACTION = 'ANSWER'
    GUESS_ACTION = 'GUESS'
    CHANGE_CARD_ACTION = 'CHANGE_CARD'
    MARK_READY_ACTION = 'MARK_READY'


class GamePhaseName(Enum):
    ANSWER_PHASE = 'ANSWER_PHASE'
    GUESS_PHASE = 'GUESS_PHASE'
    RESULT_PHASE = 'RESULT_PHASE'
    GAME_OVER_PHASE = 'GAME_OVER_PHASE'


class IllegalPlayerAction(GameError):
    def __init__(self, player: Player, action: ActionName,
                 phase: GamePhaseName, additional_info: str = None):
        message = f'Illegal game action: Player {player.guid};' \
                  f' Action: {action.value}; Game phase: {phase.value};' \
                  f' Additional information: {additional_info}'

        super().__init__(message)


class CardAlreadyChanged(GameError):
    pass


class PlayerCannotAffordBet(GameError):
    def __init__(self, player: Player, bet: int):
        message = f'Player {player.guid} tried to bet {bet}' \
                  f' while having {player.points} points'

        super().__init__(message)


class PlayerAlreadyMarkedAsReady(GameError):
    def __init__(self, player: Player):
        message = f'Player {player.guid} already marked as ready'
        super().__init__(message)


@dataclass(frozen=True, init=True)
class PlayerState:
    guid: UUID
    name: str
    points: int
    points_change: int
    awaited_to_answer: bool
    awaited_to_guess: bool
    ready: bool

    def __repr__(self) -> str:
        str_ = f'{self.name} | Points: {self.points}' \
               f' ({self.points_change})'
        if self.awaited_to_answer:
            str_ += ' | Answering now'
        elif self.awaited_to_guess:
            str_ += ' | Guessing now'
        elif self.ready:
            str_ += ' | Ready'
        return str_


@dataclass(frozen=True, init=True)
class GameState:
    time: datetime
    phase: GamePhaseName
    player_states: List[PlayerState]
    points_in_bank: int
    round_number: int
    current_card: Card
    card_changed: bool


class GameObserver(metaclass=ABCMeta):
    @abstractmethod
    def notify_game_state_changed(self, game_state: GameState) -> None:
        pass


class Clock(metaclass=ABCMeta):
    @abstractmethod
    def now(self) -> datetime:
        raise NotImplemented


@dataclass(init=True, frozen=True)
class GameContext:
    round_number: int
    max_rounds: int


@dataclass(init=True, frozen=True)
class Guess:
    answer: Answer
    bet: int


class GamePhase(metaclass=ABCMeta):
    @abstractmethod
    def answer(self, player: Player, answer: Answer) -> 'GamePhase':
        raise NotImplemented

    @abstractmethod
    def guess(self, player: Player, guess: Guess) -> 'GamePhase':
        raise NotImplemented

    @abstractmethod
    def change_card(self, player: Player) -> 'GamePhase':
        raise NotImplemented

    @abstractmethod
    def mark_ready(self, player: Player) -> 'GamePhase':
        raise NotImplemented

    @property
    @abstractmethod
    def state(self) -> GameState:
        raise NotImplemented

    @property
    @abstractmethod
    def game_over(self) -> bool:
        raise NotImplemented


class GameOver(GamePhase):
    def __init__(
        self,
        context: GameContext,
        game_table: GameTable,
        clock: Clock
    ):
        self._game_table: GameTable = game_table
        self._context: GameContext = context
        self._clock: Clock = clock

    def answer(self, player: Player, answer: Answer) -> 'GamePhase':
        raise IllegalPlayerAction(
            player,
            ActionName.ANSWER_ACTION,
            GamePhaseName.GAME_OVER_PHASE
        )

    def guess(self, player: Player, guess: Guess) -> 'GamePhase':
        raise IllegalPlayerAction(
            player,
            ActionName.GUESS_ACTION,
            GamePhaseName.GAME_OVER_PHASE
        )

    def change_card(self, player: Player) -> 'GamePhase':
        raise IllegalPlayerAction(
            player,
            ActionName.CHANGE_CARD_ACTION,
            GamePhaseName.GAME_OVER_PHASE
        )

    def mark_ready(self, player: Player) -> 'GamePhase':
        raise IllegalPlayerAction(
            player,
            ActionName.MARK_READY_ACTION,
            GamePhaseName.GAME_OVER_PHASE
        )

    @property
    def game_over(self) -> bool:
        return True

    @property
    def state(self) -> GameState:
        state = self._construct_game_state()
        return state

    def _construct_game_state(self) -> GameState:
        player_states = [self._construct_player_state(player)
                         for player in self._game_table.players]
        current_time = self._clock.now()
        return GameState(
            time=current_time,
            phase=GamePhaseName.GAME_OVER_PHASE,
            player_states=player_states,
            points_in_bank=self._game_table.points_in_bank,
            round_number=self._context.round_number,
            current_card=self._game_table.current_card,
            card_changed=False
        )

    @staticmethod
    def _construct_player_state(player: Player) -> PlayerState:
        return PlayerState(
            guid=player.guid,
            name=player.name,
            points=player.points,
            points_change=0,
            awaited_to_answer=False,
            awaited_to_guess=False,
            ready=False
        )


class ResultPhase(GamePhase):
    def __init__(
        self,
        context: GameContext,
        game_table: GameTable,
        clock: Clock
    ):
        self._context: GameContext = context
        self._game_table: GameTable = game_table
        self._ready_players_count: int = 0
        self._players_ready: defaultdict[UUID, bool] = defaultdict(bool)
        self._point_changes: defaultdict[UUID, int] = defaultdict(int)
        self._clock = clock

        self._settle()

    def answer(self, player: Player, answer: Answer) -> 'GamePhase':
        raise IllegalPlayerAction(
            player=player,
            action=ActionName.ANSWER_ACTION,
            phase=GamePhaseName.RESULT_PHASE
        )

    def guess(self, player: Player, guess: Guess) -> 'GamePhase':
        raise IllegalPlayerAction(
            player=player,
            action=ActionName.GUESS_ACTION,
            phase=GamePhaseName.RESULT_PHASE
        )

    def change_card(self, player: Player) -> 'GamePhase':
        raise IllegalPlayerAction(
            player=player,
            action=ActionName.CHANGE_CARD_ACTION,
            phase=GamePhaseName.RESULT_PHASE
        )

    def mark_ready(self, player: Player) -> 'GamePhase':
        if self._player_already_marked(player):
            raise PlayerAlreadyMarkedAsReady(player)
        self._do_mark_ready(player)
        if self._all_players_ready():
            return self._advance()
        return self

    @property
    def game_over(self) -> bool:
        return False

    @property
    def state(self) -> GameState:
        state = self._construct_game_state()
        return state

    def _settle(self) -> None:
        for player in self._game_table.guessing_players:
            self._settle_player(player)

    def _settle_player(self, player: Player) -> None:
        answer_correct = self._player_answered_correctly(player)
        bet = self._game_table.get_player_bet(player)
        if answer_correct:
            self._game_table.execute_win(player)
            self._save_point_change(player, bet)
        else:
            self._game_table.execute_loss(player)
            self._save_point_change(player, -bet)

    def _save_point_change(self, player: Player, points_count: int) -> None:
        self._point_changes[player.guid] = points_count

    def _player_answered_correctly(self, player: Player) -> bool:
        player_answer = self._game_table.get_player_answer(player)
        correct_answer = self._game_table.get_player_answer(
            self._game_table.current_player)
        return player_answer == correct_answer

    def _player_already_marked(self, player: Player) -> bool:
        return self._players_ready[player.guid]

    def _do_mark_ready(self, player: Player) -> None:
        self._players_ready[player.guid] = True
        self._ready_players_count += 1

    def _all_players_ready(self) -> bool:
        return self._ready_players_count\
               == self._game_table.in_game_players_count

    def _advance(self) -> GamePhase:
        if self._is_game_to_end():
            return self._end_game()
        return self._advance_to_next_round()

    def _is_game_to_end(self):
        return self._is_last_round()\
               or not self._at_least_two_players_left()\
               or self._no_points_left()

    def _is_last_round(self) -> bool:
        return self._context.round_number == self._context.max_rounds

    def _at_least_two_players_left(self) -> bool:
        return self._game_table.in_game_players_count > 1

    def _no_points_left(self) -> bool:
        return self._game_table.points_in_bank <= 0

    def _end_game(self) -> GamePhase:
        return GameOver(self._context, self._game_table, self._clock)

    def _advance_to_next_round(self) -> GamePhase:
        self._prepare_table_for_next_round()
        context = GameContext(
            round_number=self._context.round_number + 1,
            max_rounds=self._context.max_rounds
        )
        return AnswerPhase(context, self._game_table, self._clock)

    def _prepare_table_for_next_round(self) -> None:
        self._game_table.flush()
        self._game_table.change_card()
        self._game_table.advance_player()

    def _construct_game_state(self) -> GameState:
        player_states = [self._construct_player_state(player)
                         for player in self._game_table.players]
        return GameState(
            time=self._clock.now(),
            phase=GamePhaseName.RESULT_PHASE,
            player_states=player_states,
            points_in_bank=self._game_table.points_in_bank,
            round_number=self._context.round_number,
            current_card=self._game_table.current_card,
            card_changed=False
        )

    def _construct_player_state(self, player: Player) -> PlayerState:
        points_change = self._point_changes[player.guid]
        ready = self._players_ready[player.guid]
        return PlayerState(
            guid=player.guid,
            name=player.name,
            points=player.points,
            points_change=points_change,
            awaited_to_answer=False,
            awaited_to_guess=False,
            ready=ready
        )


class GuessPhase(GamePhase):
    def __init__(
        self,
        context: GameContext,
        game_table: GameTable,
        clock: Clock
    ):
        self._context: GameContext = context
        self._game_table: GameTable = game_table
        self._clock: Clock = clock

    def answer(self, player: Player, answer: Answer) -> 'GamePhase':
        raise IllegalPlayerAction(
            player, ActionName.ANSWER_ACTION, GamePhaseName.GUESS_PHASE)

    def guess(self, player: Player, guess: Guess) -> 'GamePhase':
        bet = guess.bet
        answer = guess.answer

        self._ensure_correct_player(player)
        self._ensure_bet_possible(player, bet)

        self._game_table.add_answer(player, answer)
        self._game_table.place_bet(player, bet)

        if self._game_table.all_players_answered:
            return self._advance()
        return self

    def change_card(self, player: Player) -> 'GamePhase':
        raise IllegalPlayerAction(player, ActionName.CHANGE_CARD_ACTION,
                                  GamePhaseName.GUESS_PHASE)

    def mark_ready(self, player: Player) -> 'GamePhase':
        raise IllegalPlayerAction(player, ActionName.MARK_READY_ACTION,
                                  GamePhaseName.GUESS_PHASE)

    @property
    def game_over(self) -> bool:
        return False

    @property
    def state(self) -> GameState:
        state = self._construct_game_state()
        return state

    def _ensure_correct_player(self, player: Player) -> None:
        current_player = self._game_table.current_player
        if player == current_player:
            raise IllegalPlayerAction(
                player, ActionName.ANSWER_ACTION,
                GamePhaseName.ANSWER_PHASE,
                additional_info='The currently answering player guess attempt')

    def _ensure_bet_possible(self, player: Player, bet: int) -> None:
        if self._game_table.player_bet(player):
            raise PlayerAlreadyBet(player)
        if not self._game_table.player_can_bet(player, bet):
            raise PlayerCannotAffordBet(player, bet)

    def _advance(self) -> 'GamePhase':
        return ResultPhase(self._context, self._game_table, self._clock)

    def _construct_game_state(self) -> GameState:
        player_states = [self._construct_player_state(player)
                         for player in self._game_table.players]
        current_time = self._clock.now()
        game_state = GameState(
            time=current_time,
            phase=GamePhaseName.GUESS_PHASE,
            player_states=player_states,
            points_in_bank=self._game_table.points_in_bank,
            round_number=self._context.round_number,
            current_card=self._game_table.current_card,
            card_changed=False
        )
        return game_state

    def _construct_player_state(self, player: Player) -> PlayerState:
        player_state = PlayerState(
            guid=player.guid,
            name=player.name,
            points=player.points,
            points_change=0,
            awaited_to_answer=False,
            awaited_to_guess=self._is_player_awaited_to_guess(player),
            ready=False
        )
        return player_state

    def _is_player_awaited_to_guess(self, player: Player) -> bool:
        return player != self._game_table.current_player \
            and not self._game_table.player_answered(player)


class AnswerPhase(GamePhase):
    def __init__(
        self,
        context: GameContext,
        game_table: GameTable,
        clock: Clock
    ):
        self._game_table: GameTable = game_table
        self._card_changed: bool = False
        self._clock: Clock = clock
        self._context = context

    def answer(self, player: Player, answer: Answer) -> 'GamePhase':
        self._ensure_correct_player(player)
        self._game_table.add_answer(player, answer)
        return self._advance()

    def guess(self, player: Player, guess: Guess) -> 'GamePhase':
        raise IllegalPlayerAction(player, ActionName.GUESS_ACTION,
                                  GamePhaseName.ANSWER_PHASE)

    def change_card(self, player: Player) -> 'GamePhase':
        self._ensure_correct_player(player)
        if self._card_changed:
            raise CardAlreadyChanged()
        self._game_table.change_card()
        return self

    def mark_ready(self, player: Player) -> 'GamePhase':
        raise IllegalPlayerAction(player, ActionName.MARK_READY_ACTION,
                                  GamePhaseName.ANSWER_PHASE)

    @property
    def game_over(self) -> bool:
        return False

    @property
    def state(self) -> GameState:
        state = self._construct_game_state()
        return state

    def _ensure_correct_player(self, player: Player) -> None:
        current_player = self._game_table.current_player
        if not player == current_player:
            raise IllegalPlayerAction(
                player, ActionName.ANSWER_ACTION,
                GamePhaseName.ANSWER_PHASE,
                additional_info='This is not the currently answering player')

    def _advance(self) -> 'GamePhase':
        return GuessPhase(self._context, self._game_table, self._clock)

    def _construct_game_state(self) -> GameState:
        player_states = [self._construct_player_state(player)
                         for player in self._game_table.players]
        current_time = self._clock.now()
        game_state = GameState(
            time=current_time,
            phase=GamePhaseName.ANSWER_PHASE,
            player_states=player_states,
            points_in_bank=self._game_table.points_in_bank,
            round_number=self._context.round_number,
            current_card=self._game_table.current_card,
            card_changed=self._card_changed
        )
        return game_state

    def _construct_player_state(self, player: Player) -> PlayerState:
        awaited_to_answer = self._is_player_awaited_to_answer(player)
        player_state = PlayerState(
            guid=player.guid,
            name=player.name,
            points=player.points,
            points_change=0,
            awaited_to_answer=awaited_to_answer,
            awaited_to_guess=False,
            ready=False
        )
        return player_state

    def _is_player_awaited_to_answer(self, player: Player) -> bool:
        return player == self._game_table.current_player \
            and not self._game_table.player_answered(player)


class Game:
    def __init__(self, lobby: Lobby, clock: Clock, observer: GameObserver):
        players = [Player(member) for member in lobby.members]
        players_pool = PlayersPool(players)
        context = GameContext(round_number=1, max_rounds=lobby.max_rounds)
        self._game_table: GameTable = GameTable(players_pool, lobby.deck)
        self._observer: GameObserver = observer
        self._game: GamePhase = AnswerPhase(context, self._game_table, clock)
        self._game_table.shuffle_deck()
        self._observer.notify_game_state_changed(self._game.state)

    def answer(self, player: Player, answer: Answer) -> None:
        self._game = self._game.answer(player, answer)
        self._observer.notify_game_state_changed(self._game.state)

    def guess(self, player: Player, guess: Guess) -> None:
        self._game = self._game.guess(player, guess)
        self._observer.notify_game_state_changed(self._game.state)

    def change_card(self, player: Player) -> None:
        self._game = self._game.change_card(player)
        self._game_table.shuffle_deck()
        self._observer.notify_game_state_changed(self._game.state)

    def mark_ready(self, player: Player) -> None:
        self._game = self._game.mark_ready(player)
        self._observer.notify_game_state_changed(self._game.state)

    @property
    def state(self) -> GameState:
        return self._game.state

    @property
    def over(self) -> bool:
        return self._game.game_over

    @property
    def players(self) -> List[Player]:
        return self._game_table.players

    @property
    def current_player(self) -> Player:
        return self._game_table.current_player

    @property
    def guessing_players(self) -> List[Player]:
        return self._game_table.guessing_players

    @property
    def current_card(self) -> Card:
        return self._game_table.current_card
