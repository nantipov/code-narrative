from codenarrative.domain.rendering import SceneState, ImageContext
from codenarrative.domain import rendering
from codenarrative.domain.scene import Scene
from codenarrative.domain.sound import SoundContext
from codenarrative.domain.storage import Location
from codenarrative.domain.keypress import Keypress, Key
from codenarrative.service import scene_service, sound_service
from codenarrative.service import storage_service
from codenarrative.service import keypress_service
from codenarrative.service import image_service
from codenarrative.service import video_service
from codenarrative.service import cursor_service

KEYPRESS_DURATION_MS = 120
OBJECT_FADE_MS = 1000


def render(scene: Scene, profile_name: str):
    profile = scene_service.profile_by_name(scene, profile_name)
    location = storage_service.location()

    # set frame numbers for keyframes
    for keyframe in scene.timeline:
        keyframe.frame = scene_service.temporal_in_frames(
            keyframe.definition, profile.fps
        )
    # sort keyframes by frame number
    scene.timeline.sort(key=lambda k: k.frame)

    image_context = image_service.create_context(scene, profile)
    sound_context = sound_service.create_context(location, profile)
    state = SceneState()
    for keyframe in scene.timeline:
        # render from `frame` till `keyframe.frame`
        # then process keyframe itself
        state.idle = True
        while state.frame < keyframe.frame:
            image_service.render_image(location, image_context, state)
            state.frame = state.frame + 1
        state.idle = False

        if keyframe.code is not None:
            state.code.syntax = keyframe.code.syntax
            text1 = state.code.text
            text2 = keyframe.code.text
            keyboard_actions = keypress_service.compute_keypresses(
                state.cursor, text1, text2
            )
            # todo: check length in frames and print warning if overlaps and supposed to be trimmed
            animate_keypresses(
                state, image_context, sound_context, location, keyboard_actions
            )

        if len(keyframe.screen_objects) > 0:
            for obj in keyframe.screen_objects:
                if obj.obj_id not in state.screen_objects:  # todo: enum
                    state.screen_objects[obj.obj_id] = rendering.ObjectAnimationState(
                        obj
                    )
            animation_frames = round(OBJECT_FADE_MS / 1000 * profile.fps)
            for object_frame in range(animation_frames + 1):
                for obj in keyframe.screen_objects:
                    animation_state = state.screen_objects[obj.obj_id]
                    match obj.action:
                        case "add":
                            animation_state.animation_progress = round(
                                object_frame * 100 / animation_frames
                            )
                        case "remove":
                            animation_state.animation_progress = round(
                                (animation_frames - object_frame)
                                * 100
                                / animation_frames
                            )
                image_service.render_image(location, image_context, state)
                state.frame = state.frame + 1
            for obj in keyframe.screen_objects:
                match obj.action:
                    case "remove":
                        del state.screen_objects[obj.obj_id]

    sound_service.release_files(sound_context)
    video_service.render_video(location, profile)


def animate_keypresses(
    state: SceneState,
    image_context: ImageContext,
    sound_context: SoundContext,
    location: Location,
    keypresses: list[Keypress],
):
    rows_data = cursor_service.get_rows_data(state.code.text)
    is_rows_data_changed = False
    for keypress in keypresses:
        match keypress.key:
            case Key.OTHER:
                if state.cursor.index >= len(state.code.text):
                    state.code.text = state.code.text + keypress.char
                else:
                    if state.cursor.is_insert:
                        state.code.text = (
                            state.code.text[: state.cursor.index]
                            + keypress.char
                            + state.code.text[state.cursor.index :]
                        )
                    else:
                        state.code.text = (
                            state.code.text[: state.cursor.index]
                            + keypress.char
                            + state.code.text[state.cursor.index + 1 :]
                        )
                state.cursor.index = state.cursor.index + 1
                if keypress.char == "\n":
                    state.cursor.pos.row = state.cursor.pos.row + 1
                    state.cursor.pos.col = 1
                else:
                    state.cursor.pos.col = state.cursor.pos.col + 1
                is_rows_data_changed = True

            case Key.ARROW_LEFT | Key.ARROW_RIGHT | Key.ARROW_UP | Key.ARROW_DOWN:
                if is_rows_data_changed:
                    rows_data = cursor_service.get_rows_data(state.code.text)
                    is_rows_data_changed = False
                cursor_service.move_cursor(
                    rows_data,
                    state.cursor,
                    keypress.key,
                    keypress.aligned_current_column,
                )

            case Key.TOGGLE_CURSOR_REPLACE:
                state.cursor.is_insert = False

            case Key.TOGGLE_CURSOR_INSERT:
                state.cursor.is_insert = True

            case Key.BACKSPACE:
                char_to_delete = state.code.text[state.cursor.index - 1]
                if state.cursor.index >= len(state.code.text):
                    state.code.text = state.code.text[: len(state.code.text) - 1]
                else:
                    state.code.text = (
                        state.code.text[: state.cursor.index - 1]
                        + state.code.text[state.cursor.index :]
                    )

                state.cursor.index = state.cursor.index - 1
                if char_to_delete == "\n":
                    if is_rows_data_changed:
                        rows_data = cursor_service.get_rows_data(state.code.text)
                    state.cursor.pos.row = state.cursor.pos.row - 1
                    state.cursor.pos.col = rows_data[state.cursor.pos.row - 1].max_cols
                else:
                    state.cursor.pos.col = state.cursor.pos.col - 1
                is_rows_data_changed = True

            case Key.DELETE:
                state.code.text = (
                    state.code.text[: state.cursor.index]
                    + state.code.text[state.cursor.index + 1 :]
                )
                char_to_delete = state.code.text[state.cursor.index - 1]
                if char_to_delete == "\n":
                    is_rows_data_changed = True

        duration_f = round(
            image_context.profile.fps * KEYPRESS_DURATION_MS / 1000
        ) + keypress_jitter_frames(state, keypress, image_context.profile.fps)

        if image_context.profile.is_debug:
            duration_f = 1

        sound_pointer = sound_service.get_sound_pointer(sound_context, keypress)
        duration_f = max(duration_f, sound_pointer.frames)
        # todo: peak

        sound_service.append_sound_sample(sound_context, sound_pointer, state.frame)

        f = 0
        while f < duration_f:
            image_service.render_image(location, image_context, state)
            state.frame = state.frame + 1
            f = f + 1


def keypress_jitter_frames(state: SceneState, keypress: Keypress, fps: int) -> int:
    jitter_f = round(fps / 3)
    jitter_chars = [
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "(",
        ")",
        "+",
        "-",
        '"',
        ":",
        ";",
        "[",
        "]",
        "=",
        ".",
        ",",
        "/",
        "\\"
    ]

    if state.cursor.pos.col == 1:
        return jitter_f

    if keypress.key != Key.OTHER or keypress.char[0] in jitter_chars:
        return jitter_f

    if not state.cursor.is_insert:
        return jitter_f

    return 0
