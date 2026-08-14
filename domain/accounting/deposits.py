from .common import CONTRA_SUBCUENTA, subcuenta, line


def _concepto(transaction):
    return "depo del dia rechazo" if "rechazo" in (transaction or "").lower() else "depo del dia"


def build_deposit_entries(rows, mapping=None):
    debit = []
    totals_by_date = {}
    for row in rows:
        date = row["gval_fechaconfirmacion"]
        amount = row["gval_importetotalcheques"] or 0
        debit.append(line(
            date,
            subcuenta(row["gval_cuentapropiadestinoname"], mapping),
            amount,
            0,
            _concepto(row["gval_numtransaccionboletarealdedeposito"]),
        ))
        totals_by_date[date] = (totals_by_date.get(date, 0) or 0) + amount

    credit = [line(date, CONTRA_SUBCUENTA, 0, total, "depo del dia")
              for date, total in totals_by_date.items()]

    return debit + credit