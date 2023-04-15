import domain.scene
import yaml


builtin_default_profile = domain.scene.Profile()
builtin_default_profile.fps = 60
builtin_default_profile.name = "default (built-in)"
builtin_default_profile.resolution = "640x480"  # todo: structure?


def read_scene_file(filename: str) -> domain.scene.Scene:
    with open(filename, "r") as file:
        return dict_to_scene(yaml.safe_load(file))


def dict_to_scene(scene_dict: dict) -> domain.scene.Scene:
    scene = domain.scene.Scene()
    scene.settings = read_settings(scene_dict)
    scene.profiles = read_profiles(scene_dict)
    scene.timeline = read_timeline(scene_dict)
    return scene


def read_settings(scene_dict: dict) -> domain.scene.Settings:
    settings = domain.scene.Settings()
    # todo: cleanup
    # settings.duration = scene_dict["duration"]
    return settings


def read_profiles(scene_dict: dict) -> list[domain.scene.Profile]:
    profiles: list[domain.scene.Profile] = []
    for p in scene_dict["profiles"]:
        profile = domain.scene.Profile()
        profile.name = str(p["name"])
        profile.resolution = str(p["resolution"])
        if "default" in p:
            profile.is_default = bool(p["default"])
        profile.fps = int(p["fps"])
        if "debug" in p:
            profile.is_debug = bool(p["debug"])
        profiles.append(profile)
    return profiles


def read_timeline(scene_dict: dict) -> list[domain.scene.Keyframe]:
    keyframes: list[domain.scene.Keyframe] = []
    for k in scene_dict["timeline"]:
        keyframe = domain.scene.Keyframe()
        keyframe.definition = str(k["keyframe"])
        if "code" in k:
            keyframe.code = read_code(k["code"])
        if "screen-objects" in k:
            keyframe.screen_objects = read_screen_objects(k["screen-objects"])
        keyframes.append(keyframe)
    return keyframes


def read_code(code_dict: dict) -> domain.scene.Code:
    code = domain.scene.Code()
    code.syntax = code_dict["syntax"]
    code.text = code_dict["text"]
    return code


def read_screen_objects(objects: list[dict]) -> list[domain.scene.ScreenObject]:
    screen_objects: list[domain.scene.ScreenObject] = []
    for obj in objects:
        screen_object = domain.scene.ScreenObject()
        screen_object.id = obj["id"]
        screen_object.action = obj["action"]
        if screen_object.action == "add":  # todo enum
            screen_object.type = obj["type"]
            screen_object.kind = obj["kind"]
            if "area" in obj:
                screen_object.screen_area = read_range(obj["area"])
            if "background-color" in obj:
                screen_object.background_color = obj["background-color"]
            # if "text_color" in obj:
            #    screen_object.text_color = obj["text_color"]
        screen_objects.append(screen_object)
    return screen_objects


def read_range(range_dict: dict) -> domain.scene.ScreenArea:
    return domain.scene.ScreenArea(
        int(range_dict["col0"]),
        int(range_dict["row0"]),
        int(range_dict["col1"]),
        int(range_dict["row1"]),
    )


# todo: parse thing like 1s3ms or 3ms or 1m3s456ms
def temporal_in_frames(temporal_definition: str, fps: int = 60) -> int:
    unit = temporal_definition[-1]
    value = temporal_definition[:-1]
    if unit == "s":
        return int(value) * fps
    elif unit == "f":
        return int(value)
    else:
        raise BaseException("unrecognized definition " + temporal_definition)


def profile_by_name(
    scene: domain.scene.Scene, profile_name: str
) -> domain.scene.Profile:
    default_profile = builtin_default_profile
    if len(scene.profiles) == 1:
        default_profile = scene.profiles[0]
    elif len(scene.profiles) > 1:
        default_profile = next(
            (p for p in scene.profiles if p.is_default), scene.profiles[0]
        )

    if len(profile_name) == 0:
        return default_profile

    # todo: handler StopIteration exception?
    return next(p for p in scene.profiles if p.name == profile_name)
