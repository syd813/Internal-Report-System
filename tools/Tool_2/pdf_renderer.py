from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import logging

logger = logging.getLogger(__name__)
NUMERIC_COLS = ["Actual"]

def format_currency(x):
    return f"{x:.2f}"

def format_date(d):
    return d.strftime('%m/%d/%Y') if d else ''

def build_pdf(df, date_from=None, date_till=None, cost_code=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)

    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16,
                                 textColor=colors.black, spaceAfter=30, alignment=1)
    elements.append(Paragraph("<b>Cost Details Report</b>", title_style))

    # Filter info
    filter_info = []
    if date_from or date_till:
        filter_info.append(f"<b>Date Range:</b> {format_date(date_from) if date_from else 'All'} to {format_date(date_till) if date_till else 'All'}")
    if cost_code:
        filter_info.append(f"<b>Cost Code:</b> {cost_code}")
    if filter_info:
        elements.append(Paragraph(" | ".join(filter_info), styles['Normal']))
        elements.append(Spacer(1, 20))

    # Table headers
    headers = ['Date', 'Cost Code', 'Cost Description', 'Narration', 'Supplier', 'LPO NO',
               'MRIR NO', 'PV REF NO', 'Actual']
    table_data = [headers]

    for _, row in df.iterrows():
        table_data.append([
            Paragraph(format_date(row['Date']), styles['Normal']),
            Paragraph(str(row['Cost Code']), styles['Normal']),
            Paragraph(str(row['Cost Description']), styles['Normal']),
            Paragraph(str(row.get('Narration', '')), styles['Normal']),
            Paragraph(str(row.get('Supplier name', '')), styles['Normal']),
            Paragraph(str(row.get('LPO NO', '')), styles['Normal']),
            Paragraph(str(row.get('MRIR NO', '')), styles['Normal']),
            Paragraph(str(row.get('PV REF NO', '')), styles['Normal']),
            Paragraph(format_currency(row['Actual']), styles['Normal'])
        ])

    total_amount = df['Actual'].sum()
    table_data.append(['', '', '', '', '', '', '', 'Total:', format_currency(total_amount)])

    table = Table(table_data, colWidths=[0.9*inch,0.8*inch,1.5*inch,2*inch,1.2*inch,0.8*inch,0.8*inch,0.9*inch,0.9*inch], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.white),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('VALIGN', (0,1), (-1,-2), 'TOP'),
        ('ALIGN', (-1,1), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 10),
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1,20))
    elements.append(Paragraph(f"<b>Summary:</b> Total Records: {len(df)} | Total Amount: {format_currency(total_amount)}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    logger.info("PDF built with %d records, total amount %.2f", len(df), total_amount)
    return buffer
