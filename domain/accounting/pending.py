from .common import line, resolve_subaccount_max, last4

NOT_FOUND_COMPANY = "PENDIENTES NO ENCONTRADOS"


def _not_found_subaccount(company_map):
    for name, sub in (company_map or {}).items():
        if name.strip().upper() == NOT_FOUND_COMPANY:
            return sub
    return 0


def build_pending_entries(rows, company_map=None):
    company_map = company_map or {}
    not_found = _not_found_subaccount(company_map)
    result = []
    for row in rows:
        date = row["gval_fechadeconfirmacion"]
        importe = row["gval_importe"] or 0
        empresa = row["gval_cuentacorrientename"]
        cheque = last4(row["gval_numcheque"])
        subaccount = resolve_subaccount_max(empresa, company_map)
        result.append(line(date, subaccount, importe, 0, "dep del dia pte " + cheque))
        result.append(line(date, not_found, 0, importe, "dep del dia " + cheque))
    return result