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