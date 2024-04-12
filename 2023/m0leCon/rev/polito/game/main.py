import pygame
import os
import ctypes

from market import Market
from ui.common.Popup import Popup
from ui.common.Button import Button
from Wrappers import PolitoWrapper, GameWrapper
from game import Game

from Config import config

class PolitoPay2Win():

    def __init__(self):

        menu_items = ["Start Game", "Market", "Pay2Win", "Quit"]

        self.selected_item = None

        self.__load_library()
        self.screen = config.screen
        font = pygame.font.Font(config.fonts['normal'], 20)

        self.buttons = [Button(item, 300, 200 + i * 70, self.screen, font) for i, item in enumerate(menu_items)]

        self.screen = config.screen

    def run(self):
        self.running = True
        
        while config.game_running and self.running:
            self.__draw_ui()
            self.__handle_events()

        # Quit Pygame
        pygame.quit()

    def __draw_ui(self):
        background = pygame.image.load(os.path.join(config.image_dir, 'bck_menu.png'))
        self.screen.blit(background, (0, 0))

        # Draw menu buttons
        for button in self.buttons:
            button.draw()
        font_big = pygame.font.Font(config.fonts['normal'], 35)
        # Header with game name
        game_name_text = font_big.render("PoliTO P2W", True, config.COLORS['white'])
        game_name_rect = game_name_text.get_rect(center=(config.SCREENSIZE[0] // 2, 100))
        
        self.screen.blit(game_name_text, game_name_rect)

        # author note
        copyright_text = pygame.font.Font(None, 20).render("@syscall", True, config.COLORS['black'])
        copyright_rect = copyright_text.get_rect(topright=(config.SCREENSIZE[0] - 10, config.SCREENSIZE[1]-20))
        self.screen.blit(copyright_text, copyright_rect)

        pygame.display.flip()


    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                for button in self.buttons:
                    if button.x < x < button.x + button.width and button.y < y < button.y + button.height:
                        button.hovered = True
                        self.selected_item = button.text
                    else:
                        button.hovered = False
                # if all buttons are not hovered, then set selected_item to None
                if all([not button.hovered for button in self.buttons]):
                    self.selected_item = None   
            if event.type == pygame.MOUSEBUTTONDOWN and self.selected_item:
                if self.selected_item == "Start Game":
                    game = Game(self.clib, self.game_instance)
                    game.run()
                elif self.selected_item == "Market":
                    market = Market(self.clib, self.game_instance)
                    print(self.game_instance)
                    market.run()
                elif self.selected_item == "Pay2Win":
                    popup = Popup(self.screen, "Pay2Win", "Not yet implemented, sorry.", "You have to play. Or no?")
                    popup.screen = self.screen
                    popup.run()

                elif self.selected_item == "Quit":
                    self.running = False




    def __load_library(self):
        ext = '.dll' if os.name == 'nt' else '.so'
        path = os.path.join(config.lib_dir, 'libgame' + ext)

        print("meme")
        self.clib = ctypes.CDLL(path)
        game_init = self.clib.polito_init
        print(game_init)
        game_init.restype = ctypes.c_void_p
        game_init.argtypes = []
        self.game_address = self.clib.polito_init()
        self.game_instance = PolitoWrapper.from_address(self.game_address) 

        self.__set_library_types()
        
    def __set_library_types(self):

        self.clib.market_buy.restype = ctypes.c_ubyte
        self.clib.market_buy.argtypes = [ctypes.POINTER(PolitoWrapper), ctypes.c_int]

        self.clib.game_decrease_lives.restype = ctypes.c_int
        self.clib.game_decrease_lives.argtypes = [ctypes.POINTER(GameWrapper)]

        self.clib.game_increase_money.restype = ctypes.c_int
        self.clib.game_increase_money.argtypes = [ctypes.POINTER(GameWrapper)]

        self.clib.game_reset.restype = ctypes.c_int
        self.clib.game_reset.argtypes = [ctypes.POINTER(GameWrapper)]
        




# Main loop
if __name__ == "__main__":
    pygame.init()
    # Create the Pygame window
    screen = pygame.display.set_mode((config.SCREENSIZE[0], config.SCREENSIZE[1]))
    pygame.display.set_caption("PoliTO Pay 2 Win")
    config.set_screen(screen)

    game = PolitoPay2Win()
    game.run()
    
