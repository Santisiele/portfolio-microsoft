from .common import line, resolve_subaccount

COLLECTION_DEBIT_SUBCUENTA = 1120002


def build_collection_entries(rows, company_map=None):
    company_map = company_map or {}
    result = []
    for row in rows:
        date = row["Fecha"]
        empresa = row["Empresa"]
        importe = row["Importe"] or 0
        concepto = "Cobranza " + (empresa or "").lower()
        subaccount = resolve_subaccount(empresa, company_map)
        result.append(line(date, COLLECTION_DEBIT_SUBCUENTA, importe, 0, concepto))
        result.append(line(date, subaccount, 0, importe, concepto))
    return result