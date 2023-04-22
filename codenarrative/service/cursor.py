import domain.rendering
import domain.keypress


def get_rows_data(text: str) -> list[domain.rendering.TextRowData]:
    text_rows: list[domain.rendering.TextRowData] = []
    col = 1
    f = 0
    min_index = 0
    while f < len(text):
        c = text[f]
        if c == "\n":
            text_rows.append(domain.rendering.TextRowData(min_index, f, col))
            min_index = f + 1
            col = 1
        else:
            col = col + 1
        f = f + 1
    text_rows.append(domain.rendering.TextRowData(min_index, f, col))
    # outstanding place for insertion at the end
    last_row = text_rows[len(text_rows) - 1]
    last_row.max_cols = last_row.max_cols + 1
    return text_rows


def move_cursor(
    rows_data: list[domain.rendering.TextRowData],
    cursor: domain.rendering.Cursor,
    key: domain.keypress.Key,
    current_col: int = -1,
):
    current_col_effective = cursor.pos.col if current_col == -1 else current_col
    match key:
        case domain.keypress.Key.ARROW_UP:
            cursor.pos.row = cursor.pos.row - 1
            row_data_after = rows_data[cursor.pos.row - 1]
            cursor.pos.col = min(current_col_effective, row_data_after.max_cols)
            cursor.index = row_data_after.min_index + cursor.pos.col - 1
        case domain.keypress.Key.ARROW_DOWN:
            cursor.pos.row = cursor.pos.row + 1
            row_data_after = rows_data[cursor.pos.row - 1]
            cursor.pos.col = min(current_col, row_data_after.max_cols)
            cursor.index = row_data_after.min_index + cursor.pos.col - 1
        case domain.keypress.Key.ARROW_LEFT:
            cursor.index = cursor.index - 1
            cursor.pos.col = cursor.pos.col - 1
        case domain.keypress.Key.ARROW_RIGHT:
            cursor.index = cursor.index + 1
            cursor.pos.col = cursor.pos.col + 1
