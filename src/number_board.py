from const import *
from move import Move
import copy

BLACK_START = 0
WHITE_START = 7
PST = [None, WHITE_START, BLACK_START]  # Piece STart


def color(piece):
    if piece == 0:
        return 0
    piece // abs(piece)


class NumberBoard:
    def __init__(self, board=None):
        if board:
            self.squares = self.from_board(board)
        self.en_passant = None  # MUST BE: a tuple of (row, col)
        self.white_castle_moved = [False, False, False]
        # Rook, King, Rook
        self.black_castle_moved = [False, False, False]
        self.castle_moved = [None, self.white_castle_moved, self.black_castle_moved]
        self.move_number = 0

    def from_board(self, board):
        number_board = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        for row in range(ROWS):
            for col in range(COLS):
                p = board.squares[row][col].piece
                number_board[row][col] = p.piece_id if p else 0
        return number_board

    def copy(self):
        nb = NumberBoard()
        nb.squares = [row[:] for row in self.squares]
        nb.en_passant = copy.deepcopy(self.en_passant)
        nb.white_castle_moved = self.white_castle_moved[:]
        nb.black_castle_moved = self.black_castle_moved[:]
        return nb

    def evaluate_board(self):
        total = 0
        for cols in self.squares:
            for piece in cols:
                total += piece
        return total

    def at(self, square):
        row, col = square
        return self.squares[row][col]

    def put(self, square, piece):
        row, col = square
        self.squares[row][col] = piece

    def _move(self, start, end):
        # start is a (row, col)
        # end is a (row, col)
        moved_piece = self.at(start)
        self.put(end, moved_piece)

    def move(self, start, end, promote=None):
        # p is the piece being moved
        # ep is the current en_passant square, when this move was made
        # ir, ic, fr & fc are the initial and final rows and columns
        p = self.at(start)
        ep = self.en_passant  # saved for pawn checks
        ir, ic = start
        fr, fc = end
        self.en_passant = None
        assert p != 0
        self._move(start, end)
        if promote:  # sanity check
            assert promote in range(2, 6)

        if abs(p) == 1:  # Pawn
            diff = fc - ic
            if diff != 0 and end == ep:
                # If a pawn took onto en_passant square,
                # delete the pawn that was next to it.
                self.put((ir, ic + diff), 0)
            elif abs(fr - ir) == 2:
                self.en_passant = ((fr + ir) // 2, fc)  # avg of start and end is middle
            else:
                pr = [None, 0, 7]  # promotion rows
                if fr == pr[color(p)]:
                    self.put(end, promote * color(p))
                    # Promote must be positive if it exists (see above assert)
        elif abs(p) == 6:  # King
            self.castle_moved[color(p)][1] = True
            diff = fc - ic
            if abs(diff) == 2:  # king moved 2(sideways). must be a castle
                rc = 0 if diff < 0 else 7  # rook column
                self.move((rc, ir), (abs(fc - ic // 2), ir))
                # rook goes to avg of where king was/is
        elif abs(p) == 4:  # Rook
            if (ic == 0 or ic == 7) and ir == PST[color(p)]:  #
                self.castle_moved[color(p)][(0 if ic == 0 else 2)] = True

    def in_board(self, square):
        row, col = square
        return 0 <= row < 8 and 0 <= col < 8

    def places_in_board(self, moves):
        return [m for m in moves if self.in_board(m)]

    def calc_moves(self, square):
        def color(piece):
            if piece == 0:
                return 0
            return piece // abs(piece)

        # calculate all moves for a square
        if self.at(square) == 0:
            return []
        row, col = square
        pcolor = color(self.at(square))

        def pawn():
            print("Pawn")
            pawn_ranks = [None, 6, 1]
            moves = []
            # row+1, ?row+2, (col+-1, row+1)
            d = -pcolor
            m = (row + d, col)
            if self.at(m) == 0:
                moves.append(m)
                m = (row + (d * 2), col)
                if row == pawn_ranks[pcolor]:
                    if self.at(m) == 0:
                        moves.append(m)
            m = (row + d, col + 1)
            if color(self.at(m)) == -pcolor or m == self.en_passant:
                moves.append(m)
            m = (row + d, col - 1)
            if color(self.at(m)) == -pcolor or m == self.en_passant:
                moves.append(m)

            return [move for move in moves if self.in_board(move)]

        def knight():
            possible_moves = [
                (row + 2, col + 1),
                (row + 2, col - 1),
                (row - 2, col - 1),
                (row - 2, col + 1),
                (row + 1, col + 2),
                (row + 1, col - 2),
                (row - 1, col - 2),
                (row - 1, col + 2),
            ]
            possible_moves = self.places_in_board(possible_moves)
            return [m for m in possible_moves if color(self.at(m)) != pcolor]

        def bishop():
            moves = []
            moves.extend(straight_line_moves((1, 1)))
            moves.extend(straight_line_moves((-1, 1)))
            moves.extend(straight_line_moves((1, -1)))
            moves.extend(straight_line_moves((-1, -1)))
            return moves

        def rook():
            moves = []
            moves.extend(straight_line_moves((1, 0)))
            moves.extend(straight_line_moves((0, 1)))
            moves.extend(straight_line_moves((-1, 0)))
            moves.extend(straight_line_moves((0, -1)))
            return moves

        def queen():
            moves = []
            moves.extend(rook())
            moves.extend(bishop())

        def king():
            possible_moves = [
                (row + 1, col - 1),
                (row + 1, col + 0),
                (row + 1, col + 1),
                (row + 0, col - 1),
                (row + 0, col + 1),
                (row - 1, col - 1),
                (row - 1, col + 0),
                (row - 1, col + 1),
            ]

            possible_moves = self.places_in_board(possible_moves)
            if not self.castle_moved[pcolor][1]:
                if (
                    not self.castle_moven[pcolor][0]
                    and self.at((row, col - 1)) == 0
                    and self.at((row, col - 2)) == 0
                ):
                    possible_moves.append((row, col - 2))
                if (
                    not self.castle_moven[pcolor][2]
                    and self.at((row, col + 1)) == 0
                    and self.at((row, col + 2)) == 0
                ):
                    possible_moves.append((row, col + 2))

            return [m for m in possible_moves if (self.at(m)) != pcolor]

        def straight_line_moves(direction):
            moves = []
            drow, dcol = direction
            mrow, mcol = row, col
            mrow += drow
            mcol += dcol
            while self.in_board((mrow, mcol)):
                p = self.at((mrow, mcol))

                if color(p) == 0:
                    moves.append((mrow, mcol))
                elif color(p) == pcolor:
                    break
                elif -1 * color(p) == pcolor:  # p is rival color
                    moves.append((mrow, mcol))
                    break
                mrow += drow
                mcol += dcol
            return moves

        funcs = [lambda: [], pawn, knight, bishop, rook, queen, king]

        return [
            m for m in funcs[abs(self.at(square))]() if not self.in_check(square, m)
        ]

    def in_check(self, start, end):
        return False
