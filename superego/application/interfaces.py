from abc import ABCMeta, abstractmethod
from typing import List, Dict
from uuid import UUID

from superego.game.game import Lobby, Card, Deck, GameSettings


class GameServer(metaclass=ABCMeta):
    @abstractmethod
    def run(self) -> None:
        raise NotImplemented

    @abstractmethod
    def stop(self) -> None:
        raise NotImplemented

    @property
    @abstractmethod
    def address(self):
        raise NotImplemented


class GameServerCreator(metaclass=ABCMeta):
    @abstractmethod
    def create(self, lobby: Lobby) -> GameServer:
        raise NotImplemented


class CardStorage(metaclass=ABCMeta):
    @abstractmethod
    def store(self, card: Card) -> None:
        raise NotImplemented

    @abstractmethod
    def get_all(self) -> List[Card]:
        raise NotImplemented


class PersonStorage(metaclass=ABCMeta):
    @abstractmethod
    def store(self, name: str) -> None:
        raise NotImplemented

    @abstractmethod
    def retrieve_guid(self, name: str) -> UUID:
        raise NotImplemented

    @abstractmethod
    def retrieve_all(self) -> Dict[str, UUID]:
        raise NotImplemented

    @abstractmethod
    def retrieve_many(self, guids: List[UUID]) -> Dict[str, UUID]:
        raise NotImplemented


class DeckStorage(metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> Deck:
        raise NotImplemented
