import pandas as pd

from config import STOCK_MARKET_SHEET_URL
from sources.base import Source, load_module
from sources.tds import read_tds
from sources.gsheet import read_public_sheet

from queries.portfolio import PORTFOLIO
from domain.portfolio_transform import put_acreditation_date, change_sold_to_us_checks_from_crm, put_company_name, put_interest_real_rate

PORTFOLIO_STEPS = [put_company_name, put_acreditation_date, change_sold_to_us_checks_from_crm, put_interest_real_rate]

COLUMN_MAP = {
    "Empresa":       "Empresa",
    "FIRMANTE":      "Firmante",
    "CUIT Librador": "Cuit Librador",
    "Fecha Acr.":    "Fecha Acr.",
    "Importe":       "Importe",
    "Cliente":       "Cliente",
    "Estado":        "Estado",
    "Fecha Cpra.":   "Fecha Compra",
    "TASA MERCADO":  "Tasa",
    "Endosante mercado": "Endoso cheque mercado"
}

DATE_FIELDS = ("Fecha Acr.", "Fecha Compra")
SOLD_TO_US_CLIENTS = ("DHF", "CONFINANCE")
RATE_FIELD = "Tasa"


def _to_date(value):
    if value is None or value == "" or (isinstance(value, float) and pd.isna(value)):
        return None
    ts = pd.to_datetime(value, dayfirst=True, errors="coerce")
    return None if pd.isna(ts) else ts.date()


def _to_rate(value):
    rate = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(rate) else float(rate) * 100


def _to_cell(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return value

def eliminate_sold_to_us_checks(rows):
    result = []
    for row in rows:
        client = str(_to_cell(row.get("Cliente")))
        if client.startswith(SOLD_TO_US_CLIENTS):
            continue
        result.append(row)
    return result

def normalize_stock_market(rows):
    result = []
    for row in rows:
        new = {canonical: _to_cell(row.get(sheet_col)) for sheet_col, canonical in COLUMN_MAP.items()}
        new["Origen"] = row.get("Origen")
        if row.get("Estado") == "VENDIDO":
            continue
        for field in DATE_FIELDS:
            new[field] = _to_date(new[field])
        new[RATE_FIELD] = _to_rate(new[RATE_FIELD])
        result.append(new)
    return result


STOCK_MARKET_STEPS = [eliminate_sold_to_us_checks, normalize_stock_market]

PORTFOLIO_SOURCES = [
    Source("DHF",        lambda: read_tds("DHF", PORTFOLIO),        steps=PORTFOLIO_STEPS),
    Source("CONFINANCE", lambda: read_tds("CONFINANCE", PORTFOLIO), steps=PORTFOLIO_STEPS),
    Source("BOLSA",      lambda: read_public_sheet(STOCK_MARKET_SHEET_URL), steps=STOCK_MARKET_STEPS),
]


def build_portfolio():
    return load_module(PORTFOLIO_SOURCES)