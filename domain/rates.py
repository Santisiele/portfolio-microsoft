import calendar
from datetime import date

from domain.balances import parse_amount

MONTH_COLUMN = "Mes"
SHEET_COLUMN = "Hoja"
RATE_COLUMN = "Tasa Total"
COST_COLUMN = "Suma Costo"
NUMERAL_COLUMN = "Numeral"
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


def _day_number(month, today):
    parts = month.split("-")
    if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return 0
    year, number = int(parts[0]), int(parts[1])
    if not 1 <= number <= 12:
        return 0
    if (year, number) == (today.year, today.month):
        return today.day
    return calendar.monthrange(year, number)[1]


def to_advance_rate(rows, today=None):
    today = today or date.today()
    for row in rows:
        if RATE_COLUMN not in row:
            continue
        cost = parse_amount(row.get(COST_COLUMN))
        numeral = parse_amount(row.get(NUMERAL_COLUMN))
        days = _day_number(row.get(MONTH_COLUMN, ""), today)
        if cost is None or not numeral or not days:
            row[RATE_COLUMN] = ""
            continue
        overdue = cost / numeral * YEAR_DAYS
        daily = overdue / YEAR_DAYS * days
        row[RATE_COLUMN] = f"{daily / (1 + daily) / days * YEAR_DAYS * 100:.2f}%"
    return rows
