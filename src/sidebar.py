#!/usr/bin/env python3

import pygame

from config import Config
from const import *

class Sidebar:
    def __init__(self, screen):
        self.move_list = []
        self.screen = screen
    def add_move(self, piece, move):
        move_list.append(move)
    def show_sidebar(screen):
        pass

    def get_promotion(self, pieces):
        def icons_from_pieces(pieces):
            icons = []
            it = 0
            for piece in pieces:
                piece.set_texture(size=80)
                img = pygame.image.load(piece.texture)
                img_center = (8 + it % 2) * SQSIZE + SQSIZE // 2, (
                    it // 2
                ) * SQSIZE + SQSIZE // 2
                piece.texture_rect = img.get_rect(center=img_center)
                icons.append((img, piece.texture_rect))
                it += 1
            return icons
        screen = self.screen
        icons = icons_from_pieces(pieces)
        selected_piece = None
        while selected_piece not in pieces:
            for icon in icons:
                screen.blit(icon[0], icon[1])
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = pygame.mouse.get_pos()
                    if (8 * SQSIZE) <= x <= (9 * SQSIZE):
                        if 0 <= y <= SQSIZE:
                            selected_piece = pieces[0]
                        elif SQSIZE <= y <= SQSIZE * 2:
                            selected_piece = pieces[2]
                    elif 9 * SQSIZE <= x <= (10 * SQSIZE):
                        if 0 <= y <= SQSIZE:
                            selected_piece = pieces[1]
                        elif SQSIZE <= y <= SQSIZE * 2:
                            selected_piece = pieces[3]
        return selected_piece
