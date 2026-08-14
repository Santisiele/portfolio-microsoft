from sources.tds import read_tds

from queries.accounting_entry import DEPOSITS, SALES
from domain.accounting import build_deposit_entries, build_sales_entries


def build_deposit_entries_table(env):
    return build_deposit_entries(read_tds(env, DEPOSITS))


def build_sales_entries_table(env):
    return build_sales_entries(read_tds(env, SALES))


def build_env_entries(env):
    return {
        "deposits": build_deposit_entries_table(env),
        "sales": build_sales_entries_table(env),
    }