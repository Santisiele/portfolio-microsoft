from sources.tds import read_tds

from queries.accounting_entry import DEPOSITS, SALES
from domain.accounting import build_deposit_entries, build_sales_entries

ENVIRONMENTS_USED = ["DHF", "CONFINANCE"]


def build_deposit_entries_table(env):
    return build_deposit_entries(read_tds(env, DEPOSITS))


def build_sales_entries_table(env):
    return build_sales_entries(read_tds(env, SALES))


def build_all_tables():
    tables = []
    for env in ENVIRONMENTS_USED:
        tables.append({"title": "Depósitos " + env, "rows": build_deposit_entries_table(env)})
    for env in ENVIRONMENTS_USED:
        tables.append({"title": "Ventas " + env, "rows": build_sales_entries_table(env)})
    return tables