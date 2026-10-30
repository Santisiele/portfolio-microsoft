import json
import logging

import pytest
from decimal import Decimal


@pytest.fixture
def client():
    import app as application
    application.app.config.update(TESTING=True)
    return application.app.test_client()


def _login(client):
    with client.session_transaction() as sess:
        sess["user"] = {"name": "Tester"}


def test_home_shows_login_when_logged_out(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Iniciar sesión" in r.get_data(as_text=True)


def test_portfolio_table_redirects_without_login(client):
    r = client.get("/portfolio/table")
    assert r.status_code == 302


def test_portfolio_table_with_login(client, monkeypatch):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "X", "Importe": 100, "Origen": "DHF"}])
    _login(client)
    r = client.get("/portfolio/table")
    assert r.status_code == 200
    assert "DHF" in r.get_data(as_text=True)


def _sample_rows():
    return [
        {"Firmante": "A", "Cliente": "Uno", "Importe": 100,
         "Origen": "DHF", "Cuenta Destino": "5001", "Estado": "En cartera"},
        {"Firmante": "B", "Cliente": "Dos", "Importe": 200,
         "Origen": "CONFINANCE", "Cuenta Destino": "5002", "Estado": "Pendiente"},
        {"Firmante": "C", "Cliente": "Tres", "Importe": 300,
         "Origen": "BOLSA", "Cuenta Destino": "5003", "Estado": "Pendiente de pago"},
    ]


def test_portfolio_has_pending_checks(client, monkeypatch):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio", _sample_rows)
    _login(client)
    r = client.get("/portfolio/table")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Pendiente" in html
    assert "Pendiente de pago" in html


def test_pending_states_survive_the_pipeline(monkeypatch):
    from presentation import format_dates, format_cuits, format_states
    rows = format_states(format_cuits(format_dates(_sample_rows())))
    states = [row["Estado"] for row in rows]
    assert "Pendiente" in states
    assert "Pendiente de pago" in states
    assert any(s in ("Pendiente", "Pendiente de pago") for s in states)


def test_panel_redirects_without_login(client):
    r = client.get("/panel")
    assert r.status_code == 302


def _panel_data():
    return {
        "guaranteed": {"dhf": Decimal("100"), "confinance": Decimal("50"), "total": Decimal("150")},
        "checking_account": {"dhf": None, "confinance": Decimal("25"), "total": Decimal("25")},
        "balances": [
            {"name": "Confinance", "amount": 362440619.0},
            {"name": "DHF", "amount": 183120474.0},
            {"name": "SC1", "amount": 878315440.61},
        ],
    }


def test_panel_shows_guaranteed_amounts(client, monkeypatch):
    import routes.financial_panel as rp
    monkeypatch.setattr(rp, "build_financial_panel", _panel_data)
    _login(client)
    r = client.get("/panel")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "$100,00" in html
    assert "$50,00" in html
    assert "$150,00" in html


def test_panel_shows_dashes_for_missing_amount(client, monkeypatch):
    import routes.financial_panel as rp
    monkeypatch.setattr(rp, "build_financial_panel", _panel_data)
    _login(client)
    html = client.get("/panel").get_data(as_text=True)
    assert "--" in html


def test_panel_shows_balance_cards_and_their_sum(client, monkeypatch):
    import routes.financial_panel as rp
    monkeypatch.setattr(rp, "build_financial_panel", _panel_data)
    _login(client)
    html = client.get("/panel").get_data(as_text=True)
    assert "Saldos de cuentas" in html
    assert "$878.315.440,61" in html
    assert "$1.423.876.533,61" in html


def test_panel_has_a_jump_link_per_group(client, monkeypatch):
    import routes.financial_panel as rp
    monkeypatch.setattr(rp, "build_financial_panel", _panel_data)
    _login(client)
    html = client.get("/panel").get_data(as_text=True)
    for group_id in ("garantizados", "cuenta-corriente", "saldos"):
        assert 'href="#' + group_id + '"' in html
        assert 'id="' + group_id + '"' in html


def test_portfolio_shows_real_rate_as_percentage(client, monkeypatch):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "X", "Importe": 100, "Origen": "DHF",
                                  "Tasa de Interes": Decimal("5"), "Tasa": 20.5}])
    _login(client)
    html = client.get("/portfolio/table").get_data(as_text=True)
    assert "20.50%" in html
    assert "Tasa de Interes" not in html


def test_portfolio_sorts_rate_as_number(client, monkeypatch):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "X", "Importe": 100, "Origen": "DHF", "Tasa": 9.5}])
    _login(client)
    html = client.get("/portfolio/table").get_data(as_text=True)
    assert 'data-type="number">Tasa<' in html


def test_portfolio_renders_rows_without_interest_rate(client, monkeypatch):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "Y", "Importe": 50, "Origen": "BOLSA"}])
    _login(client)
    r = client.get("/portfolio/table")
    assert r.status_code == 200
    assert "BOLSA" in r.get_data(as_text=True)


def test_portfolio_has_purchase_date_filter(client, monkeypatch):
    from datetime import date
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "X", "Importe": 100, "Origen": "DHF",
                                  "Fecha Compra": date(2026, 9, 3)}])
    _login(client)
    html = client.get("/portfolio/table").get_data(as_text=True)
    assert 'id="f-compra-from"' in html
    assert 'id="f-compra-to"' in html
    assert 'data-compra="2026-09-03"' in html


def test_portfolio_row_without_purchase_date_has_empty_attribute(client, monkeypatch):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "Y", "Importe": 50, "Origen": "BOLSA"}])
    _login(client)
    html = client.get("/portfolio/table").get_data(as_text=True)
    assert 'data-compra=""' in html


def test_portfolio_leaves_empty_sheet_rate_blank(client, monkeypatch):
    import math
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "Y", "Importe": 50, "Origen": "BOLSA", "Tasa": math.nan}])
    _login(client)
    html = client.get("/portfolio/table").get_data(as_text=True)
    assert "nan" not in html.lower().split("<tbody")[1]


def _rate_tables():
    return [{
        "title": "Cauciones",
        "columns": ["Mes", "Hoja", "Suma Capital"],
        "rows": [
            {"Mes": "2025-12", "Hoja": "CONFINANCE", "Suma Capital": "$3,758,383,441.43", "is_total": False},
            {"Mes": "2025-12", "Hoja": "TOTAL MES", "Suma Capital": "$15,057,975,506.43", "is_total": True},
        ],
    }]


def test_rates_redirects_without_login(client):
    assert client.get("/tasas").status_code == 302


def test_rates_shows_the_table_in_argentine_format(client, monkeypatch):
    import routes.rates as rr
    monkeypatch.setattr(rr, "build_rate_tables", _rate_tables)
    _login(client)
    html = client.get("/tasas").get_data(as_text=True)
    assert "Cauciones" in html
    assert "$3.758.383.441,43" in html
    assert "table-secondary" in html


def _availability():
    return {
        "date": "30/09",
        "columns": ["Empresa", "Cuota partes", "Valor Patrimonial"],
        "rows": [
            {"Empresa": "CONSULTATIO CONFINANCE", "Cuota partes": "8027864.465",
             "Valor Patrimonial": "$646,370,491.66", "is_total": False},
            {"Empresa": "Total", "Cuota partes": "175903243.8",
             "Valor Patrimonial": "$14,162,516,814.18", "is_total": True},
        ],
        "cheques": 13783808459.86,
    }


def test_availability_redirects_without_login(client):
    assert client.get("/disponibilidades").status_code == 302


def test_availability_shows_companies_and_cheques(client, monkeypatch):
    import routes.availability as ra
    monkeypatch.setattr(ra, "build_availability", _availability)
    _login(client)
    html = client.get("/disponibilidades").get_data(as_text=True)
    assert "CONSULTATIO CONFINANCE" in html
    assert "$646.370.491,66" in html
    assert "$13.783.808.459,86" in html
    assert "table-secondary" in html


def test_availability_without_sheet_shows_no_results(client, monkeypatch):
    import routes.availability as ra
    monkeypatch.setattr(ra, "build_availability", dict)
    _login(client)
    html = client.get("/disponibilidades").get_data(as_text=True)
    assert "Sin resultados" in html


def test_availability_paints_each_company_with_its_colour(client, monkeypatch):
    import routes.availability as ra
    monkeypatch.setattr(ra, "build_availability", _availability)
    _login(client)
    html = client.get("/disponibilidades").get_data(as_text=True)
    assert 'class="tag disp-confinance"' in html


def test_availability_leaves_the_total_row_without_colour(client, monkeypatch):
    import routes.availability as ra
    monkeypatch.setattr(ra, "build_availability", _availability)
    _login(client)
    html = client.get("/disponibilidades").get_data(as_text=True)
    assert "tag disp-" not in html.split("Total")[1]


def test_availability_shows_the_sheet_date_next_to_the_title(client, monkeypatch):
    import routes.availability as ra
    monkeypatch.setattr(ra, "build_availability", _availability)
    _login(client)
    html = client.get("/disponibilidades").get_data(as_text=True)
    assert ">Disponibilidades al 30/09</h1>" in html


def test_portfolio_has_a_download_button(client, monkeypatch):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "X", "Importe": 100, "Origen": "DHF"}])
    _login(client)
    html = client.get("/portfolio/table").get_data(as_text=True)
    assert 'id="download-xlsx"' in html
    assert "Descargar xlsx" in html


def test_portfolio_loads_the_xlsx_library(client, monkeypatch):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio",
                        lambda: [{"Firmante": "X", "Importe": 100, "Origen": "DHF"}])
    _login(client)
    html = client.get("/portfolio/table").get_data(as_text=True)
    assert "xlsx.full.min.js" in html


def _audit(caplog):
    return [json.loads(r.getMessage()) for r in caplog.records if r.name == "cartera"]


def test_audit_logs_user_route_and_status(client, caplog):
    _login(client)
    with caplog.at_level(logging.INFO, logger="cartera"):
        client.get("/")
    entry = _audit(caplog)[-1]
    assert entry["usuario"] == "Tester"
    assert entry["ruta"] == "/"
    assert entry["estado"] == 200
    assert isinstance(entry["ms"], int)


def test_audit_logs_what_the_portfolio_returned(client, monkeypatch, caplog):
    import routes.portfolio as rp
    monkeypatch.setattr(rp, "build_portfolio", lambda: [
        {"Firmante": "A", "Importe": 1, "Origen": "DHF"},
        {"Firmante": "B", "Importe": 2, "Origen": "BOLSA"},
        {"Firmante": "C", "Importe": 3, "Origen": "BOLSA"},
    ])
    _login(client)
    with caplog.at_level(logging.INFO, logger="cartera"):
        client.get("/portfolio/table")
    entry = _audit(caplog)[-1]
    assert entry["cheques"] == 3
    assert entry["origenes"] == {"DHF": 1, "BOLSA": 2}


def test_audit_logs_requests_without_session(client, caplog):
    with caplog.at_level(logging.INFO, logger="cartera"):
        client.get("/portfolio/table")
    entry = _audit(caplog)[-1]
    assert entry["usuario"] == "sin sesion"
    assert entry["estado"] == 302


def test_audit_skips_static_files(client, caplog):
    with caplog.at_level(logging.INFO, logger="cartera"):
        client.get("/static/js/portfolio.js")
    assert _audit(caplog) == []


def test_audit_logs_the_accounting_tables(client, monkeypatch, caplog):
    import routes.accounting_entry as ra
    monkeypatch.setattr(ra, "build_env_entries", lambda env: {
        "deposits": [{"FECH": "01/01/2026"}], "sales": [], "collections": [],
        "purchases": [], "tax_documents": [], "payments": [], "pending": [], "rejected": [],
    })
    _login(client)
    with caplog.at_level(logging.INFO, logger="cartera"):
        client.get("/accounting/dhf")
    entry = _audit(caplog)[-1]
    assert entry["entorno"] == "DHF"
    assert entry["asientos"]["Depósitos"] == 1


@pytest.fixture
def log_dir(tmp_path):
    from core.audit import logger, setup_file_logging
    handler = setup_file_logging(str(tmp_path))
    yield tmp_path
    if handler:
        logger.removeHandler(handler)


def test_audit_writes_a_file_when_there_is_a_log_dir(client, log_dir):
    _login(client)
    client.get("/")
    archivos = list(log_dir.glob("cartera-*.log"))
    assert len(archivos) == 1
    entry = json.loads(archivos[0].read_text(encoding="utf-8").strip().split(" ", 2)[2])
    assert entry["usuario"] == "Tester" and entry["ruta"] == "/"


def test_audit_appends_one_line_per_request(client, log_dir):
    _login(client)
    client.get("/")
    client.get("/")
    archivo = next(iter(log_dir.glob("cartera-*.log")))
    assert len(archivo.read_text(encoding="utf-8").strip().splitlines()) == 2


def test_audit_file_name_is_monthly():
    from datetime import date
    from core.audit import MonthlyFileHandler
    handler = MonthlyFileHandler("/data")
    assert handler.path(date(2026, 10, 30)).endswith("cartera-2026-10.log")


def test_audit_without_log_dir_does_not_add_a_handler():
    from core.audit import logger, setup_file_logging
    antes = len(logger.handlers)
    assert setup_file_logging("") is None
    assert len(logger.handlers) == antes
