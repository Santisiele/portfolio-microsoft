from datetime import date

import pytest

import modules.portfolio_historic.service as service
from queries.portfolio_historic import STATES, build_where, page_query, totals_query

BASE = {"desde": "2025-01-01", "hasta": "2026-01-01"}


def test_where_always_filters_by_payment_date():
    clauses, params = build_where(BASE)
    assert "gval_fechavaloroperacioncompra >= ?" in clauses
    assert params[:2] == ["2025-01-01", "2026-01-01"]


def test_where_uses_every_state_when_none_is_chosen():
    _, params = build_where(BASE)
    assert params[2:] == list(STATES)


def test_where_uses_only_the_chosen_states():
    _, params = build_where({**BASE, "estados": ["Vendido"]})
    assert params[2:] == ["Vendido"]


def test_where_adds_the_text_filters_as_parameters():
    clauses, params = build_where({**BASE, "cliente": "CILBRAKE", "cuit": "20176"})
    assert "gval_empresaname LIKE ?" in clauses
    assert "gval_firmanteunocuitcargarapida LIKE ?" in clauses
    assert "%CILBRAKE%" in params and "%20176%" in params


def test_where_ignores_empty_text_filters():
    clauses, _ = build_where({**BASE, "cliente": "   ", "firmante": ""})
    assert "LIKE" not in clauses


def test_text_filters_never_reach_the_sql_text():
    clauses, params = build_where({**BASE, "cliente": "'; DROP TABLE gval_cheque --"})
    assert "DROP TABLE" not in clauses
    assert "%'; DROP TABLE gval_cheque --%" in params


def test_page_query_adds_offset_and_size_at_the_end():
    query, params = page_query(BASE, 200, 100)
    assert "OFFSET ? ROWS FETCH NEXT ? ROWS ONLY" in query
    assert params[-2:] == [200, 100]


def test_totals_query_counts_and_sums():
    query, _ = totals_query(BASE)
    assert "COUNT(*)" in query and "SUM(gval_cheque.gval_importe)" in query
    assert "OFFSET" not in query


@pytest.fixture(autouse=True)
def sin_bolsa(monkeypatch):
    monkeypatch.setattr(service.bolsa, "filtered", lambda filters: [])
    monkeypatch.setattr(service.bolsa, "totals", lambda filters: {"cantidad": 0, "total": 0.0})


def _row(fecha, importe, cliente="X"):
    return {"Fecha Compra": fecha, "Importe": importe, "Cliente": cliente,
            "Cuenta Destino": "5001", "Estado": "En cartera"}


def _reader(por_entorno):
    def leer(env, query, params=None):
        return [dict(r) for r in por_entorno.get(env, [])]
    return leer


def test_page_merges_both_environments_newest_first(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({
        "DHF": [_row("2026-05-01", 100)],
        "CONFINANCE": [_row("2026-09-01", 200)],
    }))
    rows = service.build_historic_page(BASE, page=1, size=10)
    assert [r["Fecha Compra"] for r in rows] == ["2026-09-01", "2026-05-01"]


def test_page_tags_each_row_with_its_environment(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({
        "DHF": [_row("2026-05-01", 100)],
        "CONFINANCE": [_row("2026-09-01", 200)],
    }))
    rows = service.build_historic_page(BASE, page=1, size=10)
    assert {r["Origen"] for r in rows} == {"DHF", "CONFINANCE"}
    assert {r["Empresa"] for r in rows} == {"CRM-DHF", "CRM-CONFINANCE"}


def test_page_returns_only_the_requested_slice(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({
        "DHF": [_row("2026-09-04", 4), _row("2026-09-02", 2)],
        "CONFINANCE": [_row("2026-09-03", 3), _row("2026-09-01", 1)],
    }))
    primera = service.build_historic_page(BASE, page=1, size=2)
    segunda = service.build_historic_page(BASE, page=2, size=2)
    assert [r["Fecha Compra"] for r in primera] == ["2026-09-04", "2026-09-03"]
    assert [r["Fecha Compra"] for r in segunda] == ["2026-09-02", "2026-09-01"]


def test_page_can_read_a_single_environment(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({
        "DHF": [_row("2026-05-01", 100)],
        "CONFINANCE": [_row("2026-09-01", 200)],
    }))
    rows = service.build_historic_page(BASE, page=1, size=10, sources=("DHF",))
    assert [r["Origen"] for r in rows] == ["DHF"]


def test_page_asks_for_enough_rows_to_cover_the_offset(monkeypatch):
    pedidos = []

    def leer(env, query, params=None):
        pedidos.append(params[-2:])
        return []

    monkeypatch.setattr(service, "read_tds", leer)
    service.build_historic_page(BASE, page=3, size=50)
    assert pedidos == [[0, 150], [0, 150]]


def test_totals_add_up_both_environments(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({
        "DHF": [{"Cantidad": 10, "Total": 1000.5}],
        "CONFINANCE": [{"Cantidad": 5, "Total": 500.5}],
    }))
    assert service.build_historic_totals(BASE) == {"cantidad": 15, "total": 1501.0}


def test_totals_handle_an_empty_environment(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({
        "DHF": [{"Cantidad": 2, "Total": None}],
        "CONFINANCE": [],
    }))
    assert service.build_historic_totals(BASE) == {"cantidad": 2, "total": 0.0}


def test_default_range_covers_the_last_twelve_months():
    desde, hasta = service.default_range(date(2026, 10, 30))
    assert desde == "2025-10-30" and hasta == "2026-10-30"


def test_default_range_handles_the_29th_of_february():
    desde, _ = service.default_range(date(2024, 2, 29))
    assert desde == "2023-02-28"


def test_page_keeps_the_rate_calculation(monkeypatch):
    fila = _row("2026-09-01", 100)
    fila.update({"Dias": 360, "Tasa de Interes": 5, "Comision": 3.2})
    monkeypatch.setattr(service, "read_tds", _reader({"DHF": [fila], "CONFINANCE": []}))
    rows = service.build_historic_page(BASE, page=1, size=10)
    assert rows[0]["Tasa"] == pytest.approx(7.526882)


def _bolsa_row(fecha, importe):
    return {"Fecha Compra": fecha, "Importe": importe, "Origen": "BOLSA",
            "Empresa": "SC1", "Cliente": "mesa", "Estado": "ACREDITADO"}


def test_page_merges_the_market_sheet_with_the_crm(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({"DHF": [_row("2026-05-01", 100)]}))
    monkeypatch.setattr(service.bolsa, "filtered", lambda filters: [_bolsa_row("2026-09-01", 50)])
    rows = service.build_historic_page(BASE, page=1, size=10)
    assert [r["Origen"] for r in rows] == ["BOLSA", "DHF"]


def test_page_can_read_only_the_market_sheet(monkeypatch):
    def nunca(env, query, params=None):
        raise AssertionError("no deberia consultar el crm")

    monkeypatch.setattr(service, "read_tds", nunca)
    monkeypatch.setattr(service.bolsa, "filtered", lambda filters: [_bolsa_row("2026-09-01", 50)])
    rows = service.build_historic_page(BASE, page=1, size=10, sources=("BOLSA",))
    assert [r["Origen"] for r in rows] == ["BOLSA"]


def test_page_leaves_the_market_sheet_out_when_it_is_not_asked(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({"DHF": [_row("2026-05-01", 100)]}))
    monkeypatch.setattr(service.bolsa, "filtered", lambda filters: [_bolsa_row("2026-09-01", 50)])
    rows = service.build_historic_page(BASE, page=1, size=10, sources=("DHF",))
    assert [r["Origen"] for r in rows] == ["DHF"]


def test_totals_include_the_market_sheet(monkeypatch):
    monkeypatch.setattr(service, "read_tds", _reader({"DHF": [{"Cantidad": 3, "Total": 300.0}]}))
    monkeypatch.setattr(service.bolsa, "totals", lambda filters: {"cantidad": 2, "total": 200.0})
    assert service.build_historic_totals(BASE) == {"cantidad": 5, "total": 500.0}
