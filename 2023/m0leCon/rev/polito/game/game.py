import pygame

from ui.game.hero import Hero
from ui.game.food import Food
from ui.game.endinterface import EndInterface

import random
import os

from Config import config
from Wrappers import GameWrapper


class Game():

    ENTITY_POINT = 'thirty'
    ENTITY_DAMAGE = 'seventeen'

    IMAGE_PATHS_DICT = {
        ENTITY_POINT: os.path.join(config.image_dir, ENTITY_POINT + '.png'),
        ENTITY_DAMAGE: os.path.join(config.image_dir, ENTITY_DAMAGE + '.png'),
        'hero': [],
    }

    for i in range(1, 11):
        IMAGE_PATHS_DICT['hero'].append(os.path.join(config.sprite_dir , '%d.png' % i))
    
    def __init__(self, clib, poli):
        pygame.init()
        self.font = pygame.font.Font(config.fonts['normal'], 20)


        self.clib = clib
        self.game_instance = GameWrapper.from_address(poli.game) 
        self.polito = poli
        self.is_running = True

    def __draw_ui(self):
        # get screen width and height
        config.screen.fill(0)
        bck_img = pygame.image.load(os.path.join(config.image_dir, 'bck_game.png'))
        config.screen.blit(pygame.transform.scale(bck_img, (config.SCREENSIZE[0], config.SCREENSIZE[1])), (0, 0))
        header_img = os.path.join(config.image_dir, 'header.png')
        img = pygame.image.load(header_img)

        config.screen.blit(pygame.transform.scale(img, (200, 50)), (0, 0))
        score_text = f'Marks: {self.game_instance.money}'
        score_text = self.font.render(score_text, True, (0,0,0))
        score_rect = score_text.get_rect()
        score_rect.topleft = [15, 12]
        config.screen.blit(score_text, score_rect)

        # draw image container for lives
        config.screen.blit(pygame.transform.scale(img, (200, 50)), (config.SCREENSIZE[0]-200, 0))
        lives_text = f'Lives: {self.game_instance.lives}'
        lives_text = self.font.render(lives_text, True, (0,0,0))
        lives_rect = lives_text.get_rect()
        lives_rect.topright = [config.SCREENSIZE[0]-75, 12]
        config.screen.blit(lives_text, lives_rect)

    def __handle_events(self, hero):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            hero.move(config.SCREENSIZE, 'left')
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            hero.move(config.SCREENSIZE, 'right')

    def __load_assets(self):
        game_images = dict()
        for key, value in self.IMAGE_PATHS_DICT.items():
            if isinstance(value, list):
                game_images[key] = list()
                for path in value: game_images[key].append(pygame.image.load(path))
            else:
                game_images[key] = pygame.image.load(value)
        return game_images

    def __reset_game(self):
        self.clib.game_reset(self.game_instance)
                


    def run(self):
        game_images = self.__load_assets()
        hero = Hero(game_images['hero'], position=(375, 520))

        clock = pygame.time.Clock()

        while self.is_running:
            entity_sprites_group = pygame.sprite.Group()
            self.__reset_game()

            generate_entity_freq = random.randint(10, 20)
            generate_entity_count = 0

            while self.game_instance.lives > 0 and self.is_running:

                self.__draw_ui()
                self.__handle_events(hero)
                
                generate_entity_count += 1
                if generate_entity_count > generate_entity_freq:
                    generate_entity_freq = random.randint(1, 5)
                    generate_entity_count = 0
                    entity = Food(game_images, random.choice([self.ENTITY_POINT] * 1 + [self.ENTITY_DAMAGE]))
                    entity_sprites_group.add(entity)

                for entity in entity_sprites_group:
                    if entity.update(): entity_sprites_group.remove(entity)


                for entity in entity_sprites_group:
                    if pygame.sprite.collide_mask(entity, hero):
                        entity_sprites_group.remove(entity)
                        if entity.type == self.ENTITY_DAMAGE:
                            self.clib.game_decrease_lives(self.game_instance)
                        elif entity.type == self.ENTITY_POINT:
                            self.clib.game_increase_money(self.game_instance)

                hero.draw(config.screen)
                entity_sprites_group.draw(config.screen)

                pygame.display.flip()
                clock.tick(30)

            self.clib.polito_end_game(self.polito)

            # if exit by event
            if not self.is_running: exit()
            end = EndInterface(self.game_instance.money, self.polito.earned_money)
            end.show()
            self.is_running = end.action == 'restart'
