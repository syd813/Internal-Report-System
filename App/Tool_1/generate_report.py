import pandas as pd
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import logging
import traceback


class ReportError(Exception):
    pass


logger = logging.getLogger(__name__)


def summarize_cost_data(df: pd.DataFrame) -> pd.DataFrame:
    try:
        numeric_cols = ["Budget", "Actual", "Provision", "Total Cost", "Variance"]
        required_cols = ["Group Name", "Cost Code", "Cost Description"] + numeric_cols

        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ReportError(f"Missing columns in Excel: {missing}")

        df["Cost Code"] = df["Cost Code"].astype(str)
        df["Group Name"] = df["Group Name"].astype(str)

        all_groups = []
        for group_name, group_data in df.groupby("Group Name"):
            grouped = (
                group_data.groupby("Cost Code", as_index=False)
                .agg({
                    "Cost Description": "first",
                    **{col: "sum" for col in numeric_cols}
                })
            )
            grouped.insert(0, "Group Name", group_name)

            total_row = {
                "Group Name": group_name,
                "Cost Code": "",
                "Cost Description": "Group Total",
            }
            for col in numeric_cols:
                total_row[col] = group_data[col].sum()

            grouped = pd.concat([grouped, pd.DataFrame([total_row])], ignore_index=True)
            all_groups.append(grouped)

        return pd.concat(all_groups, ignore_index=True)

    except ReportError:
        raise
    except Exception as e:
        logger.error("Error in summarize_cost_data: %s", str(e))
        logger.debug(traceback.format_exc())
        raise ReportError("Failed to summarize cost data")


def generate_pdf_report(excel_file, as_of_date: date) -> bytes:
    try:
        logger.info("Reading Excel file...")
        df = pd.read_excel(excel_file, dtype={"Cost Code": str})

        if df.empty:
            raise ReportError("Uploaded Excel file is empty")

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(
                df["Date"], errors="coerce", dayfirst=True
            ).dt.date
            df = df.dropna(subset=["Date"])
            df = df[df["Date"] <= as_of_date]

        df_filtered = df.drop(columns=["Date"], errors="ignore")
        summary_df = summarize_cost_data(df_filtered)

        logger.info("Creating PDF report for %s rows.", len(summary_df))

        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=landscape(A3),
            leftMargin=20,
            rightMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        elements = []
        styles = getSampleStyleSheet()
        styleN = ParagraphStyle("Normal", parent=styles["Normal"], fontSize=12)
        styleB = ParagraphStyle("Bold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12)
        styleGroupName = ParagraphStyle("GroupName", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=14)
        styleTitle = ParagraphStyle("Title", parent=styles["Title"], fontSize=18)
        styleRight = ParagraphStyle("Right", parent=styles["Normal"], alignment=2, fontSize=12)
        styleBoldRight = ParagraphStyle("BoldRight", parent=styles["Normal"], fontName="Helvetica-Bold", alignment=2, fontSize=12)

        project_number = str(df.get("Project Number", ["N/A"])[0]) if "Project Number" in df.columns else "N/A"

        numeric_cols = ["Budget", "Actual", "Provision", "Total Cost", "Variance"]
        columns = ["Cost Code", "Cost Description"] + numeric_cols
        col_widths = [120, 350, 100, 100, 100, 120, 120]
        table_data = []

        table_data.append([Paragraph("Ras Amud LLC, OMAN", styleTitle)] + [""] * (len(columns) - 1))
        table_data.append([""] * len(columns))
        table_data.append([
            Paragraph(f"<b>Project Number:</b> {project_number}", styleN), "", "", "", "",
            Paragraph(f"<b>As of:</b> {as_of_date.strftime('%d-%b-%Y')}", styleN), "",
        ])
        table_data.append([""] * len(columns))

        header_row = [
            Paragraph(col, styleBoldRight if col in numeric_cols else styleB)
            for col in columns
        ]
        table_data.append(header_row)
        table_data.append([""] * len(columns))

        def get_min_cost_code(group_data):
            codes = group_data[group_data["Cost Code"] != ""]["Cost Code"]
            return codes.min() if not codes.empty else "999999"

        group_order = summary_df.groupby("Group Name").apply(get_min_cost_code).sort_values()

        for group_name in group_order.index:
            group_data = summary_df[summary_df["Group Name"] == group_name]
            table_data.append([Paragraph(group_name, styleGroupName)] + [""] * (len(columns) - 1))

            for _, row in group_data.iterrows():
                row_cells = []
                is_group_total = row["Cost Description"] == "Group Total"

                for col in columns:
                    value = row[col]
                    if col in numeric_cols:
                        value = "{:,.2f}".format(value)
                        style = styleBoldRight if is_group_total else styleRight
                    else:
                        style = styleB if is_group_total else styleN
                    row_cells.append(Paragraph(str(value), style))

                table_data.append(row_cells)

            table_data.append([""] * len(columns))

        group_totals = summary_df[summary_df["Cost Description"] == "Group Total"]
        grand_total_row = [Paragraph("", styleB), Paragraph("Grand Total", styleB)]
        for col in numeric_cols:
            grand_total_row.append(
                Paragraph("{:,.2f}".format(group_totals[col].sum()), styleBoldRight)
            )
        table_data.append(grand_total_row)

        table = Table(table_data, colWidths=col_widths, repeatRows=6)
        table.setStyle(TableStyle([
            ("SPAN", (0, 0), (-1, 0)),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        doc.build(elements)
        pdf_buffer.seek(0)

        logger.info("PDF generation complete")
        return pdf_buffer.getvalue()

    except ReportError:
        raise
    except Exception as e:
        logger.error("Error generating PDF: %s", str(e))
        logger.debug(traceback.format_exc())
        raise ReportError("PDF generation failed")
