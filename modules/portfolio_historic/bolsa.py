import time

import pandas as pd

from config import HISTORIC_BOLSA_SHEET_ID
from sources.gsheet import read_tab_records
from modules.portfolio.service import SOLD_TO_US_CLIENTS
from presentation import STATE_LABELS

BOLSA_GID = "112696699"
CACHE_SECONDS = 300
BOLSA_ORIGIN = "BOLSA"
BOLSA_STATES = ("ACREDITADO", "Rescatado", "RECHAZADO")
COLUMN_MAP = {
    "Empresa": "Empresa",
    "FIRMANTE": "Firmante",
    "CUIT Librador": "Cuit Librador",
    "Fecha Acr.": "Fecha Acr.",
    "Fecha Cpra.": "Fecha Compra",
    "Importe": "Importe",
    "Cliente": "Cliente",
    "Estado": "Estado",
    "TASA MERCADO": "Tasa",
}
DATE_FIELDS = ("Fecha Acr.", "Fecha Compra")
_cache = {}


def _to_date(value):
    stamp = pd.to_datetime(value, dayfirst=True, errors="coerce")
    return None if pd.isna(stamp) else stamp.date()


def _to_number(value):
    number = pd.to_numeric(str(value).replace(",", ""), errors="coerce")
    return None if pd.isna(number) else float(number)


def _digits(value):
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def normalize(records):
    return normalize_frame(pd.DataFrame(records, dtype=str))


def normalize_frame(frame):
    if frame.empty:
        return []

    frame = frame.fillna("")
    for columna in COLUMN_MAP:
        if columna not in frame.columns:
            frame[columna] = ""

    datos = frame[list(COLUMN_MAP)].rename(columns=COLUMN_MAP).astype(str)
    datos = datos[~datos["Cliente"].str.upper().str.startswith(SOLD_TO_US_CLIENTS)]
    datos = datos[~datos.apply(lambda columna: columna.str.strip()).eq("").all(axis=1)]
    if datos.empty:
        return []

    for field in DATE_FIELDS:
        datos[field] = pd.to_datetime(datos[field], dayfirst=True, errors="coerce").dt.date
    datos["Importe"] = pd.to_numeric(datos["Importe"].str.replace(",", "", regex=False), errors="coerce")
    datos["Tasa"] = pd.to_numeric(datos["Tasa"].str.replace(",", "", regex=False), errors="coerce") * 100
    datos["Estado"] = datos["Estado"].replace(STATE_LABELS)
    datos["Origen"] = BOLSA_ORIGIN

    rows = datos.to_dict(orient="records")
    for row in rows:
        for clave, valor in row.items():
            if valor is not None and not isinstance(valor, str) and pd.isna(valor):
                row[clave] = None
    return rows


def load(now=None):
    if not HISTORIC_BOLSA_SHEET_ID:
        return []
    now = now or time.time()
    if _cache.get("rows") is not None and now - _cache.get("at", 0) < CACHE_SECONDS:
        return _cache["rows"]
    rows = normalize(read_tab_records(HISTORIC_BOLSA_SHEET_ID, BOLSA_GID))
    _cache.update(rows=rows, at=now)
    return rows


def matches(row, filters):
    compra = row.get("Fecha Compra")
    if compra is None:
        return False
    if filters.get("desde") and compra.isoformat() < filters["desde"]:
        return False
    if filters.get("hasta") and compra.isoformat() > filters["hasta"]:
        return False

    estados = filters.get("estados")
    if estados and row.get("Estado") not in estados:
        return False

    for campo, columna in (("cliente", "Cliente"), ("firmante", "Firmante")):
        valor = (filters.get(campo) or "").strip().upper()
        if valor and valor not in str(row.get(columna) or "").upper():
            return False

    cuit = _digits(filters.get("cuit"))
    if cuit and cuit not in _digits(row.get("Cuit Librador")):
        return False

    return True


def filtered(filters):
    return [dict(row) for row in load() if matches(row, filters)]


def totals(filters):
    rows = filtered(filters)
    return {"cantidad": len(rows), "total": sum(row.get("Importe") or 0 for row in rows)}
