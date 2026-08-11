import pandas as pd


def read_public_sheet(csv_url):
    df = pd.read_csv(csv_url)
    return df.to_dict(orient="records")