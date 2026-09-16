from domain.rates import build_rate_rows, sheet_columns, to_advance_rate

GRID = [
    ["Mes", "Hoja", "Suma Capital", "Tasa Total"],
    ["2025-12", "CONFINANCE", "$3,758,383,441.43", "48.82%"],
    ["2025-12", "HERNAN", "$851,765,718.00", "67.88%"],
    ["2025-12", "JORGE", "$7,133,919,037.00", "59.50%"],
    ["2025-12", "TOTAL MES", "$15,057,975,506.43", "50.45%"],
    ["", "", "", ""],
]


def test_reads_the_column_names_from_the_sheet():
    assert sheet_columns(GRID) == ["Mes", "Hoja", "Suma Capital", "Tasa Total"]


def test_keeps_every_row_when_nothing_is_excluded():
    rows = build_rate_rows(GRID)
    assert [row["Hoja"] for row in rows] == ["CONFINANCE", "HERNAN", "JORGE", "TOTAL MES"]


def test_excludes_the_given_sheets():
    rows = build_rate_rows(GRID, ("HERNAN", "JORGE"))
    assert [row["Hoja"] for row in rows] == ["CONFINANCE", "TOTAL MES"]


def test_exclusion_ignores_case():
    rows = build_rate_rows(GRID, ("hernan",))
    assert "HERNAN" not in [row["Hoja"] for row in rows]


def test_skips_rows_without_month():
    assert all(row["Mes"] for row in build_rate_rows(GRID))


def test_marks_the_total_row():
    rows = build_rate_rows(GRID)
    assert [row["is_total"] for row in rows] == [False, False, False, True]


def test_keeps_the_values_of_each_column():
    row = build_rate_rows(GRID)[0]
    assert row["Suma Capital"] == "$3,758,383,441.43"
    assert row["Tasa Total"] == "48.82%"


def test_empty_grid_has_no_rows_or_columns():
    assert build_rate_rows([]) == []
    assert sheet_columns([]) == []


RATE_GRID = [
    ["Mes", "Hoja", "Suma Costo", "Numeral", "Tasa Total"],
    ["2025-12", "CONFINANCE", "$20,031,084.05", "$14,975,660,641.43", "48.82%"],
    ["2025-12", "TOTAL MES", "$67,697,785.18", "$48,976,193,947.43", "50.45%"],
]


def test_advance_rate_uses_cost_over_numeral_on_360_days():
    rows = to_advance_rate(build_rate_rows(RATE_GRID))
    assert rows[0]["Tasa Total"] == "48.15%"


def test_advance_rate_also_converts_the_total_row():
    rows = to_advance_rate(build_rate_rows(RATE_GRID))
    assert rows[1]["is_total"] and rows[1]["Tasa Total"] == "49.76%"


def test_advance_rate_leaves_the_other_columns_untouched():
    rows = to_advance_rate(build_rate_rows(RATE_GRID))
    assert rows[0]["Suma Costo"] == "$20,031,084.05"
    assert rows[0]["Hoja"] == "CONFINANCE"


def test_advance_rate_without_numeral_is_blank():
    grid = [RATE_GRID[0], ["2025-12", "CONFINANCE", "$20,031,084.05", "", "48.82%"]]
    assert to_advance_rate(build_rate_rows(grid))[0]["Tasa Total"] == ""


def test_advance_rate_with_zero_numeral_is_blank():
    grid = [RATE_GRID[0], ["2025-12", "CONFINANCE", "$20,031,084.05", "$0.00", "48.82%"]]
    assert to_advance_rate(build_rate_rows(grid))[0]["Tasa Total"] == ""
