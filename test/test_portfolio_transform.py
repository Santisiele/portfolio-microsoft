from datetime import date
from decimal import Decimal

import pytest

from domain.portfolio_transform import put_acreditation_date, eliminate_duplicate_checks, put_interest_real_rate

TODAY = date(2026, 8, 4)


def test_keeps_row_with_future_acreditation():
    rows = [{"Fecha Pago": date(2026, 8, 3)}]
    out = put_acreditation_date(rows, today=TODAY)
    assert len(out) == 1
    assert out[0]["Fecha Acr."] == date(2026, 8, 5)


def test_discards_row_with_past_acreditation():
    rows = [{"Fecha Pago": date(2026, 7, 8)}]
    out = put_acreditation_date(rows, today=TODAY)
    assert out == []


def test_discards_row_without_payment_date():
    rows = [{"Fecha Pago": None}]
    out = put_acreditation_date(rows, today=TODAY)
    assert len(out) == 0


def test_drops_expired_and_missing_payment_rows():
    rows = [
        {"Fecha Pago": date(2026, 8, 3)},
        {"Fecha Pago": date(2026, 7, 8)},
        {"Fecha Pago": None},
    ]
    out = put_acreditation_date(rows, today=TODAY)
    assert len(out) == 1
    assert out[0]["Fecha Pago"] == date(2026, 8, 3)


def _row(origin="DHF", account="5006", state="Vendido"):
    return {"Origen": origin, "Cuenta Destino": account, "Estado": state}


def test_removes_matching_row():
    assert eliminate_duplicate_checks([_row()]) == []


def test_keeps_when_origin_differs():
    row = _row(origin="OTRO")
    assert eliminate_duplicate_checks([row]) == [row]


def test_keeps_when_account_differs():
    row = _row(account="5005")
    assert eliminate_duplicate_checks([row]) == [row]


def test_keeps_when_state_differs():
    row = _row(state="Depositado")
    assert eliminate_duplicate_checks([row]) == [row]


def test_removes_for_both_origins():
    rows = [_row(origin="DHF"), _row(origin="CONFINANCE")]
    assert eliminate_duplicate_checks(rows) == []


def test_removes_for_both_accounts():
    rows = [_row(account="5006"), _row(account="5011")]
    assert eliminate_duplicate_checks(rows) == []


def test_keeps_others_and_preserves_order():
    keep_state = _row(state="Depositado")
    dropped = _row()
    keep_account = _row(account="5005")
    out = eliminate_duplicate_checks([keep_state, dropped, keep_account])
    assert out == [keep_state, keep_account]


def test_keeps_row_with_missing_keys():
    row = {"Firmante": "X"}
    assert eliminate_duplicate_checks([row]) == [row]


def _rate_row(days=365, interest=5, commission=3.2):
    return {"Dias": days, "Tasa de Interes": interest, "Comision": commission}


def test_real_rate_adds_interest_and_annualized_commission():
    out = put_interest_real_rate([_rate_row(interest=10, commission=1.0)])
    assert out[0]["Tasa"] == pytest.approx(11.0)


def test_real_rate_subtracts_fixed_commission_above_threshold():
    out = put_interest_real_rate([_rate_row(commission=3.2)])
    assert out[0]["Tasa"] == pytest.approx(7.0)


def test_real_rate_keeps_commission_at_threshold():
    out = put_interest_real_rate([_rate_row(commission=1.2)])
    assert out[0]["Tasa"] == pytest.approx(6.2)


def test_real_rate_keeps_commission_below_threshold():
    out = put_interest_real_rate([_rate_row(commission=1.0)])
    assert out[0]["Tasa"] == pytest.approx(6.0)


def test_real_rate_annualizes_commission_by_days():
    out = put_interest_real_rate([_rate_row(days=73, commission=2.2)])
    assert out[0]["Tasa"] == pytest.approx(10.0)


def test_real_rate_accepts_decimals_from_crm():
    row = {"Dias": Decimal("365"), "Tasa de Interes": Decimal("5"), "Comision": Decimal("3.2")}
    assert put_interest_real_rate([row])[0]["Tasa"] == pytest.approx(7.0)


def test_real_rate_keeps_the_other_columns():
    row = {"Firmante": "X", **_rate_row()}
    out = put_interest_real_rate([row])
    assert out[0]["Firmante"] == "X"
    assert out[0]["Tasa de Interes"] == 5


def test_real_rate_keeps_every_row_in_order():
    out = put_interest_real_rate([_rate_row(days=30), _rate_row(days=60)])
    assert [row["Dias"] for row in out] == [30, 60]


def test_real_rate_is_none_without_days():
    out = put_interest_real_rate([_rate_row(days=None)])
    assert out[0]["Tasa"] is None


def test_real_rate_is_none_without_interest():
    out = put_interest_real_rate([_rate_row(interest=None)])
    assert out[0]["Tasa"] is None


def test_real_rate_is_none_without_commission():
    out = put_interest_real_rate([_rate_row(commission=None)])
    assert out[0]["Tasa"] is None


def test_real_rate_is_none_with_zero_days():
    out = put_interest_real_rate([_rate_row(days=0)])
    assert out[0]["Tasa"] is None


def test_row_without_rate_data_does_not_break_the_others():
    out = put_interest_real_rate([_rate_row(days=None), _rate_row(commission=3.2)])
    assert len(out) == 2
    assert out[0]["Tasa"] is None
    assert out[1]["Tasa"] == pytest.approx(7.0)
