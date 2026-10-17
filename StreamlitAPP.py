import json
import os
import traceback

import pandas as pd
import streamlit as st

from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.logger import logging

# Template that tells the LLM what JSON structure to return
RESPONSE_JSON = {
    "1": {
        "mcq": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here",
        },
        "correct": "correct answer",
    },
    "2": {
        "mcq": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here",
        },
        "correct": "correct answer",
    },
}


st.set_page_config(
    page_title="Yardi AI Africa | MCQ Generator",
    page_icon="🌍",
    layout="wide",
)

if os.path.exists("logo.png"):
    st.image("logo.png", width="stretch")

st.title("Yardi AI Africa ")
st.subheader("MCQs Creator Application with LangChain 🦜⛓️")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=50, value=5)
    subject = st.text_input("Subject", max_chars=50)
    tone = st.text_input("Complexity level", max_chars=20, placeholder="Simple")
    submitted = st.form_submit_button("Create MCQs")

if submitted:
    if uploaded_file is None or not subject or not tone:
        st.warning("Please upload a file and fill in the subject and complexity level.")
    else:
        with st.spinner("Generating MCQs..."):
            try:
                text = read_file(uploaded_file)
                response = generate_evaluate_chain.invoke(
                    {
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON),
                    }
                )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                logging.error(f"Error generating MCQs: {e}")
                st.error(f"Something went wrong: {e}")
            else:
                quiz = response.get("quiz") if isinstance(response, dict) else None

                if quiz is None:
                    st.error("No quiz was returned by the model.")
                else:
                    table_data = get_table_data(quiz)
                    if table_data:
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        st.table(df)

                        st.download_button(
                            "Download as CSV",
                            df.to_csv(index=False).encode("utf-8"),
                            file_name="quiz.csv",
                            mime="text/csv",
                        )

                        review = response.get("review")
                        if review:
                            st.text_area("Review", value=review, height=180)
                    else:
                        st.error("Could not parse the quiz output into a table.")
st.markdown("---")
st.caption("© 2026 Yardi AI Africa | AI Training, Consultancy and Automation"
    "Contact: 0718387844 - Gichuki Thuita, C.E.O, YARDI AI AFRICA  \n"
    "Email: [yardiaiafrica@gmail.com](mailto:yardiaiafrica@gmail.com)"
)