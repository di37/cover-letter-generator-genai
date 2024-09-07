from langchain.prompts.prompt import PromptTemplate

# Prompt template for crafting a cold email based on a job description
COVER_LETTER_PROMPT_TEMPLATE = """### JOB DESCRIPTION:
{job_description}

### INSTRUCTION:
You are Isham, a motivated job seeker applying for the position mentioned in the job description. In your cover letter, introduce yourself, highlight your relevant skills, and explain why you are an excellent fit for the role. Be sure to emphasize how your experience and qualifications align with the needs of the company, as described in the job description.

Include a brief but compelling summary of how your past experiences, skills, and career accomplishments make you the ideal candidate. Additionally, incorporate relevant projects or case studies from your portfolio using the following links: {link_list} to showcase your work and demonstrate your qualifications.

Express your enthusiasm for the opportunity and your desire to contribute to the company’s goals.

Ensure the tone remains professional, enthusiastic, and tailored to the specific job role and company.

### COVER LETTER (START DIRECTLY WITH THE MESSAGE):
"""



# Prompt template for extracting job postings from scraped career page text
JOB_POST_EXTRACTION_PROMPT_TEMPLATE = """### SCRAPED TEXT FROM WEBSITE:
{page_data}

### INSTRUCTION:
The text provided is scraped from a website’s careers page. Your task is to extract the job postings from the text and return them in a structured JSON format. Each job posting should contain the following keys: `company name`, `role`, `experience`, `skills`, and `description`.

Ensure that the output is valid JSON. Return only the JSON response without any additional information or preamble.

### OUTPUT (VALID JSON ONLY):
"""

# Creating templates
COVER_LETTER_PROMPT = PromptTemplate.from_template(COVER_LETTER_PROMPT_TEMPLATE)
JOB_POST_EXTRACTION_PROMPT = PromptTemplate.from_template(JOB_POST_EXTRACTION_PROMPT_TEMPLATE)
