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

def put_company_name(rows):
    result = []
    for row in rows:
        origin = row.get("Origen")
        row["Empresa"] = "CRM-" + origin
        result.append(row)
    return result

RATE_COLUMNS = ("Dias", "Tasa de Interes", "Comision")


def _has_rate_data(row):
    if any(row.get(col) is None for col in RATE_COLUMNS):
        return False
    return float(row.get("Dias")) != 0


def put_interest_real_rate(rows):
    result = []
    for row in rows:
        if not _has_rate_data(row):
            row["Tasa"] = None
            result.append(row)
            continue
        days = float(row.get("Dias"))
        raw_interest_rate = float(row.get("Tasa de Interes"))
        raw_commission_rate = float(row.get("Comision"))

        real_comission_rate = raw_commission_rate - 1.2 if raw_commission_rate > 1.2 else raw_commission_rate

        real_interest_rate = raw_interest_rate + real_comission_rate / days * 365
        row["Tasa"] = real_interest_rate
        result.append(row)
    return result 