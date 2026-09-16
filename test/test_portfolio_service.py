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
    assert by_origin["DHF"]["Tasa"] == pytest.approx(7.0)
    assert by_origin["CONFINANCE"]["Tasa"] == pytest.approx(7.0)
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
