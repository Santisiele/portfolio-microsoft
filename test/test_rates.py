from domain.rates import build_rate_rows, sheet_columns, to_arrears_rate

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
    ["Mes", "Hoja", "Días Prom. Ponderados", "Suma Costo", "Tasa Total"],
    ["2026-01", "CONFINANCE", "20.96", "$12,292,188.69", "29.22%"],
    ["2026-01", "TOTAL MES", "26.63", "$56,973,602.01", "29.67%"],
]


def test_arrears_rate_converts_the_advance_rate():
    rows = to_arrears_rate(build_rate_rows(RATE_GRID))
    assert rows[0]["Tasa Total"] == "29.72%"


def test_arrears_rate_also_converts_the_total_row():
    rows = to_arrears_rate(build_rate_rows(RATE_GRID))
    assert rows[1]["is_total"] and rows[1]["Tasa Total"] == "30.33%"


def test_arrears_rate_is_higher_than_the_advance_rate():
    rows = to_arrears_rate(build_rate_rows(RATE_GRID))
    assert float(rows[0]["Tasa Total"].rstrip("%")) > 29.22


def test_arrears_rate_depends_on_the_term():
    grid = [RATE_GRID[0], ["2026-01", "CONFINANCE", "40.00", "$12,292,188.69", "29.22%"]]
    largo = to_arrears_rate(build_rate_rows(grid))[0]["Tasa Total"]
    corto = to_arrears_rate(build_rate_rows(RATE_GRID))[0]["Tasa Total"]
    assert float(largo.rstrip("%")) > float(corto.rstrip("%"))


def test_arrears_rate_leaves_the_other_columns_untouched():
    rows = to_arrears_rate(build_rate_rows(RATE_GRID))
    assert rows[0]["Suma Costo"] == "$12,292,188.69"
    assert rows[0]["Hoja"] == "CONFINANCE"


def test_arrears_rate_without_term_is_blank():
    grid = [RATE_GRID[0], ["2026-01", "CONFINANCE", "", "$12,292,188.69", "29.22%"]]
    assert to_arrears_rate(build_rate_rows(grid))[0]["Tasa Total"] == ""


def test_arrears_rate_with_zero_term_is_blank():
    grid = [RATE_GRID[0], ["2026-01", "CONFINANCE", "0", "$12,292,188.69", "29.22%"]]
    assert to_arrears_rate(build_rate_rows(grid))[0]["Tasa Total"] == ""


def test_arrears_rate_without_rate_is_blank():
    grid = [RATE_GRID[0], ["2026-01", "CONFINANCE", "20.96", "$12,292,188.69", ""]]
    assert to_arrears_rate(build_rate_rows(grid))[0]["Tasa Total"] == ""


def test_arrears_rate_when_the_advance_rate_covers_the_whole_term_is_blank():
    grid = [RATE_GRID[0], ["2026-01", "CONFINANCE", "365", "$12,292,188.69", "150.00%"]]
    assert to_arrears_rate(build_rate_rows(grid))[0]["Tasa Total"] == ""
