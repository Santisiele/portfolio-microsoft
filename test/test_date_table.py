from datetime import date
from domain.date_table import (
    build_calendar, last_business_day, last_n_business_days, is_selected_date_valid,
)

TODAY = "2026-08-03"


def test_holiday_is_not_business_day():
    df = build_calendar(today=TODAY)
    independence = df[df.date == date(2026, 7, 9)].iloc[0]
    assert independence.is_holiday == 1
    assert independence.is_business_day == 0


def test_weekend_is_not_business_day():
    df = build_calendar(today=TODAY)
    saturday = df[df.date == date(2026, 7, 11)].iloc[0]
    assert saturday.is_weekend == 1
    assert saturday.is_business_day == 0


def test_regular_day_is_business_day():
    df = build_calendar(today=TODAY)
    wednesday = df[df.date == date(2026, 7, 8)].iloc[0]
    assert wednesday.is_business_day == 1


def test_last_business_day():
    df = build_calendar(today=TODAY)
    assert last_business_day(df, TODAY) == date(2026, 7, 31)


def test_last_20_business_days_count():
    df = build_calendar(today=TODAY)
    assert int(df.is_last_20_business_days.sum()) == 20


def test_is_selected_date_valid():
    df = build_calendar(today=TODAY)
    assert is_selected_date_valid("2026-08-03", df, TODAY) == 1
    assert is_selected_date_valid("2026-07-01", df, TODAY) == 0