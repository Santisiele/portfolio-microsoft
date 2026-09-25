from domain.balances import parse_amount

MONTH_COLUMN = "Mes"
SHEET_COLUMN = "Hoja"
RATE_COLUMN = "Tasa Total"
TERM_COLUMN = "Días Prom. Ponderados"
TOTAL_LABEL = "TOTAL MES"
YEAR_DAYS = 365


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


def to_arrears_rate(rows):
    for row in rows:
        if RATE_COLUMN not in row:
            continue
        rate = parse_amount(row.get(RATE_COLUMN))
        days = parse_amount(row.get(TERM_COLUMN))
        if rate is None or not days:
            row[RATE_COLUMN] = ""
            continue
        advance = rate / 100 / YEAR_DAYS * days
        if advance >= 1:
            row[RATE_COLUMN] = ""
            continue
        row[RATE_COLUMN] = f"{advance / (1 - advance) / days * YEAR_DAYS * 100:.2f}%"
    return rows
