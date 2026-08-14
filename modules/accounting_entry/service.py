from sources.tds import read_tds
from sources.gsheet import read_public_sheet

from config import COMPANY_SUBACCOUNT_SHEET
from queries.accounting_entry import DEPOSITS, SALES, COLLECTIONS
from domain.accounting import build_deposit_entries, build_sales_entries, build_collection_entries
from domain.accounting.common import build_company_subaccount_map


def load_company_subaccounts(env):
    url = COMPANY_SUBACCOUNT_SHEET.get(env, "")
    if not url:
        return {}
    return build_company_subaccount_map(read_public_sheet(url))


def build_deposit_entries_table(env):
    return build_deposit_entries(read_tds(env, DEPOSITS))


def build_sales_entries_table(env):
    return build_sales_entries(read_tds(env, SALES))


def build_collection_entries_table(env):
    company_map = load_company_subaccounts(env)
    return build_collection_entries(read_tds(env, COLLECTIONS), company_map)


def build_env_entries(env):
    return {
        "deposits": build_deposit_entries_table(env),
        "sales": build_sales_entries_table(env),
        "collections": build_collection_entries_table(env),
    }