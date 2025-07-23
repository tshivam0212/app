from fpdf import FPDF
import pandas as pd

def generate_pdf(df: pd.DataFrame, summary: str, filename="Vulnerability_Report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Vulnerability Report", ln=True)
    pdf.multi_cell(0, 10, summary)
    pdf.ln(10)
    for _, row in df.iterrows():
        pdf.multi_cell(
            0, 5, f"{row['QID']} - {row['Title']} - {row['Severity']} - {row['Solution']}"
        )
    pdf.output(filename)
    return filename
