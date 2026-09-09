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
    assert "Saldo Confinance" in html
    assert "$878.315.440,61" in html
    assert "Saldo total" in html
    assert "$1.423.876.533,61" in html
