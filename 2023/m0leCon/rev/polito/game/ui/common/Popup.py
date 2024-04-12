import pygame
import sys
import os

font_path = os.path.join('assets', 'font', 'kenvector_future.ttf')


class Popup:
    def __init__(self, screen, title, message, mes2=''):
        self.screen = screen
        self.title = title
        self.message = message
        self.popup_rect = pygame.Rect(0, 0, 400, 200)
        self.popup_rect.center = screen.get_rect().center
        self.font_title = pygame.font.Font(font_path, 25)
        self.font = pygame.font.Font(font_path, 15)
        self.close_button = pygame.Rect(self.popup_rect.right - 30, self.popup_rect.top, 30, 30)
        self.is_open = True
        self.mes2 = mes2

    def draw(self):
        # Draw the background
        pygame.draw.rect(self.screen, (255, 255, 255), self.popup_rect)
        
        # Draw the title
        title_text = self.font_title.render(self.title, True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(self.popup_rect.centerx, self.popup_rect.top + 15))
        self.screen.blit(title_text, title_rect)
        
        # Draw the message
        message_text = self.font.render(self.message, True, (0, 0, 0))
        message_rect = message_text.get_rect(center=self.popup_rect.center)
        self.screen.blit(message_text, message_rect)

        message2_text = self.font.render(self.mes2, True, (0, 0, 0))
        message2_rect = message2_text.get_rect(center=(self.popup_rect.centerx, self.popup_rect.centery+20))
        self.screen.blit(message2_text, message2_rect)

        
        # Draw the close button
        pygame.draw.rect(self.screen, (255, 0, 0), self.close_button)
        close_text = pygame.font.Font(None, 20).render("X", True, (255, 255, 255))
        close_rect = close_text.get_rect(center=self.close_button.center)
        self.screen.blit(close_text, close_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_button.collidepoint(event.pos):
                    self.is_open = False

    def run(self):
        while self.is_open:
            self.handle_events()
            self.draw()
            pygame.display.flip()

