import streamlit as st
import pandas as pd
import os
import logging
import traceback
from chatbot import create_chatbot
from report import generate_pdf
import plotly.express as px

# Setup error logging
logging.basicConfig(filename="error.log", level=logging.ERROR, format="%(asctime)s [%(levelname)s] - %(message)s")

st.set_page_config(page_title="Vulnerability Chatbot", layout="wide")
st.title("🛡 Vulnerability Chatbot & Report Generator")

try:
    DATA_FILE = "qualys.xlsx"
    if not os.path.exists(DATA_FILE):
        st.error(f"❌ Data file {DATA_FILE} not found!")
        st.stop()

    chatbot = create_chatbot(DATA_FILE)
    df = pd.read_excel(DATA_FILE)

    if "history" not in st.session_state:
        st.session_state.history = []

    user_query = st.text_input("Ask a question about vulnerabilities:")
    if st.button("Ask"):
        if user_query:
            try:
                response = chatbot.invoke({"question": user_query})
                st.session_state.history.append((user_query, response["answer"]))
            except Exception as e:
                err = traceback.format_exc()
                logging.error(err)
                st.error("❌ Error during chatbot response.")
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
            summary = chatbot.invoke({"question": f"Summarize vulnerabilities for {report_query}"})
            pdf_path = generate_pdf(filtered_df, summary["answer"])
            with open(pdf_path, "rb") as file:
                st.download_button("Download Report", file, pdf_path, "application/pdf")
        except Exception as e:
            err = traceback.format_exc()
            logging.error(err)
            st.error("❌ Error during report generation.")
            st.text(err)

    st.subheader("📊 Vulnerability Trends")
    try:
        if "Severity" in df.columns:
            fig = px.histogram(df, x="Severity", title="Vulnerabilities by Severity")
            st.plotly_chart(fig)
    except Exception as e:
        err = traceback.format_exc()
        logging.error(err)
        st.error("❌ Error displaying chart.")
        st.text(err)

except Exception as e:
    err = traceback.format_exc()
    logging.error(err)
    st.error("❌ App failed to load.")
    st.text(err)
