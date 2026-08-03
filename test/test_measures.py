from domain.measures import total_by_month


def test_total_by_month_groups_and_sums():
    rows = [
        {"date": "2026-07-02", "amount": 1000},
        {"date": "2026-07-20", "amount": 500},
        {"date": "2026-08-01", "amount": 300},
    ]
    out = total_by_month(rows, "amount", "date")
    assert {"year_month": "2026-07", "amount": 1500} in out
    assert {"year_month": "2026-08", "amount": 300} in out


def test_total_by_month_empty():
    assert total_by_month([], "amount", "date") == []