import os
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

from utils import JOB_POST_EXTRACTION_PROMPT, COVER_LETTER_PROMPT

from custom_logger import logger

load_dotenv()


class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile",
        )

    def extract_job(self, cleaned_text):
        logger.info("Extracting job from the job post")
        chain_extract = JOB_POST_EXTRACTION_PROMPT | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
            logger.info("Job extracted successfully")
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res[0] if isinstance(res, list) else res

    def write_mail(self, job, links):
        logger.info("Writing email")
        chain_email = COVER_LETTER_PROMPT | self.llm
        response = chain_email.invoke({"job_description": str(job), "link_list": links})
        logger.info("Email written successfully")
        return response.content


if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))
