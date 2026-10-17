import json
import traceback

import PyPDF2

from src.mcqgenerator.logger import logging


def read_file(file):
    """
    Read text from an uploaded file (.pdf or .txt).

    `file` is a file-like object with a `.name` attribute
    (e.g. a Streamlit UploadedFile or an open file in binary mode).
    """
    filename = file.name.lower()

    if filename.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            logging.info("PDF file read successfully")
            return text
        except Exception as e:
            logging.error(f"Error reading the PDF file: {e}")
            raise Exception("Error reading the PDF file") from e

    elif filename.endswith(".txt"):
        try:
            content = file.read()
            # Handle both bytes (uploaded file) and str (text-mode file)
            text = content.decode("utf-8") if isinstance(content, bytes) else content
            logging.info("Text file read successfully")
            return text
        except Exception as e:
            logging.error(f"Error reading the text file: {e}")
            raise Exception("Error reading the text file") from e

    else:
        raise Exception("Unsupported file format. Only PDF and TXT files are supported.")


def get_table_data(quiz_str):
    """
    Convert the quiz JSON string returned by the LLM into a list of dicts
    that can be displayed as a table (e.g. with pandas.DataFrame).

    Expected format:
    {
        "1": {
            "mcq": "Question text",
            "options": {"a": "...", "b": "...", "c": "...", "d": "..."},
            "correct": "a"
        },
        ...
    }
    """
    try:
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []

        for _, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " | ".join(
                f"{option}: {option_value}"
                for option, option_value in value["options"].items()
            )
            correct = value["correct"]
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        logging.error(f"Error building table data: {e}")
        return False