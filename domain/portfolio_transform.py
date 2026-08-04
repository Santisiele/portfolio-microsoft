from datetime import date
from domain.date_table import build_calendar, calculate_acreditation_from_payment


def enrich_portfolio(rows, today=None):
    today = today or date.today()
    calendar = build_calendar()
    result = []
    for row in rows:
        fecha = row.get("Fecha Pago")
        if fecha is None:
            row["Fecha Acr."] = None
            result.append(row)
            continue

        acr = calculate_acreditation_from_payment(fecha, calendar=calendar)
        if acr <= today:
            continue

        row["Fecha Acr."] = acr
        result.append(row)
    return result