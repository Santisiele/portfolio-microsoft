from config import STOCK_MARKET_SHEET_URL
from sources.base import Source, load_module
from sources.tds import read_tds
from sources.gsheet import read_public_sheet

from queries.portfolio import PORTFOLIO
from domain.portfolio_transform import put_acreditation_date, eliminate_duplicate_checks

PORTFOLIO_STEPS = [put_acreditation_date, eliminate_duplicate_checks]


def _stock_market_rules(rows):
    return rows


PORTFOLIO_SOURCES = [
    Source("DHF",        lambda: read_tds("DHF", PORTFOLIO),               steps=PORTFOLIO_STEPS),
    Source("CONFINANCE", lambda: read_tds("CONFINANCE", PORTFOLIO),        steps=PORTFOLIO_STEPS),
    Source("STOCK",      lambda: read_public_sheet(STOCK_MARKET_SHEET_URL), steps=[_stock_market_rules]),
]


def build_portfolio():
    return load_module(PORTFOLIO_SOURCES)