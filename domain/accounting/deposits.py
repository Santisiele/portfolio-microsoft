SUBCUENTA = {
    "017": 1120001,
    "322": 1120002,
    "338": 1120003,
    "5001": 1120005,
    "5004": 1120006,
    "5005": 1120006,
    "5006": 1120006,
    "5011": 1120006,
    "5007": 1120010,
    "072": 1120014,
}
SUBCUENTA_DEFAULT = 1120006
CONTRA_SUBCUENTA = 1300001

def _subcuenta(account):
    return SUBCUENTA.get(account, SUBCUENTA_DEFAULT)


def _concepto(transaction):
    return "depo del dia rechazo" if "rechazo" in (transaction or "").lower() else "depo del dia"


def build_deposit_entries(rows):
    debit = []
    totals_by_date = {}
    for row in rows:
        date = row["gval_fechaconfirmacion"]
        amount = row["gval_importetotalcheques"] or 0
        debit.append({
            "FECH": date,
            "SUBCTA": _subcuenta(row["gval_cuentapropiadestinoname"]),
            "CONTRA": "",
            "DEBE": amount,
            "CONCEPTO": _concepto(row["gval_numtransaccionboletarealdedeposito"]),
            "HABER": 0,
        })
        totals_by_date[date] = (totals_by_date.get(date, 0) or 0) + amount

    credit = [{
        "FECH": date,
        "SUBCTA": CONTRA_SUBCUENTA,
        "CONTRA": "",
        "DEBE": 0,
        "CONCEPTO": "depo del dia",
        "HABER": total,
    } for date, total in totals_by_date.items()]

    return debit + credit