import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move

# I made a comment for fun.


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")
        self.game = Game()

    def check_game_over(self):
        game = self.game
        total_moves = []
        total_moves.append(self.get_total_moves("white"))
        print(total_moves)
        if len(total_moves) == 0:
            game.display_winner("black")
            game.set_game_over(True)
        total_moves = []
        total_moves.append(self.get_total_moves("black"))
        print(total_moves)
        if len(total_moves) == 0:
            game.display_winner("white")
            game.set_game_over(True)

    def get_total_moves(self, color):
        total_moves = []
        for row in range(ROWS):
            for col in range(COLS):
                if (
                    self.game.board.squares[row][col].has_piece()
                    and self.game.board.squares[row][col].piece.color == color
                ):
                    piece = self.game.board.squares[row][col].piece
                    total_moves.append(piece.moves)
        return total_moves

    def mainloop(self):
        screen = self.screen
        game = self.game
        dragger = game.dragger
        board = game.board

        while game.over == False:
            # Show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_hover(screen)
            game.show_pieces(screen)

            if dragger.dragging:
                dragger.update_blit(screen)  # update blit

            for event in pygame.event.get():

                # Click Event (clicking and selecting a piece)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE
                    # Determining if clicked square has a piece
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece

                        # Valid piece, color, making sure you can only play on your turn
                        if piece.color == game.next_player:
                            self.check_game_over()
                            board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            # Show methods
                            game.show_bg(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                # Mouse Motion event (Dragging pieces)
                elif event.type == pygame.MOUSEMOTION:
                    # Set hover
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE
                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        # Show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_hover(screen)
                        game.show_pieces(screen)
                        dragger.update_blit(screen)

                # Click Release (letting a piece go)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        if not (
                            released_col in range(0, 8) and released_col in range(0, 8)
                        ):
                            dragger.undrag_piece(piece)
                            continue

                        # Create possible move.
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        # Valid move?
                        if board.valid_move(dragger.piece, move):
                            # Normal Capture.......
                            captured = board.squares[released_row][
                                released_col
                            ].has_piece()
                            board.move(dragger.piece, move, screen)

                            board.set_true_en_passant(dragger.piece)

                            # Sound
                            game.play_sound(captured)

                            # draw/show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)

                            # next turn...
                            game.next_turn()

                    dragger.undrag_piece(piece)

                # Key Press to change Theme or restart
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        game.change_theme()
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        dragger = game.dragger
                        board = game.board

                # Quit Application
                elif event.type == pygame.QUIT:
                    game.end_the_game()
            pygame.display.update()
        game.end_the_game()


main = Main()
main.mainloop()
