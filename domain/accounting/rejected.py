from .common import line, subcuenta, resolve_subaccount, last4

EXPENSE_SUBACCOUNT = 7020003
VAT_SUBACCOUNT = 3300002
ACCOUNT_4002_SUBACCOUNT = 1120097

BANK_NAME = {
    "017": "bbva",
    "322": "bind",
    "338": "bst",
    "5001": "conosur",
    "5004": "ivsa",
    "5005": "ivsa",
    "5006": "ivsa",
    "5011": "ivsa",
    "5007": "ieb",
    "072": "santander",
}
BANK_NAME_DEFAULT = "ivsa"


def _bank_name(account):
    return BANK_NAME.get(account, BANK_NAME_DEFAULT)


def build_rejected_entries(rows, company_map=None):
    company_map = company_map or {}
    result = []
    for row in rows:
        date = row["gval_fechadeconfirmacion"]
        importe = row["gval_importe"] or 0
        gastos = row["gval_gastos"] or 0
        iva = row["gval_iva"] or 0
        empresa = row["gval_cuentacorrientename"]
        account = row["Cuenta"]
        cheque = last4(row["gval_numcheque"])
        empresa_sub = resolve_subaccount(empresa, company_map)
        expenses_concepto = "gtos " + cheque
        credit_concepto = "rech " + cheque + " " + (empresa or "").lower()

        if account == "4002":
            result.append(line(date, empresa_sub, importe, 0, "rech " + cheque + " (4002 p reg)"))
            result.append(line(date, empresa_sub, gastos + iva, 0, expenses_concepto))
            result.append(line(date, ACCOUNT_4002_SUBACCOUNT, 0, importe, credit_concepto))
            result.append(line(date, VAT_SUBACCOUNT, 0, iva, credit_concepto))
            result.append(line(date, EXPENSE_SUBACCOUNT, 0, gastos, credit_concepto))
        else:
            debit_concepto = "rech " + cheque + " " + _bank_name(account)
            result.append(line(date, empresa_sub, importe, 0, debit_concepto))
            result.append(line(date, empresa_sub, gastos + iva, 0, expenses_concepto))
            result.append(line(date, subcuenta(account), 0, importe, credit_concepto))
            result.append(line(date, EXPENSE_SUBACCOUNT, 0, gastos, credit_concepto))
            result.append(line(date, VAT_SUBACCOUNT, 0, iva, credit_concepto))
    return result