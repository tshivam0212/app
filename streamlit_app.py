import streamlit as st
import pandas as pd
import os
from pathlib import Path
import traceback
import logging
import plotly.express as px

from chatbot import create_chatbot
from report import generate_pdf

# Logging setup
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(page_title="Vulnerability Chatbot", layout="wide")
st.title("🛡 Vulnerability Chatbot & Report Generator")

DATA_FILE = Path("qualys.xlsx")

try:
    if not os.path.exists(DATA_FILE):
        msg = f"Data file {DATA_FILE} not found!"
        logging.error(msg)
        st.error(msg)
        st.stop()

    logging.info("Reading Excel file...")
    df = pd.read_excel(DATA_FILE)

    logging.info("Creating chatbot instance...")
    chatbot = create_chatbot(DATA_FILE)

    if "history" not in st.session_state:
        st.session_state.history = []

    user_query = st.text_input("Ask a question about vulnerabilities:")
    if st.button("Ask"):
        if user_query:
            try:
                response = chatbot.invoke({"question": user_query})
                st.session_state.history.append((user_query, response["answer"]))
            except Exception:
                err = traceback.format_exc()
                logging.error(err)
                st.error("Error while invoking chatbot.")
                st.text(err)

    for q, a in st.session_state.history:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Bot:** {a}")

    st.subheader("Generate PDF Report")
    report_query = st.text_input("Enter filter keyword for report (e.g., '.NET'):")

    if st.button("Generate Report"):
        try:
            filtered_df = df
            if report_query:
                filtered_df = df[df.apply(lambda x: x.astype(str).str.contains(report_query, case=False).any(), axis=1)]

            logging.info(f"Generating summary for report: {report_query}")
            summary = chatbot.invoke({"question": f"Summarize vulnerabilities for {report_query}"})

            logging.info("Generating PDF...")
            pdf_path = generate_pdf(filtered_df, summary["answer"])
            with open(pdf_path, "rb") as file:
                st.download_button("Download Report", file, pdf_path.name, "application/pdf")
        except Exception:
            err = traceback.format_exc()
            logging.error(err)
            st.error("❌ Error generating report.")
            st.text(err)

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
    except Exception:
        err = traceback.format_exc()
        logging.error(err)
        st.error("❌ Error displaying chart.")
        st.text(err)

except Exception:
    err = traceback.format_exc()
    logging.critical("Unhandled exception during app load:\n" + err)
    st.error("App failed to start.")
    st.text(err)
