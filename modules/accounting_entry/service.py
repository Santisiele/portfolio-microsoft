from sources.tds import read_tds

from queries.accounting_entry import DEPOSITS
from domain.accounting import build_deposit_entries


def build_deposit_entries_table():
    rows = read_tds("CONFINANCE", DEPOSITS)
    return build_deposit_entries(rows)