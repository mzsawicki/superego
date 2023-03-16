import uuid

from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, String

meta = MetaData()

guid_function = lambda: str(uuid.uuid4())

deck = Table(
    'deck', meta,

    Column('id', Integer, primary_key=True),
    Column('guid', String(36), default=guid_function, nullable=False),
    Column('name', String(128), nullable=False)
)

card = Table(
    'card', meta,

    Column('id', Integer, primary_key=True),
    Column('guid', String(36), default=guid_function, nullable=False),
    Column('question', String(2048), nullable=False),
    Column('answer_a', String(256), nullable=False),
    Column('answer_b', String(256), nullable=False),
    Column('answer_c', String(256), nullable=False),
)

person = Table(
    'person', meta,

    Column('id', Integer, primary_key=True),
    Column('guid', String(36), default=guid_function, nullable=False),
    Column('name', String(64), nullable=False)
)