from config import RATES_SHEET_ID
from sources.gsheet import read_tab_grid
from domain.rates import build_rate_rows, sheet_columns, to_advance_rate

RATE_TABS = [
    {"title": "Ventas IVSA", "gid": "1629166573", "advance_rate": False},
    {"title": "Cauciones", "gid": "469877672", "advance_rate": True},
]


def build_rate_tables():
    if not RATES_SHEET_ID:
        return []
    tables = []
    for tab in RATE_TABS:
        grid = read_tab_grid(RATES_SHEET_ID, tab["gid"])
        rows = build_rate_rows(grid)
        if tab["advance_rate"]:
            to_advance_rate(rows)
        tables.append({
            "title": tab["title"],
            "columns": sheet_columns(grid),
            "rows": rows,
        })
    return tables
