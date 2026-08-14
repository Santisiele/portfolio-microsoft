SUBCUENTA_CONFINANCE = {
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


def subcuenta(account, mapping=None):
    return (mapping or SUBCUENTA_CONFINANCE).get(account, SUBCUENTA_DEFAULT)


def line(date, subcta, debe, haber, concepto):
    return {
        "FECH": date,
        "SUBCTA": subcta,
        "CONTRA": "",
        "DEBE": debe,
        "CONCEPTO": concepto,
        "HABER": haber,
    }


def parse_money(s):
    s = (s or "").strip()
    if not s:
        return 0.0
    last_dot = s.rfind(".")
    last_comma = s.rfind(",")
    if last_dot == -1 and last_comma == -1:
        num = s
    elif last_comma > last_dot:
        num = s.replace(".", "").replace(",", ".")
    else:
        num = s.replace(",", "")
    try:
        return float(num)
    except ValueError:
        return 0.0


def amount_after(text, marker):
    text = text or ""
    i = text.find(marker)
    if i == -1:
        return 0.0
    start = i + len(marker)
    end = text.find("\n", start)
    if end == -1:
        end = len(text)
    return parse_money(text[start:end])


def build_company_subaccount_map(rows, company_col="Empresa", subaccount_col="SubCuenta"):
    result = {}
    for row in rows:
        company = row.get(company_col)
        subaccount = row.get(subaccount_col)
        if not company:
            continue
        try:
            result[str(company).strip()] = int(subaccount)
        except (TypeError, ValueError):
            continue
    return result