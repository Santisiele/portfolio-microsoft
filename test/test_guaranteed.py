from datetime import date
from decimal import Decimal

from domain.guaranteed import guaranteed_total

TODAY = date(2026, 8, 12)


def test_only_future_acreditation_counts():
    rows = [
        {"Fecha": date(2026, 8, 11), "Garantizado": Decimal("100")},
        {"Fecha": date(2026, 6, 1), "Garantizado": Decimal("50")},
    ]
    assert guaranteed_total(rows, today=TODAY) == Decimal("100")


def test_all_past_returns_none():
    rows = [{"Fecha": date(2026, 6, 1), "Garantizado": Decimal("50")}]
    assert guaranteed_total(rows, today=TODAY) is None


def test_empty_returns_none():
    assert guaranteed_total([], today=TODAY) is None


def test_none_fecha_or_amount_skipped():
    rows = [
        {"Fecha": None, "Garantizado": Decimal("100")},
        {"Fecha": date(2026, 8, 11), "Garantizado": None},
    ]
    assert guaranteed_total(rows, today=TODAY) is None


def test_sums_several_future_dates():
    rows = [
        {"Fecha": date(2026, 8, 11), "Garantizado": Decimal("100")},
        {"Fecha": date(2026, 8, 12), "Garantizado": Decimal("200")},
    ]
    assert guaranteed_total(rows, today=TODAY) == Decimal("300")