from domain.accounting import build_tax_document_entries

MAP = {"CILBRAKE SRL": 555}


def _doc(tipo, importe=1000, iva=210, empresa="CILBRAKE SRL"):
    return {"Fecha": "2026-08-10", "Tipo documento": tipo, "Importe": importe,
            "Iva": iva, "Empresa": empresa}


def test_factura_debits_company_credits_net_and_vat():
    entries = build_tax_document_entries([_doc("Factura")], MAP)
    company = next(e for e in entries if e["SUBCTA"] == 555)
    assert company["DEBE"] == 1210 and company["CONCEPTO"] == "factura interes"
    net = next(e for e in entries if e["SUBCTA"] == 7000001)
    vat = next(e for e in entries if e["SUBCTA"] == 3300002)
    assert net["HABER"] == 1000 and vat["HABER"] == 210


def test_nota_credito_reverses_sides():
    entries = build_tax_document_entries([_doc("Nota Crédito")], MAP)
    company = next(e for e in entries if e["SUBCTA"] == 555)
    assert company["HABER"] == 1210
    net = next(e for e in entries if e["SUBCTA"] == 7000001)
    assert net["DEBE"] == 1000


def test_prefix_by_type_and_default():
    assert build_tax_document_entries([_doc("Nota Débito")], MAP)[0]["CONCEPTO"] == "n/d interes"
    assert build_tax_document_entries([_doc("Otro")], MAP)[0]["CONCEPTO"] == "n/d interes"


def test_balances():
    entries = build_tax_document_entries([_doc("Factura"), _doc("Nota Crédito")], MAP)
    assert sum(e["DEBE"] for e in entries) == sum(e["HABER"] for e in entries)