from enum import Enum

MIN_ROWS: int = 3
INITIAL_ROWS: int = 5
MAX_ROWS: int = 30

MIN_COLS: int = 4
INITIAL_COLS: int = 7
MAX_COLS: int = 40

MAX_MINES_LIMITER_FACTOR: float = 1.5


def reasonable_max_number_of_mines(num_rows: int, num_cols: int) -> int:
    return min(round(MAX_MINES_LIMITER_FACTOR * (num_rows + num_cols - 1)), num_rows * num_cols - 1)


MIN_MINES: int = 0
INITIAL_MINES: int = 9
MAX_MINES: int = reasonable_max_number_of_mines(MAX_ROWS, MAX_COLS)


BUTTON_WIDTH_FACTOR = 0.90
BUTTON_HEIGHT_FACTOR = 0.96

MINE_SYMBOL = 'X'
FLAG_SYMBOL = '!'


class Coloring(Enum):
    NORMALIZE = ('lightblue', 'black')
    FLAG = ('red', 'black')
    EMPHASIZE = ('white', 'black')
    WIN = ('lightgreen', 'black')
    LOSS = ('orangered', 'black')
