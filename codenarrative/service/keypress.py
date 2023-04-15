import domain.keypress
import domain.rendering
import difflib
import service.cursor

class OpCode:
    def __init__(self, code: tuple[str, int, int, int, int]):
        self.tag, self.i1, self.i2, self.j1, self.j2 = code

def compute_keypresses(init_cursor: domain.rendering.Cursor, text1: str, text2: str) -> list[domain.keypress.Keypress]:
    matcher = difflib.SequenceMatcher(a=text1, b=text2)
    codes = [OpCode(c) for c in matcher.get_opcodes()]
    keypresses = []
    cursor = domain.rendering.copy_cursor(init_cursor)

    max_cols = service.cursor.get_max_cols(text1)
    text = text1

    for code in codes:
        match code.tag:
            case "replace":
                for key in bring_cursor(cursor, max_cols, code.i1):
                    keypresses.append(key)

                keypresses.append(domain.keypress.Keypress(domain.keypress.Key.TOGGLE_CURSOR_REPLACE))
                for j in range(code.j1, code.j2):
                    char = text2[j]
                    i = code.i1 + j - code.j1
                    text = text[:i] + char + text[i+1:]
                    keypresses.append(domain.keypress.Keypress(domain.keypress.Key.OTHER, char))
                    cursor.index = cursor.index + 1
                    if char == "\n":
                        cursor.pos.row = cursor.pos.row + 1
                        cursor.pos.col = 1
                    else:
                        cursor.pos.col = cursor.pos.col + 1
                keypresses.append(domain.keypress.Keypress(domain.keypress.Key.TOGGLE_CURSOR_INSERT))
                max_cols = service.cursor.get_max_cols(text)
            case "delete":
                for key in bring_cursor(cursor, max_cols, code.i2):
                    keypresses.append(key)
                charaters_to_delete = code.i2 - code.i1
                for f in range(charaters_to_delete):
                    i = code.i2 - f
                    keypresses.append(domain.keypress.Keypress(domain.keypress.Key.BACKSPACE))
                    cursor.index = cursor.index - 1
                    char = text[i]
                    if char == "\n":
                        cursor.pos.row = cursor.pos.row - 1
                        cursor.pos.col = max_cols[cursor.pos.row - 1]
                    else:
                        cursor.pos.col = cursor.pos.col - 1
                for patch_code in codes:
                    if patch_code != code and patch_code.i1 >= code.i1:
                        patch_code.i1 = patch_code.i1 - charaters_to_delete
                        patch_code.i2 = patch_code.i2 - charaters_to_delete
                max_cols = service.cursor.get_max_cols(text)
            case "insert":
                for key in bring_cursor(cursor, max_cols, code.i1):
                    keypresses.append(key)

                for j in range(code.j1, code.j2):
                    char = text2[j]
                    i = code.i1 + j - code.j1
                    text = text[:i] + char + text[i:]
                    keypresses.append(domain.keypress.Keypress(domain.keypress.Key.OTHER, char))
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
                max_cols = service.cursor.get_max_cols(text)
            case "equal":
                continue

    return keypresses

def bring_cursor(current_cursor: domain.rendering.Cursor, max_cols: list[int], target_index: int) -> list[domain.keypress.Keypress]:
    keypresses: list[domain.keycurrent_cursorpress.Keypress] = []
    aligned_col = current_cursor.pos.col
    while target_index != current_cursor.index:
        line_max_col = max_cols[current_cursor.pos.row - 1]
        line_min_index = current_cursor.index - current_cursor.pos.col + 1 # beginning of the line
        line_max_index = line_min_index + line_max_col - 1 # end of the line
        if target_index < line_min_index: # target is somewhere at line above
            key = domain.keypress.Key.ARROW_UP
            service.cursor.move_cursor(max_cols, current_cursor, key, aligned_col)
            keypresses.append(domain.keypress.Keypress(key, aligned_current_column=aligned_col))
        elif target_index < current_cursor.index: # target is within the line, to the left side of cursor
            key = domain.keypress.Key.ARROW_LEFT
            while target_index < current_cursor.index:
                service.cursor.move_cursor(max_cols, current_cursor, key, aligned_col)
                aligned_col = current_cursor.pos.col
                keypresses.append(domain.keypress.Keypress(key, aligned_current_column=aligned_col))
        elif target_index > line_max_index: # target is somehere at line below
            key = domain.keypress.Key.ARROW_DOWN
            service.cursor.move_cursor(max_cols, current_cursor, key, aligned_col)
            keypresses.append(domain.keypress.Keypress(key, aligned_current_column=aligned_col))
        elif target_index > current_cursor.index: # target is within the line, to the right side of cursor
            key = domain.keypress.Key.ARROW_RIGHT
            while target_index > current_cursor.index:
                service.cursor.move_cursor(max_cols, current_cursor, key, aligned_col)
                aligned_col = current_cursor.pos.col
                keypresses.append(domain.keypress.Keypress(key, aligned_current_column=aligned_col))
    return keypresses
