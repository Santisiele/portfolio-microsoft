from flask import Blueprint, session, redirect, url_for, render_template

from modules.accounting_entry.service import build_env_entries
from presentation import format_dates, format_amounts

bp = Blueprint("accounting", __name__)


def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


def _render(env, title):
    data = build_env_entries(env)
    tables = [
        {"title": "Depósitos", "rows": data["deposits"]},
        {"title": "Ventas", "rows": data["sales"]},
        {"title": "Cobranzas", "rows": data["collections"]},
        {"title": "Compras", "rows": data["purchases"]},
        {"title": "Documentos fiscales", "rows": data["tax_documents"]},
        {"title": "Pagos", "rows": data["payments"]},
        {"title": "Pendientes", "rows": data["pending"]},
        {"title": "Rechazados", "rows": data["rejected"]},
    ]
    for t in tables:
        t["rows"] = format_dates(t["rows"], columns=["FECH"])
        t["rows"] = format_amounts(t["rows"], columns=["DEBE", "HABER"])
    return render_template("accounting.html", title=title, tables=tables)


@bp.route("/accounting/dhf")
def dhf():
    guard = _require_login()
    if guard:
        return guard
    return _render("DHF", "Asientos — DHF")


@bp.route("/accounting/confinance")
def confinance():
    guard = _require_login()
    if guard:
        return guard
    return _render("CONFINANCE", "Asientos — CONFINANCE")