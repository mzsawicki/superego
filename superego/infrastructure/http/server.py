from aiohttp import web
from sqlalchemy import create_engine

from superego.settings import config
from superego.application.usecases import AddCardUseCase
from superego.infrastructure.database.storage import DataBaseCardStorage
from superego.infrastructure.database.dsn import connection_string


async def db_context(app):
    engine = create_engine(connection_string)
    app['db'] = engine
    yield
    app['db'].close()


async def add_new_card(request):
    with request.app['db'].connect() as connection:
        card_storage = DataBaseCardStorage(connection)
        add_card = AddCardUseCase(card_storage)
        data = await request.post()
        try:
            question = data['question']
            answer_a = data['answer_a']
            answer_b = data['answer_b']
            answer_c = data['answer_c']
        except KeyError as e:
            raise web.HTTPBadRequest(text='Missing data') from e
        add_card(question=question, answer_A=answer_a, answer_B=answer_b, answer_C=answer_c)
    return web.Response()


def run():
    app = web.Application()
    app.router.add_post('/cards', add_new_card)
    app['config'] = config
    app.cleanup_ctx.append(db_context)
    web.run_app(app)