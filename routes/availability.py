from flask import Blueprint, session, redirect, url_for, render_template

from modules.availability.service import build_availability
from presentation import format_sheet_values, format_ars

bp = Blueprint("availability", __name__)

TEXT_COLUMNS = ("Empresa",)


def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


@bp.route("/disponibilidades")
def index():
    guard = _require_login()
    if guard:
        return guard
    data = build_availability()
    if data:
        format_sheet_values(data["rows"], data["columns"])
        data["cheques"] = format_ars(data["cheques"])
    return render_template("availability.html", data=data, text_columns=TEXT_COLUMNS)
