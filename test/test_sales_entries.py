import pytest

from domain.accounting.common import parse_money, amount_after
from domain.accounting import build_sales_entries


@pytest.mark.parametrize("raw,expected", [
    ("1.234,56", 1234.56),
    ("1,234.56", 1234.56),
    ("500,00", 500.0),
    ("105.00", 105.0),
    ("1234", 1234.0),
    ("", 0.0),
    ("0", 0.0),
])
def test_parse_money(raw, expected):
    assert parse_money(raw) == expected


def test_amount_after_reads_until_newline():
    obs = "INTERESES: $1.234,56\nCOMISION: $500,00\nIVA: $105,00"
    assert amount_after(obs, "INTERESES: $") == 1234.56
    assert amount_after(obs, "COMISION: $") == 500.0
    assert amount_after(obs, "IVA: $") == 105.0


def test_amount_after_missing_marker_is_zero():
    assert amount_after("sin nada", "IVA: $") == 0.0


def _normal_row():
    return {
        "gval_fechaconfirmacion": "2026-08-10",
        "gval_cuentapropiadestinoname": "5006",
        "gval_importetotalcheques": 1000,
        "gval_numerodeventa": "VC-00042",
        "gval_observaciones": "INTERESES: $100,00\nCOMISION: $50,00\nIVA: $10,50",
    }


def test_normal_sale_produces_six_lines():
    entries = build_sales_entries([_normal_row()])
    assert len(entries) == 6


def test_normal_sale_concept_strips_prefix_and_zeros():
    entries = build_sales_entries([_normal_row()])
    assert entries[0]["CONCEPTO"] == "ivsa vta 42"


def test_normal_sale_breaks_out_interest_commission_vat():
    entries = build_sales_entries([_normal_row()])
    debits = {e["SUBCTA"]: e["DEBE"] for e in entries if e["DEBE"]}
    assert debits[1120006] == 1000
    assert debits[6000001] == 100.0
    assert debits[6000002] == 50.0
    assert debits[3300001] == 10.5


def test_normal_sale_balances():
    entries = build_sales_entries([_normal_row()])
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)


def test_account_4002_uses_two_lines_and_obs_concept():
    row = {
        "gval_fechaconfirmacion": "2026-08-11",
        "gval_cuentapropiadestinoname": "4002",
        "gval_importetotalcheques": 777,
        "gval_numerodeventa": "VC-1",
        "gval_observaciones": "Pago Proveedor XYZ $500",
    }
    entries = build_sales_entries([row])
    assert len(entries) == 2
    assert entries[0]["SUBCTA"] == 1120097
    assert entries[0]["CONCEPTO"] == "venta pago proveedor xyz"
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)


def test_vat_goes_to_its_own_account():
    entries = build_sales_entries([_normal_row()])
    vat = [e for e in entries if e["DEBE"] == 10.5]
    assert len(vat) == 1 and vat[0]["SUBCTA"] == 3300001


def test_vat_does_not_use_an_expense_account():
    entries = build_sales_entries([_normal_row()])
    assert 6000003 not in [e["SUBCTA"] for e in entries]


def test_interest_and_commission_keep_their_accounts():
    entries = build_sales_entries([_normal_row()])
    debits = {e["SUBCTA"]: e["DEBE"] for e in entries if e["DEBE"]}
    assert debits[6000001] == 100.0 and debits[6000002] == 50.0


def test_sale_without_amounts_in_observations_leaves_them_in_zero():
    row = _normal_row()
    row["gval_observaciones"] = "venta sin detalle"
    entries = build_sales_entries([row])
    debits = {e["SUBCTA"]: e["DEBE"] for e in entries}
    assert debits[6000001] == 0.0 and debits[6000002] == 0.0 and debits[3300001] == 0.0
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)


@pytest.mark.parametrize("raw,expected", [
    ("$1.234,56", 1234.56),
    ("$1,234.56", 1234.56),
    (" $ 500,00", 500.0),
    ("474,861.22", 474861.22),
])
def test_parse_money_ignores_the_currency_symbol(raw, expected):
    assert parse_money(raw) == expected


SIN_SIMBOLO = "INTERESES: 474,861.22\nCOMISION: 288,873.91\nIVA: 110,523.95"
CON_SIMBOLO = "INTERESES: $1.005.330,75\nCOMISION: $18.724,14\nIVA: $3.932,07"


def test_amount_after_reads_amounts_without_the_symbol():
    assert amount_after(SIN_SIMBOLO, "INTERESES:") == 474861.22
    assert amount_after(SIN_SIMBOLO, "COMISION:") == 288873.91
    assert amount_after(SIN_SIMBOLO, "IVA:") == 110523.95


def test_amount_after_still_reads_amounts_with_the_symbol():
    assert amount_after(CON_SIMBOLO, "INTERESES:") == 1005330.75
    assert amount_after(CON_SIMBOLO, "COMISION:") == 18724.14
    assert amount_after(CON_SIMBOLO, "IVA:") == 3932.07


def _row_without_symbol():
    row = _normal_row()
    row["gval_observaciones"] = SIN_SIMBOLO
    return row


def test_sale_without_currency_symbol_breaks_out_the_amounts():
    entries = build_sales_entries([_row_without_symbol()])
    debits = {e["SUBCTA"]: e["DEBE"] for e in entries if e["DEBE"]}
    assert debits[6000001] == 474861.22
    assert debits[6000002] == 288873.91
    assert debits[3300001] == 110523.95


def test_sale_without_currency_symbol_balances():
    entries = build_sales_entries([_row_without_symbol()])
    assert sum(e["DEBE"] for e in entries) == pytest.approx(sum(e["HABER"] for e in entries))


def test_sale_without_currency_symbol_credits_the_three_amounts():
    entries = build_sales_entries([_row_without_symbol()])
    assert entries[-1]["HABER"] == pytest.approx(874259.08)


def test_both_observation_formats_work_together():
    entries = build_sales_entries([_normal_row(), _row_without_symbol()])
    debits = [e["DEBE"] for e in entries if e["SUBCTA"] == 6000001]
    assert debits == [100.0, 474861.22]
