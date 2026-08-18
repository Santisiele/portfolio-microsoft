from domain.accounting import build_rejected_entries

MAP = {"CILBRAKE SRL": 555}


def _row(account, importe=1000, gastos=50, iva=10, empresa="CILBRAKE SRL", numcheque="00099876"):
    return {"gval_fechadeconfirmacion": "2026-08-10", "gval_importe": importe,
            "gval_gastos": gastos, "gval_iva": iva, "gval_cuentacorrientename": empresa,
            "gval_numcheque": numcheque, "Cuenta": account}


def test_normal_five_lines_and_bank_name():
    entries = build_rejected_entries([_row("017")], MAP)
    assert len(entries) == 5
    assert entries[0]["CONCEPTO"] == "rech 9876 bbva"
    bank = next(e for e in entries if e["SUBCTA"] == 1120001)
    assert bank["HABER"] == 1000


def test_unknown_bank_uses_default_name_and_subaccount():
    entries = build_rejected_entries([_row("999")], MAP)
    assert entries[0]["CONCEPTO"] == "rech 9876 ivsa"
    assert any(e["SUBCTA"] == 1120006 and e["HABER"] == 1000 for e in entries)


def test_4002_uses_special_accounts():
    entries = build_rejected_entries([_row("4002")], MAP)
    assert len(entries) == 5
    assert any(e["SUBCTA"] == 1120097 and e["HABER"] == 1000 for e in entries)
    assert entries[0]["CONCEPTO"] == "rech 9876 (4002 p reg)"


def test_credit_concept_is_lowercase_company():
    entries = build_rejected_entries([_row("017")], MAP)
    credit = next(e for e in entries if e["SUBCTA"] == 1120001)
    assert credit["CONCEPTO"] == "rech 9876 cilbrake srl"


def test_balances():
    entries = build_rejected_entries([_row("017"), _row("4002")], MAP)
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)