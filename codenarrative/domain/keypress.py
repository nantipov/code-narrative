from enum import Enum


class Key(Enum):
    OTHER = 0
    ARROW_LEFT = 1
    ARROW_RIGHT = 2
    ARROW_UP = 3
    ARROW_DOWN = 4
    TOGGLE_CURSOR_REPLACE = 5
    TOGGLE_CURSOR_INSERT = 6
    BACKSPACE = 7
    DELETE = 8


class Keypress:
    def __init__(self, k: Key, c: str = "", aligned_current_column=-1):
        self.key = k
        self.char = c
        self.aligned_current_column = aligned_current_column
