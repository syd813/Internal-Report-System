from .data_processing import validate_and_prepare_df
from .pdf_renderer import build_pdf
import pandas as pd

def generate_cost_report(excel_file_path, date_from=None, date_till=None, cost_code=None):
    df = pd.read_excel(excel_file_path, dtype={'Cost Code': str})
    df = validate_and_prepare_df(df, date_from=date_from, date_till=date_till, cost_code=cost_code)
    return build_pdf(df, date_from=date_from, date_till=date_till, cost_code=cost_code)
