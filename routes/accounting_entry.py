from flask import Blueprint, session, redirect, url_for, render_template

from modules.accounting_entry.service import build_all_tables
from presentation import format_dates, format_amounts

bp = Blueprint("accounting", __name__)


def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


@bp.route("/accounting")
def accounting():
    guard = _require_login()
    if guard:
        return guard
    tables = build_all_tables()
    for t in tables:
        t["rows"] = format_dates(t["rows"], columns=["FECH"])
        t["rows"] = format_amounts(t["rows"], columns=["DEBE", "HABER"])
    return render_template("accounting.html", tables=tables)