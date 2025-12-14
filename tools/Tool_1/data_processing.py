import pandas as pd
import logging

logger = logging.getLogger(__name__)

NUMERIC_COLS = ["Budget", "Actual", "Provision", "Total Cost", "Variance"]
REQUIRED_COLS = ["Group Name", "Cost Code", "Cost Description"] + NUMERIC_COLS


def validate_and_prepare_df(df: pd.DataFrame, as_of_date):
    if df.empty:
        raise ValueError("Uploaded Excel file is empty.")

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if "Date" in df.columns:
        before = len(df)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df = df.dropna(subset=["Date"])
        df = df[df["Date"] <= as_of_date]
        dropped = before - len(df)

        logger.info("Date filter removed %d rows", dropped)

        if before > 0 and dropped / before > 0.2:
            raise ValueError(
                "More than 20% of rows were removed by date filter. Please verify the Date column."
            )

    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Cost Code"] = df["Cost Code"].astype(str)
    df["Group Name"] = df["Group Name"].astype(str)

    return df.drop(columns=["Date"], errors="ignore")


def summarize_cost_data(df: pd.DataFrame) -> pd.DataFrame:
    all_groups = []

    for group_name, group_data in df.groupby("Group Name"):
        grouped = (
            group_data.groupby("Cost Code", as_index=False)
            .agg({
                "Cost Description": "first",
                **{col: "sum" for col in NUMERIC_COLS}
            })
        )
        grouped.insert(0, "Group Name", group_name)

        total_row = {
            "Group Name": group_name,
            "Cost Code": "",
            "Cost Description": "Group Total",
            **{col: group_data[col].sum() for col in NUMERIC_COLS},
        }

        grouped = pd.concat([grouped, pd.DataFrame([total_row])], ignore_index=True)
        all_groups.append(grouped)

    result = pd.concat(all_groups, ignore_index=True)
    logger.info("Generated summary with %d rows", len(result))
    return result
