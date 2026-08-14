from flask import Blueprint, session, redirect, url_for, render_template

from modules.accounting_entry.service import build_deposit_entries_table
from presentation import format_dates, format_amounts

bp = Blueprint("accounting", __name__)


def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


@bp.route("/accounting/deposits")
def deposits():
    guard = _require_login()
    if guard:
        return guard
    rows = build_deposit_entries_table()
    rows = format_dates(rows, columns=["FECH"])
    rows = format_amounts(rows, columns=["DEBE", "HABER"])
    return render_template("accounting_deposits.html", rows=rows)