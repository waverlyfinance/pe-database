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




# LLM identifies URL links only. Outputs them as a list 
class url(BaseModel):
    url: str | None = Field(None, description="E.g. https://www.inovia.vc/active-companies/certn")

class urls(BaseModel):
    urls: list[url]

urls_schema = urls.schema()

def extract_urls(processed_html):
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": """You will be provided raw HTML containing classes + href links. 
            Please identify all the URL links which lead to pages of individual companies. For example: 
            https://www.inovia.vc/active-companies/certn
            /portfolio/audible-reality
            /portfolio/botpress
            /3dns
            /dot-box
            https://serentcapital.com/portfolio/bio/actionstep/



            Exclude irrelevant links that are not portfolio companies, such as:  
            https://careers.klass.com/jobs
            https://www.linkedin.com/company/klass-capital-corporation/
            /en/contact-us
            https://policies.google.com/privacy

            The output must be expressed as JSON. Do not output something that starts with "'''json"
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
                "name": "extract_urls",
                "description": """extract URL links to individual companies' pages, following the structure of 'urls_schema'""",
                "parameters": urls_schema
                },
        },],
    temperature=0
    )

    output = completion.choices[0].message.tool_calls[0].function.arguments

    try:
        json_output = json.loads(output)

    
    except json.JSONDecodeError as error:
        print(f"failed to decode JSON. {error}")    

    return json_output



# LLM takes URL of individual portco. And extracts key fields
class Company(BaseModel):
    company_name: str | None = Field(None, description="E.g. Exactech, winc, Anaplan, etc.")
    company_description: str | None = Field(None, description="Just copy and paste the description verbatim from the source. Don't change anything. Pick the longer description if multiple options are available")
    # industry: str | None = Field(None, description="E.g. Technology, Business Services, Healthcare, Consumer, Education, Financial, Real Estate, etc.")
    # date_of_investment: str | None = Field(None, description="E.g. January 2022, or 2022, or 1/19/2022 are all acceptable")
    # status_current: str | None = Field(None, description="Current or Active vs. Realized or Former or Exited")
    # region: str | None = Field(None, description="E.g. North America, Asia, Europe, etc.")
    fund: str | None = Field(None, description="Which sub-fund this company belongs to. E.g. Growth, Buyout, Rise, Real Estate, Fund XI, etc. Can be null")
    hq: str | None = Field(None, description="E.g. New York, Barcelona, Boston, Grand Rapids, etc.")
    website: str | None = Field(None, description="url or path to the portfolio company's website")

company_schema = Company.schema()

class Companies(BaseModel):
    companies: list[Company]

companies_schema = Companies.schema()

def extract_data(processed_html):
    completion = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {
            "role": "system",
            "content": """
            Think step by step. 
            You are a financial analyst, reviewing an investment firm's list of portfolio companies. 
            You will be provided raw HTML.
            Use the tools available to you to extract certain data about each portfolio company from the raw HTML. Note that these fields provided in the tools are only certain examples. There can be more or fewer fields, depending on the raw HTML
            Only state an answer if the data is provided explicitly provided. null is an acceptable answer. 
            For example, if there are global offices in Canada, the US, and Australia - but the HTML does not provide a field that says "region: Global", return null
            You MUST output JSON. Do not output something that starts with "'''json"
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
                "name": "extract_data",
                "description": """extract data following the structure of provided next""",
                "parameters": companies_schema
                },
        },],
    temperature=0
    )

    output = completion.choices[0].message.tool_calls[0].function.arguments

    try:
        json_output = json.loads(output)

    
    except json.JSONDecodeError as error:
        print(f"failed to decode JSON. {error}")    
    print(json_output)

    return json_output
