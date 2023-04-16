import domain.scene
import domain.rendering
import domain.storage
from PIL import Image, ImageDraw, ImageFont
from pygments.lexers import get_lexer_by_name
from pygments.token import (
    Token,
    Name,
    Operator,
    Keyword,
    Generic,
    Comment,
    Number,
    String,
    Literal,
    Punctuation,
    Error,
    _TokenType,
)


styles = {
    Token: "#dcdccc",
    Error: "#e37170",
    Keyword: "#efdcbc",
    Keyword.Type: "#dfdfbf",
    Keyword.Constant: "#dca3a3",
    Keyword.Declaration: "#f0dfaf",
    Keyword.Namespace: "#f0dfaf",
    Name: "#dcdccc",
    Name.Tag: "#e89393",
    Name.Entity: "#cfbfaf",
    Name.Constant: "#dca3a3",
    Name.Class: "#efef8f",
    Name.Function: "#efef8f",
    Name.Builtin: "#efef8f",
    Name.Builtin.Pseudo: "#dcdccc",
    Name.Attribute: "#efef8f",
    Name.Exception: "#c3bf9f",
    Literal: "#9fafaf",
    String: "#cc9393",
    String.Doc: "#7f9f7f",
    String.Interpol: "#dca3a3",
    Number: "#8cd0d3",
    Number.Float: "#c0bed1",
    Operator: "#f0efd0",
    Punctuation: "#f0efd0",
    Comment: "#7f9f7f italic",
    Comment.Preproc: "#dfaf8f",
    Comment.PreprocFile: "#cc9393",
    Comment.Special: "#dfdfdf",
    Generic: "#ecbcbc",
    Generic.Emph: "#ffffff",
    Generic.Output: "#5b605e",
    Generic.Heading: "#efefef",
    Generic.Deleted: "#c3bf9f",
    Generic.Inserted: "#709080",
    Generic.Traceback: "#80d4aa",
    Generic.Subheading: "#efefef",
}


def create_context(
    scene: domain.scene.Scene, profile: domain.scene.Profile
) -> domain.rendering.ImageContext:
    context = domain.rendering.ImageContext(scene, profile)
    view = scene.view
    text_size = 15  # todo: style from scene
    context.font = ImageFont.truetype(
        "fonts/AzeretMono-Medium.ttf", size=text_size
    )  # todo: assets directory fonts, sounds?
    (char_left, char_top, char_right, char_bottom) = context.font.getbbox(text="O")
    context.char_w = char_right - char_left
    context.char_h = (char_bottom - char_top) * 1.5

    context.view_rectangle = (
        round(profile.resolution[0] * view.left / 100),
        round(profile.resolution[1] * view.top / 100),
        round(profile.resolution[0] * view.right / 100),
        round(profile.resolution[1] * view.bottom / 100),
    )
    return context


def render_image(
    location: domain.storage.Location,
    context: domain.rendering.ImageContext,
    state: domain.rendering.SceneState,
):
    filename = location.frame_file(state.frame, "png")
    im = Image.new(
        mode="RGBA", size=context.profile.resolution, color="#3f3f3f"
    )  # todo: add styles, background to the scene file
    draw = ImageDraw.Draw(im)

    im_layer2 = None
    draw_layer2 = None
    if len(state.screen_objects) > 0:
        im_layer2 = Image.new(mode="RGBA", size=im.size)
        draw_layer2 = ImageDraw.Draw(im_layer2)

    if context.profile.is_debug:
        draw.rectangle(
            xy=context.view_rectangle, outline="#bf00ff"
        )  # todo: style - debug color

    if not state.code is None:
        draw_code(context, draw, state)

    draw_cursor(context, draw, state)

    draw_screen_objects(context, draw_layer2, state)

    # cursor position debug
    if context.profile.is_debug:
        draw.text(
            xy=(0, 400),
            text=f"{state.cursor.pos.col} x {state.cursor.pos.row}: {state.cursor.index}",
            fill="#ffffff",
        )

    if im_layer2 is None:
        im.save(filename, "PNG")
    else:
        im_composite = Image.alpha_composite(im, im_layer2)
        im_composite.save(filename, "PNG")


def draw_code(
    context: domain.rendering.ImageContext,
    draw: ImageDraw.Draw,
    state: domain.rendering.SceneState,
):
    current_char_x = context.view_rectangle[0]
    current_char_y = context.view_rectangle[1]

    lexer = get_lexer_by_name(state.code.syntax, stripall=True)
    for token_type, token_value in lexer.get_tokens(text=state.code.text):
        if token_value != "\n":
            draw.text(
                xy=(current_char_x, current_char_y),
                text=token_value,
                font=context.font,
                fill=token_color(token_type),
            )

        if token_value == "\n":
            # new line symbol debug
            if context.profile.is_debug:
                draw.text(
                    xy=(current_char_x, current_char_y),
                    text="n",
                    font=context.font,
                    fill="#bf00ff",  # todo style - debug color
                )
            current_char_x = context.view_rectangle[0]
            current_char_y = current_char_y + context.char_h
        else:
            current_char_x = current_char_x + context.char_w * len(token_value)


def draw_cursor(
    context: domain.rendering.ImageContext,
    draw: ImageDraw.Draw,
    state: domain.rendering.SceneState,
):
    if not state.idle or state.frame % context.profile.fps > context.profile.fps / 3:
        if state.cursor.is_insert:
            draw.rectangle(
                xy=(
                    (state.cursor.pos.col - 1) * context.char_w
                    + context.view_rectangle[0],
                    (state.cursor.pos.row - 1) * context.char_h
                    - context.char_h * 0.1
                    + context.view_rectangle[1],
                    (state.cursor.pos.col - 1) * context.char_w
                    + context.char_w / 4
                    + context.view_rectangle[0],
                    (state.cursor.pos.row - 1) * context.char_h
                    + context.char_h
                    + context.char_h * 0.1
                    + context.view_rectangle[1],
                ),
                fill="#FFBF00",  # todo: style - cursor color
            )
        else:
            draw.rectangle(
                xy=(
                    (state.cursor.pos.col - 1) * context.char_w
                    + context.view_rectangle[0],
                    (state.cursor.pos.row - 1) * context.char_h
                    - context.char_h * 0.1
                    + context.view_rectangle[1],
                    (state.cursor.pos.col - 1) * context.char_w
                    + context.char_w
                    + context.view_rectangle[0],
                    (state.cursor.pos.row - 1) * context.char_h
                    + context.char_h
                    + context.char_h * 0.1
                    + context.view_rectangle[1],
                ),
                fill="#FFBF00",
            )
            if not state.code is None:
                char = state.code.text[state.cursor.index]
                draw.text(
                    xy=(
                        (state.cursor.pos.col - 1) * context.char_w
                        + context.view_rectangle[0],
                        (state.cursor.pos.row - 1) * context.char_h
                        + context.view_rectangle[1],
                    ),
                    text=char,
                    font=context.font,
                    fill="#3f3f3f",  # todo: background color
                )


def draw_screen_objects(
    context: domain.rendering.ImageContext,
    draw: ImageDraw.Draw,
    state: domain.rendering.SceneState,
):
    for _, obj_state in state.screen_objects.items():
        obj = obj_state.obj
        alpha_value = round(
            obj_state.animation_progress * 128 / 100
        )  # todo: declare as constant 128-max opactity?
        alpha_color = (
            f"{alpha_value:02x}"  # todo: load as color and then modify alpha channel
        )
        draw.rounded_rectangle(
            xy=(
                (obj.screen_area.col0 - 1) * context.char_w + context.view_rectangle[0],
                (obj.screen_area.row0 - 1) * context.char_h + context.view_rectangle[1],
                (obj.screen_area.col1 - 1 + 1) * context.char_w
                + context.view_rectangle[0],
                (obj.screen_area.row1 - 1 + 1) * context.char_h
                + context.view_rectangle[1],
            ),
            radius=round(context.char_h / 5),  # todo: depends on resolution? char size?
            fill=obj.background_color + alpha_color,
        )
        # object debug
        if context.profile.is_debug:
            draw.text(
                xy=(100, 400),
                text=f"progress: {obj_state.animation_progress}; alpha: {alpha_value} : {obj.background_color + alpha_color}",
                fill="#ffffff",
            )


def token_color(token_type: _TokenType) -> str:
    if token_type in styles:
        return styles[token_type]
    else:
        return "#ffffff"  # todo: settings - default color
