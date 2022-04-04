from abc import ABCMeta
from uuid import UUID

from superego.game.game import Lobby, LobbyMember, Deck


class LobbyStorage(metaclass=ABCMeta):
    def store(self, lobby: Lobby) -> None:
        raise NotImplemented

    def __contains__(self, guid: UUID) -> bool:
        raise NotImplemented

    def get(self, guid: UUID) -> Lobby:
        raise NotImplemented


class PersonStorage(metaclass=ABCMeta):
    def store(self, person: LobbyMember) -> None:
        raise NotImplemented

    def __contains__(self, guid: UUID) -> bool:
        raise NotImplemented

    def get(self, guid: UUID) -> LobbyMember:
        raise NotImplemented


class DeckStorage(metaclass=ABCMeta):
    def store(self, deck: Deck) -> None:
        raise NotImplemented

    def __contains__(self, guid: UUID) -> bool:
        raise NotImplemented

    def get(self, guid: UUID) -> Deck:
        raise NotImplemented

