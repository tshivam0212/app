from fpdf import FPDF
import pandas as pd
from io import BytesIO

def generate_pdf(df: pd.DataFrame, summary: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    pdf.cell(0, 10, "Vulnerability Report", ln=True)
    pdf.ln(5)

    if summary:
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, "Summary:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, summary)
        pdf.ln(5)
    
    if df.empty:
        pdf.cell(0, 10, "No records found for the provided filter.", ln=True)
    else:
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, "Details:", ln=True)
        pdf.set_font("Arial", size=10)

        for _, row in df.iterrows():
            row_text = ', '.join(f"{col}: {val}" for col, val in row.items())
            pdf.multi_cell(0, 10, row_text)
            pdf.ln(2)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer
