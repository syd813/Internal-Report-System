from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import logging

logger = logging.getLogger(__name__)

NUMERIC_COLS = ["Budget", "Actual", "Provision", "Total Cost", "Variance"]


def format_currency(value: float) -> str:
    return "{:,.2f}".format(value)


def build_pdf(summary_df, project_number, as_of_date) -> bytes:
    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(A3),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()
    styleN = ParagraphStyle(name="Normal", parent=styles["Normal"], fontSize=12)
    styleB = ParagraphStyle(name="Bold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12)
    styleRight = ParagraphStyle(name="Right", parent=styles["Normal"], alignment=2)
    styleBoldRight = ParagraphStyle(name="BoldRight", parent=styles["Normal"], fontName="Helvetica-Bold", alignment=2)
    styleGroup = ParagraphStyle(name="Group", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=14)

    columns = ["Cost Code", "Cost Description"] + NUMERIC_COLS
    col_widths = [120, 350, 100, 100, 100, 120, 120]

    table_data = [
        [Paragraph("Ras Amud LLC, OMAN", styles["Title"])] + [""] * (len(columns) - 1),
        [""] * len(columns),
        [
            Paragraph(f"<b>Project Number:</b> {project_number}", styleN),
            "", "", "", "",
            Paragraph(f"<b>As of:</b> {as_of_date.strftime('%d-%b-%Y')}", styleN),
            "",
        ],
        [""] * len(columns),
        [Paragraph(c, styleBoldRight if c in NUMERIC_COLS else styleB) for c in columns],
        [""] * len(columns),
    ]

    for group_name, group_df in summary_df.groupby("Group Name"):
        table_data.append([Paragraph(group_name, styleGroup)] + [""] * (len(columns) - 1))

        for _, row in group_df.iterrows():
            is_total = row["Cost Description"] == "Group Total"
            row_cells = []

            for col in columns:
                if col in NUMERIC_COLS:
                    txt = format_currency(row[col])
                    style = styleBoldRight if is_total else styleRight
                else:
                    txt = row[col]
                    style = styleB if is_total else styleN

                row_cells.append(Paragraph(str(txt), style))

            table_data.append(row_cells)

        table_data.append([""] * len(columns))

    grand_totals = summary_df[summary_df["Cost Description"] == "Group Total"][NUMERIC_COLS].sum()
    logger.info("Grand totals: %s", grand_totals.to_dict())

    grand_row = ["", "Grand Total"] + [format_currency(grand_totals[c]) for c in NUMERIC_COLS]
    table_data.append([Paragraph(str(c), styleB) for c in grand_row])

    table = Table(table_data, colWidths=col_widths, repeatRows=6)
    table.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))

    doc.build([table])
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
