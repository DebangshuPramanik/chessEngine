import pygame
import sys

from board import Board
from const import *
from dragger import Dragger
from config import Config
from square import Square


class Game:
    def __init__(self):
        self.board = Board()
        self.dragger = Dragger()
        self.next_player = "white"
        self.hovered_sqr = None
        self.config = Config()
        self.over = False
        self.winner = None

        # Show methods (background and pieces respectively)

    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):
                # Color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # Rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # Blit
                pygame.draw.rect(surface, color, rect)

                # Row coordinates (chess notation board labels by ranks)
                if col == 0:
                    # color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(str(ROWS - row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)
                # Column coordinates (chess notation board labels by files)
                if row == 7:
                    # color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)
        new_rect = (800, 0, 200, 800)
        pygame.draw.rect(surface, (255, 255, 255), new_rect)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    # All pieces except dragger pieces
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = (
                            col * SQSIZE + SQSIZE // 2,
                            row * SQSIZE + SQSIZE // 2,
                        )
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme
        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all possible moves, and then blit them
            for move in piece.moves:
                # color
                color = (
                    theme.moves.light
                    if (move.final.row + move.final.col) % 2 == 0
                    else theme.moves.dark
                )
                # rect
                rect = (
                    move.final.col * SQSIZE,
                    move.final.row * SQSIZE,
                    SQSIZE,
                    SQSIZE,
                )
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                # color
                color = (
                    theme.trace.light
                    if (pos.row + pos.col) % 2 == 0
                    else theme.trace.dark
                )
                # rect
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            # color
            color = (180, 180, 180)
            # rect
            rect = (
                self.hovered_sqr.col * SQSIZE,
                self.hovered_sqr.row * SQSIZE,
                SQSIZE,
                SQSIZE,
            )
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    # other methods
    def next_turn(self):
        self.next_player = "white" if self.next_player == "black" else "black"

    def set_hover(self, row, col):
        if row in range(0, 8) and col in range(0, 8):
            self.hovered_sqr = self.board.squares[row][col]
        else:
            self.hovered_sqr = None

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()

    def end_the_game(self):
        pygame.quit()
        sys.exit()

    def check_game_over(self):
        # To do: fix stalemate. It ends the game, but doesn't display the message.
        # Necessary Lists that are traversed to check for checks, and then for stalemate or checkmate, whichever occurs on the board
        total_black_moves = 0
        total_white_moves = 0
        black_pieces = []
        black_last_moves = []
        white_pieces = []
        white_last_moves = []

        # Shorthanding self.board to board
        board = self.board

        # Traversing through the board, calculating the moves of every piece alive, maybe this can be reduced in length to reduce lag???
        for row in range(ROWS):
            for col in range(COLS):
                # Fills up the initialized lists with all the information it is supposed to contain.
                if board.squares[row][col].has_piece():
                    piece = board.squares[row][col].piece
                    board.calc_moves(
                        piece, row, col, bool=True
                    )  # Without a shadow of a doubt, this is the line that causes the lag...if there is any
                    moves = piece.moves
                    if piece.color == "black":
                        total_black_moves += len(moves)
                        black_pieces.append(piece)
                        if len(moves) >= 1:
                            black_last_moves.append(moves[-1])
                    else:
                        total_white_moves += len(moves)
                        white_pieces.append(piece)
                        if len(moves) >= 1:
                            white_last_moves.append(moves[-1])

        # Use of lists to determine checkmate or stalemate if one side has no moves..
        # moves_bool is a boolean made to store a condition throughout the for loops below: whether or not there are any moves. 
        if total_black_moves == 0:
            for a_piece in black_pieces:
                    if a_piece.name == "king":
                            black_king = piece
                            if board.in_check(black_king, board.last_move):
                                self.dispay_winner("White")
                            else:
                                self.display_stalemate()
            self.over = True    

        elif total_white_moves == 0:
            for a_piece in white_pieces:
                    if a_piece.name == "king":
                            white_king = piece
                            if board.in_check(white_king, board.last_move):
                                self.dispay_winner("Black")
                            else:
                                self.display_stalemate()
            self.over = True    

        # To do: implement 50-move rule. Checkmate and stalemate are coded.
        # To do: make this method less laggy, or find a way to use more threads.
        # To do: implement draw by insufficient material


    def dispay_winner(self, color):
        self.winner = color
        print(f"{self.winner} has won the game")

    def display_stalemate(self):
        print("The game is a draw by stalemate!")
