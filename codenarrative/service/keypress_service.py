from codenarrative.domain.keypress import Keypress, Key
from codenarrative.domain.rendering import Cursor, TextRowData
from codenarrative.domain import rendering
from codenarrative.service import cursor_service
import difflib


class OpCode:
    def __init__(self, code: tuple[str, int, int, int, int]):
        self.tag, self.i1, self.i2, self.j1, self.j2 = code


def compute_keypresses(init_cursor: Cursor, text1: str, text2: str) -> list[Keypress]:
    matcher = difflib.SequenceMatcher(a=text1, b=text2)
    codes = [OpCode(c) for c in matcher.get_opcodes()]
    keypresses = []
    cursor = rendering.copy_cursor(init_cursor)

    rows_data = cursor_service.get_rows_data(text1)
    text = text1

    for code in codes:
        match code.tag:
            case "replace":
                for key in bring_cursor(cursor, rows_data, code.i1):
                    keypresses.append(key)

                # it turned out 'replace' code might combine actual replace, insert and delete
                keypresses.append(Keypress(Key.TOGGLE_CURSOR_REPLACE))
                for j in range(code.j1, code.j2):
                    char = text2[j]
                    i = code.i1 + j - code.j1
                    if i < code.i2:  # replace
                        text = text[:i] + char + text[i + 1 :]
                    else:  # insert
                        text = text[:i] + char + text[i:]
                    keypresses.append(Keypress(Key.OTHER, char))
                    cursor.index = cursor.index + 1
                    if char == "\n":
                        cursor.pos.row = cursor.pos.row + 1
                        cursor.pos.col = 1
                    else:
                        cursor.pos.col = cursor.pos.col + 1
                    if i == min(code.i2 - 1, code.j2 - 1):  # end of replace
                        keypresses.append(Keypress(Key.TOGGLE_CURSOR_INSERT))
                patch_len = (code.j2 - code.j1) - (code.i2 - code.i1)
                if patch_len < 0:  # delete
                    deletion_index = code.i1 + (code.j2 - code.j1)
                    for _ in range(abs(patch_len)):
                        text = text[:deletion_index] + text[deletion_index + 1 :]
                        keypresses.append(Keypress(Key.DELETE))
                if patch_len != 0:  # insert or delete was involved
                    for patch_code in codes:
                        if patch_code != code and patch_code.i1 >= code.i1:
                            patch_code.i1 = patch_code.i1 + patch_len
                            patch_code.i2 = patch_code.i2 + patch_len
                rows_data = cursor_service.get_rows_data(text)
            case "delete":
                for key in bring_cursor(cursor, rows_data, code.i2):
                    keypresses.append(key)
                characters_to_delete = code.i2 - code.i1
                for f in range(characters_to_delete):
                    i = code.i2 - f
                    char = text[i]
                    text = text[:i] + text[i + 1 :]
                    keypresses.append(Keypress(Key.BACKSPACE))
                    cursor.index = cursor.index - 1
                    if char == "\n":
                        cursor.pos.row = cursor.pos.row - 1
                        cursor.pos.col = rows_data[cursor.pos.row - 1].max_cols
                    else:
                        cursor.pos.col = cursor.pos.col - 1
                for patch_code in codes:
                    if patch_code != code and patch_code.i1 >= code.i1:
                        patch_code.i1 = patch_code.i1 - characters_to_delete
                        patch_code.i2 = patch_code.i2 - characters_to_delete
                rows_data = cursor_service.get_rows_data(text)
            case "insert":
                for key in bring_cursor(cursor, rows_data, code.i1):
                    keypresses.append(key)

                for j in range(code.j1, code.j2):
                    char = text2[j]
                    i = code.i1 + j - code.j1
                    text = text[:i] + char + text[i:]
                    keypresses.append(Keypress(Key.OTHER, char))
                    cursor.index = cursor.index + 1
                    if char == "\n":
                        cursor.pos.row = cursor.pos.row + 1
                        cursor.pos.col = 1
                    else:
                        cursor.pos.col = cursor.pos.col + 1
                patch_len = code.j2 - code.j1
                for patch_code in codes:
                    if patch_code != code and patch_code.i1 >= code.i1:
                        patch_code.i1 = patch_code.i1 + patch_len
                        patch_code.i2 = patch_code.i2 + patch_len
                rows_data = cursor_service.get_rows_data(text)
            case "equal":
                continue

    return keypresses


def bring_cursor(
    current_cursor: Cursor,
    rows_data: list[TextRowData],
    target_index: int,
) -> list[Keypress]:
    keypresses: list[Keypress] = []
    aligned_col = current_cursor.pos.col
    while target_index != current_cursor.index:
        row_data = rows_data[current_cursor.pos.row - 1]
        if target_index < row_data.min_index:  # target is somewhere at line above
            key = Key.ARROW_UP
            cursor_service.move_cursor(rows_data, current_cursor, key, aligned_col)
            keypresses.append(Keypress(key, aligned_current_column=aligned_col))
        elif (
            target_index < current_cursor.index
        ):  # target is within the line, to the left side of cursor
            key = Key.ARROW_LEFT
            while target_index < current_cursor.index:
                cursor_service.move_cursor(rows_data, current_cursor, key, aligned_col)
                aligned_col = current_cursor.pos.col
                keypresses.append(Keypress(key, aligned_current_column=aligned_col))
        elif target_index > row_data.max_index:  # target is somewhere at line below
            key = Key.ARROW_DOWN
            cursor_service.move_cursor(rows_data, current_cursor, key, aligned_col)
            keypresses.append(Keypress(key, aligned_current_column=aligned_col))
        elif (
            target_index > current_cursor.index
        ):  # target is within the line, to the right side of cursor
            key = Key.ARROW_RIGHT
            while target_index > current_cursor.index:
                cursor_service.move_cursor(rows_data, current_cursor, key, aligned_col)
                aligned_col = current_cursor.pos.col
                keypresses.append(Keypress(key, aligned_current_column=aligned_col))
    return keypresses
