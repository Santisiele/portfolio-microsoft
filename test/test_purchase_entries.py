from domain.accounting.common import resolve_subaccount_max
from domain.accounting import build_purchase_entries


def test_resolve_max_picks_highest_matching_subaccount():
    company_map = {"CILBRAKE": 100, "CILBRAKE SRL": 500}
    assert resolve_subaccount_max("CILBRAKE SRL", company_map) == 500


def test_resolve_max_no_match_is_zero():
    assert resolve_subaccount_max("NUEVA SA", {"CILBRAKE": 100}) == 0


def _row(**kw):
    base = {
        "Fecha": "2026-08-10", "Bruto": 0, "Comision": 0, "Intereses": 0,
        "Interior": 0, "Iva": 0, "Saldo a descontar": 0, "Neto final": 0,
        "Nombre cliente": "CILBRAKE SRL", "Cuenta destino": "banco",
    }
    base.update(kw)
    return base


def test_daily_gross_debit():
    rows = [_row(Bruto=1000), _row(Bruto=500)]
    entries = build_purchase_entries(rows)
    f1 = [e for e in entries if e["SUBCTA"] == 1300001]
    assert len(f1) == 1
    assert f1[0]["DEBE"] == 1500


def test_one_two_percent_only_on_rows_with_interest_or_commission():
    rows = [_row(Bruto=1000, Intereses=10), _row(Bruto=2000)]
    entries = build_purchase_entries(rows)
    debit = next(e for e in entries if e["SUBCTA"] == 7010001 and e["DEBE"])
    credit = next(e for e in entries if e["SUBCTA"] == 7020001)
    assert round(debit["DEBE"], 2) == 12.0
    assert round(credit["HABER"], 2) == 12.0


def test_net_goes_to_bank_when_not_aforo():
    entries = build_purchase_entries([_row(**{"Neto final": 800, "Cuenta destino": "banco"})])
    f8 = [e for e in entries if e["SUBCTA"] == 1120002]
    assert len(f8) == 1 and f8[0]["HABER"] == 800


def test_net_goes_to_company_when_aforo():
    row = _row(**{"Neto final": 800, "Cuenta destino": "aforo", "Nombre cliente": "CILBRAKE SRL"})
    entries = build_purchase_entries([row], {"CILBRAKE SRL": 555})
    company_credits = [e for e in entries if e["SUBCTA"] == 555 and e["CONCEPTO"] == "deja saldo en cta"]
    assert len(company_credits) == 1 and company_credits[0]["HABER"] == 800


def test_saldo_a_descontar_creates_company_credit():
    row = _row(**{"Saldo a descontar": 300, "Nombre cliente": "CILBRAKE SRL"})
    entries = build_purchase_entries([row], {"CILBRAKE SRL": 555})
    f7 = [e for e in entries if e["CONCEPTO"] == "cobro x su cta"]
    assert len(f7) == 1 and f7[0]["SUBCTA"] == 555 and f7[0]["HABER"] == 300


def test_zero_lines_are_filtered_out():
    entries = build_purchase_entries([_row(**{"Bruto": 1000, "Neto final": 1000})])
    assert all(e["DEBE"] or e["HABER"] for e in entries)


def test_balanced_entry():
    row = _row(**{
        "Bruto": 1000, "Intereses": 100, "Comision": 50, "Iva": 10,
        "Interior": 20, "Saldo a descontar": 0, "Neto final": 820, "Cuenta destino": "banco",
    })
    entries = build_purchase_entries([row])
    assert round(sum(e["DEBE"] for e in entries), 2) == round(sum(e["HABER"] for e in entries), 2)