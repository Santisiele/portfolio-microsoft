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