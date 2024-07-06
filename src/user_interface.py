# This file will have all of the user input framework from selecting colors to choosing player versus player and player versus computer. 
from tkinter import *
from const import *
import os

# Storing all of the game-related images. 
class Button_Inventory:
    def __init__(self, screen):
        # Pulling all the photos
        self.accept_button_image = PhotoImage(os.path.join("assets/buttons/accept_button.png"))
        self.analysis_button_image = PhotoImage(os.path.join("assets/buttons/analysis_image.png"))
        self.draw_button_image = PhotoImage(os.path.join("assets/buttons/draw_button.png"))
        self.reject_button_image = PhotoImage(os.path.join("assets/buttons/reject_button.png"))
        self.versus_computer_image = PhotoImage(os.path.join("assets/buttons/versus_computer_image.png"))
        self.versus_player_image = PhotoImage(os.path.join("assets/buttons/versus_player_image.png"))
        # Storing all the buttons IN A LIST
        self.buttons_list = self.create_game_buttons()
        self.window = screen

    def create_button(self, image_file, fun, bg_color, fg_color, font, active_bg, active_fg): # Method to create EACH of the buttons. 
        return Button(self.window, file = image_file, command = fun, font = font, fg = fg_color, bg = bg_color, activebackground = active_bg, active_bg = active_fg)
    
    # Button functions! ! ! ! ! !
    def accept_button_fun(self):
        pass
    def analysis_button_fun(self):
        pass
    def draw_button_fun(self):
        pass
    def reject_button_fun(self):
        pass
    def versus_computer_fun(self):
        pass
    def versus_player_fun(self):
        pass
    
    def create_game_buttons(self): # Method to create ALL the buttons. 
        bg_color = '#808080'
        fg_color = '00FFFF'
        font = ('Ink Free', 12, 'bold')
        active_fg = '#FF0000'
        active_bg = 'fffb1f'
        accept_button = self.create_button(self.accept_button_image, self.accept_button_fun, bg_color, fg_color, font, active_bg, active_fg)
        analysis_button = self.create_button(self.analysis_button_image, self.analysis_button_fun, bg_color, fg_color, font, active_bg, active_fg)
        draw_button = self.create_button(self.draw_button_image, self.draw_button_fun, bg_color, fg_color, font, active_bg, active_fg)
        reject_button = self.create_button(self.reject_button_image, self.reject_button_fun, bg_color, fg_color, font, active_bg, active_fg)
        versus_computer_button = self.create_button(self.versus_computer_image, self.versus_computer_fun, bg_color, fg_color, font, active_bg, active_fg)
        versus_player_button = accept_button = self.create_button(self.versus_player_image, self.versus_player_fun, bg_color, fg_color, font, active_bg, active_fg)
        return [accept_button, analysis_button, draw_button, reject_button, versus_computer_button, versus_player_button]
    
    