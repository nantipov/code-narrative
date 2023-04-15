class Profile:
    def __init__(self):
        self.name: str = ""
        self.fps: int = 0
        self.resolution: tuple[int, int]
        self.is_debug = False
        self.is_default: bool = False


class View:
    def __init_(self):
        self.top = 0
        self.left = 0
        self.right = 0
        self.bottom = 0
        self.font_size_px_string = ""
        self.font_size_px = 0


class Code:
    def __init__(self):
        self.syntax = "text"
        self.text = ""


class ScreenObjectArea:
    def __init__(self, col0, row0, col1, row1):
        self.col0 = col0
        self.row0 = row0
        self.col1 = col1
        self.row1 = row1


class ScreenObject:
    def __init__(self):
        self.id = id
        self.type = ""
        self.action = ""
        self.kind = ""
        self.background_color = ""
        self.text_color = ""
        self.screen_area = ScreenObjectArea(0, 0, 0, 0)


class Keyframe:
    def __init__(self):
        self.definition: str = ""
        self.frame: int = 0
        self.code: Code = None
        self.screen_objects: list[ScreenObject] = []


class Scene:
    def __init__(self):
        self.profiles: list[Profile] = []
        self.view = View()
        self.timeline: list[Keyframe] = []
