from aiohttp import web
from sqlalchemy import create_engine
import json

from superego.infrastructure.settings import config
from superego.application.usecases import AddCardUseCase, AddPersonUseCase, RetrievePersonGUIDUseCase,\
    RetrieveAllPeopleUseCase
from superego.infrastructure.database.storage import DataBaseCardStorage, DataBasePersonStorage
from superego.infrastructure.database.dsn import connection_string


async def db_context(app):
    engine = create_engine(connection_string)
    app['db'] = engine
    yield


async def add_new_card(request):
    with request.app['db'].connect() as connection:
        card_storage = DataBaseCardStorage(connection)
        add_card = AddCardUseCase(card_storage)
        data_raw = await request.text()
        data = json.loads(data_raw)
        try:
            question = data['question']
            answer_a = data['answer_a']
            answer_b = data['answer_b']
            answer_c = data['answer_c']
        except KeyError as e:
            raise web.HTTPBadRequest(text='Missing data') from e
        add_card(question=question, answer_A=answer_a, answer_B=answer_b, answer_C=answer_c)
    return web.Response(status=200)


async def add_new_person(request):
    with request.app['db'].connect() as connection:
        person_storage = DataBasePersonStorage(connection)
        add_person = AddPersonUseCase(person_storage)
        data_raw = await request.text()
        data = json.loads(data_raw)
        try:
            name = data['name']
        except KeyError as e:
            raise web.HTTPBadRequest(text='Missing data') from e
        add_person(name)
    return web.Response(status=200)


async def get_people(request):
    with request.app['db'].connect() as connection:
        person_storage = DataBasePersonStorage(connection)
        retrieve_person_guid = RetrievePersonGUIDUseCase(person_storage)
        retrieve_all_people = RetrieveAllPeopleUseCase(person_storage)
        if 'name' in request.rel_url.query:
            name = request.rel_url.query['name']
            guid = retrieve_person_guid(name)
            return web.json_response({'guid': str(guid)})
        else:
            people = retrieve_all_people()
            content = {name: str(guid) for name, guid in people.items()}
            return web.json_response(content)


def run():
    app = web.Application()
    app.router.add_post('/cards', add_new_card)
    app.router.add_get('/people', get_people)
    app.router.add_post('/people', add_new_person)
    app['config'] = config
    app.cleanup_ctx.append(db_context)
    web.run_app(app)


if __name__ == '__main__':
    run()