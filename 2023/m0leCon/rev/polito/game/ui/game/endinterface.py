
import pygame
import os

from Config import config

class EndInterface:
    def __init__(self, game_money, total_money):
        self.game_money = game_money
        self.total_money = total_money
        self.action = 'None'

    def show(self):
        font_big = pygame.font.Font(config.fonts['normal'], 30)
        font_small = pygame.font.Font(None, 25)
        

        text_title = font_big.render(f"You lose", True, (255, 0, 0))
        text_title_rect = text_title.get_rect()
        text_title_rect.centerx = config.screen.get_rect().centerx
        text_title_rect.centery = config.screen.get_rect().centery - 100

        text_tip = font_small.render(f"Enter Q to go back to menu or Enter R to restart game", True, (0, 0, 0))
        text_tip_rect = text_tip.get_rect()
        text_tip_rect.centerx = config.screen.get_rect().centerx
        text_tip_rect.centery = config.screen.get_rect().centery + 60


        text_money = font_small.render(f"You got {self.game_money} marks", True, (0, 0, 0))
        text_money_rect = text_money.get_rect()
        text_money_rect.centerx = config.screen.get_rect().centerx
        text_money_rect.centery = config.screen.get_rect().centery + 90

        text_money2 = font_small.render(f"You have {self.total_money} total marks", True, (0, 0, 0))
        text_money_rect2 = text_money2.get_rect()
        text_money_rect2.centerx = config.screen.get_rect().centerx
        text_money_rect2.centery = config.screen.get_rect().centery + 120




        while self.action == 'None':
            bck_menu = os.path.join(config.image_dir, 'bck_menu.png')
            background = pygame.image.load(bck_menu)
            config.screen.blit(background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.action = 'menu'
                    elif event.key == pygame.K_r:
                        self.action = 'restart'
            config.screen.blit(text_title, text_title_rect)
            config.screen.blit(text_tip, text_tip_rect)
            config.screen.blit(text_money, text_money_rect)
            config.screen.blit(text_money2, text_money_rect2)
            pygame.display.flip()