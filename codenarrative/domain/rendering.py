import domain.scene
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
    def __init__(self, obj: domain.scene.ScreenObject):
        self.animation_progress = 0
        self.obj = obj


class SceneState:
    def __init__(self):
        self.code = domain.scene.Code()
        self.cursor = Cursor()
        self.frame = 0
        self.idle = False
        self.screen_objects: dict[str, ObjectAnimationState] = {}


class ImageContext:
    def __init__(self, scene: domain.scene.Scene, profile: domain.scene.Profile):
        self.scene = scene
        self.profile = profile
        self.view_rectangle = (0, 0, 0, 0)
        self.font: ImageFont = None
        self.char_w = 0
        self.char_h = 0


def copy_cursor(cursor: Cursor) -> Cursor:
    c = Cursor()
    c.index = cursor.index
    c.is_insert = cursor.is_insert
    c.pos.col = cursor.pos.col
    c.pos.row = cursor.pos.row
    return c
