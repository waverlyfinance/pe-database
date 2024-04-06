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

    


# STANDARDIZING FOR DATABASE

class Portco(BaseModel):
    company_name: str | None 
    company_description: str | None 
    industry: str | None = Field(None, description="Must be only one of the following options: Technology, Healthcare, Industrials, Consumer, Financials, Real Estate, Infrastructure, Business Services")
    date_of_investment: str | None = Field(None, description="E.g. January 2022, or 2022, or 1/19/2022 are all acceptable")
    status_current: str | None = Field(None, description="Whether the company is current / active, or realized / former")
    region: str | None = Field(None, description="E.g. North America, Asia, Europe, etc.")
    fund: str | None = Field(None, description="Which sub-fund this company belongs to. E.g. Growth, Buyout, Rise, Real Estate, etc.")
    hq: str | None 
    website: str | None = Field(None, description="url or path to the portfolio company's website")
    PE_firm: str = Field(None, description="Name of the private equity firm. E.g. TPG, KKR, Bain Capital, etc.")



class standardized_fields(BaseModel):
    industry: str | None = Field(None, description="Must be only one of the following options: Technology, Healthcare, Industrials, Consumer, Financials, Real Estate, Infrastructure, Business Services")
    date_of_investment: int | None = Field(None, description="Must be an integer in mm/dd/yyyy format. If no date or month is given, assume the 1st day or 1st month.")
    region: str | None = Field(None, description="Must be one of: North America, Europe, LatAm, Asia Pacific, or Other")
    status_current: str | None = Field(None, description="Must be either 1 of 2 values: 'current' (e.g. active) or 'realized' (e.g. historical).")

fields_schema = standardized_fields.schema()


# inputs are the original data
def transform_fields(original_industry, original_date, original_region, original_status):
    
    completion = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {
            "role": "system",
            "content": """You will be provided data from a company, such as the company's industry and date of investment.  
            You must transform the original inputs using your available tools.
            The output must be expressed as a tuple. The 1st, 3rd and 4th entries are strings. The 2nd entry is an int.
            You MUST follow the rules in the description. E.g. "industry" can only be one of 8 options, and nothing else. 
            Here are some hints:
            Technology: E.g. Software, servers, computer chips, IT, vertical software (e.g. software for real estate)
            Healthcare: E.g. Hospitals, pharmaceuticals, biotech, insurance tech, vertical healthcare software (software specifically for healthcare), doctors
            Industrials: E.g. Construction, chemicals, waste management
            Consumer: E.g. Retail, e-commerce, direct-to-consumer, apparel, groceries
            Business Services: Document shredding, facilities cleaning, office supplies
            Financials: E.g. Payments, banks, lenders, insurance 
            Real Estate: E.g. Housing, commercial real estate
            Infrastructure: bridges, airports, shipping yards, roads, solar farms, wind turbines 

            
            """
        # date_of_investment must be an integer in mm/dd/yyyy format. If no date or month is given, assume the 1st day or 1st month.
        },
        {
            "role": "user", 
            "content": f"{original_industry}, {original_date}, {original_region}, {original_status}"
        },],
    tools = [
        {   
            "type": "function",
            "function": {
                "name": "transform_fields",
                "description": """Transform input, as per instructions provided in 'fields_schema'""",
                "parameters": fields_schema
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

#transform_fields("sportswear", "Jan 2019", "Mexico", "active")


