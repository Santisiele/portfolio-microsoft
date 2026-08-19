from .common import SUBCUENTA_CONFINANCE, CONTRA_SUBCUENTA, subcuenta, line, amount_after

SUBCUENTA_SALES = {**SUBCUENTA_CONFINANCE, "4002": 1120097}
INTEREST_SUBCUENTA = 6000001
COMMISSION_SUBCUENTA = 6000002
VAT_SUBCUENTA = 6000003


def _concepto(sale_number):
    s = sale_number or ""
    i = s.find("-")
    part = s[i + 1:] if i != -1 else s
    try:
        return "ivsa vta " + str(int(part))
    except ValueError:
        return "ivsa vta " + part


def _concepto_4002(obs):
    obs = obs or ""
    i = obs.find("$")
    text = (obs[:i] if i > 0 else obs).strip()
    return "venta " + text.lower()


def build_sales_entries(rows, mapping=None):
    mapping = mapping or SUBCUENTA_SALES
    result = []
    for row in rows:
        account = row["gval_cuentapropiadestinoname"]
        subcta = subcuenta(account, mapping)
        importe = row["gval_importetotalcheques"] or 0
        obs = row["gval_observaciones"]
        date = row["gval_fechaconfirmacion"]

        if account == "4002":
            concepto = _concepto_4002(obs)
            result.append(line(date, subcta, importe, 0, concepto))
            result.append(line(date, CONTRA_SUBCUENTA, 0, importe, concepto))
        else:
            concepto = _concepto(row["gval_numerodeventa"])
            interest = amount_after(obs, "INTERESES: $")
            commission = amount_after(obs, "COMISION: $")
            vat = amount_after(obs, "IVA: $")
            result.append(line(date, subcta, importe, 0, concepto))
            result.append(line(date, INTEREST_SUBCUENTA, interest, 0, concepto))
            result.append(line(date, COMMISSION_SUBCUENTA, commission, 0, concepto))
            result.append(line(date, VAT_SUBCUENTA, vat, 0, concepto))
            result.append(line(date, CONTRA_SUBCUENTA, 0, importe, concepto))
            result.append(line(date, subcta, 0, interest + commission + vat, concepto))

    return result