class Settings: #todo: class -> instance if any
    duration: str

class Profile:
    def __init__(self):
        self.name: str = ""
        self.fps: int = 0
        self.resolution: tuple[int, int] #todo: structure?
        self.is_debug = False
        self.is_default: bool = False

class Code:
    def __init__(self):
        self.syntax = "text"
        self.text = ""

class ScreenArea:
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
        self.screen_area = ScreenArea(0, 0, 0, 0)
        

class Highlight: #todo: class -> instance
    id: str
    action: str
    background_color: str
    text_color: str
    presentation: str = "fade"
    range: str #todo: structure?

class Note: #todo: class -> instance
    id: str
    action: str
    background_color: str
    text_color: str
    presentation: str
    shape: str
    text: str

class Keyframe:
    def __init__(self):
        self.definition: str = ""
        self.frame: int = 0
        self.code: Code = None
        self.screen_objects: list[ScreenObject] = []
        #self.highlights: list[Highlight] = []
        #self.notes: list[Note] = []

class Scene:
    def __init__(self):
        self.settings: Settings
        self.profiles: list[Profile] = []
        self.timeline: list[Keyframe] = []
