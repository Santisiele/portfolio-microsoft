from domain.accounting import build_deposit_entries


def _rows():
    return [
        {"gval_fechaconfirmacion": "2026-08-10", "gval_cuentapropiadestinoname": "5006",
         "gval_importetotalcheques": 100, "gval_numtransaccionboletarealdedeposito": "abc123"},
        {"gval_fechaconfirmacion": "2026-08-10", "gval_cuentapropiadestinoname": "017",
         "gval_importetotalcheques": 50, "gval_numtransaccionboletarealdedeposito": "RECHAZO-9"},
        {"gval_fechaconfirmacion": "2026-08-11", "gval_cuentapropiadestinoname": "999",
         "gval_importetotalcheques": 200, "gval_numtransaccionboletarealdedeposito": "xyz"},
    ]


def test_debit_line_per_deposit():
    entries = build_deposit_entries(_rows())
    debit = [e for e in entries if e["SUBCTA"] != 1300001]
    assert len(debit) == 3


def test_account_maps_to_subaccount():
    entries = build_deposit_entries(_rows())
    assert entries[0]["SUBCTA"] == 1120006
    assert entries[1]["SUBCTA"] == 1120001


def test_unknown_account_uses_default():
    entries = build_deposit_entries(_rows())
    assert entries[2]["SUBCTA"] == 1120006


def test_rechazo_changes_concept():
    entries = build_deposit_entries(_rows())
    assert entries[1]["CONCEPTO"] == "depo del dia rechazo"
    assert entries[0]["CONCEPTO"] == "depo del dia"


def test_credit_grouped_and_summed_by_date():
    entries = build_deposit_entries(_rows())
    credit = {e["FECH"]: e["HABER"] for e in entries if e["SUBCTA"] == 1300001}
    assert credit["2026-08-10"] == 150
    assert credit["2026-08-11"] == 200


def test_debit_and_credit_balance():
    entries = build_deposit_entries(_rows())
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)