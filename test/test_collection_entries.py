from domain.accounting.common import resolve_subaccount
from domain.accounting import build_collection_entries


def test_resolve_exact_match():
    assert resolve_subaccount("CILBRAKE SRL", {"CILBRAKE SRL": 1361400}) == 1361400


def test_resolve_substring_sheet_name_inside_company():
    company_map = {"CILBRAKE SRL": 1361400}
    assert resolve_subaccount("CILBRAKE SRL SUCURSAL 2", company_map) == 1361400


def test_resolve_no_match_returns_zero():
    assert resolve_subaccount("EMPRESA NUEVA SA", {"CILBRAKE SRL": 1361400}) == 0


def test_resolve_ambiguous_distinct_values_returns_zero():
    company_map = {"CILBRAKE": 111, "CILBRAKE SRL": 222}
    assert resolve_subaccount("CILBRAKE SRL", company_map) == 0


def test_resolve_multiple_matches_same_value_returns_it():
    company_map = {"CILBRAKE": 111, "CILBRAKE SRL": 111}
    assert resolve_subaccount("CILBRAKE SRL", company_map) == 111


def _rows():
    return [
        {"Fecha": "2026-08-10", "Empresa": "CILBRAKE SRL", "Importe": 1000},
        {"Fecha": "2026-08-11", "Empresa": "EMPRESA SIN CUENTA SA", "Importe": 500},
    ]


def test_two_lines_per_collection():
    entries = build_collection_entries(_rows(), {"CILBRAKE SRL": 1361400})
    assert len(entries) == 4


def test_debit_is_fixed_credit_is_company_subaccount():
    entries = build_collection_entries(_rows(), {"CILBRAKE SRL": 1361400})
    assert entries[0]["SUBCTA"] == 1120002 and entries[0]["DEBE"] == 1000
    assert entries[1]["SUBCTA"] == 1361400 and entries[1]["HABER"] == 1000


def test_unmatched_company_credit_uses_zero():
    entries = build_collection_entries(_rows(), {"CILBRAKE SRL": 1361400})
    assert entries[3]["SUBCTA"] == 0


def test_concept_is_lowercase_company():
    entries = build_collection_entries(_rows(), {})
    assert entries[0]["CONCEPTO"] == "Cobranza cilbrake srl"


def test_collection_balances():
    entries = build_collection_entries(_rows(), {"CILBRAKE SRL": 1361400})
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)