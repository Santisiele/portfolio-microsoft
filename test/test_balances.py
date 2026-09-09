from domain.balances import cell, parse_amount, balance_at

GRID = [
    ["DHF", " $  183,120,474.00 "],
    ["CONFINANCE", "$362,440,619.00"],
    ["BINAGA", "(738,813.00)"],
    ["VACIO", None],
]


def test_cell_resolves_a1_notation():
    assert cell(GRID, "A1") == "DHF"
    assert cell(GRID, "B2") == "$362,440,619.00"


def test_cell_outside_grid_is_none():
    assert cell(GRID, "Z1") is None
    assert cell(GRID, "A99") is None


def test_cell_handles_two_letter_columns():
    assert cell([["x"] * 27 + ["ultima"]], "AB1") == "ultima"


def test_parse_amount_strips_currency_and_spaces():
    assert parse_amount(" $  183,120,474.00 ") == 183120474.0


def test_parse_amount_reads_argentine_separators():
    assert parse_amount("$1.234.567,89") == 1234567.89


def test_parse_amount_reads_parentheses_as_negative():
    assert parse_amount("(738,813.00)") == -738813.0


def test_parse_amount_without_digits_is_none():
    assert parse_amount(None) is None
    assert parse_amount("") is None
    assert parse_amount("nan") is None


def test_balance_at_reads_and_parses():
    assert balance_at(GRID, "B1") == 183120474.0
    assert balance_at(GRID, "B3") == -738813.0


def test_balance_at_empty_cell_is_none():
    assert balance_at(GRID, "B4") is None
