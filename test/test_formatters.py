from datetime import date, datetime
from decimal import Decimal
from presentation import format_dates, format_amounts, format_cuits, format_ars, format_percentages


def test_formats_date_to_ddmmyyyy():
    rows = [{"Fecha Pago": date(2026, 7, 8)}]
    assert format_dates(rows)[0]["Fecha Pago"] == "08/07/2026"


def test_formats_datetime_to_ddmmyyyy():
    rows = [{"Fecha Pago": datetime(2026, 7, 8, 0, 0)}]
    assert format_dates(rows)[0]["Fecha Pago"] == "08/07/2026"


def test_leaves_none_date_untouched():
    rows = [{"Fecha Pago": None}]
    assert format_dates(rows)[0]["Fecha Pago"] is None


def test_leaves_non_date_columns_untouched():
    rows = [{"Importe": 1000, "Estado": "En cartera"}]
    out = format_dates(rows)
    assert out[0]["Estado"] == "En cartera"


def test_formats_amount_argentine_style():
    rows = [{"Importe": 1234567.8}]
    assert format_amounts(rows)[0]["Importe"] == "1,234,567.80"


def test_formats_small_amount():
    rows = [{"Importe": 50.5}]
    assert format_amounts(rows)[0]["Importe"] == "50.50"


def test_leaves_none_amount_untouched():
    rows = [{"Importe": None}]
    assert format_amounts(rows)[0]["Importe"] is None


def test_formats_decimal_amount():
    rows = [{"Importe": Decimal("387552.56000000000000000")}]
    assert format_amounts(rows)[0]["Importe"] == "387,552.56"


def test_formats_cuit_from_decimal():
    rows = [{"Cuit Librador": Decimal("20313890733")}]
    assert format_cuits(rows)[0]["Cuit Librador"] == "20-31389073-3"
 
 
def test_leaves_none_cuit_untouched():
    rows = [{"Cuit Librador": None}]
    assert format_cuits(rows)[0]["Cuit Librador"] is None
 
 
def test_leaves_invalid_length_cuit_untouched():
    rows = [{"Cuit Librador": "123"}]
    assert format_cuits(rows)[0]["Cuit Librador"] == "123"


def test_none_shows_dashes():
    assert format_ars(None) == "--"
 
 
def test_argentine_thousands_and_decimals():
    assert format_ars(Decimal("180000000")) == "$180.000.000,00"
 
 
def test_decimal_places():
    assert format_ars(1234.5) == "$1.234,50"
 
 
def test_zero_is_not_dashes():
    assert format_ars(0) == "$0,00"


def test_formats_percentage_with_two_decimals():
    rows = [{"Tasa": 20.256}]
    assert format_percentages(rows)[0]["Tasa"] == "20.26%"


def test_formats_percentage_from_decimal():
    rows = [{"Tasa": Decimal("19.87")}]
    assert format_percentages(rows)[0]["Tasa"] == "19.87%"


def test_formats_percentage_from_numeric_string():
    rows = [{"Tasa": "20.15"}]
    assert format_percentages(rows)[0]["Tasa"] == "20.15%"


def test_percentage_always_shows_two_decimals():
    rows = [{"Tasa": Decimal("20.5")}, {"Tasa": 20.5}, {"Tasa": 20}]
    assert [row["Tasa"] for row in format_percentages(rows)] == ["20.50%", "20.50%", "20.00%"]


def test_leaves_none_percentage_untouched():
    rows = [{"Tasa": None}]
    assert format_percentages(rows)[0]["Tasa"] is None


def test_percentage_skips_rows_without_the_column():
    rows = [{"Importe": 100}]
    assert format_percentages(rows) == [{"Importe": 100}]


def test_percentage_columns_are_configurable():
    rows = [{"Tasa de Interes": 4.25}]
    assert format_percentages(rows, columns=["Tasa de Interes"])[0]["Tasa de Interes"] == "4.25%"
