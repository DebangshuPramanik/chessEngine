from game import Game

from const import *
import copy



class Bot:
    def __init__(self, game):
        self.game = game

    # creates a copy of the board, makes a move on that copy and evaluates the board too
    def evaluate_move(self, move, piece, castling=False):
        temp_board = copy.deepcopy(self.game.board)
        temp_board.move(piece, move, testing=True, castling=castling)

        return temp_board.evaluate_board()

    # loops through the board and evaluates each possible move given a depth
    # currently it's depth=1 so I'll change this later
    def find_best_move(self, board, depth=1):
        # TODO: 
        #   account for who you're playing as, and find the best move as that player (most likely using a dictionary),
        #   implement recursion to a specific depth (and change the default depth while you're at it to 4)
        #   Remember that depth must be an even number if you're playing as white, and an odd number if black


        # Find a better solution later
        max = -999999999999999999999999999
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_team_piece("white"):
                    moves = board.calc_moves(
                        board.squares[row][col].piece, row, col)
                    for move in board.squares[row][col].piece.moves:
                        if self.evaluate_move(move, board.squares[row][col].piece) > max:
                            max = self.evaluate_move(move, board.squares[row][col].piece)

        return max
