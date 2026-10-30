from flask import Blueprint, session, redirect, url_for, render_template, request

from modules.portfolio_historic.service import (
    build_historic_page, build_historic_totals, default_range, SOURCES, PAGE_SIZE,
)
from queries.portfolio_historic import STATES
from modules.portfolio_historic.bolsa import BOLSA_STATES
from presentation import format_dates, format_cuits, format_states, format_percentages, format_ars
from core import record

bp = Blueprint("historic", __name__)

DATE_COLUMNS = ["Fecha Compra", "Fecha Pago", "Fecha Acr."]


def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


def _filters():
    desde, hasta = default_range()
    return {
        "desde": request.args.get("desde") or desde,
        "hasta": request.args.get("hasta") or hasta,
        "cliente": request.args.get("cliente", ""),
        "firmante": request.args.get("firmante", ""),
        "cuit": request.args.get("cuit", ""),
        "estados": request.args.getlist("estado"),
    }


def _sources(elegido):
    return (elegido,) if elegido in SOURCES else SOURCES


@bp.route("/cartera-historica")
def index():
    guard = _require_login()
    if guard:
        return guard
    filters = _filters()
    fuente = request.args.get("fuente", "")
    sources = _sources(fuente)
    page = max(request.args.get("pagina", type=int) or 1, 1)

    rows = build_historic_page(filters, page=page, sources=sources)
    totals = build_historic_totals(filters, sources=sources)
    record(cheques=totals["cantidad"], pagina=page, fuentes=list(sources))

    rows = format_dates(rows, columns=DATE_COLUMNS)
    rows = format_cuits(rows)
    rows = format_states(rows)
    rows = format_percentages(rows)
    for row in rows:
        row["Importe"] = format_ars(row.get("Importe"))

    paginas = max(-(-totals["cantidad"] // PAGE_SIZE), 1)
    return render_template("portfolio_historic.html", rows=rows, filters=filters,
                           fuente=fuente, fuentes=SOURCES, estados=STATES + BOLSA_STATES,
                           page=page, paginas=paginas, totals=totals,
                           total_ars=format_ars(totals["total"]))
