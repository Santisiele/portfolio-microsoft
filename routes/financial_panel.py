from flask import Blueprint, session, redirect, url_for, render_template

from modules.financial_panel.service import build_financial_panel
from presentation import format_ars

bp = Blueprint("panel", __name__)


def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


def _cards(metric):
    return [
        {"title": "Confinance", "value": format_ars(metric["confinance"])},
        {"title": "Total", "value": format_ars(metric["total"])},
        {"title": "DHF", "value": format_ars(metric["dhf"])},
    ]


def _balance_cards(balances):
    return [{"title": balance["name"], "value": format_ars(balance["amount"])}
            for balance in balances]


def _balance_total_card(balances):
    amounts = [balance["amount"] for balance in balances if balance["amount"] is not None]
    return {"title": "Total", "value": format_ars(sum(amounts) if amounts else None)}


@bp.route("/panel")
def index():
    guard = _require_login()
    if guard:
        return guard
    panel = build_financial_panel()
    groups = []
    if panel["balances"]:
        groups.append({"id": "saldos", "title": "Saldos de cuentas",
                       "cards": _balance_cards(panel["balances"]),
                       "total": _balance_total_card(panel["balances"])})
    groups.append({"id": "garantizados", "title": "Cheques garantizados",
                   "cards": _cards(panel["guaranteed"])})
    groups.append({"id": "cuenta-corriente", "title": "Cuenta corriente",
                   "cards": _cards(panel["checking_account"])})
    return render_template("financial_panel.html", groups=groups)
