from domain.balances import parse_amount

COMPANY_COLUMN = "Empresa"
TOTAL_LABEL = "Total"
CHEQUES_LABEL = "VALOR ACTUAL CHEQUES"
CHEQUES_INDEX = 2
WIDTH = 5


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _values(line):
    return [_text(line[index]) if index < len(line) else "" for index in range(WIDTH)]


def availability_date(grid):
    return _text(grid[0][0]) if grid and len(grid[0]) else ""


def availability_columns(grid):
    if not grid:
        return []
    return [COMPANY_COLUMN] + [_text(cell) for cell in grid[0][1:WIDTH]]


def _row(columns, values, is_total):
    row = dict(zip(columns, values))
    row["is_total"] = is_total
    return row


def build_availability_rows(grid):
    columns = availability_columns(grid)
    if len(columns) < WIDTH:
        return []
    rows = []
    for line in grid[1:]:
        values = _values(line)
        if not values[0]:
            if any(values[1:]):
                rows.append(_row(columns, [TOTAL_LABEL] + values[1:], True))
            break
        rows.append(_row(columns, values, False))
    return rows


def cheques_value(grid):
    for line in grid:
        if _text(line[0] if len(line) else "") == CHEQUES_LABEL:
            return parse_amount(line[CHEQUES_INDEX]) if len(line) > CHEQUES_INDEX else None
    return None
