from kivy.uix.togglebutton import ToggleButton

from APP.configuration import MINE_SYMBOL, FLAG_SYMBOL, Coloring


class GameButton(ToggleButton):
    def __init__(self, font_size: float, i: int, j: int, **kwargs):
        super(GameButton, self).__init__(**kwargs)
        self.font_size = font_size
        self.i: int = i
        self.j: int = j
        self.has_mine: bool = False
        self.flagged: bool = False
        self.number_of_surrounding_mines: int = 0
        self.neighbors: [GameButton] = []
        self.number_of_flagged_neighbors: int = 0
        self.normalize()

    def reveal(self):
        if self.has_mine:
            self.text = MINE_SYMBOL
            return
        if self.number_of_surrounding_mines > 0:
            self.text = str(self.number_of_surrounding_mines)
            return
        self.text = ''

    def change_color(self, coloring: Coloring):
        # values of coloring: NORMALIZE, FLAG, EMPHASIZE, WIN, LOSS
        self.background_color, self.color = coloring.value

    def toggle_flagged(self):
        if self.flagged:
            self.text = ''
            self.flagged = False
            for n in self.neighbors:
                n.number_of_flagged_neighbors -= 1
        else:
            self.text = FLAG_SYMBOL
            self.flagged = True
            for n in self.neighbors:
                n.number_of_flagged_neighbors += 1

    def lose(self):
        self.reveal()
        self.change_color(Coloring.LOSS)

    def win(self):
        self.reveal()
        self.change_color(Coloring.WIN)

    def emphasize(self):
        self.change_color(Coloring.EMPHASIZE)

    def normalize(self):
        self.change_color(Coloring.NORMALIZE)
