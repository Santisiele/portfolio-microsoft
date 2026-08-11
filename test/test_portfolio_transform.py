from datetime import date
from domain.portfolio_transform import put_acreditation_date, eliminate_duplicate_checks

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