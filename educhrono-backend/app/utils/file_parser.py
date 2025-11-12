import pandas as pd
from io import BytesIO

def parse_excel(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes))
    df = df.fillna("")
    return df.to_dict(orient="records")
