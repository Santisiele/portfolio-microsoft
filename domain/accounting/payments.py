from .common import line, resolve_subaccount

BANK_ACCOUNT = 1120002


def build_payment_entries(rows, company_map=None):
    company_map = company_map or {}
    result = []
    for row in rows:
        date = row["gval_fechaconfirmacion"]
        importe = row["gval_importe"] or 0
        empresa = row["gval_empresaname"]
        subaccount = resolve_subaccount(empresa, company_map)
        result.append(line(date, BANK_ACCOUNT, 0, importe, "adelanto x bco"))
        result.append(line(date, subaccount, importe, 0, "adelanto x bco " + (empresa or "").lower()))
    return result