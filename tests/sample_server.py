from superego.infrastructure.websockets.server import WebsocketsServerConfig
from superego.infrastructure.websockets.assemble\
    import assemble_websockets_server
from superego.game.game import Lobby, LobbyMember, GameSettings
from tests.test_deck import test_deck
from uuid import UUID, uuid4
import logging

HOST = '0.0.0.0'
PORT = 8000
ENCODING = 'utf-8'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    host = LobbyMember('Bob')
    host._guid = UUID('f19b26d2-d146-422c-a952-d45cfc276b85')
    guest_1 = LobbyMember('Alice')
    guest_1._guid = UUID('a7da476f-c81b-4bc7-ac17-e7e675ccc95f')
    guest_2 = LobbyMember('Drew')
    guest_2._guid = UUID('d3299cf9-3305-41e9-b2b1-bfdd3e22a7c2')
    guest_3 = LobbyMember('Mary')
    guest_3._guid = uuid4()
    guest_4 = LobbyMember('Mike')
    guest_4._guid = uuid4()
    guest_5 = LobbyMember('Gary')
    guest_5._guid = uuid4()
    

    deck = test_deck

    game_settings = GameSettings(deck, 3)

    lobby = Lobby(host, game_settings)
    lobby.add_member(guest_1)
    lobby.add_member(guest_2)
    lobby.add_member(guest_3)
    lobby.add_member(guest_4)
    lobby.add_member(guest_5)

    config = WebsocketsServerConfig(host=HOST, port=PORT, encoding=ENCODING)

    server = assemble_websockets_server(config, lobby)

    server.run()
