import domain.rendering
import domain.storage
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.style import Style
from io import StringIO


def render_html(location: domain.storage.Location, state: domain.rendering.SceneState):
    filename = location.frame_file(state.frame, "html")
    with open(filename, 'w') as writer:
        # header
        print(
            f"""
            <html>
              <head>
                <title>frame {state.frame}</title>
                <link rel="stylesheet" href="main.css">
              </head>
              <body>
            """,
            file=writer
        )

        # code and cursor
        if not state.code is None:
            print("<div><pre>", file=writer)
            lexer = get_lexer_by_name(state.code.syntax, stripall=True)
            formatter = HtmlFormatter(nowrap=True, style=OwnStyle)

            code_index = 0
            tokens: list[tuple] = []
            for token_type, token_value in lexer.get_tokens(text=state.code.text):
                if code_index > state.cursor.index:
                    tokens.append((token_type, token_value))
                elif code_index + len(token_value) <= state.cursor.index:
                    tokens.append((token_type, token_value))
                elif code_index + len(token_value) > state.cursor.index:
                    cursor_index = state.cursor.index - code_index
                    pre_cursor = token_value[:cursor_index]
                    in_cursor = "" if state.cursor.is_insert else token_value[cursor_index]
                    post_cursor = token_value[cursor_index:]
                    tokens.append((token_type, pre_cursor))
                    output = format_text(formatter, tokens) + cursor(state, in_cursor)
                    print(output, file=writer)
                    tokens.clear()
                    tokens.append((token_type, post_cursor))
                code_index = code_index + len(token_value)

            output = ""
            if len(tokens) > 0:
              output = output + format_text(formatter, tokens)

            if code_index < state.cursor.index:
                output = output + cursor(state, "")

            print(output, file=writer)
            print("</pre></div>", file=writer)

        # highlights

        # notes

        # footer
        print(
            f"""
              </body>
            </html>
            """,
            file=writer
        )

def format_text(formatter: HtmlFormatter, tokens: list) -> str:
    with StringIO() as str_stream:
        formatter.format(tokens, str_stream)
        str_stream.flush()
        value = str_stream.getvalue()
        if value[-1] == "\n":
            return value[:-1]
        else:
            return value

def cursor(state: domain.rendering.SceneState, in_cursor_text: str) -> str:
    cycle = round(state.profile.fps/2)
    cursor_text = "&nbsp;" if len(in_cursor_text) == 0 else in_cursor_text
    inv = 0
    if state.frame % cycle < cycle/2:
        inv = 0.7    
    return f"<span style=\"background-color: white; color: black; filter: invert({inv})\">{cursor_text}</span>"

def write_styles(location: domain.storage.Location):
    #filename = location.file("main", "css")
    html_dir, _ = location.directory_and_file("main", "html")
    filename = f"{html_dir}/main.css"
    with open(filename, 'w') as writer:
        print(HtmlFormatter().get_style_defs(), file=writer)
        print(
        """
        body {
          background-color: white;
        }
        """, file=writer)

class OwnStyle(Style):
    background_color = "white"

