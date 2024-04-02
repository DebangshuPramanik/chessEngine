
from const import *
from move import Move

BLACK_START = 0
WHITE_START = 7

class NumberBoard:
    def __init__(self, board):
        self.squares = self.from_board(board)
        self.en_passant = None
        self.white_castle_moved = (False, False, False)
        # Rook, King, Rook
        self.black_castle_moved = (False, False, False)

    def from_board(self, board):
        number_board = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        for row in range(ROWS):
            for col in range(COLS):
                p = board.squares[row][col].piece
                number_board[row][col] = p.piece_id if p else 0
        return number_board

    def evaluate_board(self):
        total = 0
        for cols in self.squares:
            for piece in cols:
                total += piece
        return total

    def at(square):
        row, col = square
        return self.squares[row][col]

    def put(square, piece):
        row, col = square
        self.squares[row][col] = piece

    def _move(self, start, end):
        # start is a (row, col)
        # end is a (row, col)
        moved_piece = self.at(start)
        self.put(end, moved_piece)

    def in_board(self, square):
        row, col = square
        return 0 <= row < 8 and 0 <= col < 8

    def calc_moves(self, square):
        def color(piece):
            if piece == 0: return 0
            piece//abs(piece)
        # calculate all moves for a square
        if self.at(square) == 0: return []
        row, col = square
        pcolor = color(self.at(square))

        def pawn():
            pawn_ranks = [None, 6, 1]
            moves = []
            # row+1, ?row+2, (col+-1, row+1)
            m = (row + 1, col)
            if(self.at(m) == 0):
                moves.append(m)
                m = (row + 2, col)
                if(row == pawn_ranks[color]):
                    if(self.at(m) == 0):
                        moves.append(m)
            m = (row, col + 1)
            if(color(self.at(m)) == -pcolor or m == self.en_passant):
                moves.append(m)
            m = (row, col - 1)
            if(color(self.at(m)) == -pcolor or m == self.en_passant):
                moves.append(m)

            return filter(self.in_board, moves)
        def knight():
            possible_moves = [
                (2, 1), (2, -1), (-2, -1), (-2, 1),
                (1, 2), (1, -2), (-1, -2), (-1, 2)
            ]
            possible_moves = filter(self.in_board, possible_moves)
            moves = filter(lambda m: color(self.at(m)), possible_moves)
        def bishop():
            pass
        def rook():
            pass
        def queen():
            pass
        def king():
            pass
        funcs = [lambda: [], pawn, knight, bishop,
                 rook, queen, king]

        return funcs[abs(self.at(square))]()
