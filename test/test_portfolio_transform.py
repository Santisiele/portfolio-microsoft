from datetime import date
from domain.portfolio_transform import enrich_portfolio

TODAY = date(2026, 8, 4)


def test_keeps_row_with_future_acreditation():
    rows = [{"Fecha Pago": date(2026, 8, 3)}]
    out = enrich_portfolio(rows, today=TODAY)
    assert len(out) == 1
    assert out[0]["Fecha Acr."] == date(2026, 8, 5)


def test_discards_row_with_past_acreditation():
    rows = [{"Fecha Pago": date(2026, 7, 8)}]
    out = enrich_portfolio(rows, today=TODAY)
    assert out == []


def test_keeps_row_without_payment_date():
    rows = [{"Fecha Pago": None}]
    out = enrich_portfolio(rows, today=TODAY)
    assert len(out) == 1
    assert out[0]["Fecha Acr."] is None


def test_filters_only_the_expired_rows():
    rows = [
        {"Fecha Pago": date(2026, 8, 3)},
        {"Fecha Pago": date(2026, 7, 8)},
        {"Fecha Pago": None},
    ]
    out = enrich_portfolio(rows, today=TODAY)
    assert len(out) == 2