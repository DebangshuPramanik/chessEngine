import copy
import os

from math import ceil

from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
from number_board import NumberBoard
from time import time

# This class (the Board class) sets up the board as a 2D array of Square objects, some of them have pieces.
# This is the class that checks whether there is a check on the board, and this is the class used to evaluate all the positions.


class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.number_squares = None
        self.last_move = None
        self.en_passant = None
        self._create()
        self._add_pieces("white")
        self._add_pieces("black")
        self.counter = 0  # Used for FEN and for counting the total number of turns played on the board.
        self.moves = []
        self.played_moves = []
        self.positions = []  # Used to store positions to check for repetition
        self.positions.append(self.position_to_FEN().split(" ")[0])

    # Evaluate function which returns a number: A high positive number means white is winning,
    # a high absolute value negative number means black is winning, and the closer this eval is to a 0, the more even the position is)
    def evaluate_board(self):
        total_eval = 0.0

        # Evaluates the intrinsic value of a Pawn based on its position and squares controlled.
        def pawn_eval(row, col, piece):
            # Getting the moves a piece has (i.e., the squares that it controls)
            moves = self.calc_moves(piece, row, col)

            # Initially, the piece is worth the amount of points it has in the game by default
            eval = piece.value
            # Shorthanding the value sign of a piece.
            vs = piece.value_sign
            # rr measures how many squares the pawn is advanced, it stands for "real row" on the board of the pawn
            rr = row if piece.color == "black" else 8 - row

            if moves != None:
                num_moves = len(
                    moves
                )  # Stores the number of possible moves of the piece in this position.
                increment = num_moves * vs
                if num_moves == 0 or num_moves == None:  # Pawn cannot move
                    eval -= vs * 0.1 * increment
                elif rr < 2:  # Pawn is not advanced.
                    eval -= vs * 0.16 * increment
                elif rr < 3:  # Pawn is advanced 1 square.
                    eval += vs * 0.16 * increment
                elif rr < 5:  # Pawn is advanced 2 or 3 squares.
                    eval += vs * 0.2 * increment
                elif rr < 7:  # Pawn is advanced between 3 squares and 6 squares.
                    eval += vs * 0.1 * increment
                else:  # Pawn is advanced almost to promotion!!!
                    eval += vs * 0.5 * increment
                moves.clear()
            return eval  # Returns the instantaneous positional value of the pawn

        # Evaluates the intrinsic value of a Knight based on its position and squares controlled.
        def knight_eval(row, col, piece):
            # Initially, the piece is worth the amount of points it has in the game by default
            eval = piece.value
            # Shorthanding the value sign of a piece.
            vs = piece.value_sign
            # Getting the list of moves a piece has (i.e., the squares that it controls)
            moves = self.calc_moves(piece, row, col)
            # rr measures how many squares the knight is advanced, it stands for "real row" on the board of the pawn
            rr = row if piece.color == "black" else 8 - row
            if moves != None:
                num_moves = len(
                    moves
                )  # The length of this list would be its total possible moves.
                if num_moves == 8 and (
                    rr >= 2 and rr <= 5 and col >= 2 and col <= 5
                ):  # Centralized knight that controls enemy/empty space
                    eval += vs * 0.2
                if self.two_pieces_of_type_on_board(
                    "knight", piece.color
                ):  # Knight pair bonus
                    eval += vs * 0.2
                if rr >= 2 and rr <= 5 and col >= 2 and col <= 5:  # Centralized knight
                    eval += vs * 0.1
                elif (
                    rr == 1 or col == 1 or rr == 6 or col == 6
                ):  # Edge Knight, but not rim
                    eval -= vs * 0.08
                else:
                    eval -= vs * 0.16  # Rim knight, "A knight on the rim is dim"
                moves.clear()
            return eval  # Returns the instantaneous potential value of the knight

        # Evaluates the intrinsic value of a Bishop based on its position and squares controlled.
        def bishop_eval(row, col, piece):
            # Initially, the piece is worth the amount of points it has in the game by default
            eval = piece.value
            # Shorthanding the value sign of a piece.
            vs = piece.value_sign
            # Getting the list of moves a piece has (i.e., the squares that it controls)
            moves = self.calc_moves(piece, row, col)
            if moves != None:
                num_moves = len(moves)
                if self.two_pieces_of_type_on_board(
                    "bishop", piece.color
                ):  # Power of Bishop Pair
                    eval += vs * 0.25
                if num_moves > 11:  # Bishop has a lot of scope
                    eval += vs * 0.03
                elif num_moves >= 6:  # Bishop has a decent amount of scope
                    eval += vs * 0.2
                elif num_moves >= 4:  # Bishop has little scope
                    eval += vs * 0.05
                else:  # Bishop has no scope.
                    eval -= vs * 0.15
                moves.clear()
            return eval

        # Evaluates the intrinsic value of a Rook based on its position and squares controlled.
        def rook_eval(row, col, piece):
            # Initially, the piece is worth the amount of points it has in the game by default
            eval = piece.value
            # Shorthanding the value sign of a piece.
            vs = piece.value_sign
            # Getting the list of moves a piece has (i.e., the squares that it controls)
            moves = self.calc_moves(piece, row, col)
            if moves != None:
                num_moves = len(moves)
                if self.two_pieces_of_type_on_board("rook", piece.color):
                    eval += 0.3
                if num_moves > 11:  # Rook has a lot of scope
                    eval += vs * 0.03
                elif num_moves >= 6:  # Rook has a decent amount of scope
                    eval += vs * 0.2
                elif num_moves >= 4:  # Rook has little scope
                    eval += vs * 0.05
                else:  # Rook has no scope.
                    eval -= vs * 0.15
                moves.clear()
            return eval

        # Evaluates the intrinsic value of a Queen based on its position and squares controlled.
        def queen_eval(row, col, piece):
            vs = piece.value_sign
            return (
                bishop_eval(row, col, piece)
                - (6 * vs)
                + rook_eval(row, col, piece)
                - (4 * vs)
                + vs
            )  # Rook (5) + Bishop (3) + 1 = Queen (9), * Piece (Points)
            # This works because a queen is literally a rook and bishop in one piece, and worth one more point than a rook and bishop together

        # Evaluates the intrinsic value of a King based on its position and squares controlled.
        def king_eval(row, col, piece):
            eval = 0
            moves = self.calc_moves(piece, row, col)
            pieces = self.get_pieces_and_locs_on_board()[0]
            vs = piece.value_sign
            if moves != None and pieces != None:
                increment = 1 / len(pieces)
                if len(pieces) <= 3:
                    eval += vs * (increment + 0.3)
                elif len(pieces) <= 6:
                    eval += vs * (increment + 0.1)
                else:
                    eval -= vs * increment
                moves.clear()
            return eval

        # Using get_pieces_and_locs_on_board to get the pieces and their prospective rows and columns all in the form of parallel lists
        # These parallel lists are stored in a tuple.
        pieces_rows_cols_tuple = self.get_pieces_and_locs_on_board()
        pieces = pieces_rows_cols_tuple[0]
        rows_list = pieces_rows_cols_tuple[1]
        cols_list = pieces_rows_cols_tuple[2]

        # Traversing through all pieces on board and calculating how much they are worth using their type, location, and eval methods written above
        for i in range(len(pieces)):
            piece = pieces[i]
            row = rows_list[i]
            col = cols_list[i]
            if isinstance(piece, Pawn):
                total_eval += pawn_eval(row, col, piece)
            elif isinstance(piece, Knight):
                total_eval += knight_eval(row, col, piece)
            elif isinstance(piece, Bishop):
                total_eval += bishop_eval(row, col, piece)
            elif isinstance(piece, Rook):
                total_eval += rook_eval(row, col, piece)
            elif isinstance(piece, Queen):
                total_eval += queen_eval(row, col, piece)
            else:
                total_eval += king_eval(row, col, piece)
        return total_eval  # Returns the total eval of the position

    def get_pieces_and_locs_on_board(
        self,
    ):  # Returns all the pieces of the board and the piece's coordinates in a tuple of lists.
        pieces = []
        rows_list = []
        cols_list = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    pieces.append(self.squares[row][col].piece)
                    rows_list.append(row)
                    cols_list.append(col)
        result = (pieces, rows_list, cols_list)
        return result

    def move(self, piece, move, sidebar=None, testing=False, castling=False):
        initial = move.initial
        final = move.final

        # En-passant boolean
        en_passant_empty = self.squares[final.row][final.col].isEmpty()

        if not (testing or castling):
            self.add_move(piece, move)  # note, this adds the piece being taken to move

            # Updating the move count and adding the last made move to the moves list.
            self.counter += 1
            self.last_move = self.moves[-1]
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
                left_rook = self.squares[final.row][0].piece
                right_rook = self.squares[final.row][7].piece
                rook = left_rook if (diff < 0) else right_rook
                rook_start_col = 0 if (diff < 0) else 7
                rook_move = Move(
                    self.at((final.row, rook_start_col)),
                    self.at((final.row, (final.col + initial.col) // 2)),
                )
                self.move(rook, rook_move, castling=True)
                castling_sound.play()
        if move.pawn_move_or_capture():
            self.positions.clear()
        self.positions.append(self.position_to_FEN().split()[0])

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = (move, piece)

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
            (last_move, last_piece) = (
                self.last_move
            )  # Shorthanding self.last_move to last_move
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

            # this was the only thing I could think of for checking if a piece has moved already
            piece.moved = False
            for tup in self.moves:
                p, m, s = tup
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
                    temp_board.calc_moves(p, row, col)
                    # bool is there to prevent infinite looping between in_check() and calc_moves(), as both methods are called within each other.
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

    def check_in_between_move_squares(
        self, piece, move
    ):  # Necessary for some discovered checks where pieces could jump over enemy pieces to block check without this function...
        def there_is_interference(move):
            r = move.final.row
            c = move.final.col
            return self.squares[r][c].has_piece()

        if len(piece.moves) > 0:
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
                    ib_move_final = self.squares[r][c]
                    ib_move = Move(move.initial, ib_move_final)
                    if there_is_interference(ib_move):
                        if move in piece.moves:
                            piece.moves.remove(move)
                            piece.set_addable_moves(False)
                    c += col_step
            # Checks vertical (rook style UP AND DOWN the board!)
            elif col_step != 0:
                for c in range(initial_col + col_step, final_col, col_step):
                    ib_move_final = self.squares[initial_row][c]
                    ib_move = Move(move.initial, ib_move_final)
                    if there_is_interference(ib_move):
                        if move in piece.moves:
                            piece.moves.remove(move)
                            piece.set_addable_moves(False)

            # Checks horizontal (rook style LEFT AND RIGHT on the Board!)
            else:
                for r in range(initial_row, final_row + row_step, row_step):
                    ib_move_final = self.squares[r][initial_col]
                    ib_move = Move(move.initial, ib_move_final)
                    if there_is_interference(ib_move):
                        if move in piece.moves:
                            piece.moves.remove(move)
                            piece.set_addable_moves(False)

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

    def at(self, loc):
        row, col = loc
        return self.squares[row][col]

    def calc_moves(self, piece, row, col):
        loc = (row, col)  # location
        nb = NumberBoard(self)  # Creation of number board
        ms = nb.calc_moves(loc)  # generated moves list.

        def cnmbm(m):  # convert number board to board move
            sq = self.at(m.start)
            eq = self.at(m.end)
            return Move(sq, eq)

        Ms = [cnmbm(m) for m in ms]
        for M in Ms:
            if M.final.has_piece():
                M.set_capture(True)
            if isinstance(M.initial.piece, Pawn):
                M.set_pawn_move(True)
        piece.moves = Ms

    def testcm(self):
        start = time()
        self.calc_color_moves("white")
        end = time()
        return end - start

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
        if isinstance(piece, Pawn):
            move.set_pawn_move(True)
        if move.final.piece:
            move.set_capture(True)
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

    def two_pieces_of_type_on_board(self, piece, color):
        counter = 0
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    other = self.square[row][col].piece
                    if other.color == color and other.name == piece:
                        counter += 1
        return counter >= 2
