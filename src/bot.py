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
    # currently it's depth=1 so I'll change this later
    def find_best_move(self, board, depth=2):
        # TODO: implement recursion to find the best move

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
                        # if(depth >  0):
                        #     temp = copy.deepcopy(temp_board)
                        #    temp.move(temp.squares[row][col].piece, move, testing=True, sidebar=None)
                        #    self.find_best_move(temp, depth=(depth-1))
                        evaluated_move = self.evaluate_move(
                            temp_board, move, temp_board.squares[row][col].piece
                        )
                        if player_mod * evaluated_move > max:
                            max = player_mod * evaluated_move
                            best_move = move
                            best_piece = temp_board.squares[row][col].piece

        return [best_move, best_piece]
