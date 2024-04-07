from game import Game
from const import *

import copy


class Bot:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.best_piece = None
        self.best_move = None

    # creates a copy of the board, makes a move on that copy and evaluates the board too
    def evaluate_move(self, board, move, piece, castling=False):
        temp_board = copy.deepcopy(board)
        temp_board.move(piece, move, testing=True, castling=castling)

        return temp_board.evaluate_board()

    # loops through the board and evaluates each possible move given a depth
    def mini_max(self, board, depth):
        # TODO: implement recursion to find the best move
        player_shorthand = {0: "white", 1: "black"}
        player_mod = 1 if board.counter % 2 == 0 else -1

        if depth == 0:
            return player_mod*board.evaluate_board()

        temp_board = copy.deepcopy(board)
        maxi = -999999999999999999999999999
        for tup in temp_board.calc_color_moves(player_shorthand[temp_board.counter % 2]): 
            piece,move = tup
            temp_board.move(piece, move, testing=True)
            score = -self.mini_max(temp_board, depth=(depth-1))

            if player_mod * score > maxi:
                maxi = score

        return maxi

    def find_best_move(self, board, depth=1):
        a = self.mini_max(board, depth)
        print(a)
        return (self.best_move, self.best_piece)
