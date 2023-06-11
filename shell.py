#!python3

import argparse
from uuid import UUID

from superego.application.usecases import RetrieveAllPeopleUseCase, AddPersonUseCase, RemovePersonUseCase
from superego.infrastructure.database.engine import get_db
from superego.infrastructure.database.storage import DataBasePersonStorage
from superego.infrastructure.http.server import run as run_http_server


db = get_db().connect()
people_storage = DataBasePersonStorage(db)

retrieve_all_people = RetrieveAllPeopleUseCase(people_storage)
add_person = AddPersonUseCase(people_storage)
remove_person = RemovePersonUseCase(people_storage)


def show_people() -> None:
    people = retrieve_all_people()
    for name, guid in people.items():
        print(f'{name} ({guid})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='SuperEgo', description='SuperEgo server control')
    subparsers = parser.add_subparsers(required=True, dest='command')

    # People
    people_parser = subparsers.add_parser('people', help='Players management')
    people_subparsers = people_parser.add_subparsers(required=True, metavar='people subcommand',
                                                     dest='people_subcommand')
    people_show_parser = people_subparsers.add_parser('show', help='Show existing players')
    people_add_parser = people_subparsers.add_parser('add', help='Add player')
    people_add_parser.add_argument('name', type=str, action='store')
    people_remove_parser = people_subparsers.add_parser('remove', help='Remove player')
    people_remove_parser.add_argument('guid', type=UUID, action='store')

    # Server
    server_parser = subparsers.add_parser('server', help='HTTP server management')
    server_subparsers = server_parser.add_subparsers(required=True, metavar='server subcommand',
                                                     dest='server_subcommand')
    server_run_parser = server_subparsers.add_parser('start', help='Start HTTP server')

    # Game
    game_parser = subparsers.add_parser('game', help='Game session management (requires HTTP server running)')
    game_subparsers = game_parser.add_subparsers(required=True, metavar='game subcommand', dest='game_subcommand')
    game_check_parser = game_subparsers.add_parser('check', help='Check if there is ongoing game session')
    game_show_parser = game_subparsers.add_parser('show', help='Show ongoing game state')
    game_start_parser = game_subparsers.add_parser('start', help='Start game session')
    game_stop_parser = game_subparsers.add_parser('stop', help='Stop and close game session')

    args = parser.parse_args()

    match args.command:
        case 'people':
            match args.people_subcommand:
                case 'show':
                    show_people()
                case 'add':
                    add_person(args.name)
                case 'remove':
                    remove_person(args.guid)
                case _:
                    print(f'Unknown subcommand: {args.people_subcommand}')
        case 'server':
            match args.server_subcommand:
                case 'start':
                    run_http_server()
                case _:
                    print(f'Unknown subcommand: {args.server_subcommand}')

        case 'game':
            pass