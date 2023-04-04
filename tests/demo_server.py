from superego.infrastructure.websockets.gameserver import WebsocketsServerConfig
from superego.infrastructure.websockets.creator \
    import assemble_websockets_server
from superego.game.game import GameSettings, Lobby, LobbyMember
from tests.demo_deck import demo_deck
from uuid import UUID
import logging

HOST = '0.0.0.0'
PORT = 8000
ENCODING = 'utf-8'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    host = LobbyMember('Wicek')
    host._guid = UUID('f19b26d2-d146-422c-a952-d45cfc276b85')
    guest_1 = LobbyMember('Sissi')
    guest_1._guid = UUID('a7da476f-c81b-4bc7-ac17-e7e675ccc95f')
    guest_2 = LobbyMember('ILikeKetchup')
    guest_2._guid = UUID('d3299cf9-3305-41e9-b2b1-bfdd3e22a7c2')
    guest_3 = LobbyMember('OwiesJadalnyDlaKota')

    deck = demo_deck

    game_settings = GameSettings(deck, 3)

    lobby = Lobby(host, game_settings)
    lobby.add_member(guest_1)
    lobby.add_member(guest_2)
    lobby.add_member(guest_3)

    config = WebsocketsServerConfig(host=HOST, port=PORT, encoding=ENCODING)

    server = assemble_websockets_server(config, lobby)

    server.run()