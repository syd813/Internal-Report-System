import pandas as pd
import logging

logger = logging.getLogger(__name__)

NUMERIC_COLS = ["Actual"]
REQUIRED_COLS = ["Date", "Cost Code", "Cost Description"] + NUMERIC_COLS

def normalize_cost_code(x):
    if pd.isna(x) or str(x).strip().lower() == 'nan' or str(x).strip() == '':
        return ''
    try:
        return str(int(float(x))).zfill(5)
    except:
        return str(x).strip()

def validate_and_prepare_df(df: pd.DataFrame, date_from=None, date_till=None, cost_code=None) -> pd.DataFrame:
    """Validate columns, normalize codes, filter by date/cost_code, and ensure numeric columns."""
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in Excel: {missing}")

    df['Cost Code'] = df['Cost Code'].apply(normalize_cost_code)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    before = len(df)
    df = df.dropna(subset=['Date'])
    dropped = before - len(df)
    if before > 0 and dropped / before > 0.2:
        raise ValueError("More than 20% of rows removed due to invalid dates.")

    # Filter by dates
    if date_from:
        date_from = pd.to_datetime(date_from, errors='coerce')
        if date_from:
            df = df[df['Date'] >= date_from]
    if date_till:
        date_till = pd.to_datetime(date_till, errors='coerce')
        if date_till:
            df = df[df['Date'] <= date_till]

    # Filter by cost code
    if cost_code:
        df = df[df['Cost Code'] == str(cost_code).zfill(5)]

    # Ensure numeric columns
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if df.empty:
        raise ValueError(f"No records found matching filters: date_from={date_from}, date_till={date_till}, cost_code={cost_code}")

    logger.info("Prepared DataFrame with %d rows", len(df))
    return df
