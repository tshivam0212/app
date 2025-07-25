import streamlit as st
import pandas as pd
import os
from chatbot import create_chatbot
from report import generate_pdf
import plotly.express as px

st.set_page_config(page_title="Vulnerability Chatbot", layout="wide")
st.title("🛡 Vulnerability Chatbot & Report Generator")

DATA_FILE = "qualys.xlsx"
if not os.path.exists(DATA_FILE):
    st.error(f"Data file {DATA_FILE} not found!")
    st.stop()

chatbot = create_chatbot(DATA_FILE)
df = pd.read_excel(DATA_FILE)

if "history" not in st.session_state:
    st.session_state.history = []

user_query = st.text_input("Ask a question about vulnerabilities:")
if st.button("Ask"):
    if user_query:
        response = chatbot.invoke({"question": user_query})
        st.session_state.history.append((user_query, response["answer"]))

for q, a in st.session_state.history:
    st.markdown(f"**You:** {q}")
    st.markdown(f"**Bot:** {a}")

st.subheader("Generate PDF Report")
report_query = st.text_input("Enter filter keyword for report (e.g., '.NET'):")

if st.button("Generate Report"):
    filtered_df = df
    if report_query:
        filtered_df = df[df.apply(lambda x: x.astype(str).str.contains(report_query, case=False).any(), axis=1)]
    summary = chatbot.invoke({"question": f"Summarize vulnerabilities for {report_query}"})
    pdf_path = generate_pdf(filtered_df, summary["answer"])
    with open(pdf_path, "rb") as file:
        st.download_button("Download Report", file, pdf_path, "application/pdf")

st.subheader("📊 Vulnerability Trends")

try:
    if "Severity" in df.columns:
        severity_color_map = {
            "Low": "#2ca02c",       # Green
            "Medium": "#ff7f0e",    # Orange
            "High": "#d62728",      # Red
            "Critical": "#9467bd"   # Purple
        }

        fig = px.histogram(
            df,
            x="Severity",
            color="Severity",
            color_discrete_map=severity_color_map,
            title="Vulnerabilities by Severity"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
except Exception as e:
    err = traceback.format_exc()
    logging.error(err)
    st.error("❌ Error displaying chart.")
    st.text(err)

