from openai import OpenAI
import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field, create_model

# Openai stuff
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Langchain chunking. Splits raw HTML document into chunks of 10K characters each
def chunk_html(html):
    length_function = len

    # Chunk size of 10,000 characters. Carlyle HTML doc has 440,000 characters. So will return ~44 chunks
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=10000, 
        chunk_overlap=200,
        length_function=length_function,
    )
    text = html
    splits = splitter.split_text(text)

    return splits

# LLM identifies structure to be extracted. Inputs are processed HTML
def identify_schema(processed_html):
    completion = client.chat.completions.create(
        model= "gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """Think step by step. 
                You will be given a HTML file of an investment firm's list of portfolio companies.
                Read the HTML to identify what structured data could be extracted. 
                Structured data requires multiple repetitions of the same field, for multiple companies    
                Here is just some examples. There can be many more fields beyond these: 
                {
                    company_name: str,
                    company_description: str,
                    industry: str,
                    date_of_investment: int or str,
                    status_current: str,
                    region: str,
                    fund: str,
                    website: str
                    },

                Only state a data field if you are confident that it is correct.
                You MUST output a JSON object. Do not output something that starts with "'''json". Do NOT actually populate the fields. Just provide the dictionary structure
                """
            },
            {
                "role": "user", 
                "content": processed_html
            },
        ],
        temperature=0,
    )

    output = completion.choices[0].message.content

    try:
        json_output = json.loads(output)
    except json.JSONDecodeError as error:
        print(f"failed to decode JSON. {error}")

    # create a JSON schema using Pydantic, which is required to be passed into the next LLM function
    json_object = create_model(
        "extracted_fields",
        **{key: value for key, value in json_output.items()}
    )

    class json_objects(BaseModel): # we need a list of multiple companies
        companies: list[json_object]
    
    schema = json_objects.schema()

    return schema
    

# LLM extracts the relevant information. Inputs are (1) processed HTML from the PE firm, and (2) schema of desired inputs
def extract_html(processed_html, schema):
    
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": """
            You will be provided with an HTML file. Extract the relevant fields using the tools available to you. You must output raw JSON. Only extract if you are confident that the info is correct. 
            Expect some fields to be 'Null', if nothing relevant applies. 
            """
        },
        {
            "role": "user", 
            "content": processed_html
        },],
    tools = [
        {   
            "type": "function",
            "function": {
                "name": "extract_html",
                "description": """Extract the relevant fields from an HTML input provided. Follow the schema provided""",
                "parameters": schema
                },
        },],
    temperature=0
    )

    output = completion.choices[0].message.tool_calls[0].function.arguments

    try:
        json_output = json.loads(output)
        print(json_output)
    except json.JSONDecodeError as error:
        print(f"failed to decode JSON. {error}")
        json_output = None

    return json_output


# EXPERIMENT: Try getting the Python code to scrape deterministically
def scrape_code(processed_html):
    
    completion = client.chat.completions.create(
        model= "gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": """Think step by step. 
                You will be given a HTML file of an investment firm's list of portfolio companies. You have 2 options:
                Option 1. Read the HTML to identify what structured data could be extracted. 
                Structured data requires multiple repetitions of the same field, for multiple companies    
                Here are just some examples. There can be many more fields beyond these: 
                {
                    company_name: str,
                    company_description: str,
                    industry: str,
                    date_of_investment: int or str,
                    status_current: str,
                    region: str,
                    fund: str,
                    website: str
                    },

                Option 2. Important: If there is NOT sufficient data in the provided HTML, instead grab the URL links for each portfolio company
                
                Output: Provide the Python code using BeautifulSoup. Your output MUST be structured as code
                """
            },
            {
                "role": "user", 
                "content": processed_html
            },
        ],
        temperature=0,
    )

    output = completion.choices[0].message.content

    # print(output)

    



