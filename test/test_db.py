import pyodbc
import core.db as db


def test_consolidates_both_environments_with_origin(monkeypatch):
    monkeypatch.setattr(db, "dataverse_sql",
                        lambda query, env, params=None: [{"id": env.lower(), "amount": 100}])

    rows = db.dataverse_sql_all("SELECT id, amount FROM x")

    assert len(rows) == 2
    assert {r["Origen"] for r in rows} == {"DHF", "CONFINANCE"}


def test_retries_on_08S01(monkeypatch):
    monkeypatch.setattr(db, "WAIT", 0)
    calls = {"n": 0}

    class Cursor:
        description = [("x",)]

        def execute(self, q, p):
            pass

        def fetchall(self):
            return [(1,)]

    class Conn:
        timeout = 0

        def cursor(self):
            return Cursor()

        def close(self):
            pass

    def fake_connect(url):
        calls["n"] += 1
        if calls["n"] == 1:
            raise pyodbc.Error("08S01", "Communication link failure")
        return Conn()

    monkeypatch.setattr(db, "_connect", fake_connect)

    rows = db.dataverse_sql("SELECT x FROM y", "DHF")

    assert rows == [{"x": 1}]
    assert calls["n"] == 2