from datetime import date
import pandas as pd

MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

HOLIDAYS_AR = {
    "2026-01-01": "Año Nuevo",
    "2026-02-16": "Carnaval",
    "2026-02-17": "Carnaval",
    "2026-03-23": "No laborable turístico",
    "2026-03-24": "Día de la Memoria",
    "2026-04-02": "Malvinas",
    "2026-04-03": "Viernes Santo",
    "2026-05-01": "Día del Trabajador",
    "2026-05-25": "Revolución de Mayo",
    "2026-06-15": "Güemes",
    "2026-07-09": "Independencia",
    "2026-07-10": "No laborable turístico",
    "2026-08-17": "San Martín",
    "2026-10-12": "Día de la Raza",
    "2026-11-06": "Día del Empleado Bancario",
    "2026-11-23": "Soberanía Nacional",
    "2026-12-07": "No laborable turístico",
    "2026-12-08": "Inmaculada Concepción",
    "2026-12-25": "Navidad",
}


def _today(today):
    if today is None:
        return date.today()
    if isinstance(today, str):
        return date.fromisoformat(today)
    return today


def last_business_day(df: pd.DataFrame, today=None):
    today = _today(today)
    days = df[(df["is_business_day"] == 1) & (df["date"] < today)]["date"]
    return days.max() if not days.empty else None


def last_n_business_days(df: pd.DataFrame, n: int = 20, today=None) -> set:
    today = _today(today)
    days = df[(df["is_business_day"] == 1) & (df["date"] <= today)]["date"]
    return set(sorted(days, reverse=True)[:n])


def is_selected_date_valid(selected_date, df: pd.DataFrame, today=None) -> int:
    if isinstance(selected_date, str):
        selected_date = date.fromisoformat(selected_date)
    minimum = last_business_day(df, today)
    return int(minimum is not None and selected_date >= minimum)


def build_calendar(start: str = "2026-01-01", end: str = "2026-12-31",
    holidays: dict = None, today=None) -> pd.DataFrame:
    holidays = holidays if holidays is not None else HOLIDAYS_AR
    today = _today(today)

    dates = pd.date_range(start, end, freq="D")
    df = pd.DataFrame({"date": dates})

    df["year"]        = df.date.dt.year
    df["month"]       = df.date.dt.month
    df["month_name"]  = df.month.map(lambda m: MONTHS[m - 1])
    df["year_month"]  = df.date.dt.strftime("%Y-%m")
    df["day"]         = df.date.dt.day
    df["weekday_num"] = df.date.dt.weekday + 1
    df["day_name"]    = df.date.dt.weekday.map(lambda d: DAYS[d])
    df["is_weekend"]  = (df.weekday_num >= 6).astype(int)

    df["date"] = df.date.dt.date

    date_str = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["is_holiday"]   = date_str.isin(holidays).astype(int)
    df["holiday_name"] = date_str.map(holidays)

    df["is_business_day"] = (~((df.is_weekend == 1) | (df.is_holiday == 1))).astype(int)

    last = last_business_day(df, today)
    df["is_valid_calendar_date"] = (df["date"] >= last).astype(int) if last else 0

    top20 = last_n_business_days(df, 20, today)
    df["is_last_20_business_days"] = df["date"].isin(top20).astype(int)

    return df