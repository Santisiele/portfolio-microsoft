from domain.accounting.common import parse_money

COLUMN_BASE = 26


def _column_index(letters):
    index = 0
    for letter in letters:
        index = index * COLUMN_BASE + (ord(letter) - ord("A") + 1)
    return index - 1


def cell(grid, ref):
    letters = "".join(ch for ch in ref if ch.isalpha()).upper()
    digits = "".join(ch for ch in ref if ch.isdigit())
    if not letters or not digits:
        return None
    row = int(digits) - 1
    column = _column_index(letters)
    if not 0 <= row < len(grid):
        return None
    if not 0 <= column < len(grid[row]):
        return None
    return grid[row][column]


def parse_amount(value):
    if value is None:
        return None
    text = str(value).strip()
    negative = text.startswith("(") and text.endswith(")")
    number = "".join(ch for ch in text if ch.isdigit() or ch in ".,-")
    if not any(ch.isdigit() for ch in number):
        return None
    amount = parse_money(number)
    return -amount if negative else amount


def balance_at(grid, ref):
    return parse_amount(cell(grid, ref))
