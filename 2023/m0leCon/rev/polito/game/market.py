import pygame
import os

from Config import config
from ui.common.Popup import Popup
from ui.common.Button import Button

from Wrappers import MarketWrapper


class MarketElement:

    CELL_SIZE = 50

    def __init__(self, market_el, icon, pos, selected=False):
        self.name = market_el.name.decode('utf-8')
        self.description = market_el.desc.decode('utf-8')
        self.price = market_el.price
        self.element = market_el
        self.icon = icon
        self.x, self.y = pos

        self.selected = selected

        self.load_button_images()


    def load_button_images(self):
        self.btn_default = pygame.image.load(os.path.join(config.ui_dir, 'red_button09.png'))
        self.btn_hovered = pygame.image.load(os.path.join(config.ui_dir, 'red_button05.png'))
        self.btn_selected = pygame.image.load(os.path.join(config.ui_dir, 'red_button07.png'))
        self.btn_bought = pygame.image.load(os.path.join(config.ui_dir, 'red_button03.png'))

    def draw(self):
        # draw based on x and y
        if self.element.bought:
            config.screen.blit(self.btn_bought, (self.x, self.y))
        else:    
            if self.selected:
                config.screen.blit(self.btn_selected, (self.x, self.y))
            else:
                config.screen.blit(self.btn_default, (self.x, self.y))

        icon_img = pygame.image.load(os.path.join(config.icon_dir, f'{self.icon}.png'))
        config.screen.blit(pygame.transform.scale(icon_img, (self.CELL_SIZE-20, self.CELL_SIZE-20)), (self.x+10, self.y+7))


class Market:
    GRID_WIDTH, GRID_HEIGHT = 4, 2


    def __init__(self, clib, poli):

        self.market = MarketWrapper.from_address(poli.market)
        
        self.clib = clib
        self.polito = poli
        self.market_elements = self.market.elements
        self.elements = []

        self.hovered_element = None
        self.selected_element = None


        home_button_rect = pygame.Rect(10, 10, 80, 50)
        font = pygame.font.Font(config.fonts['normal'], 15)

        self.btn = None
        self.backbtn = Button("Home", home_button_rect.x, home_button_rect.y, config.screen, font)

        count = 0
        icons = ['coffe_cup', 'scroll', 'book_open', 'popi_sweatshirt', 'degree_scroll', 'degree_hat', 'unknown']
        for j in range(self.GRID_HEIGHT):
            for i in range(self.GRID_WIDTH):
                if count < len(self.market_elements):

                    element = MarketElement(self.market_elements[count], icons[count], (160 + i * 50, 186 + j * 50))
                    self.elements.append(element)
                count +=1

                    
    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
               self.__handle_events(event)

            self.draw()


    def __handle_events(self, event):
        backbtn_boundaries = pygame.Rect(10, 10, 80, 50)
        
        if event.type == pygame.QUIT:
            config.game_running = False
            self.running = False

        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            self.hovered_element = self.selected_element
            for button in self.elements:
                if button.x < x < button.x + 50 and button.y < y < button.y + 50:
                    self.hovered_element = button

            self.backbtn.hovered = 10 < x < 200 and 10 < y < 60
            if self.btn is not None:
                self.btn.hovered = 500 < x < 700 and 450 < y < 500


        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            for button in self.elements:
                if button.x < x < button.x + 50 and button.y < y < button.y + 50:
                    button.selected = True
                    self.selected_element = button
                else:
                    button.selected = False

            if 10 < x < 200 and 0 < y < 50:
                self.running = False


            # handle click on "BUY" button
            if 500 < x < 700 and 450 < y < 500:
                if self.selected_element is not None:
                        index = self.elements.index(self.selected_element)
                        ret = self.clib.market_buy(self.polito, index)
                        title, message, desc = "", "", ""
                        if ret == 1:
                            title = "Success"
                            message = "Item bought successfully"
                            if index == 6:
                                self.elements[index].name = self.market_elements[index].name.decode('utf-8')
                                self.elements[index].description = self.market_elements[index].desc.decode('utf-8')
                                self.elements[index].description = 'flag\n: ptm{p4tch1ng_3xecut4bl3s_1s_fun}'
                                print(self.elements[index].description)
                        elif ret == 2:
                            title = "Error"
                            message = "You already bought this item" 
                        
                        else:
                            title = "Error"
                            message = "Uhm... You are still a freshman" 
                            desc = "come back later"
                        
                        popup = Popup(config.screen, title, message, desc)
                        popup.run()                            

    def __draw_selected_item(self):
        selected_item_container = pygame.Rect(410, 140, 300, 300)
        img = pygame.image.load(os.path.join(config.ui_dir, 'red_group_2.png')) 
        config.screen.blit(pygame.transform.scale(img, (selected_item_container.width+10, selected_item_container.height)), selected_item_container)


        # draw element name 
        font = pygame.font.Font(None, 26)
        if self.hovered_element is None:
            text = font.render("Item description", True, config.COLORS['black'])
        else:
            text = font.render(self.hovered_element.name, True, config.COLORS['black'])
        text_rect = text.get_rect(center=(selected_item_container.centerx+10, selected_item_container.top+15))
        config.screen.blit(text, text_rect)


        font = pygame.font.Font(None, 20)
        if self.hovered_element is None:
            text = ""
        else:
            text = self.hovered_element.description

        render_text_centered(text, font, config.COLORS['black'], selected_item_container.centerx, selected_item_container.top+35, config.screen, selected_item_container.width-15)

        # draw element price at the bottom of the container
        font = pygame.font.Font(config.fonts['normal'], 16)
        if self.hovered_element is None:
            text = font.render("", True, config.COLORS['black'])
        else:
            text = font.render(f"Price: {self.hovered_element.price}", True, config.COLORS['black'])

        text_rect = text.get_rect(center=(selected_item_container.centerx, selected_item_container.bottom-15))
        config.screen.blit(text, text_rect)

        # Add a "BUY" button
        buy_button_rect = pygame.Rect(selected_item_container.centerx-50, selected_item_container.bottom+10, 100, 50)
        text_rect = text.get_rect(center=buy_button_rect.center)


        if self.btn is None:
            self.btn = Button("Buy", buy_button_rect.x, buy_button_rect.y, config.screen, font)
        self.btn.draw()

    def __draw_money_display(self, font):
        # show top right the money
        text = font.render(f"Marks: {self.polito.earned_money}", True, config.COLORS['white'])
        text_rect = text.get_rect(center=(config.SCREENSIZE[0]-100, 25))
        config.screen.blit(text, text_rect)

    def __draw_market_grid(self, font):
        text = font.render("PoliTO Market", True, config.COLORS['white'])
        text_rect = text.get_rect(center=(config.SCREENSIZE[0] // 2, 80))
        config.screen.blit(text, text_rect)

        container_rect = pygame.Rect(150, 180, 200, 100)
        group_img = pygame.image.load(os.path.join(config.ui_dir, 'group_btn.png')) 
        config.screen.blit(pygame.transform.scale(group_img, (container_rect.width+18, container_rect.height+13)), container_rect)

        # Create a grid of elements
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                element_index = y * self.GRID_WIDTH + x
                # if should be drawn
                if element_index < len(self.market_elements):
                    self.elements[element_index].draw()

    def draw(self):
        # Clear the screen
        background = pygame.image.load(os.path.join(config.image_dir, 'bck_menu.png'))
        config.screen.blit(background, (0, 0))
        self.backbtn.draw()

        font = pygame.font.Font(config.fonts['normal'], 23)

        self.__draw_money_display(font)
        self.__draw_market_grid(font)
        self.__draw_selected_item()
        
        pygame.display.flip()





def render_text_centered(text, font, colour, x, y, screen, allowed_width):
    # first, split the text into words
    words = text.split()

    # now, construct lines out of these words
    lines = []
    while len(words) > 0:
        # get as many words as will fit within allowed_width
        line_words = []
        while len(words) > 0:
            line_words.append(words.pop(0))
            fw, fh = font.size(' '.join(line_words + words[:1]))
            if fw > allowed_width:
                break

        # add a line consisting of those words
        line = ' '.join(line_words)
        lines.append(line)

    y_offset = 0
    for line in lines:
        fw, fh = font.size(line)

        # (tx, ty) is the top-left of the font surface
        tx = x - fw / 2
        ty = y + y_offset

        font_surface = font.render(line, True, colour)
        screen.blit(font_surface, (tx, ty))

        y_offset += fh

    
