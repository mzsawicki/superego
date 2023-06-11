from sqlalchemy import create_engine, Engine

from superego.infrastructure.database.dsn import connection_string


def get_db() -> Engine:
    return create_engine(connection_string)