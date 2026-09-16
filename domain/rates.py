from domain.balances import parse_amount

MONTH_COLUMN = "Mes"
SHEET_COLUMN = "Hoja"
RATE_COLUMN = "Tasa Total"
COST_COLUMN = "Suma Costo"
NUMERAL_COLUMN = "Numeral"
TOTAL_LABEL = "TOTAL MES"
ADVANCE_DAYS = 360


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _header(grid):
    if not grid:
        return []
    return [(index, _text(cell)) for index, cell in enumerate(grid[0]) if _text(cell)]


def sheet_columns(grid):
    return [name for _, name in _header(grid)]


def build_rate_rows(grid, excluded=()):
    header = _header(grid)
    if not header:
        return []
    skip = {name.upper() for name in excluded}
    rows = []
    for line in grid[1:]:
        row = {name: _text(line[index]) if index < len(line) else "" for index, name in header}
        if not row.get(MONTH_COLUMN):
            continue
        sheet = row.get(SHEET_COLUMN, "").upper()
        if sheet in skip:
            continue
        row["is_total"] = sheet == TOTAL_LABEL
        rows.append(row)
    return rows


def to_advance_rate(rows):
    for row in rows:
        if RATE_COLUMN not in row:
            continue
        cost = parse_amount(row.get(COST_COLUMN))
        numeral = parse_amount(row.get(NUMERAL_COLUMN))
        if cost is None or not numeral:
            row[RATE_COLUMN] = ""
            continue
        row[RATE_COLUMN] = f"{cost / numeral * ADVANCE_DAYS * 100:.2f}%"
    return rows
