from typing import List, Dict, Tuple
from uuid import UUID

from sqlalchemy import Connection, insert, select, Row, delete

from superego.application.interfaces import CardStorage, PersonStorage, DeckStorage
from superego.game.game import Card, Deck

from superego.infrastructure.database.tables import card as card_table
from superego.infrastructure.database.tables import person


class DataBaseCardStorage(CardStorage):
    def __init__(self, connection: Connection):
        self._connection = connection

    def store(self, card: Card) -> None:
        self._connection.execute(
            insert(card_table).values(
                question=card.question,
                answer_a=card.answer_A,
                answer_b=card.answer_B,
                answer_c=card.answer_C
            )
        )
        self._connection.commit()

    def get_all(self) -> List[Card]:
        result = self._connection.execute(
            select(card_table.c.question, card_table.c.answer_a, card_table.c.answer_b, card_table.c.answer_c)
        )
        cards = [self._convert_row_to_card(row) for row in result]
        return cards

    @staticmethod
    def _convert_row_to_card(row: Row) -> Card:
        question, answer_a, answer_b, answer_c = row
        card = Card(question=question, answer_A=answer_a, answer_B=answer_b, answer_C=answer_c)
        return card


class DataBasePersonStorage(PersonStorage):
    def __init__(self, connection: Connection):
        self._connection = connection

    def store(self, name: str) -> None:
        self._connection.execute(
            insert(person).values(name=name)
        )
        self._connection.commit()

    def retrieve_guid(self, name: str) -> UUID:
        result = self._connection.execute(
            select(person.c.guid).where(person.c.name == name).limit(1)
        )
        for row in result:
            guid = UUID(*row)
            return guid

    def retrieve_all(self) -> Dict[str, UUID]:
        result = self._connection.execute(
            select(person.c.name, person.c.guid)
        )
        pairs = [self._convert_row_to_pair(row) for row in result]
        dict_ = {name: guid for name, guid in pairs}
        return dict_

    def retrieve_many(self, guids: List[UUID]) -> Dict[str, UUID]:
        guids_as_str = [str(guid) for guid in guids]
        result = self._connection.execute(
            select(person.c.name, person.c.guid).where(person.c.guid.in_(guids_as_str))
        )
        pairs = [self._convert_row_to_pair(row) for row in result]
        dict_ = {name: guid for name, guid in pairs}
        return dict_

    def remove(self, guid: UUID) -> None:
        self._connection.execute(
            delete(person).where(person.c.guid == str(guid))
        )
        self._connection.commit()

    @staticmethod
    def _convert_row_to_pair(row: Row) -> Tuple[str, UUID]:
        name, guid_raw = row
        guid = UUID(guid_raw)
        return name, guid


class DatabaseDeckStorage(DeckStorage):
    def __init__(self, connection: Connection):
        self._connection = connection

    def get(self) -> Deck:
        result = self._connection.execute(
            select(card_table.c.question, card_table.c.answer_a, card_table.c.answer_b, card_table.c.answer_c)
        )
        cards = [self._convert_row_to_card(row) for row in result]
        deck = Deck("Default deck", cards)
        return deck

    @staticmethod
    def _convert_row_to_card(row: Row) -> Card:
        question, answer_a, answer_b, answer_c = row
        card = Card(question=question, answer_A=answer_a, answer_B=answer_b, answer_C=answer_c)
        return card

