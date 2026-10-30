from flask import Blueprint, session, redirect, url_for, render_template

from modules.rates.service import build_rate_tables
from presentation import format_sheet_values
from core import record

bp = Blueprint("rates", __name__)

TEXT_COLUMNS = ("Mes", "Hoja")


def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


@bp.route("/tasas")
def index():
    guard = _require_login()
    if guard:
        return guard
    tables = build_rate_tables()
    for table in tables:
        format_sheet_values(table["rows"], table["columns"])
    record(tasas={t["title"]: len(t["rows"]) for t in tables})
    return render_template("rates.html", tables=tables, text_columns=TEXT_COLUMNS)
