import pandas as pd

GVIZ_CSV = "https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&headers=0"
EXPORT_CSV = "https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
EXPORT_RANGE = EXPORT_CSV + "&range={cell_range}"


def read_public_sheet(csv_url):
    df = pd.read_csv(csv_url)
    return df.to_dict(orient="records")


def read_tab_grid(sheet_id, gid, cell_range=None):
    if cell_range:
        url = EXPORT_RANGE.format(sheet_id=sheet_id, gid=gid, cell_range=cell_range)
    else:
        url = EXPORT_CSV.format(sheet_id=sheet_id, gid=gid)
    df = pd.read_csv(url, header=None, dtype=str).fillna("")
    return df.values.tolist()


def read_first_tab_grid(sheet_id):
    df = pd.read_csv(GVIZ_CSV.format(sheet_id=sheet_id), header=None, dtype=str)
    return df.values.tolist()
