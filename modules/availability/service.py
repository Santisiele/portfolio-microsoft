from config import AVAILABILITY_SHEET_ID
from sources.gsheet import read_tab_grid
from domain.availability import availability_columns, build_availability_rows, cheques_value

AVAILABILITY_GID = "1139858595"
AVAILABILITY_RANGE = "A1:E30"


def build_availability():
    if not AVAILABILITY_SHEET_ID:
        return {}
    grid = read_tab_grid(AVAILABILITY_SHEET_ID, AVAILABILITY_GID, AVAILABILITY_RANGE)
    return {
        "columns": availability_columns(grid),
        "rows": build_availability_rows(grid),
        "cheques": cheques_value(grid),
    }
