from enum import Enum
from kivy.core.audio import SoundLoader


class Sounds(Enum):
    SLIDER_MOVE = 'sounds/slider_move.wav'
    BUTTON_DOWN = 'sounds/button_down.wav'
    BUTTON_UP = 'sounds/button_up.wav'
    ENGINE = 'sounds/computer_processing.wav'
    DATA_REVEAL = 'sounds/data_reveal.wav'
    COMPUTER_PROCESSING = 'sounds/engine.wav'


def play_sound(sound_type: Sounds):
    sound = SoundLoader.load(sound_type.value)
    sound.volume = 1
    sound.play()
