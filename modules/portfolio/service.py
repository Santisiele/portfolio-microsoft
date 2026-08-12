import pandas as pd

from config import STOCK_MARKET_SHEET_URL
from sources.base import Source, load_module
from sources.tds import read_tds
from sources.gsheet import read_public_sheet

from queries.portfolio import PORTFOLIO
from domain.portfolio_transform import put_acreditation_date, eliminate_duplicate_checks

PORTFOLIO_STEPS = [put_acreditation_date, eliminate_duplicate_checks]

COLUMN_MAP = {
    "FIRMANTE":      "Firmante",
    "CUIT Librador": "Cuit Librador",
    "Fecha Acr.":    "Fecha Acr.",
    "Importe":       "Importe",
    "Cliente":       "Cliente",
    "Estado":        "Estado",
    "Fecha Cpra.":   "Fecha Compra",
}

DATE_FIELDS = ("Fecha Acr.", "Fecha Compra")


def _to_date(value):
    if value is None or value == "" or (isinstance(value, float) and pd.isna(value)):
        return None
    ts = pd.to_datetime(value, dayfirst=True, errors="coerce")
    return None if pd.isna(ts) else ts.date()


def normalize_stock_market(rows):
    result = []
    for row in rows:
        new = {canonical: row.get(sheet_col) for sheet_col, canonical in COLUMN_MAP.items()}
        new["Origen"] = row.get("Origen")
        for field in DATE_FIELDS:
            new[field] = _to_date(new[field])
        result.append(new)
    return result


STOCK_MARKET_STEPS = [normalize_stock_market]

PORTFOLIO_SOURCES = [
    Source("DHF",        lambda: read_tds("DHF", PORTFOLIO),        steps=PORTFOLIO_STEPS),
    Source("CONFINANCE", lambda: read_tds("CONFINANCE", PORTFOLIO), steps=PORTFOLIO_STEPS),
    Source("BOLSA",      lambda: read_public_sheet(STOCK_MARKET_SHEET_URL), steps=STOCK_MARKET_STEPS),
]


def build_portfolio():
    return load_module(PORTFOLIO_SOURCES)