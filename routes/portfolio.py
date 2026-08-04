from flask import Blueprint, session, redirect, url_for, jsonify, render_template

from core import dataverse_sql_all
from queries.portfolio import PORTFOLIO
from domain.portfolio_transform import enrich_portfolio
from presentation import format_dates

bp = Blueprint("portfolio", __name__)

def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


@bp.route("/portfolio")
def portfolio_json():
    guard = _require_login()
    if guard:
        return guard
    rows = dataverse_sql_all(PORTFOLIO)
    rows = format_dates(rows)  
    return jsonify({"count": len(rows), "data": rows})


@bp.route("/portfolio/table")
def portfolio_table():
    guard = _require_login()
    if guard:
        return guard
    rows = dataverse_sql_all(PORTFOLIO)
    rows = enrich_portfolio(rows)
    rows = format_dates(rows)  
    return render_template("portfolio.html", rows=rows)