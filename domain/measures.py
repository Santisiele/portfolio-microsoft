import pandas as pd
from .date_table import build_calendar, last_n_business_days


def total_by_month(rows: list[dict], value_col: str, date_col: str) -> list[dict]:
    df = pd.DataFrame(rows)
    if df.empty:
        return []
    df[date_col] = pd.to_datetime(df[date_col])
    df["year_month"] = df[date_col].dt.strftime("%Y-%m")
    out = df.groupby("year_month")[value_col].sum().reset_index()
    return out.to_dict(orient="records")


def only_last_n_business_days(rows: list[dict], date_col: str, n: int = 20, today=None) -> list[dict]:
    calendar = build_calendar(today=today)
    valid = {d.isoformat() for d in last_n_business_days(calendar, n, today)}
    return [r for r in rows if str(r.get(date_col))[:10] in valid]