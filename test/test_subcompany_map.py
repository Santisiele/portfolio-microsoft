from domain.accounting.common import build_company_subaccount_map


def test_builds_map_from_sheet_rows():
    rows = [
        {"Empresa": "J.B BIS-DEL SA", "SubCuenta": 1341900},
        {"Empresa": "AIRES DEL SUR S.A.", "SubCuenta": 1365100},
        {"Empresa": "PENDIENTES NO ENCONTRADOS", "SubCuenta": 1300010},
    ]
    m = build_company_subaccount_map(rows)
    assert m["J.B BIS-DEL SA"] == 1341900
    assert m["AIRES DEL SUR S.A."] == 1365100
    assert m["PENDIENTES NO ENCONTRADOS"] == 1300010


def test_strips_whitespace_and_skips_bad_rows():
    rows = [
        {"Empresa": "  CILBRAKE SRL  ", "SubCuenta": "1361400"},
        {"Empresa": "", "SubCuenta": 999},
        {"Empresa": "SIN CUENTA", "SubCuenta": None},
    ]
    m = build_company_subaccount_map(rows)
    assert m["CILBRAKE SRL"] == 1361400
    assert "" not in m
    assert "SIN CUENTA" not in m