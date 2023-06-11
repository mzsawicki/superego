import json
from uuid import UUID

from aiohttp import web

from superego.application.usecases import AddCardUseCase, AddPersonUseCase, RetrievePersonGUIDUseCase,\
    RetrieveAllPeopleUseCase, StartNewGameUseCase, StopGameUseCase
from superego.application.interfaces import GameServer
from superego.infrastructure.settings import config
from superego.infrastructure.database.storage import DataBaseCardStorage, DataBasePersonStorage, DatabaseDeckStorage
from superego.infrastructure.database.engine import get_db
from superego.infrastructure.websockets.creator import GameServerCreator
from superego.infrastructure.websockets.gameserver import WebsocketsServerConfig


async def db_context(app):
    engine = get_db()
    app['db'] = engine
    yield


class GameServerPool:
    def __init__(self):
        self._instance = None

    def store(self, game_server: GameServer) -> None:
        self._instance = game_server

    def get(self) -> GameServer:
        if not self._instance:
            raise ValueError()
        return self._instance

    def flush(self):
        self._instance = None

    @property
    def is_ongoing(self) -> bool:
        return self._instance is not None

game_server_pool = GameServerPool()

async def game_server_context(app):
    pool = game_server_pool
    app['game_server_pool'] = pool
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

async def remove_person(request):
    with request.app['db'].connect() as connection:
        person_storage = DataBasePersonStorage(connection)


async def get_people(request):
    with request.app['db'].connect() as connection:
        person_storage = DataBasePersonStorage(connection)
        retrieve_person_guid = RetrievePersonGUIDUseCase(person_storage)
        retrieve_all_people = RetrieveAllPeopleUseCase(person_storage)
        if 'name' in request.rel_url.query:
            name = request.rel_url.query['name']
            guid = retrieve_person_guid(name)
            if not guid:
                return web.Response(status=404)
            return web.json_response({'guid': str(guid)})
        else:
            people = retrieve_all_people()
            content = {name: str(guid) for name, guid in people.items()}
            return web.json_response(content)

async def start_game(request):
    with request.app['db'].connect() as connection:
        person_storage = DataBasePersonStorage(connection)
        deck_storage = DatabaseDeckStorage(connection)
        settings = request.app['config']['websockets']
        websockets_config = WebsocketsServerConfig(settings['host'], settings['port'], settings['encoding'])
        game_server_creator = GameServerCreator(websockets_config)
        game_rounds = int(request.app['config']['game']['rounds'])
        start_game_ = StartNewGameUseCase(person_storage, deck_storage, game_server_creator, game_rounds)

        data_raw = await request.text()
        data = json.loads(data_raw)
        try:
            player_guids = [UUID(guid) for guid in data['player_guids']]
        except KeyError as e:
            raise web.HTTPBadRequest(text='Missing data') from e

        game_server = start_game_(player_guids)
        request.app['game_server_pool'].store(game_server)
        game_server.run()
        return web.Response(status=200)

async def ongoing_game(request):
    game_server_pool_: GameServerPool = request.app['game_server_pool']
    if game_server_pool_.is_ongoing:
        game_server = game_server_pool_.get()
        content = {"address": game_server.address}
        return web.json_response(content)
    return web.HTTPNotFound()


async def stop_game(request):
    game_server_pool_: GameServerPool = request.app['game_server_pool']
    game_server = game_server_pool_.get()
    if game_server:
        stop_game_ = StopGameUseCase(game_server)
        stop_game_()
        game_server_pool.flush()
        return web.Response(status=200)
    else:
        return web.Response(status=404)


def run():
    app = web.Application()
    app.router.add_post('/cards', add_new_card)
    app.router.add_get('/people', get_people)
    app.router.add_post('/people', add_new_person)
    app.router.add_post('/game', start_game)
    app.router.add_delete('/game', stop_game)
    app.router.add_get('/game', ongoing_game)
    app['config'] = config
    app.cleanup_ctx.append(db_context)
    app.cleanup_ctx.append(game_server_context)

    host = config['http']['host']
    port = config['http']['port']
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    run()