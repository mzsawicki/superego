from uuid import UUID
from typing import List

from superego.game.game import Game, Answer, Player, Guess, GameState


class UseError(RuntimeError):
    pass


class InvalidAnswerValue(UseError):
    def __init__(self, answer_text: str):
        message = f'Invalid answer value: {answer_text}'
        super().__init__(message)


class AnswerEventIssuerIsNotCurrentPlayer(UseError):
    def __init__(self, issuer_guid: UUID, current_player_guid: UUID):
        message = f'Answer issuer is not current player.' \
                  f' Issuer ID: {issuer_guid}.' \
                  f' Current player ID: {current_player_guid}'
        super().__init__(message)


class GuessEventIssuerIsNotCurrentlyGuessingPlayer(UseError):
    def __init__(self, issuer_guid: UUID, guessing_players_id: List[UUID]):
        message = f'Guess issuer is not one of currently guessing players.' \
                  f' Issuer ID: {issuer_guid}.' \
                  f' Currently guessing players: {guessing_players_id}'
        super().__init__(message)


class AnswerUseCase:
    def __init__(self, game: Game):
        self._game: Game = game

    def __call__(self, answer_text: str, player_id: UUID) -> None:
        answer = _convert_answer(answer_text)
        self._ensure_issuer_is_current_player(player_id)
        player = self._game.current_player
        self._game.answer(player, answer)

    def _ensure_issuer_is_current_player(self, player_name: UUID) -> None:
        current_player = self._game.current_player
        if current_player.guid != player_name:
            raise AnswerEventIssuerIsNotCurrentPlayer(player_name,
                                                      current_player.guid)


class GuessUseCase:
    def __init__(self, game: Game):
        self._game: Game = game

    def __call__(self, answer_text: str, bet: int, player_id: UUID) -> None:
        answer = _convert_answer(answer_text)
        guess = Guess(answer=answer, bet=bet)
        self._ensure_player_is_guessing_player(player_id)
        player = self._get_player(player_id)
        self._game.guess(player, guess)

    def _ensure_player_is_guessing_player(self, player_id: UUID) -> None:
        guessing_players_ids = [player.guid
                                for player in self._game.guessing_players]
        if player_id not in guessing_players_ids:
            raise GuessEventIssuerIsNotCurrentlyGuessingPlayer(
                player_id, guessing_players_ids)

    def _get_player(self, issuer_guid: UUID) -> Player:
        for player in self._game.guessing_players:
            if player.guid == issuer_guid:
                return player


class ChangeCardUseCase:
    def __init__(self, game: Game):
        self._game: Game = game

    def __call__(self, player_id: UUID) -> None:
        self._ensure_issuer_is_current_player(player_id)
        player = self._game.current_player
        self._game.change_card(player)

    def _ensure_issuer_is_current_player(self, player_id: UUID) -> None:
        current_player = self._game.current_player
        if current_player.guid != player_id:
            raise AnswerEventIssuerIsNotCurrentPlayer(player_id,
                                                      current_player.guid)

class ReadyUseCase:
    def __init__(self, game: Game):
        self._game = game

    def __call__(self, player_id: UUID) -> None:
        player = self._get_player(player_id)
        self._game.mark_ready(player)

    def _get_player(self, player_id: UUID) -> Player:
        for player in self._game.players:
            if player.guid == player_id:
                return player


class GetGameStateUseCase:
    def __init__(self, game: Game):
        self._game = game

    def __call__(self) -> GameState:
        return self._game.state


def _convert_answer(answer_text: str) -> Answer:
    if answer_text == Answer.ANSWER_A.value:
        return Answer.ANSWER_A
    elif answer_text == Answer.ANSWER_B.value:
        return Answer.ANSWER_B
    elif answer_text == Answer.ANSWER_C.value:
        return Answer.ANSWER_C
    else:
        raise InvalidAnswerValue(answer_text)
