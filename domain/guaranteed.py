from datetime import date

from domain.date_table import build_calendar, calculate_acreditation_from_payment


def guaranteed_total(rows, today=None, calendar=None):
    today = today or date.today()
    calendar = calendar if calendar is not None else build_calendar()
    total = None
    for row in rows:
        fecha = row.get("Fecha")
        amount = row.get("Garantizado")
        if fecha is None or amount is None:
            continue
        acr = calculate_acreditation_from_payment(fecha, calendar=calendar)
        if acr <= today:
            continue
        total = (total or 0) + amount
    return total