from typing import List

from sqlalchemy import Connection, insert

from superego.application.storage import CardStorage
from superego.game.game import Card

from superego.infrastructure.database.tables import card as card_table

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
        pass