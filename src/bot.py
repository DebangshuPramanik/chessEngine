from const import *
from number_board import NumberBoard
from number_board import Move as NMove
from move import *

import copy


class Bot:
    def __init__(self, player):
        self.player = player
        self.current_best_move = None
        
    # loops through the board and evaluates each possible move given a depth
    def mini_max(self, board, depth):
        maxi = -99999999999999999999
        best_move = None
        player_mod = 1 if board.move_number % 2 == 0 else -1

        if depth == 1: 
            bmove = None
            tboard = board.copy()
            for move in tboard.calc_color_moves(
            player_mod
            ):
                tboard.move(move)

                score = player_mod*board.evaluate_board()

                if score > maxi:
                    maxi = score
                    bmove = move
                tboard.take_back()
            
            return [maxi, best_move]

        temp_board = board.copy()
        for move in temp_board.calc_color_moves(
            player_mod
        ):
            temp_board.move(move)
            score = -self.mini_max(temp_board, depth=(depth - 1))[0]

            if score > maxi:
                maxi = score
                best_move = move
                print(best_move)
            
            temp_board.take_back()
                

        return [maxi, best_move]


    def tbm(self, nb ,m):  # convert a number board move to a board move
        sq = nb.at(m.start)
        eq = nb.at(m.end)
        return Move(sq, eq)

    def find_best_move(self, board, depth=3):
        nb = NumberBoard(board=board)
        l = self.mini_max(nb, depth)
        return self.tbm(board, l[1])
