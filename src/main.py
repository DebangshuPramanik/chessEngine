import pygame

from const import *
from game import Game
from square import Square
from move import Move
from sidebar import Sidebar
from bot import Bot
from piece import *
from other_bot import find_best_move
from number_board import NumberBoard
from time import time

class Main:
    def __init__(self):
        # Note: the main game screen is referred to as self.screen, as it was the primary and only screen when we started the project
                                                # and is too ubiquitously used to replace everywhere
        # Pygame and game screen initialization
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")

        # Game and Bot initialization
        self.game = Game()
        self.sidebar = Sidebar(self.screen)
        self.bot = Bot("black")
        self.bot_playing = False
        self.bot_index = 0

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
                board.calc_moves(piece, clicked_row, clicked_col)
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

            if (not (released_col in range(0, 8) and released_row in range(0, 8))) or (released_col in range(0, 8) and not released_row in range(0, 8)):
                dragger.undrag_piece()
                return

            # Create possible move.
            initial = Square(dragger.initial_row, dragger.initial_col)
            final = Square(released_row, released_col)
            move = Move(initial, final)

            # Valid move?
            if board.valid_move(dragger.piece, move):

                # Normal Capture.......
                captured = board.squares[released_row][released_col].has_piece()
                if captured:
                    move.set_capture(True)
                piece = dragger.piece
                if isinstance(piece, Pawn):
                    move.set_pawn_move(True)
                board.move(dragger.piece, move, sidebar)

                # Sound
                game.play_sound(captured)

                # if the bot is playing, make it's move and then move on
                if self.bot_playing:
                    start = time()
                    best_move = find_best_move(board=board)
                    end = time()
                    print("found best move in "+str(end-start)+" seconds")
                    captured = board.squares[best_move.final.row][
                        best_move.final.col
                    ].has_piece()
                    best_piece = best_move.initial.piece

                    board.move(best_piece, best_move, sidebar)

                    game.play_sound(captured)
                    game.next_turn()

                # draw/show methods
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_pieces(screen)

                # print(board.evaluate_board())

                # next turn...
                game.next_turn()

                # print(board.position_to_FEN())
                # print(board.move_to_pgn(board.moves[-1]))

        dragger.undrag_piece()
        game.check_game_over()

    def main_loop(self):
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
                    if event.key == pygame.K_y:
                        board.take_back()
                        game.next_turn()
                    if event.key == pygame.K_t:
                        game.change_theme()
                    elif event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        dragger = game.dragger
                        board = game.board
                    # toggles whether you're playing against the bot
                    elif event.key == pygame.K_b:
                        game.reset()
                        game = self.game
                        dragger = game.dragger
                        board = game.board
                        self.bot_playing = True if self.bot_index % 2 == 0 else False
                        self.bot_index += 1
                    elif event.key == pygame.K_n:
                        nb = NumberBoard(board=game.board)
                        print(nb.testcm())
                        print(str(nb.evaluate_board()))

                # Quit Application
                elif event.type == pygame.QUIT:
                    game.end_the_game()
            pygame.display.update()
        game.end_the_game(screen)

    def start_loop(self):  # Start screen loop; this will render the start screen
        font = pygame.font.SysFont(
            "Times New Roman", 20
        )  # Setting the font of this screen.
        screen = pygame.display.set_mode((800, 800))  # Creating new screen

        # Colors in tuples
        sky_blue = (135, 206, 235)  
        black = (0, 0, 0)
        blue = (0, 0, 128)
        golden = (255, 215, 0)
        light_green = (144, 238, 144)
        light_gray = (211, 211, 211)

        # Background rect
        bg_rect = (
            0, 
            0, 
            800, 
            800
        )
        pygame.draw.rect(screen, light_gray, bg_rect)

        # Creating the 'play vs player', or pvp, game button
        pvp_button_rect = (
            25,
            25,
            250,
            250
        )  # rect is created with parameters in this order: x, y, length, and height; x and y are of top left corner
        pygame.draw.rect(screen, sky_blue, pvp_button_rect)
        pvp_button_text = font.render("Play vs Player", True, black, sky_blue)

        # Creating the 'play with computer', or pvc, game button
        pvc_button_rect = (
            300, 
            75,
            150,
            150
        )
        pygame.draw.rect(screen, golden, pvc_button_rect)
        pvc_button_text = font.render("Play vs Computer", True, black, golden)

        # Creating the 'analysis' button
        analysis_button_rect = (
            180, 
            300, 
            150, 
            150
        )
        pygame.draw.rect(screen, light_green, analysis_button_rect)
        analysis_button_text = font.render("Analyze a game!", True, black, light_green)

        # Start screen loop to run the screen. 
        while True:
            screen.blit(pvp_button_text, pvp_button_rect)
            screen.blit(pvc_button_text, pvc_button_rect)
            screen.blit(analysis_button_text, analysis_button_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                x, y = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONUP:
                    if(75 <= y <= 225): # Checking for clicking of player v. player or player v. computer buttons
                        if(150 <= x <= 225): # Player v. Player button
                            self.__init__() # Quickly restarts program, since this is how the program starts
                            return self.main_loop() # Starts the game main loop. 
                        elif(300 <= x <= 450): # Player v. computer button activated
                            self.__init__()
                            self.bot_playing = True # Starts the main game with the computer having been chosen. 
                            return self.main_loop()
                    elif((180 <= x <= 330) and (300 <= y <= 450)):
                        self.__init__()
                        return self.analysis_loop()
            pygame.display.update()

    def selection_loop(self):
        pass

    def end_loop(self):  # Ending screen loop
        pass

    def analysis_loop(self):  # Analysis screen loop
        print("analysis")
        pygame.quit()



# Creation of a main object before running the game's main loop (the game itself).
main = Main()
main.start_loop()