from .common import line, resolve_subaccount_max

NET_SUBACCOUNT = 7000001
VAT_SUBACCOUNT = 3300002

PREFIJO = {
    "Nota Débito": "n/d",
    "Nota Crédito": "n/c",
    "Factura": "factura",
}
PREFIJO_DEFAULT = "n/d"


def _prefijo(tipo):
    return PREFIJO.get(tipo, PREFIJO_DEFAULT)


def build_tax_document_entries(rows, company_map=None):
    company_map = company_map or {}
    result = []
    for row in rows:
        date = row["Fecha"]
        importe = row["Importe"] or 0
        iva = row["Iva"] or 0
        empresa = row["Empresa"]
        tipo = row["Tipo documento"]
        subaccount = resolve_subaccount_max(empresa, company_map)
        prefijo = _prefijo(tipo)
        es_credito = tipo == "Nota Crédito"
        total = importe + iva
        concepto = prefijo + " " + (empresa or "").lower()

        result.append(line(date, subaccount,
                           0 if es_credito else total,
                           total if es_credito else 0,
                           prefijo + " interes"))
        result.append(line(date, NET_SUBACCOUNT,
                           importe if es_credito else 0,
                           0 if es_credito else importe,
                           concepto))
        result.append(line(date, VAT_SUBACCOUNT,
                           iva if es_credito else 0,
                           0 if es_credito else iva,
                           concepto))
    return [e for e in result if e["DEBE"] or e["HABER"]]