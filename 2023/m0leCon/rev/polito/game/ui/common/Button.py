import os
import pygame
from Config import config

class Button:
    def __init__(self, text, x, y, screen, font, width=200, height=50):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.button_normal = pygame.image.load(os.path.join(config.ui_dir, 'red_button01.png'))
        self.button_hover = pygame.image.load(os.path.join(config.ui_dir, 'red_button00.png'))


        self.hovered = False
        self.screen = screen
        self.font = font

    def draw(self):
        RED = (255, 0, 0)
        WHITE = (255, 255, 255)

        if self.hovered:
            self.screen.blit(self.button_hover, (self.x, self.y))
            text = self.font.render(self.text, True, RED)
        else:
            self.screen.blit(self.button_normal, (self.x, self.y))
            text = self.font.render(self.text, True, WHITE)

        text_rect = text.get_rect(center=((self.x + self.width / 2)-5, self.y + self.height / 2))
        self.screen.blit(text, text_rect)