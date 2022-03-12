from superego.application.app import App
from superego.infrastructure.server import WebSocketsServer


HOST = '0.0.0.0'
PORT = 8000

if __name__ == '__main__':
    print(f'Starting game server on: ws://{HOST}:{PORT}')
    app = App(WebSocketsServer(HOST, PORT))
    app.start()
    print('Game server stopped. Shutting down.')
