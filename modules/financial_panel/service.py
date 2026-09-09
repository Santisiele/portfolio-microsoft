from sources.tds import read_tds

from queries.financial_panel import GUARANTEED_AMOUNT, CHECKING_ACCOUNT
from domain.guaranteed import guaranteed_total


def guaranteed_amount(env):
    return guaranteed_total(read_tds(env, GUARANTEED_AMOUNT))


def checking_account_amount(env):
    rows = read_tds(env, CHECKING_ACCOUNT)
    return rows[0]["Cuenta corriente"] if rows else None


def _per_env(fn):
    dhf = fn("DHF")
    confinance = fn("CONFINANCE")
    return {"dhf": dhf, "confinance": confinance, "total": (dhf or 0) + (confinance or 0)}


def build_financial_panel():
    return {
        "guaranteed": _per_env(guaranteed_amount),
        "checking_account": _per_env(checking_account_amount),
    }