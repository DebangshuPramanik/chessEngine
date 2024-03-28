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
    def find_best_move(self, board, depth=1):
        # TODO: 
        #   account for who you're playing as, and find the best move as that player (most likely using a dictionary),
        #   implement recursion to a specific depth (and change the default depth while you're at it to 4)
        #   Remember that depth must be an even number if you're playing as white, and an odd number if black

        player_shorthand = {0:"white", 1:"black"}

        player_mod = 1 if self.game.board.counter % 2 == 0 else -1

        temp_board = copy.deepcopy(board)

        # Find a better solution later
        max = -999999999999999999999999999
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_team_piece(player_shorthand[(self.game.board.counter % 2)]):
                    moves = temp_board.calc_moves(
                        temp_board.squares[row][col].piece, row, col)
                    for move in temp_board.squares[row][col].piece.moves:
                        if player_mod*self.evaluate_move(temp_board, move, temp_board.squares[row][col].piece) > max:
                            max = player_mod * self.evaluate_move(board, move, temp_board.squares[row][col].piece)

        return player_mod * max
