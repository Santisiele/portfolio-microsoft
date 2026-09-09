from decimal import Decimal

from modules.financial_panel.service import _per_env


def test_per_env_sums_treating_none_as_zero():
    result = _per_env(lambda env: Decimal("100") if env == "DHF" else None)
    assert result["dhf"] == Decimal("100")
    assert result["confinance"] is None
    assert result["total"] == Decimal("100")


def test_per_env_total_adds_both():
    result = _per_env(lambda env: Decimal("100") if env == "DHF" else Decimal("50"))
    assert result["total"] == Decimal("150")


def test_per_env_all_none_total_zero():
    result = _per_env(lambda env: None)
    assert result["dhf"] is None and result["confinance"] is None
    assert result["total"] == 0


def _grid():
    grid = [[""] * 5 for _ in range(21)]
    grid[7][1] = " $  183,120,474.00 "
    grid[20][1] = "$362,440,619.00"
    grid[10][4] = " $  878,315,440.61 "
    return grid


def test_build_account_balances_reads_the_three_cells(monkeypatch):
    import modules.financial_panel.service as service
    monkeypatch.setattr(service, "ACCOUNT_BALANCE_SHEET_ID", "una-planilla")
    monkeypatch.setattr(service, "read_first_tab_grid", lambda sheet_id: _grid())
    balances = service.build_account_balances()
    assert {b["name"]: b["amount"] for b in balances} == {
        "Confinance": 362440619.0,
        "DHF": 183120474.0,
        "SC1": 878315440.61,
    }


def test_build_account_balances_without_sheet_id_is_empty(monkeypatch):
    import modules.financial_panel.service as service
    monkeypatch.setattr(service, "ACCOUNT_BALANCE_SHEET_ID", "")
    assert service.build_account_balances() == []
