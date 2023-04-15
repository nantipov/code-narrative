import domain.rendering
import domain.keypress

def get_max_cols(text: str) -> list[int]:
    lines: list[int] = []
    col = 1
    row = 1
    f = 0
    while f < len(text):
        c = text[f]
        if c == "\n":
            lines.append(col)
            row = row + 1
            col = 1
        else:
            col = col + 1
        f = f + 1
    lines.append(col)
    # outstanding place for insertion at the end
    lines[len(lines) - 1] = lines[len(lines) - 1] + 1
    return lines

def move_cursor(max_cols: list[int], cursor: domain.rendering.Cursor, key: domain.keypress.Key, current_col: int = -1):
    current_col_effective = cursor.pos.col if current_col == -1 else current_col
    line_max_col = max_cols[cursor.pos.row - 1]
    line_min_index = cursor.index - cursor.pos.col + 1
    line_max_index = line_min_index + line_max_col - 1
    match key:
        case domain.keypress.Key.ARROW_UP:
            col_before_rowchange = cursor.pos.col
            cursor.pos.row = cursor.pos.row - 1
            new_row_max_col = max_cols[cursor.pos.row - 1]
            cursor.pos.col = min(current_col_effective, new_row_max_col)
            cursor.index = cursor.index - col_before_rowchange - new_row_max_col + cursor.pos.col
        case domain.keypress.Key.ARROW_DOWN:
            cursor.pos.row = cursor.pos.row + 1
            cursor.pos.col = min(current_col, max_cols[cursor.pos.row - 1])
            cursor.index = line_max_index + cursor.pos.col - 1
        case domain.keypress.Key.ARROW_LEFT:
            cursor.index = cursor.index - 1
            cursor.pos.col = cursor.pos.col - 1
        case domain.keypress.Key.ARROW_RIGHT:
            cursor.index = cursor.index + 1
            cursor.pos.col = cursor.pos.col + 1
