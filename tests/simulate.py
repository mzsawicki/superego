import sys
from datetime import datetime

from tests.utils import create_test_lobby, random_answer, random_guess
from superego.game.game import Game, GameObserver, Clock, GameState


class PrintingObserver(GameObserver):
    def notify_game_state_changed(self, game_state: GameState) -> None:
        print(f'Time: {game_state.time}')
        print(f'Round {game_state.round_number}')
        print(f'Phase: {game_state.phase.value}')
        print(f'Points in bank: {game_state.points_in_bank}')
        print(f'Current question: {game_state.current_card.question}')
        print(f'Players:')
        for player_state in game_state.player_states:
            change = self._format_points_change(player_state.points_change)
            status = f'{player_state.name};' \
                     f' Points: {player_state.points} ({change})'
            if player_state.awaited_to_answer:
                status += ' |NOW ANSWERING|'
            elif player_state.awaited_to_guess:
                status += ' |NOW GUESSING|'
            elif player_state.ready:
                status += ' |READY|'
            print(status)
        print('--------------------------------------------------')

    @staticmethod
    def _format_points_change(change: int) -> str:
        if change > 0:
            return f'+{change}'
        else:
            return str(change)


class SimpleClock(Clock):
    def now(self) -> datetime:
        return datetime.now()


if __name__ == '__main__':
    players_count, rounds_per_player = int(sys.argv[1]), int(sys.argv[2])
    lobby = create_test_lobby(players_count, rounds_per_player)
    game = Game(lobby, SimpleClock(), PrintingObserver())
    while not game.over:
        game.answer(game.current_player, random_answer())
        for guessing_player in game.guessing_players:
            game.guess(guessing_player, random_guess())
        for player in game.players:
            game.mark_ready(player)
