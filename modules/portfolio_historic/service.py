from datetime import date

from sources.tds import read_tds
from queries.portfolio_historic import page_query, totals_query
from domain.portfolio_transform import (
    put_company_name,
    change_sold_to_us_checks_from_crm,
    put_interest_real_rate,
)
from modules.portfolio_historic import bolsa

ENVIRONMENTS = ("DHF", "CONFINANCE")
BOLSA = "BOLSA"
SOURCES = ENVIRONMENTS + (BOLSA,)
PAGE_SIZE = 100
HISTORIC_STEPS = [put_company_name, change_sold_to_us_checks_from_crm, put_interest_real_rate]


def _tag(rows, origin):
    for row in rows:
        row["Origen"] = origin
    for step in HISTORIC_STEPS:
        rows = step(rows)
    return rows


def _sort_key(row):
    fecha = row.get("Fecha Compra")
    clave = fecha.isoformat() if hasattr(fecha, "isoformat") else str(fecha or "")
    return (clave, float(row.get("Importe") or 0))


def default_range(today=None):
    today = today or date.today()
    try:
        desde = today.replace(year=today.year - 1)
    except ValueError:
        desde = today.replace(year=today.year - 1, day=28)
    return desde.isoformat(), today.isoformat()


def _crm_environments(sources):
    return [source for source in sources if source in ENVIRONMENTS]


def build_historic_page(filters, page=1, size=PAGE_SIZE, sources=SOURCES):
    offset = max(page - 1, 0) * size
    rows = []

    for env in _crm_environments(sources):
        query, params = page_query(filters, 0, offset + size)
        rows += _tag(read_tds(env, query, params), env)

    if BOLSA in sources:
        de_bolsa = bolsa.filtered(filters)
        de_bolsa.sort(key=_sort_key, reverse=True)
        rows += de_bolsa[:offset + size]

    rows.sort(key=_sort_key, reverse=True)
    return rows[offset:offset + size]


def build_historic_totals(filters, sources=SOURCES):
    cantidad = 0
    total = 0.0

    for env in _crm_environments(sources):
        query, params = totals_query(filters)
        filas = read_tds(env, query, params)
        if filas:
            cantidad += filas[0].get("Cantidad") or 0
            total += float(filas[0].get("Total") or 0)

    if BOLSA in sources:
        propios = bolsa.totals(filters)
        cantidad += propios["cantidad"]
        total += propios["total"]

    return {"cantidad": cantidad, "total": total}
