from datetime import date

from domain.date_table import next_business_day


def test_regular_day_returns_next_day():
    assert next_business_day("2026-08-12") == date(2026, 8, 13)


def test_friday_returns_monday():
    assert next_business_day("2026-08-07") == date(2026, 8, 10)


def test_friday_before_holiday_skips_weekend_and_holiday():
    assert next_business_day("2026-08-14") == date(2026, 8, 18)


def test_saturday_returns_next_business_day():
    assert next_business_day("2026-08-15") == date(2026, 8, 18)


def test_skips_monday_holiday():
    assert next_business_day("2026-05-22") == date(2026, 5, 26)


def test_never_returns_weekend_or_holiday():
    result = next_business_day("2026-12-24")
    assert result == date(2026, 12, 28)