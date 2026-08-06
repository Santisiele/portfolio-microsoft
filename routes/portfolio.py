from flask import Blueprint, session, redirect, url_for, render_template
from modules.portfolio.service import build_portfolio
from presentation import format_dates, format_cuits

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
    return render_template("portfolio.html", rows=rows)