import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


import os

from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from src.mcqgenerator.logger import logging

load_dotenv(find_dotenv())

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
    max_retries=5,
)

quiz_prompt = PromptTemplate.from_template(
    """
Text: {text}
You are an expert MCQ maker. Given the above text, create a quiz of {number} multiple choice questions
for {subject} students in a {tone} tone.
Make sure the questions are not repeated and that every question conforms to the text.
Format your response exactly like RESPONSE_JSON below, and make exactly {number} MCQs.
Return only valid JSON, with no explanation and no markdown fences.
### RESPONSE_JSON
{response_json}
"""
)

review_prompt = PromptTemplate.from_template(
    """
You are an expert English grammarian and writer. Given a multiple choice quiz for {subject} students,
evaluate the complexity of the questions and give a short analysis of the quiz, using at most 50 words.
If the quiz does not match the students' cognitive and analytical abilities, say which questions
should change and how the tone should be adjusted.

Quiz_MCQs:
{quiz}

Expert review:
"""
)

quiz_chain = quiz_prompt | llm | StrOutputParser()
review_chain = review_prompt | llm | StrOutputParser()


def _generate_and_evaluate(inputs: dict) -> dict:
    logging.info("Generating quiz")
    quiz = quiz_chain.invoke(inputs)
    logging.info("Reviewing quiz")
    review = review_chain.invoke({"subject": inputs["subject"], "quiz": quiz})
    return {"quiz": quiz, "review": review}


# Same usage as the trainer's: generate_evaluate_chain.invoke({...})
generate_evaluate_chain = RunnableLambda(_generate_and_evaluate)