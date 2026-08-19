from domain.accounting import build_payment_entries

MAP = {"CILBRAKE SRL": 555}


def _row(importe=900, empresa="CILBRAKE SRL"):
    return {"gval_fechaconfirmacion": "2026-08-10", "gval_importe": importe,
            "gval_empresaname": empresa}


def test_two_lines_bank_and_company():
    entries = build_payment_entries([_row()], MAP)
    assert entries[0]["SUBCTA"] == 1120002 and entries[0]["HABER"] == 900
    assert entries[1]["SUBCTA"] == 555 and entries[1]["DEBE"] == 900


def test_concept_is_lowercase_company():
    entries = build_payment_entries([_row()], MAP)
    assert entries[0]["CONCEPTO"] == "adelanto x bco"
    assert entries[1]["CONCEPTO"] == "adelanto x bco cilbrake srl"


def test_unmatched_company_uses_zero():
    entries = build_payment_entries([_row(empresa="EMPRESA NUEVA SA")], MAP)
    assert entries[1]["SUBCTA"] == 0


def test_balances():
    entries = build_payment_entries([_row()], MAP)
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)