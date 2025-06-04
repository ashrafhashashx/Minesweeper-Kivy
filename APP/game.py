from enum import Enum
from random import sample
from APP.configuration import reasonable_max_number_of_mines
from APP.game_button import GameButton
from APP.play_sound import play_sound, Sounds


class Result(Enum):
    UNFINISHED, WIN, LOSS = 0, 1, 2


class Game:
    def __init__(
            self,
            num_rows: int,
            num_cols: int,
            num_mines: int,
            button_size: float,
            on_press
    ):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.num_mines: int = num_mines

        assert num_rows > 0
        assert num_cols > 0
        assert 0 <= num_mines <= reasonable_max_number_of_mines(num_rows, num_cols)
        assert button_size > 0

        self.most_recently_pressed_button = GameButton(-1, -1, -1)  # GameButton
        self.safe_buttons_remaining: int = num_rows * num_cols - num_mines
        self.is_first_button_press: bool = True
        self.result = Result.UNFINISHED

        buttons: [GameButton] = []
        for i in range(num_rows):
            row: [GameButton] = []
            for j in range(num_cols):
                button = GameButton(
                    font_size=button_size,
                    i=i,
                    j=j,
                    on_press=on_press
                )

                row.append(button)
            buttons.append(row)

        self.buttons: [GameButton] = buttons

        for i in range(num_rows):
            for j in range(num_cols):
                neighbors: [GameButton] = []
                for ii in [i - 1, i, i + 1]:
                    for jj in [j - 1, j, j + 1]:
                        if all([
                            ii in range(num_rows),
                            jj in range(num_cols),
                            (ii != i or jj != j)
                        ]):
                            neighbors.append(buttons[ii][jj])
                self.buttons[i][j].neighbors = neighbors

    def player_press(self, button: GameButton, is_mouse_right_click: bool = False):
        # Seems like the button changes state (down / normal) before this function triggers. So, if the player presses
        # a 'down' button then the button we deal with in this function is 'normal' and vise versa.
        # The same goes for left-clicking and right-clicking.

        self.update_emphasis(button)
        if is_mouse_right_click:
            if button.state is 'normal':
                button.state = 'down'
                return
            play_sound(Sounds.BUTTON_UP)
            button.toggle_flagged()
            button.state = 'normal'
            return
        play_sound(Sounds.BUTTON_DOWN)
        if self.is_first_button_press:
            self.is_first_button_press = False
            self.distribute_mines(button.i, button.j)

        if button.state is 'normal':  # (After state change due to player click)
            button.state = 'down'
            if button.number_of_surrounding_mines == button.number_of_flagged_neighbors:
                self.press_all_neighbors(button)
            return

        # if button state is down after the player clicked it:
        if button.flagged:
            # TODO maybe enum on button state makes sense (decoupling)
            button.state = 'normal'
            return
        # only possibilities left now are : has mine ... TODO
        button.state = 'normal'
        self.press(button)

    def press(self, button: GameButton):
        # always: left-click
        if button.flagged or button.state is 'down':
            return
        # Dealing with a 'normal' unflagged button:
        button.reveal()
        button.state = 'down'
        if button.has_mine:
            # TODO consider triggering end_game from here
            self.result = Result.LOSS
            return
        self.safe_buttons_remaining -= 1
        if self.safe_buttons_remaining == 0:
            self.result = Result.WIN
            return
        if button.number_of_surrounding_mines == 0:
            self.press_all_neighbors(button)

    def press_all_neighbors(self, button: GameButton):
        for n in button.neighbors:
            self.press(n)

    def update_emphasis(self, newly_pressed_button: GameButton):
        if self.most_recently_pressed_button:
            self.most_recently_pressed_button.normalize()
        newly_pressed_button.emphasize()
        self.most_recently_pressed_button = newly_pressed_button

    # i0 and j0 are the coordinates of the first pressed button of the game.
    def distribute_mines(self, i0: int, j0: int):
        # Make a list of button coordinates
        to_choose_from = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if i != i0 and j != j0:
                    to_choose_from.append((i, j))

        # Choose a random sample of these based on the preset requested number of mines. These will be
        # the coordinates of buttons containing mines.
        # TODO I do not know why I have to add this 'round'. It won't work without it.
        will_have_mine = sample(to_choose_from, round(self.num_mines))
        for (i, j) in will_have_mine:
            b = self.buttons[i][j]
            b.has_mine = True
            for n in b.neighbors:
                n.number_of_surrounding_mines += 1

    def end(self, is_game_won: bool):
        if is_game_won:
            for row in self.buttons:
                for button in row:
                    button.win()
                    button.set_disabled(True)
                    self.most_recently_pressed_button.emphasize()
        else:
            for row in self.buttons:
                for button in row:
                    button.lose()
                    button.set_disabled(True)
                    self.most_recently_pressed_button.emphasize()
