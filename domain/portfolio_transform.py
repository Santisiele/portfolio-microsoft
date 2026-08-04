from domain.date_table import build_calendar, calculate_acreditation_from_payment

def enrich_portfolio(rows):
    calendar = build_calendar()
    for row in rows:
        fecha = row.get("fecha_pago")
        if fecha is None:
            row["Fecha Acr."] = None
            continue
        row["Fecha Acr."] = calculate_acreditation_from_payment(fecha, calendar=calendar)
    return rows