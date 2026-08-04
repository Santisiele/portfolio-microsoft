import time
import struct
from core.auth import get_access_token
import pyodbc
from config import ENVIRONMENTS, scope_for, server_for, database_for

SQL_COPT_SS_ACCESS_TOKEN = 1256
RETRIES = 3
WAIT = 1.5


def _token_struct(url: str):
    token = get_access_token(scope_for(url))
    if not token:
        raise RuntimeError(f"No valid session for {url}. Go back to LogIn.")
    tb = token.encode("utf-16-le")
    return struct.pack(f"<I{len(tb)}s", len(tb), tb)


def _connect(url: str):
    import pyodbc
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server_for(url)},1433;"
        f"DATABASE={database_for(url)};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    conn = pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: _token_struct(url)}, timeout=30)
    conn.timeout = 60
    return conn


def dataverse_sql(query: str, env: str, params=None) -> list[dict]:
    if env not in ENVIRONMENTS:
        raise ValueError(f"Unknown enviroment'{env}'. Available: {list(ENVIRONMENTS)}")
    url = ENVIRONMENTS[env]
    last = None
    for _ in range(RETRIES):
        conn = None
        try:
            conn = _connect(url)
            cur = conn.cursor()
            cur.execute(query, params or [])
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, fila)) for fila in cur.fetchall()]
        except pyodbc.Error as e:
            ultimo = e
            if e.args and e.args[0] in ("08S01", "08001", "HYT00"):
                time.sleep(RETRIES)
                continue
            raise
        finally:
            if conn is not None:
                try: conn.close()
                except Exception: pass
    raise RuntimeError(f"{env} TDS dropped the connection after {RETRIES} retries. Last error: {last}")


def dataverse_sql_all(query: str, params=None, origin_column: str = "Origen") -> list[dict]:
    rows = []
    for env in ENVIRONMENTS:
        for row in dataverse_sql(query, env, params):
            row[origin_column] = env
            rows.append(row)
    return rows