from game import Game
from const import *

import copy


class Bot:
    def __init__(self, game, player):
        self.game = game
        self.player = player

    # creates a copy of the board, makes a move on that copy and evaluates the board too
    def evaluate_move(self, board, move, piece, castling=False):
        temp_board = copy.deepcopy(board)
        temp_board.move(piece, move, testing=True, castling=castling)

        return temp_board.evaluate_board()

    # loops through the board and evaluates each possible move given a depth
    def find_best_move(self, board, depth=2):
        # TODO: implement recursion to find the best move
        score=0
        if depth == 0:
            return board.evaluate_board()

        player_shorthand = {0: "white", 1: "black"}
        player_mod = 1 if self.game.board.counter % 2 == 0 else -1

        temp_board = copy.deepcopy(board)
        best_move = None
        best_piece = None

        # Find a better solution later
        max = -999999999999999999999999999
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_team_piece(
                    player_shorthand[(self.game.board.counter % 2)]
                ):
                    temp_board.calc_moves(temp_board.squares[row][col].piece, row, col)
                    for move in temp_board.squares[row][col].piece.moves:
                        temp_board.move(piece
                        score = self.find_best_move(temp_board, depth=(depth-1))
                        #m,p = evaluated_move

                        #score = evalute_move(temp_board, m, p)

                        if player_mod * score > max:
                            max = player_mod * score
                            best_move = m
                            best_piece = p

        return evaluated_move
