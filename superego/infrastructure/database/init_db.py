from sqlalchemy import create_engine, MetaData

from superego.infrastructure.database.tables import deck, card, person
from superego.infrastructure.database.dsn import connection_string

def create_tables(engine_):
    meta = MetaData()
    meta.create_all(bind=engine_, tables=[deck, card, person])

if __name__ == '__main__':
    engine = create_engine(connection_string)
    create_tables(engine)