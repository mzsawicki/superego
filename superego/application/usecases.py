from uuid import UUID
from typing import List, Dict

from superego.game.game import Game, Answer, Player, Guess, GameState, Card, Lobby, LobbyMember, GameSettings
from superego.application.interfaces import GameServer, CardStorage, PersonStorage, GameServerCreator, DeckStorage


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


class AddCardUseCase:
    def __init__(self, card_storage: CardStorage):
        self._storage = card_storage

    def __call__(self, **kwargs) -> None:
        card = Card(**kwargs)
        self._storage.store(card)


class AddPersonUseCase:
    def __init__(self, person_storage: PersonStorage):
        self._storage = person_storage

    def __call__(self, name: str) -> None:
        self._storage.store(name)


class RetrievePersonGUIDUseCase:
    def __init__(self, person_storage: PersonStorage):
        self._storage = person_storage

    def __call__(self, name: str) -> UUID:
        return self._storage.retrieve_guid(name)


class RetrieveAllPeopleUseCase:
    def __init__(self, person_storage: PersonStorage):
        self._storage = person_storage

    def __call__(self) -> Dict[str, UUID]:
        return self._storage.retrieve_all()

class StartNewGameUseCase:
    def __init__(self, person_storage: PersonStorage, deck_storage: DeckStorage, server_creator: GameServerCreator):
        self._person_storage = person_storage
        self._deck_storage = deck_storage
        self._creator = server_creator

    def __call__(self, player_guids: List[UUID]) -> GameServer:
        people = self._person_storage.retrieve_many(player_guids)
        deck = self._deck_storage.get()
        lobby_members = [LobbyMember(name, guid) for name, guid in people.items()]
        game_settings = GameSettings(deck, 1)
        lobby = Lobby(lobby_members[0], game_settings)
        game_server = self._creator.create(lobby)
        return game_server


class StopGameUseCase:
    def __init__(self, game_server: GameServer):
        self._game_server = game_server

    def __call__(self) -> None:
        self._game_server.stop()


def _convert_answer(answer_text: str) -> Answer:
    if answer_text == Answer.ANSWER_A.value:
        return Answer.ANSWER_A
    elif answer_text == Answer.ANSWER_B.value:
        return Answer.ANSWER_B
    elif answer_text == Answer.ANSWER_C.value:
        return Answer.ANSWER_C
    else:
        raise InvalidAnswerValue(answer_text)
