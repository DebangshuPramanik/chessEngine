import pygame
import copy
import os

from math import ceil

from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound

# Could someone write a short description of this class up here?


class Board:

    # rudimentary bot stuff
    def evaluate_board(self):
        total = 0
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    total += self.squares[row][col].piece.value
        return total

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self.en_passant = None
        self._create()
        self._add_pieces("white")
        self._add_pieces("black")
        self.counter = 0
        self.moves = []

    def move(self, piece, move, sidebar=None, testing=False, castling=False):
        initial = move.initial
        final = move.final

        # En-passant boolean
        en_passant_empty = self.squares[final.row][final.col].isEmpty()

        if not (testing or castling):
            self.add_move(piece, move)  # note, this adds the piece being taken to move

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        self.en_passant = None
        # For all moves but 1 type, en_passant is not allowed.

        if isinstance(piece, Pawn):
            # en passant capture
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                # console board move update
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(os.path.join("assets/sounds/capture.wav"))
                    sound.play()
            elif (
                not testing and abs(final.row - initial.row) == 2
            ):  # this can be an elif, cause you wont move 2 squares to a promotion
                self.en_passant = ((final.row + initial.row) // 2, final.col)
            else:
                # pawn promotion
                # don't need to check for castling, because that is not a pawn move
                if not testing:
                    assert sidebar != None
                    self.check_promotion(piece, final, sidebar)

        # king castling
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                castling_sound = Sound(os.path.join("assets/sounds/castle.wav"))
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1], castling=True)
                castling_sound.play()

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final, sidebar):
        if (final.row == 0 and piece.color == "white") or (
            final.row == 7 and piece.color == "black"
        ):
            # The tutorial showed only how to get a queen promotion using the uncommented version of the line below. I however, wanted all promotion options
            # self.squares[final.row][final.col].piece = Queen(piece.color)
            k = Knight(piece.color)
            b = Bishop(piece.color)
            r = Rook(piece.color)
            q = Queen(piece.color)
            choices = [k, b, r, q]
            selected_piece = None

            selected_piece = sidebar.get_promotion(choices)

            self.squares[final.row][final.col].piece = selected_piece
            promotion_sound = Sound(os.path.join("assets/sounds/promote.wav"))
            promotion_sound.play()

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_rival_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    # bool is there to prevent infinite looping between in_check() and calc_moves(), as both methods are called within each other.
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

    def calc_moves(self, piece, row, col, bool=True):
        """
        Calculate all the possible (valid) moves of an specific piece on a specific position
        """

        # NB. There was an error w/ piece moves (found w/ en passant) where if
        # you checked a pieces moves, and then did not move it, the added moves
        # would remain until you moved the piece.  This allowed en passant (and
        # other moves) to persist after it should no longer be possible, it had
        # been checked and availible, but that piece had not been played.
        piece.clear_moves()

        def pawn_moves():
            # steps
            steps = 1 if piece.moved else 2

            def normal_pawn_moves():
                # vertical moves
                start = row + piece.dir
                end = row + (piece.dir * (1 + steps))
                for possible_move_row in range(start, end, piece.dir):
                    if Square.in_range(possible_move_row):
                        if self.squares[possible_move_row][col].isEmpty():
                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(possible_move_row, col)
                            # create a new move
                            move = Move(initial, final)
                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)
                        # blocked
                        else:
                            break
                    # not in range
                    else:
                        break
                # diagonal moves
                possible_move_row = row + piece.dir
                possible_move_cols = [col - 1, col + 1]
                for possible_move_col in possible_move_cols:
                    if Square.in_range(possible_move_row, possible_move_col):
                        if self.squares[possible_move_row][
                            possible_move_col
                        ].has_rival_piece(piece.color):
                            # create initial and final move squares
                            initial = Square(row, col)
                            final_piece = self.squares[possible_move_row][
                                possible_move_col
                            ].piece
                            final = Square(
                                possible_move_row, possible_move_col, final_piece
                            )
                            # create a new move
                            move = Move(initial, final)

                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)

            # en passant moves
            def en_passant_moves():
                ir = 3 if piece.color == "white" else 4  # ir = initial row
                if self.en_passant == None:
                    return
                # There is a square that can be en passanted to.
                er, ec = self.en_passant
                # Are we taking the right color?
                if not (row == ir):
                    return  # Our starting row is not right for our color
                # Yes. Are we diagonal to it?
                if not (abs(row - er) == 1 and abs(col - ec) == 1):
                    return

                # check potential checks
                move = Move(Square(row, col), Square(er, ec))
                if bool:
                    if not self.in_check(piece, move):
                        piece.add_move(move)
                else:
                    piece.add_move(move)

            normal_pawn_moves()
            en_passant_moves()

        def knight_moves():
            # 8 possible moves
            possible_moves = [
                (row - 2, col + 1),
                (row - 1, col + 2),
                (row + 1, col + 2),
                (row + 2, col + 1),
                (row + 2, col - 1),
                (row + 1, col - 2),
                (row - 1, col - 2),
                (row - 2, col - 1),
            ]
            # Finding valid moves
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][
                        possible_move_col
                    ].isEmpty_or_rival(piece.color):
                        # create squares of the new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][
                            possible_move_col
                        ].piece
                        final = Square(
                            possible_move_row, possible_move_col, final_piece
                        )
                        # create new move
                        move = Move(initial, final)

                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)

        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # create squares of the possible new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][
                            possible_move_col
                        ].piece
                        final = Square(
                            possible_move_row, possible_move_col, final_piece
                        )
                        # create a possible new move
                        move = Move(initial, final)

                        # empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].isEmpty():
                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)

                        # has enemy piece = add move + break
                        elif self.squares[possible_move_row][
                            possible_move_col
                        ].has_rival_piece(piece.color):
                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                                    break
                            else:
                                # append new move
                                piece.add_move(move)
                                break

                        # has team piece = break
                        elif self.squares[possible_move_row][
                            possible_move_col
                        ].has_team_piece(piece.color):
                            break

                    # not in range
                    else:
                        break

                    # incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            adjs = [
                (row - 1, col + 0),  # up
                (row - 1, col + 1),  # up-right
                (row + 0, col + 1),  # right
                (row + 1, col + 1),  # down-right
                (row + 1, col + 0),  # down
                (row + 1, col - 1),  # down-left
                (row + 0, col - 1),  # left
                (row - 1, col - 1),  # up-left
            ]

            # normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][
                        possible_move_col
                    ].isEmpty_or_rival(piece.color):
                        # create squares of the new move
                        rival_piece = self.squares[possible_move_row][possible_move_col].piece
                        initial = Square(row, col)
                        final = Square(
                            possible_move_row, possible_move_col, rival_piece
                        )  # piece=piece
                        # create new move
                        move = Move(initial, final)
                        # check potencial checks
                        if bool:
                            if (
                                not self.in_check(piece, move)
                            ) and final.isEmpty_or_rival(piece.color):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

            # castling moves
            if not piece.moved:
                # queen castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            # castling is not possible because there are pieces in between ?
                            if self.squares[row][c].has_piece():
                                break

                            if c == 3:
                                # adds left rook to king
                                piece.left_rook = left_rook

                                # rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                # check potencial checks
                                if bool:
                                    if not self.in_check(
                                        piece, moveK
                                    ) and not self.in_check(left_rook, moveR):
                                        # append new move to rook
                                        left_rook.add_move(moveR)
                                        # append new move to king
                                        piece.add_move(moveK)
                                else:
                                    # append new move to rook
                                    left_rook.add_move(moveR)
                                    # append new move king
                                    piece.add_move(moveK)

                # king castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            # castling is not possible because there are pieces in between ?
                            if self.squares[row][c].has_piece():
                                break

                            if c == 6:
                                # adds right rook to king
                                piece.right_rook = right_rook

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)

                                # check potencial checks
                                if bool:
                                    if not self.in_check(
                                        piece, moveK
                                    ) and not self.in_check(right_rook, moveR):
                                        # append new move to rook
                                        right_rook.add_move(moveR)
                                        # append new move to king
                                        piece.add_move(moveK)
                                else:
                                    # append new move to rook
                                    right_rook.add_move(moveR)
                                    # append new move king
                                    piece.add_move(moveK)

        if isinstance(piece, Pawn):
            pawn_moves()

        elif isinstance(piece, Knight):
            knight_moves()

        elif isinstance(piece, Bishop):
            straightline_moves(
                [
                    (-1, 1),  # up-right
                    (-1, -1),  # up-left
                    (1, 1),  # down-right
                    (1, -1),  # down-left
                ]
            )

        elif isinstance(piece, Rook):
            straightline_moves(
                [
                    (-1, 0),  # up
                    (0, 1),  # right
                    (1, 0),  # down
                    (0, -1),  # left
                ]
            )

        elif isinstance(piece, Queen):
            straightline_moves(
                [
                    (-1, 1),  # up-right
                    (-1, -1),  # up-left
                    (1, 1),  # down-right
                    (1, -1),  # down-left
                    (-1, 0),  # up
                    (0, 1),  # right
                    (1, 0),  # down
                    (0, -1),  # left
                ]
            )

        elif isinstance(piece, King):
            king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == "white" else (1, 0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # Adding the kings
        self.squares[row_other][4] = Square(row_other, 4, King(color))

    # Position to FEN for future use
    def position_to_FEN(self):
        # Crappy temporary solution I thought of while waiting for my bus
        map_num = {
            0: "",
            1: "1",
            2: "2",
            3: "3",
            4: "4",
            5: "5",
            6: "6",
            7: "7",
            8: "8",
        }
        FEN = ""
        for row in range(ROWS):
            count = 0
            for col in range(COLS):
                # If the square has a piece, append the column number and the piece according to the name_to_shorthand function in piece.py
                if self.squares[row][col].has_piece():
                    FEN += map_num[count]
                    FEN += self.squares[row][col].piece.name_to_shorthand(
                        self.squares[row][col].piece.name,
                        self.squares[row][col].piece.color,
                    )
                    count = 0
                    pieceHere = True
                else:
                    count += 1
            if not pieceHere:
                FEN += "8"
            if row != 7:
                FEN += "/"
            pieceHere = False

        player = "w" if self.counter % 2 == 0 else "b"
        FEN += " " + player

        TURN = ceil(self.counter / 2)
        FEN += " " + str(TURN)
        return FEN

    def add_move(self, piece, move):
        piece_taken = self.squares[move.final.row][move.final.col].piece
        move.final.piece = piece_taken
        self.moves.append((piece, move))  # feels hacky

    def move_to_pgn(self, board_move):
        # TODO: handle castling, and specifying which piece moved when neccessary
        # (NB. specifying which piece will need to be done in add_move probably)
        # (it needs the board state when/before the move is done)
        # board_move should be of the form (piece, move)
        def place_shorthand(final):
            return Square.get_alphacol(final.col) + str(final.row)

        piece, move = board_move
        init = move.initial
        final = move.final
        if final.piece != None:
            return piece.shorthand + "x" + place_shorthand(final)
        else:
            return piece.shorthand + place_shorthand(final)

    def moves_to_pgn(self):
        pass
