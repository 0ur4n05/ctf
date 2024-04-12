import pygame
import random
from Config import config

class Food(pygame.sprite.Sprite):
    def __init__(self, images_dict, selected_key, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.image = images_dict[selected_key]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.bottom = random.randint(20, config.SCREENSIZE[0]-20), -10
        self.speed = random.randrange(5, 10)
        self.type = selected_key

    def update(self):
        self.rect.bottom += self.speed
        if self.rect.top > config.SCREENSIZE[1]:
            return True
        return False