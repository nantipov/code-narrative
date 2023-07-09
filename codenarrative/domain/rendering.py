from codenarrative.domain.scene import Scene, ScreenObject, Profile, Code
from PIL import ImageFont


class Position:
    def __init__(self):
        self.col = 1
        self.row = 1


class Cursor:
    def __init__(self):
        self.pos = Position()
        self.index = 0
        self.is_insert = True


class ObjectAnimationState:
    def __init__(self, obj: ScreenObject):
        self.animation_progress = 0
        self.obj = obj


class SceneState:
    def __init__(self):
        self.code = Code()
        self.cursor = Cursor()
        self.frame = 0
        self.idle = False
        self.screen_objects: dict[str, ObjectAnimationState] = {}


class ImageContext:
    def __init__(self, scene: Scene, profile: Profile):
        self.scene = scene
        self.profile = profile
        self.view_rectangle = (0.0, 0.0, 0.0, 0.0)
        self.font: ImageFont = None
        self.char_w = 0.0
        self.char_h = 0.0


class TextRowData:
    def __init__(self, min_index: int, max_index: int, max_cols: int):
        self.min_index = min_index
        self.max_index = max_index
        self.max_cols = max_cols


def copy_cursor(cursor: Cursor) -> Cursor:
    c = Cursor()
    c.index = cursor.index
    c.is_insert = cursor.is_insert
    c.pos.col = cursor.pos.col
    c.pos.row = cursor.pos.row
    return c
