import os


class Config:
    COLORS = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'green': (0, 255, 0),
        'red': (255, 0, 0),
    }

    SCREEN = None
    SCREENSIZE = (800, 600)

    def __init__(self):

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.lib_dir = os.path.join(self.base_dir, 'lib')
        self.asset_dir = os.path.join(self.base_dir, 'assets')

        self.font_dir = os.path.join(self.asset_dir, 'font')
        self.image_dir = os.path.join(self.asset_dir, 'elements')
        self.sprite_dir = os.path.join(self.asset_dir, 'sprite')
        self.icon_dir = os.path.join(self.asset_dir, 'icons')
        self.ui_dir = os.path.join(self.asset_dir, 'ui')

        self.game_running = True

        self.fonts = {
            'thin': os.path.join(self.font_dir, 'kenvector_future_thin.ttf'),
            'normal': os.path.join(self.font_dir, 'kenvector_future.ttf'),
        }
        self.screen = None

    def set_screen(self, screen):
        self.screen = screen

config = Config()