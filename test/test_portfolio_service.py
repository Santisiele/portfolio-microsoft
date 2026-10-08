from datetime import date, timedelta
from decimal import Decimal

import pytest

import modules.portfolio.service as service


def _crm_row():
    return {
        "Fecha Pago": date.today() + timedelta(days=7),
        "Cuenta Destino": "5001",
        "Estado": "En cartera",
        "Importe": Decimal("100"),
        "Tasa de Interes": Decimal("5"),
        "Comision": Decimal("3.2"),
        "Dias": Decimal("360"),
    }


def test_crm_rows_get_real_rate_and_sheet_rows_keep_the_sheet_rate(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [_crm_row()])
    monkeypatch.setattr(service, "read_public_sheet",
                        lambda url: [{"Empresa": "SC1", "Importe": 50, "TASA MERCADO": 0.5421}])
    by_origin = {row["Origen"]: row for row in service.build_portfolio()}
    assert by_origin["DHF"]["Tasa"] == pytest.approx(7.526882)
    assert by_origin["CONFINANCE"]["Tasa"] == pytest.approx(7.526882)
    assert by_origin["BOLSA"]["Tasa"] == pytest.approx(54.21)


def test_sheet_row_without_rate_has_no_value(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet", lambda url: [{"Empresa": "SC1", "Importe": 50}])
    rows = service.build_portfolio()
    assert rows[0]["Tasa"] is None


def test_sheet_rate_with_non_numeric_text_has_no_value(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet",
                        lambda url: [{"Empresa": "SC1", "Importe": 50, "TASA MERCADO": "sin dato"}])
    assert service.build_portfolio()[0]["Tasa"] is None


def test_sheet_empty_cell_becomes_blank(monkeypatch):
    import math
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet",
                        lambda url: [{"Empresa": "SC1", "Importe": 50, "Endosante mercado": math.nan}])
    assert service.build_portfolio()[0]["Endoso cheque mercado"] == ""


def test_sheet_missing_column_becomes_blank(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet", lambda url: [{"Empresa": "SC1", "Importe": 50}])
    assert service.build_portfolio()[0]["Endoso cheque mercado"] == ""


def test_sheet_endorser_with_value_is_kept(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet",
                        lambda url: [{"Empresa": "SC1", "Importe": 50, "Endosante mercado": "INC S. A."}])
    assert service.build_portfolio()[0]["Endoso cheque mercado"] == "INC S. A."


def _sheet(rows):
    return lambda url: rows


def test_sold_sheet_rows_are_dropped(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet",
                        _sheet([{"Empresa": "SC1", "Importe": 50, "Estado": "VENDIDO"}]))
    assert service.build_portfolio() == []


def test_sheet_rows_in_cartera_are_kept(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet",
                        _sheet([{"Empresa": "SC1", "Importe": 50, "Estado": "CARTERA"}]))
    rows = service.build_portfolio()
    assert len(rows) == 1 and rows[0]["Estado"] == "CARTERA"


def test_sheet_rows_without_state_are_kept(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet", _sheet([{"Empresa": "SC1", "Importe": 50}]))
    assert len(service.build_portfolio()) == 1


def test_only_the_sold_sheet_rows_are_dropped(monkeypatch):
    monkeypatch.setattr(service, "read_tds", lambda env, query: [])
    monkeypatch.setattr(service, "read_public_sheet", _sheet([
        {"Empresa": "SC1", "Importe": 50, "Estado": "CARTERA"},
        {"Empresa": "PLATINUM", "Importe": 70, "Estado": "VENDIDO"},
        {"Empresa": "CONFINANCE", "Importe": 90, "Estado": "CARTERA"},
    ]))
    rows = service.build_portfolio()
    assert [row["Empresa"] for row in rows] == ["SC1", "CONFINANCE"]


def test_crm_sold_cheques_are_kept(monkeypatch):
    row = _crm_row()
    row["Estado"] = "Vendido"
    row["Cuenta Destino"] = "5005"
    monkeypatch.setattr(service, "read_tds", lambda env, query: [dict(row)])
    monkeypatch.setattr(service, "read_public_sheet", _sheet([]))
    rows = service.build_portfolio()
    assert [r["Origen"] for r in rows] == ["DHF", "CONFINANCE"]
    assert all(r["Estado"] == "Vendido" for r in rows)
