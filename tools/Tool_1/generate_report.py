import pandas as pd
from datetime import date
import logging
from .data_processing import validate_and_prepare_df, summarize_cost_data
from .pdf_renderer import build_pdf

logger = logging.getLogger(__name__)


def generate_pdf_report(excel_file, as_of_date: date) -> bytes:
    df = pd.read_excel(excel_file, dtype={"Cost Code": str})

    df = validate_and_prepare_df(df, as_of_date)
    summary_df = summarize_cost_data(df)

    project_number = (
        str(df.get("Project Number", ["N/A"])[0])
        if "Project Number" in df.columns else "N/A"
    )

    return build_pdf(summary_df, project_number, as_of_date)
