import pygame
import copy
import os

from math import ceil

from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound

# This class (the Board class) sets up the board as a 2D array of Square objects, some of them have pieces.
# This is the class that checks whether there is a check on the board, and this is the class used to evaluate all the positions.


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
        self.counter = 0  # Used for FEN and for counting the total number of turns played on the board.
        self.moves = []
        self.played_moves = []

    def move(self, piece, move, sidebar=None, testing=False, castling=False):
        initial = move.initial
        final = move.final

        # En-passant boolean
        en_passant_empty = self.squares[final.row][final.col].isEmpty()

        if not (testing or castling):
            self.add_move(piece, move)  # note, this adds the piece being taken to move
            self.counter += 1
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
            ):  # this can be an elif, because you wont move 2 squares to a promotion
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
        self.last_move = (move, piece)

        # add the last move to the list of played_moves
        self.played_moves.append(self.last_move)

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

    def take_back(self):
        if (
            len(self.moves) >= 1
        ):  # Checking that at least one move has been played, to ensure that undoing a move is possible
            (last_move,last_piece) = self.last_move  # Shorthanding self.last_move to last_move
            final = last_move.final
            piece = last_piece  # Storing initial and final squares of last_move
            initial = last_move.initial
            captured_piece = None

            if final.piece:
                captured_piece = last_move.final.piece        

            # console board move update
            self.squares[final.row][final.col].piece = None
            self.squares[initial.row][initial.col].piece = piece
            move = Move(
                final, initial
            )  # Undoes last move by reversing initial and final positions.
            self.move(piece, move, testing=True)
            self.moves.pop()
            self.counter -= 1
            
            #this was the only thing I could think of for checking if a piece has moved already
            piece.moved = False
            for tup in self.moves:
                p,m,s = tup
                if piece == p:
                    piece.moved = True
                    break

            # put captured piece on final square
            self.squares[final.row][final.col].piece = captured_piece

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def in_check(
        self, piece, move
    ):  # Used to determine whether a move will result in the king being taken, and if so, that move is not appended.
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

    def check_in_between_move_squares(
        self, piece, move
    ):  # Necessary for some discovered checks where pieces could jump over enemy pieces to block check without this function...
        piece.set_addable_moves(True)

        def check_for_interference(move):
            r = move.final.row
            c = move.final.col
            if self.squares[r][c].has_piece():
                return True
            return False

        if (
            isinstance(piece, Bishop)
            or isinstance(piece, Rook)
            or isinstance(piece, Queen)
        ) and (len(piece.moves) > 0):
            initial_row = move.initial.row
            initial_col = move.initial.col

            final_row = move.final.row
            final_col = move.final.col

            if final_col != initial_col and final_row != initial_row:
                # Sets up steps in terms of rows and columns
                row_step = (abs(final_row - initial_row)) // (final_row - initial_row)
                col_step = (abs(final_col - initial_col)) // (final_col - initial_col)
            elif final_col != initial_col:
                row_step = 0
                col_step = (abs(final_col - initial_col)) // (final_col - initial_col)
            elif final_row != initial_row:
                row_step = (abs(final_row - initial_row)) // (final_row - initial_row)
                col_step = 0
            else:
                row_step = 0
                col_step = 0

            # Checks diagonal (bishop style) moves for any interfering pieces.
            if (col_step != 0) and (row_step != 0):
                for r in range(initial_row + row_step, final_row, row_step):
                    c = initial_col + col_step
                    ib_move_final = Square(r, c)
                    ib_move = Move(move.initial, ib_move_final)
                    if check_for_interference(ib_move):
                        if move in piece.moves:
                            piece.moves.remove(move)
                    c += col_step
            # Checks vertical (rook style UP AND DOWN the board!)
            elif col_step != 0:
                for c in range(initial_col + col_step, final_col, col_step):
                    ib_move_final = Square(initial_row, c)
                    ib_move = Move(move.initial, ib_move_final)
                    if check_for_interference(ib_move):
                        if move in piece.moves:
                            piece.moves.remove(move)

            # Checks horizontal (rook style LEFT AND RIGHT on the Board!)
            else:
                for r in range(initial_row, final_row + row_step, row_step):
                    ib_move_final = Square(r, initial_col)
                    ib_move = Move(move.initial, ib_move_final)
                    if check_for_interference(ib_move):
                        if move in piece.moves:
                            piece.moves.remove(move)

    def check_in_check(
        self, color
    ):  # Checks if a color (white or black) is currently in check, RIGHT NOW, ON THE ORIGINAL GAME BOARD
        opponent_color = "black" if color == "white" else "white"
        pieces = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    piece = self.squares[row][col].piece
                    if piece.color == opponent_color:
                        pieces.append(piece)
        for piece in pieces:
            for m in piece.moves:
                if m.final.has_rival_piece(opponent_color):
                    if isinstance(m.final.piece, King):
                        return True
        return False

    def calc_moves(self, piece, row, col, bool=True):
        """
        Calculate all the possible (valid) moves of a specific piece on a specific position
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
                            move.set_pawn_move(True)
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
                            move.set_pawn_move_and_capture(True)
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
                move.set_pawn_move_and_capture(True)
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
                        if isinstance(final_piece, Piece):
                            move.set_capture(True)
                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
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

                        if isinstance(final_piece, Piece):
                            move.set_capture(True)
                        # empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].isEmpty():
                            # check potential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new moves
                                    piece.add_move(move)
                            else:
                                # append new moves
                                piece.add_move(move)

                        # has enemy piece = add move + break
                        elif self.squares[possible_move_row][
                            possible_move_col
                        ].has_rival_piece(piece.color):
                            # check potential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new moves
                                    piece.add_move(move)
                                    break
                            else:
                                # append new moves
                                piece.add_move(move)
                                break

                        # has team piece = break
                        elif self.squares[possible_move_row][
                            possible_move_col
                        ].has_team_piece(piece.color):
                            break
                        for move in piece.moves:
                            if self.check_in_check(piece.color):
                                # generate in-between moves and make sure pieces can't "jump".
                                self.check_in_between_move_squares(piece, move)
                    # not in range
                    else:
                        break

                    # incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():

            def normal_king_moves():
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
                            rival_piece = self.squares[possible_move_row][
                                possible_move_col
                            ].piece
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

            def check_castling(direction):
                # castling moves
                if not piece.moved:
                    left_rook = self.squares[row][0].piece
                    right_rook = self.squares[row][7].piece
                    if direction == "queenside":
                        rook = left_rook
                        start_col = 1  # the start_col and end_col are the columns for which we want to check for pieces between king and rook.
                        end_col = 4  # Castling should not be valid if there are pieces between them.
                        king_end_col = 2  # Final column where king will end up if castles queenside is played.
                        rook_start_col = 0  # Left rook is being moved if castles queenside, from its starting position
                        rook_end_col = (
                            king_end_col + 1
                        )  # Left rook's final position is the square to the right of the castled king.
                    else:
                        rook = right_rook
                        start_col = 5  # the start_col and end_col are the columns for which we want to check for pieces between king and rook.
                        end_col = 7  # Castling should not be valid if there are pieces between them.
                        king_end_col = 6  # Final column where king will end up if castles kingside is played.
                        rook_start_col = 7  # Right rook is being moved if castles kingside, from its starting position
                        rook_end_col = (
                            king_end_col - 1
                        )  # Right rook's final position is the square to the left of the castled king.
                    if isinstance(rook, Rook):
                        if not rook.moved:
                            for c in range(start_col, end_col):
                                # castling is not possible because there are pieces in between, as checked for by this if statement.
                                if self.squares[row][c].has_piece():
                                    break
                                if c == 3:
                                    piece.left_rook = rook  # If squares checked for queenside castling are clear, set left rook to left rook of king to allow castling in move()
                                    rook = piece.left_rook
                                if c == 6:
                                    piece.right_rook = rook  # If squares checked for kingside castling are clear, set right rook to right rook of king to allow castling in move()
                                    rook = piece.right_rook
                                # rook move
                                initial = Square(row, rook_start_col)
                                final = Square(row, rook_end_col)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, king_end_col)
                                moveK = Move(initial, final)
                                move_direction = -1 if direction == "queenside" else 1
                                through_move = Move(  # For checking the square between the king and its end position: if that square is covered by the opponent, you can't castle.
                                    initial, Square(row, col + move_direction)
                                )

                                # check potencial checks
                                if bool:
                                    if (
                                        not self.in_check(piece, moveK)
                                        and not self.in_check(rook, moveR)
                                        and not self.in_check(piece, through_move)
                                        and self.squares[row][
                                            king_end_col
                                        ].isEmpty()  # Checking that the destination castling square for the king is indeed empty.
                                        and self.squares[row][
                                            rook_end_col
                                        ].isEmpty()  # Checking that the destination castling square for the rook is indeed empty.
                                    ):
                                        # append new move to rook
                                        rook.add_move(moveR)
                                        # append new move to king
                                        piece.add_move(moveK)
                                else:
                                    # append new move to rook
                                    rook.add_move(moveR)
                                    # append new move king
                                    piece.add_move(moveK)

            def castling_moves():
                check_castling("queenside")
                check_castling("kingside")

            normal_king_moves()
            castling_moves()

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
        pieceHere = False
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

    def others_can_do(self, piece, end):
        ret = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    p = self.squares[row][col].piece
                    if type(piece) == type(p) and piece != p:
                        self.calc_moves(p, row, col)
                        for m in p.moves:
                            if m.final == end:
                                ret.append(((row, col), p))
        return ret

    def add_move(self, piece, move):
        piece_taken = self.squares[move.final.row][move.final.col].piece
        move.final.piece = piece_taken
        others = self.others_can_do(piece, move.final)
        same_row = False
        same_col = False
        do_row = False
        do_col = False
        print(others)
        if others:
            for o in others:
                orow, ocol = o[0]
                if orow == move.initial.row:
                    same_row = True
                if ocol == move.initial.col:
                    same_col = True

            do_col = not same_col
            do_row = same_col
            if same_col and same_row:
                do_col = True
        specifiers = {"row": do_row, "col": do_col}
        print(specifiers)
        self.moves.append((piece, move, specifiers))  # feels hacky

    def move_to_pgn(self, board_move):
        def place_shorthand(final):
            return Square.get_alphacol(final.col) + str(8 - final.row)

        piece, move, s = board_move
        init = move.initial
        final = move.final

        if isinstance(piece, King):
            if self.castling(init, final):
                if init.col - final.col > 0:
                    return "O-O-O"
                else:
                    return "O-O"

        piece_full_shorthand = ""
        if s["col"]:
            piece_full_shorthand += Square.get_alphacol(init.col)
        if s["row"]:
            piece_full_shorthand += str(init.row)
        piece_full_shorthand += piece.shorthand
        if final.piece != None:
            return piece_full_shorthand + "x" + place_shorthand(final)
        else:
            return piece_full_shorthand + place_shorthand(final)

    def moves_to_pgn(self):
        pass

    def two_kings_on_board(self):
        # Prelude to chesskers: if any king is taken, the game ends
        all_colors = ["white", "black"]
        colors = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    piece = self.squares[row][col].piece
                    if isinstance(piece, King):
                        colors.append(piece.color)
        for a_color in all_colors:
            if a_color not in colors:
                return False
        return True

    def accumulate_pieces(self, fun):
        # note: fun must always return a list
        acc = []
        for row in self.squares:
            for square in row:
                if square.has_piece():
                    acc.extend(fun(square.piece))
        return acc

    def map_pieces(self, fun):
        acc = []
        for row in self.squares:
            for square in row:
                if square.has_piece():
                    acc.append(fun(square.piece))
        return acc

    def accumulate_piece_coords(self, fun):
        # note, fun must always return a list
        acc = []
        for row in self.squares:
            for square in row:
                if square.has_piece():
                    acc.extend(fun(square.piece, square.row, square.col))
        return acc

    def calc_color_moves(self, color):
        def get_moves(piece, row, column):
            if piece.color != color:
                return []
            self.calc_moves(piece, row, column)
            return [(piece, move) for move in piece.moves]

        return self.accumulate_piece_coords(get_moves)
