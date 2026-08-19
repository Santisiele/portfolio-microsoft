from decimal import Decimal

from .common import line, resolve_subaccount_max

BRUTO_DEBIT = 1300001
TAX_ACTIVE_DEBIT = 7010001
TAX_ACTIVE_CREDIT = 7020001
INTERESES_CREDIT = 7000001
COMISION_CREDIT = 7010001
IVA_CREDIT = 3300002
INTERIOR_CREDIT = 7020002
NET_ACCOUNT = 1120002
TAX_RATE = Decimal("0.012")

AFORO_VALUES = {"-", "--", "A AFORO", "A FORO", "AAFORO", "AFORO", "-AFORO", "AFOTO"}


def _is_aforo(cuenta):
    return (cuenta or "").strip().upper() in AFORO_VALUES


def build_purchase_entries(rows, company_map=None):
    company_map = company_map or {}

    dates = []
    bruto = {}
    bruto_taxed = {}
    intereses = {}
    comision = {}
    iva = {}
    interior = {}
    for row in rows:
        d = row["Fecha"]
        if d not in bruto:
            dates.append(d)
        b = row["Bruto"] or 0
        i = row["Intereses"] or 0
        c = row["Comision"] or 0
        bruto[d] = (bruto.get(d, 0) or 0) + b
        if i != 0 or c != 0:
            bruto_taxed[d] = (bruto_taxed.get(d, 0) or 0) + b
        intereses[d] = (intereses.get(d, 0) or 0) + i
        comision[d] = (comision.get(d, 0) or 0) + c
        iva[d] = (iva.get(d, 0) or 0) + (row["Iva"] or 0)
        interior[d] = (interior.get(d, 0) or 0) + (row["Interior"] or 0)

    f1 = [line(d, BRUTO_DEBIT, bruto[d], 0, "Operaciones del dia") for d in dates]
    f2 = [line(d, TAX_ACTIVE_DEBIT, bruto_taxed.get(d, 0) * TAX_RATE, 0, "pase a imp al ch x activa") for d in dates]
    f3 = [line(d, TAX_ACTIVE_CREDIT, 0, bruto_taxed.get(d, 0) * TAX_RATE, "pase de com x activa") for d in dates]
    f4 = [line(d, INTERESES_CREDIT, 0, intereses[d], "Operaciones del dia") for d in dates]
    f5 = [line(d, COMISION_CREDIT, 0, comision[d], "Operaciones del dia") for d in dates]
    f6 = [line(d, IVA_CREDIT, 0, iva[d], "Operaciones del dia") for d in dates]
    f10 = [line(d, INTERIOR_CREDIT, 0, interior[d], "Operaciones del dia") for d in dates]

    f7 = []
    f8 = []
    f9 = []
    for row in rows:
        d = row["Fecha"]
        subaccount = resolve_subaccount_max(row["Nombre cliente"], company_map)
        saldo = row["Saldo a descontar"]
        neto = row["Neto final"] or 0
        if saldo:
            f7.append(line(d, subaccount, 0, saldo, "cobro x su cta"))
        if _is_aforo(row["Cuenta destino"]):
            f9.append(line(d, subaccount, 0, neto, "deja saldo en cta"))
        else:
            f8.append(line(d, NET_ACCOUNT, 0, neto, "Operaciones del dia"))

    entries = f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8 + f9 + f10
    return [e for e in entries if e["DEBE"] or e["HABER"]]