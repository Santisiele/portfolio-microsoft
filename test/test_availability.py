from domain.availability import availability_columns, availability_date, build_availability_rows, cheques_value

GRID = [
    ["24/09", "Cuota partes", "Aportes Nominal", "Valor cuota partes", "Valor Patrimonial"],
    ["CONSULTATIO CONFINANCE", "8027864.465", "$297,074,484.83", "$80.52", "$646,370,491.66"],
    ["CONSULTATIO DHF B", "", "", "", ""],
    ["INVIU EYZOR", "0", "-$18,894,864.92", "", "$0.00"],
    ["", "175903243.8", "$10,468,320,191.91", "", "$14,162,516,814.18"],
    ["", "", "", "IG", "14,162,517,161.35"],
    ["24/09/2026", "Calculo", "Informe Gestion", "Diferencia", "-$347.17"],
    ["VALOR ACTUAL CHEQUES", "$13,783,909,884.35", "$13,783,808,459.86", "$101,424.49", ""],
]


def test_reads_the_column_names_and_labels_the_first_one():
    assert availability_columns(GRID) == [
        "Empresa", "Cuota partes", "Aportes Nominal", "Valor cuota partes", "Valor Patrimonial",
    ]


def test_keeps_one_row_per_company():
    rows = build_availability_rows(GRID)
    assert [row["Empresa"] for row in rows] == [
        "CONSULTATIO CONFINANCE", "CONSULTATIO DHF B", "INVIU EYZOR", "Total",
    ]


def test_marks_the_total_row():
    rows = build_availability_rows(GRID)
    assert [row["is_total"] for row in rows] == [False, False, False, True]


def test_keeps_the_values_of_each_company():
    row = build_availability_rows(GRID)[0]
    assert row["Cuota partes"] == "8027864.465"
    assert row["Valor Patrimonial"] == "$646,370,491.66"


def test_company_without_values_keeps_its_name():
    row = build_availability_rows(GRID)[1]
    assert row["Empresa"] == "CONSULTATIO DHF B"
    assert row["Valor Patrimonial"] == ""


def test_stops_before_the_second_block():
    assert all(row["Empresa"] != "24/09/2026" for row in build_availability_rows(GRID))


def test_reads_the_cheques_value_from_the_management_report():
    assert cheques_value(GRID) == 13783808459.86


def test_cheques_value_is_none_when_the_row_is_missing():
    assert cheques_value([GRID[0], GRID[1]]) is None


def test_empty_grid_has_no_rows_or_columns():
    assert build_availability_rows([]) == []
    assert availability_columns([]) == []


def test_reads_the_date_from_the_first_cell():
    assert availability_date(GRID) == "24/09"


def test_date_is_blank_when_the_cell_is_empty():
    assert availability_date([["", "Cuota partes"], ["X", "1"]]) == ""


def test_date_is_blank_without_grid():
    assert availability_date([]) == ""
