import pytest


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