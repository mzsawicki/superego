from superego.infrastructure.websockets.server import WebsocketsServerConfig
from superego.infrastructure.websockets.assemble\
    import assemble_websockets_server
from superego.game.game import Lobby, LobbyMember, GameSettings
from tests.test_deck import test_deck
from uuid import UUID
import logging

HOST = '0.0.0.0'
PORT = 8000
ENCODING = 'utf-8'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    host = LobbyMember('Bob')
    guest_1 = LobbyMember('Alice')
    guest_1._guid = UUID('a7da476f-c81b-4bc7-ac17-e7e675ccc95f')
    guest_2 = LobbyMember('Drew')

    deck = test_deck

    game_settings = GameSettings(deck, 3)

    lobby = Lobby(host, game_settings)
    lobby.add_member(guest_1)
    lobby.add_member(guest_2)

    config = WebsocketsServerConfig(host=HOST, port=PORT, encoding=ENCODING)

    server = assemble_websockets_server(config, lobby)

    server.run()
