import domain.scene


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
    def __init__(self, profile: domain.scene.Profile, view: domain.scene.View):
        self.profile = profile
        self.view = view
        self.code = domain.scene.Code()
        self.cursor = Cursor()
        self.frame = 0
        self.idle = False
        self.screen_objects: dict[str, ObjectAnimationState] = {}


def copy_cursor(cursor: Cursor) -> Cursor:
    c = Cursor()
    c.index = cursor.index
    c.is_insert = cursor.is_insert
    c.pos.col = cursor.pos.col
    c.pos.row = cursor.pos.row
    return c
