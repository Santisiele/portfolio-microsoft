from datetime import date
from domain.date_table import build_calendar, calculate_acreditation_from_payment

def put_acreditation_date(rows, today=None):
    today = today or date.today()
    calendar = build_calendar()
    result = []
    for row in rows:
        payment_date = row.get("Fecha Pago")
        if payment_date is None:
            continue
        acr = calculate_acreditation_from_payment(payment_date, calendar=calendar)
        if acr <= today:
            continue
        row["Fecha Acr."] = acr
        result.append(row)
    return result


def eliminate_duplicate_checks(rows):
    result = []
    for row in rows:
        destination_acount = row.get("Cuenta Destino")
        origin = row.get("Origen")
        state = row.get("Estado")

        if (origin == "DHF" or origin == "CONFINANCE") and (destination_acount == "5006" or destination_acount == "5011") and (state == "Vendido"):
            continue

        result.append(row)
    return result