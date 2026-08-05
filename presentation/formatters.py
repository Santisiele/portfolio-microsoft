from datetime import date, datetime
from decimal import Decimal

DATE_COLUMNS = ["Fecha Compra", "Fecha Pago", "Fecha Acr."]
AMOUNT_COLUMNS = ["Importe"]
CUIT_COLUMNS = ["Cuit Librador"]


def format_dates(rows, columns=DATE_COLUMNS):
    for row in rows:
        for col in columns:
            value = row.get(col)
            if isinstance(value, (date, datetime)):
                row[col] = value.strftime("%d/%m/%Y")
    return rows


def format_amounts(rows, columns=AMOUNT_COLUMNS):
    for row in rows:
        for col in columns:
            value = row.get(col)
            if isinstance(value, (int, float, Decimal)):
                row[col] = f"{float(value):,.2f}"
    return rows


def format_cuits(rows, columns=CUIT_COLUMNS):
    for row in rows:
        for col in columns:
            value = row.get(col)
            if value is None:
                continue
            if isinstance(value, (int, float, Decimal)):
                digits = str(int(value))
            else:
                digits = "".join(ch for ch in str(value) if ch.isdigit())
            if len(digits) == 11:
                row[col] = f"{digits[:2]}-{digits[2:10]}-{digits[10:]}"
    return rows