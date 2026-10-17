import json
import traceback

from PyPDF2 import PdfReader

from src.mcqgenerator.logger import logging


def read_file(file):
    """Read an uploaded .pdf or .txt file and return its text."""
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            logging.error(f"Error reading the PDF file: {e}")
            raise Exception("error reading the PDF file")

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception(
            "unsupported file format, only pdf and text files are supported"
        )


def get_table_data(quiz_str):
    """Convert the quiz (JSON string or dict) into a list of rows for a table."""
    try:
        # Accept either a JSON string or an already-parsed dict
        if isinstance(quiz_str, str):
            start, end = quiz_str.find("{"), quiz_str.rfind("}")
            quiz_dict = json.loads(quiz_str[start:end + 1])
        else:
            quiz_dict = quiz_str

        quiz_table_data = []
        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " || ".join(
                f"{option} -> {option_value}"
                for option, option_value in value["options"].items()
            )
            correct = value["correct"]
            quiz_table_data.append(
                {"MCQ": mcq, "Choices": options, "Correct": correct}
            )

        return quiz_table_data

    except Exception as e:
        logging.error(f"Error building table data: {e}")
        traceback.print_exception(type(e), e, e.__traceback__)
        return False