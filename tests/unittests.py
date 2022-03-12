from superego.game.game import\
    Answer,\
    Guess,\
    Game

from tests.utils import create_test_lobby, ArtificialClock, ObserverStub


def test_won_bet_executed_correctly():
    lobby = create_test_lobby(3, 1)
    game = Game(lobby, ArtificialClock(), ObserverStub())
    current_player_answer = Answer.ANSWER_A
    game.answer(game.current_player, current_player_answer)
    guessing_player_1, guessing_player_2 = game.guessing_players
    guessing_player_1_initial_points = guessing_player_1.points
    game.guess(guessing_player_1, Guess(answer=current_player_answer, bet=2))
    game.guess(guessing_player_2, Guess(answer=Answer.ANSWER_B, bet=2))
    guessing_player_1_valid_points = guessing_player_1_initial_points + 2
    assert guessing_player_1_valid_points == guessing_player_1.points


def test_lost_bet_executed_correctly():
    lobby = create_test_lobby(3, 1)
    game = Game(lobby, ArtificialClock(), ObserverStub())
    current_player_answer = Answer.ANSWER_A
    game.answer(game.current_player, current_player_answer)
    guessing_player_1, guessing_player_2 = game.guessing_players
    guessing_player_2_initial_points = guessing_player_2.points
    game.guess(guessing_player_1, Guess(answer=current_player_answer, bet=2))
    game.guess(guessing_player_2, Guess(answer=Answer.ANSWER_B, bet=2))
    guessing_player_2_valid_points = guessing_player_2_initial_points - 2
    assert guessing_player_2_valid_points == guessing_player_2.points


