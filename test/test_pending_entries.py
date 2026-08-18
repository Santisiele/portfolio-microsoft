from domain.accounting import build_pending_entries

MAP = {"CILBRAKE SRL": 555, "PENDIENTES NO ENCONTRADOS": 1300010}


def _row(importe=400, empresa="CILBRAKE SRL", numcheque="12345678"):
    return {"gval_fechadeconfirmacion": "2026-08-10", "gval_importe": importe,
            "gval_cuentacorrientename": empresa, "gval_numcheque": numcheque}


def test_debit_company_credit_not_found():
    entries = build_pending_entries([_row()], MAP)
    assert entries[0]["SUBCTA"] == 555 and entries[0]["DEBE"] == 400
    assert entries[1]["SUBCTA"] == 1300010 and entries[1]["HABER"] == 400


def test_concept_uses_last_four_of_cheque():
    entries = build_pending_entries([_row()], MAP)
    assert entries[0]["CONCEPTO"] == "dep del dia pte 5678"
    assert entries[1]["CONCEPTO"] == "dep del dia 5678"


def test_balances():
    entries = build_pending_entries([_row()], MAP)
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)