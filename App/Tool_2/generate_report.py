import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io


class ReportError(Exception):
    pass


def generate_cost_report(excel_file_path, date_from=None, date_till=None, cost_code=None):
    """Generate a PDF report and return it as a BytesIO object"""

    try:
        df = pd.read_excel(excel_file_path, dtype={'Cost Code': str})
    except FileNotFoundError:
        raise ReportError("Excel file not found")
    except Exception as e:
        raise ReportError(f"Failed to read Excel file: {e}")

    try:
        df.columns = df.columns.str.strip()

        required_columns = {
            'Date', 'Cost Code', 'Cost Description', 'Narration',
            'Supplier name', 'LPO NO', 'MRIR NO', 'PV REF NO', 'Actual'
        }
        missing = required_columns - set(df.columns)
        if missing:
            raise ReportError(f"Missing required columns: {', '.join(missing)}")

        df['Cost Code'] = df['Cost Code'].apply(
            lambda x: str(int(float(x))).zfill(5) if pd.notna(x) and x != 'nan' else ''
        )

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        if date_from:
            date_from = pd.to_datetime(date_from, errors='coerce')
            if date_from is pd.NaT:
                raise ReportError("Invalid start date")
            df = df[df['Date'] >= date_from]

        if date_till:
            date_till = pd.to_datetime(date_till, errors='coerce')
            if date_till is pd.NaT:
                raise ReportError("Invalid end date")
            df = df[df['Date'] <= date_till]

        if cost_code:
            df = df[df['Cost Code'] == str(cost_code).zfill(5)]

        if df.empty:
            raise ReportError("No records found matching the filters")

        df['Actual'] = pd.to_numeric(df['Actual'], errors='coerce')
        if df['Actual'].isna().any():
            raise ReportError("Invalid numeric values in Actual column")

        df['Date'] = df['Date'].dt.strftime('%m/%d/%Y')

    except ReportError:
        raise
    except Exception as e:
        raise ReportError(f"Data processing failed: {e}")

    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=18
        )

        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            spaceAfter=30,
            alignment=1
        )

        elements.append(Paragraph("<b>Cost Details Report</b>", title_style))

        filter_info = []
        if date_from or date_till:
            filter_info.append(
                f"<b>Date Range:</b> "
                f"{date_from.strftime('%m/%d/%Y') if date_from else 'All'} to "
                f"{date_till.strftime('%m/%d/%Y') if date_till else 'All'}"
            )
        if cost_code:
            filter_info.append(f"<b>Cost Code:</b> {cost_code}")

        if filter_info:
            elements.append(Paragraph(" | ".join(filter_info), styles['Normal']))
            elements.append(Spacer(1, 20))

        table_data = [[
            'Date', 'Cost Code', 'Cost Description', 'Narration',
            'Supplier', 'LPO NO', 'MRIR NO', 'PV REF NO', 'Actual'
        ]]

        for _, row in df.iterrows():
            table_data.append([
                Paragraph(str(row['Date']), styles['Normal']),
                Paragraph(str(row['Cost Code']), styles['Normal']),
                Paragraph(str(row['Cost Description']), styles['Normal']),
                Paragraph(str(row['Narration']), styles['Normal']),
                Paragraph(str(row['Supplier name']) if pd.notna(row['Supplier name']) else '', styles['Normal']),
                Paragraph(str(row['LPO NO']) if pd.notna(row['LPO NO']) else '', styles['Normal']),
                Paragraph(str(row['MRIR NO']) if pd.notna(row['MRIR NO']) else '', styles['Normal']),
                Paragraph(str(row['PV REF NO']) if pd.notna(row['PV REF NO']) else '', styles['Normal']),
                Paragraph(f"{float(row['Actual']):.2f}", styles['Normal'])
            ])

        total_amount = df['Actual'].sum()
        table_data.append(['', '', '', '', '', '', '', 'Total:', f"{total_amount:.2f}"])

        table = Table(
            table_data,
            colWidths=[
                0.9*inch, 0.8*inch, 1.5*inch, 2*inch,
                1.2*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch
            ],
            repeatRows=1
        )

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
        elements.append(Spacer(1, 20))
        elements.append(
            Paragraph(
                f"<b>Summary:</b> Total Records: {len(df)} | Total Amount: {total_amount:.2f}",
                styles['Normal']
            )
        )

        doc.build(elements)
        buffer.seek(0)
        return buffer

    except Exception as e:
        raise ReportError(f"PDF generation failed: {e}")
