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
    assert debits[6000003] == 10.5


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