from const import *
from number_board import NumberBoard
from number_board import Move as NMove
from move import *


class Bot:
    def __init__(self, player):
        self.player = player
        self.current_best_move = None
        
    # loops through the board and evaluates each possible move given a depth
    def mini_max(self, board, depth):
        maxi = -99999999999999999999
        best_move = None
        player_mod = 1 if board.move_number % 2 == 0 else -1

        if depth == 0:
            return [player_mod*board.evaluate_board(), best_move]

        temp_board = board.copy()
        for move in temp_board.calc_color_moves(
            player_mod
        ):
            board.move(move)
            score = -self.mini_max(temp_board, depth=(depth - 1))[0]

            if score > maxi:
                maxi = score
                best_move = move
            
            board.take_back()
                

        return [maxi, best_move]

    def tbm(self, nb ,m):  # convert a number board move to a board move
        sq = nb.at(m.start)
        eq = nb.at(m.end)
        return Move(sq, eq)

    def find_best_move(self, board, depth=1):
        nb = NumberBoard(board=board)
        l = self.mini_max(nb, depth)
        return self.tbm(board, l[1])
