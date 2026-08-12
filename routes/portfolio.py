from flask import Blueprint, session, redirect, url_for, render_template
from modules.portfolio.service import build_portfolio
from presentation import format_dates, format_cuits, format_states
from domain.date_table import next_business_day

bp = Blueprint("portfolio", __name__)

def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))

@bp.route("/portfolio/table")
def portfolio_table():
    guard = _require_login()
    if guard:
        return guard
    rows = build_portfolio()
    rows = format_dates(rows)
    rows = format_cuits(rows)
    rows = format_states(rows)
    nbd = next_business_day()
    return render_template("portfolio.html", rows=rows,
                           next_business_day=nbd.isoformat() if nbd else "")