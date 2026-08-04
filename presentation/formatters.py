from datetime import date, datetime

DATE_COLUMNS = ["fecha_compra", "fecha_pago", "Fecha Acr."]

def format_dates(rows, columns=DATE_COLUMNS):
    for row in rows:
        for col in columns:
            value = row.get(col)
            if isinstance(value, (date, datetime)):
                row[col] = value.strftime("%d/%m/%Y")
    return rows