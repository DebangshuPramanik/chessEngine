import pygame

from const import *
from game import Game
from square import Square
from move import Move
from sidebar import Sidebar
from bot import Bot

# I made a comment for fun.
# So did I
# Now I commented too!


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")
        self.game = Game()
        self.sidebar = Sidebar(self.screen)
        self.bot = Bot(self.game)

    def mousedown(self, event):
        game = self.game
        screen = self.screen
        dragger = game.dragger
        board = game.board

        dragger.update_mouse(event.pos)
        clicked_row = dragger.mouseY // SQSIZE
        clicked_col = dragger.mouseX // SQSIZE

        # Determining if clicked square has a piece
        if board.squares[clicked_row][clicked_col].has_piece():
            piece = board.squares[clicked_row][clicked_col].piece

            # Valid piece, color, making sure you can only play on your turn
            if piece.color == game.next_player:
                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                dragger.save_initial(event.pos)
                dragger.drag_piece(piece)
                # Show methods
                game.show_bg(screen)
                game.show_moves(screen)
                game.show_pieces(screen)

    def mousemotion(self, event):
        game = self.game
        dragger = game.dragger
        # Set hover
        motion_row = event.pos[1] // SQSIZE
        motion_col = event.pos[0] // SQSIZE
        game.set_hover(motion_row, motion_col)

        if dragger.dragging:
            dragger.update_mouse(event.pos)

    def mouseup(self, event):
        game = self.game
        screen = self.screen
        sidebar = self.sidebar
        dragger = game.dragger
        board = game.board

        if dragger.dragging:
            # dragger.update_mouse(event.pos)
            released_row = dragger.mouseY // SQSIZE
            released_col = dragger.mouseX // SQSIZE

            if not (released_col in range(0, 8) and released_col in range(0, 8)):
                dragger.undrag_piece()
                return

            # Create possible move.
            initial = Square(dragger.initial_row, dragger.initial_col)
            final = Square(released_row, released_col)
            move = Move(initial, final)

            # Valid move?
            if board.valid_move(dragger.piece, move):
                # counter to determine which player's turn it is (remove this and update the FEN notation method in the board file if this is unecessary)
                game.board.counter += 1

                # Normal Capture.......
                captured = board.squares[released_row][released_col].has_piece()
                board.move(dragger.piece, move, sidebar)

                # Sound
                game.play_sound(captured)

                # draw/show methods
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_pieces(screen)

                # next turn...
                game.next_turn()

                print(board.evaluate_board())
                print(board.position_to_FEN())
                
                print("Current Score: " + str(board.evaluate_board()))
                print("Score Associated with best move: " + str(self.bot.find_best_move(board)))

        dragger.undrag_piece()
        game.check_game_over()

    def mainloop(self):
        screen = self.screen
        game = self.game
        dragger = game.dragger
        board = game.board
        sidebar = self.sidebar

        while not game.over:
            # Show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_hover(screen)
            game.show_pieces(screen)
            sidebar.show_sidebar()

            if dragger.dragging:
                dragger.update_blit(screen)  # update blit

            for event in pygame.event.get():

                # Click Event (clicking and selecting a piece)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mousedown(event)

                # Mouse Motion event (Dragging pieces)
                elif event.type == pygame.MOUSEMOTION:
                    self.mousemotion(event)

                # Click Release (letting a piece go)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseup(event)

                # Key Press to change Theme or restart
                elif event.type == pygame.KEYDOWN:
                    # if event.key == pygame.K_y:
                    #     board.take_back()  # NOTE: THIS DOES NOT WORK YET!!!!!!!!!! WE NEED TO WORK ON THIS!!!!!!!
                    if event.key == pygame.K_t:
                        game.change_theme()
                    elif event.key == pygame.K_r:
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
# test
