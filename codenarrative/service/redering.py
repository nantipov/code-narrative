import domain.rendering
import domain.scene
import domain.storage
import domain.keypress
import service.scene
import service.storage
import service.keypress
import service.png
import service.video
import service.cursor

KEYPRESS_DURATION_MS = 150
OBJECT_FADE_MS = 1000  # 500


def render(scene: domain.scene.Scene, profile_name: str):
    profile = service.scene.profile_by_name(scene, profile_name)
    location = service.storage.location()

    # set frame numbers for keyframes
    for k in scene.timeline:
        k.frame = service.scene.temporal_in_frames(k.definition, profile.fps)
    # sort keyframes by frame number
    scene.timeline.sort(key=lambda k: k.frame)

    state = domain.rendering.SceneState(profile)
    for keyframe in scene.timeline:
        # render from `frame` till `keyframe.frame`
        # then process keyframe itself
        state.idle = True
        while state.frame < keyframe.frame - 1:
            service.png.render_png(location, state)
            state.frame = state.frame + 1
        state.idle = False

        if not keyframe.code is None:
            state.code.syntax = keyframe.code.syntax
            text1 = state.code.text
            text2 = keyframe.code.text
            keyboard_actions = service.keypress.compute_keypresses(
                state.cursor, text1, text2
            )
            # todo: check length in frames and print warning if overlaps and supposed to be trimmed
            animate_keypresses(state, location, keyboard_actions)

        if len(keyframe.screen_objects) > 0:
            for obj in keyframe.screen_objects:
                if (
                    obj.action == "add" and not obj.id in state.screen_objects
                ):  # todo: enum
                    state.screen_objects[
                        obj.id
                    ] = domain.rendering.ObjectAnimationState(obj)
            animation_frames = round(OBJECT_FADE_MS / 1000 * state.profile.fps)
            for object_frame in range(animation_frames + 1):
                for obj in keyframe.screen_objects:
                    animation_state = state.screen_objects[obj.id]
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
                service.png.render_png(location, state)
                state.frame = state.frame + 1
            for obj in keyframe.screen_objects:
                match obj.action:
                    case "remove":
                        del state.screen_objects[obj.id]

    # service.png.render_all_pngs(location, state)
    # todo: compose timeline for a sound track
    # todo: write the sound file (wav or raw), parallel to pngs?
    service.video.render_video(location, state)


def animate_keypresses(
    state: domain.rendering.SceneState,
    location: domain.storage.Location,
    keypresses: list[domain.keypress.Keypress],
):
    max_cols = service.cursor.get_max_cols(state.code.text)
    is_max_cols_changed = False
    for keypress in keypresses:
        match keypress.key:
            case domain.keypress.Key.OTHER:
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
                is_max_cols_changed = True

            case domain.keypress.Key.ARROW_LEFT | domain.keypress.Key.ARROW_RIGHT | domain.keypress.Key.ARROW_UP | domain.keypress.Key.ARROW_DOWN:
                if is_max_cols_changed:
                    max_cols = service.cursor.get_max_cols(state.code.text)
                    is_max_cols_changed = False
                service.cursor.move_cursor(
                    max_cols,
                    state.cursor,
                    keypress.key,
                    keypress.aligned_current_column,
                )

            case domain.keypress.Key.TOGGLE_CURSOR_REPLACE:
                state.cursor.is_insert = False

            case domain.keypress.Key.TOGGLE_CURSOR_INSERT:
                state.cursor.is_insert = True

            case domain.keypress.Key.BACKSPACE:
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
                    if is_max_cols_changed:
                        max_cols = service.cursor.get_max_cols(state.code.text)
                    state.cursor.pos.row = state.cursor.pos.row - 1
                    state.cursor.pos.col = max_cols[state.cursor.pos.row - 1]
                else:
                    state.cursor.pos.col = state.cursor.pos.col - 1
                is_max_cols_changed = True

        # duration_f = round(state.profile.fps * KEYPRESS_DURATION_MS / 1000) + keypress_jitter_frames(state)
        duration_f = 1
        f = 0
        while f < duration_f:
            service.png.render_png(location, state)
            state.frame = state.frame + 1
            f = f + 1


def keypress_jitter_frames(state: domain.rendering.SceneState) -> int:
    jitter_f = round(state.profile.fps / 3)
    jitter_chars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", '"', ":"]
    if state.cursor.pos.col == 1:
        return jitter_f
    if (
        not state.code is None
        and len(state.code.text) > state.cursor.index
        and state.code.text[state.cursor.index] in jitter_chars
    ):
        return jitter_f
    return 0
