from game import Game
from const import *

import copy


class Bot:
    def __init__(self, player):
        self.player = player
        
    # loops through the board and evaluates each possible move given a depth
    def mini_max(self, board, depth):
        best_move = None
        player_shorthand = {0: "white", 1: "black"}
        player_mod = 1 if board.counter % 2 == 0 else -1

        if depth == 0:
            return player_mod * board.evaluate_board()

        temp_board = board.copy()
        maxi = -999999999999999999999999999
        for move in temp_board.calc_color_moves(
            player_shorthand[temp_board.counter % 2]
        ):
            temp_board.move(move)
            score = -self.mini_max(temp_board, depth=(depth - 1))[0]

            if player_mod * score > maxi:
                maxi = score
                best_move = move
                

        return [maxi, best_move]

    def find_best_move(self, board, depth=1):
        l = self.mini_max(board, depth)
        return l[1]
