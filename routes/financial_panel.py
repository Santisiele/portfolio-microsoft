from flask import Blueprint, session, redirect, url_for, render_template

from modules.financial_panel.service import build_financial_panel
from presentation import format_ars

bp = Blueprint("panel", __name__)


def _require_login():
    return None if session.get("user") else redirect(url_for("auth.login"))


def _cards(metric, label):
    return [
        {"title": label + " Confinance", "value": format_ars(metric["confinance"])},
        {"title": label + " total", "value": format_ars(metric["total"])},
        {"title": label + " DHF", "value": format_ars(metric["dhf"])},
    ]


def _balance_cards(balances):
    return [{"title": "Saldo " + balance["name"], "value": format_ars(balance["amount"])}
            for balance in balances]


def _balance_total_card(balances):
    amounts = [balance["amount"] for balance in balances if balance["amount"] is not None]
    return [{"title": "Saldo total", "value": format_ars(sum(amounts) if amounts else None)}]


@bp.route("/panel")
def index():
    guard = _require_login()
    if guard:
        return guard
    panel = build_financial_panel()
    groups = [
        _cards(panel["guaranteed"], "Cheques garantizados"),
        _cards(panel["checking_account"], "Cuenta corriente"),
    ]
    if panel["balances"]:
        groups.append(_balance_cards(panel["balances"]))
        groups.append(_balance_total_card(panel["balances"]))
    return render_template("financial_panel.html", groups=groups)
