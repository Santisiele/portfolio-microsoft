import pandas as pd

GVIZ_CSV = "https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&headers=0"


def read_public_sheet(csv_url):
    df = pd.read_csv(csv_url)
    return df.to_dict(orient="records")


def read_first_tab_grid(sheet_id):
    df = pd.read_csv(GVIZ_CSV.format(sheet_id=sheet_id), header=None, dtype=str)
    return df.values.tolist()
