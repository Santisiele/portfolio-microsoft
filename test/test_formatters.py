from datetime import date, datetime
from presentation import format_dates


def test_formats_date_to_ddmmyyyy():
    rows = [{"fecha_pago": date(2026, 7, 8)}]
    assert format_dates(rows)[0]["fecha_pago"] == "08/07/2026"


def test_formats_datetime_to_ddmmyyyy():
    rows = [{"fecha_pago": datetime(2026, 7, 8, 0, 0)}]
    assert format_dates(rows)[0]["fecha_pago"] == "08/07/2026"


def test_leaves_none_untouched():
    rows = [{"fecha_pago": None}]
    assert format_dates(rows)[0]["fecha_pago"] is None


def test_leaves_non_date_columns_untouched():
    rows = [{"importe": 1000, "estado": "En cartera"}]
    out = format_dates(rows)
    assert out[0]["importe"] == 1000
    assert out[0]["estado"] == "En cartera"