from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.config import Config

from APP.game import Game, Result
from APP.game_button import GameButton
from APP.play_sound import play_sound, Sounds
from APP.configuration import (
    MAX_COLS, MAX_ROWS, INITIAL_COLS, INITIAL_MINES, INITIAL_ROWS, MIN_ROWS, MIN_COLS, MIN_MINES, MAX_MINES,
    BUTTON_WIDTH_FACTOR, BUTTON_HEIGHT_FACTOR, reasonable_max_number_of_mines
)

# Prevent red dots from appearing when right-clicking
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

game: Game

menu_screen: Screen
game_screen: Screen


def initialize_window_and_get_appropriate_button_size(num_rows: int, num_cols: int):
    # Maximize window to make place for the buttons
    Window.maximize()

    window_height: int
    window_width: int
    window_width, window_height = Window.size

    # Set button dimensions as big as possible but also small enough to fit the screen.
    button_width = BUTTON_WIDTH_FACTOR * (window_width / num_cols)
    button_height = BUTTON_HEIGHT_FACTOR * (window_height / num_rows)
    return min(button_height, button_width)


class MenuWindow(Screen):
    @staticmethod
    def slider_on_value(update_type, *args):
        must_update_num_max_mines: bool = False

        # Get value from slider event
        value: int = args[1]

        if update_type == 'rows_update':
            menu_screen.rows_label.text = f'Number of rows = {value}'
            must_update_num_max_mines = True
        elif update_type == 'cols_update':
            menu_screen.cols_label.text = f'Number of cols = {value}'
            must_update_num_max_mines = True
        elif update_type == 'mines_update':
            menu_screen.mines_label.text = f'Number of mines = {value}'
        else:
            raise Exception('Error! Unknown update type!!!')

        if must_update_num_max_mines:
            # Get the current values of the sliders.
            num_rows: int = menu_screen.rows_slider.value
            num_cols: int = menu_screen.cols_slider.value
            num_mines: int = menu_screen.mines_slider.value
            # Validate mines value and max value
            num_max_mines: int = reasonable_max_number_of_mines(num_rows, num_cols)
            num_mines = min(num_mines, num_max_mines)
            # Update mines slider:
            menu_screen.mines_slider.max = num_max_mines
            menu_screen.mines_slider.value = num_mines

        # Play feedback sound
        play_sound(Sounds.SLIDER_MOVE)

    @staticmethod
    def start_game():
        play_sound(Sounds.COMPUTER_PROCESSING)
        # Get the values from the menu screen sliders.
        num_rows: int = menu_screen.rows_slider.value
        num_cols: int = menu_screen.cols_slider.value
        num_mines: int = menu_screen.mines_slider.value

        button_size: float = initialize_window_and_get_appropriate_button_size(num_rows, num_cols)

        # Initialize a grid.
        grid: GridLayout = game_screen.grid
        grid.clear_widgets()

        # Set the number of rows and columns of the grid so that it can contain exactly as many buttons as
        # we are going to add into it with rows and cols.
        grid.rows = num_rows
        grid.cols = num_cols

        grid.col_default_width = grid.row_default_height = button_size
        grid.col_force_default = grid.row_force_default = True

        # Create a game.
        global game
        game = Game(
            num_rows=num_rows,
            num_cols=num_cols,
            num_mines=num_mines,
            button_size=button_size,
            on_press=GameWindow.on_press
        )
        '''
            creator=(lambda x y: GameButton(
                    font_size=button_size,
                    i=i,
                    j=j,
                    on_press=on_press
                )
        )'''

        for row in game.buttons:
            for button in row:
                grid.add_widget(button)

        game_screen.remaining_label.text = str(game.safe_buttons_remaining)


def end_game(is_game_won: bool):
    popup = Popup(
        title=['Sorry...', 'Congratulations!'][is_game_won],
        content=Label(text=['You have lost the game...', 'You have won the game!'][is_game_won]),
        size_hint=(None, None), size=(210, 100),
        background_color=['orangered', 'lightgreen'][is_game_won],
        overlay_color=[0, 0, 0, 0]
    )
    popup.opacity = 0.8
    popup.open()

    game.end(is_game_won)


class GameWindow(Screen):
    @staticmethod
    def on_press(*args, issued_by_player: bool = True):
        # Get the pressed button as an object
        button: GameButton = args[0]
        game.player_press(button, is_mouse_right_click=button.last_touch.button is 'right')
        game_screen.remaining_label.text = str(game.safe_buttons_remaining)
        # TODO
        if game.result is Result.WIN:
            end_game(is_game_won=True)
        if game.result is Result.LOSS:
            end_game(is_game_won=False)

    @staticmethod
    def restart_game():
        pass


class MyWindowManager(ScreenManager):
    pass


kv = Builder.load_file('APP/kv.kv')


class MyApp(MDApp):
    def build(self):
        global game, menu_screen, game_screen
        menu_screen = kv.screens[0]
        game_screen = kv.screens[1]
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Yellow'

        # Make sure that the values on the GUI adhere to 'configuration.py'
        menu_screen.rows_slider.min = MIN_ROWS
        menu_screen.cols_slider.min = MIN_COLS
        menu_screen.mines_slider.min = MIN_MINES

        menu_screen.rows_slider.max = MAX_ROWS
        menu_screen.cols_slider.max = MAX_COLS
        menu_screen.mines_slider.max = MAX_MINES

        menu_screen.rows_slider.value = INITIAL_ROWS
        menu_screen.cols_slider.value = INITIAL_COLS
        menu_screen.mines_slider.value = INITIAL_MINES

        return kv


LabelBase.register(name='lcd',
                   fn_regular='RESOURCES/fonts/digital-7.ttf')
LabelBase.register(name='breitkopf',
                   fn_regular='RESOURCES/fonts/BreitkopfFraktur.ttf')
LabelBase.register(name='lcd',
                   fn_regular='RESOURCES/fonts/steelfish eb.otf')

if __name__ == '__main__':
    MyApp().run()
