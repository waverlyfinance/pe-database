from openai import OpenAI
import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

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

# LLM extracts the relevant information. Inputs are (1) processed HTML from the PE firm, and (2) schema of desired inputs
def extract_html(processed_html, schema):
    
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": """Extract the relevant fields from an HTML input provided. You must output raw JSON. Only extract if you are confident that the info is correct. 
            Expect many fields to be 'Null', if nothing relevant applies. 
            For example, if you are looking for 'date_of_investment' but there is a field that says 'founded in 2003', that should be ignored.
            For the company_description field, keep it concise and factual. No more than 50-60 words. Avoid marketing language."""
        },
        {
            "role": "user", 
            "content": processed_html
        },],
    tools = [
        {   
            "type": "function",
            "function": {
                "name": "parse_html",
                "description": """Extract the relevant fields from an HTML input provided. Only extract if you are confident in the answer""",
                "parameters": schema
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



# STANDARDIZING FOR DATABASE

class standardized_fields(BaseModel):
    industry: str | None = Field(None, description="Must be only one of the following options: Technology, Healthcare, Industrials, Consumer, Financials, Real Estate, Infrastructure")
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
            The output must be expressed as a tuple. The first entry is a string, the second entry is an int.
            You MUST follow the rules in the description. E.g. "industry" can only be one of 8 options, and nothing else. 
            Here are some hints:
            Technology: E.g. Software, servers, computer chips, IT, vertical software (e.g. software for real estate)
            Healthcare: E.g. Hospitals, pharmaceuticals, biotech, insurance tech, vertical healthcare software (software specifically for healthcare), doctors
            Industrials: E.g. Construction, chemicals, waste, document shredding
            Consumer: E.g. Retail, e-commerce, direct-to-consumer, apparel, groceries
            Financials: E.g. Payments, banks, lenders, insurance 
            Real Estate: E.g. Housing, commercial real estate
            Infrastructure: bridges, airports, shipping yards, roads 

            
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



def main():
    url = ""
    html = requests.get(url, headers=headers).text

    processed_html = process_html(html)

    splits = chunk_html(processed_html)
    
    combined_chunks = []
    for chunk in splits[:5]:
        extracted_chunk = extract_html(chunk)
        combined_chunks.append(extracted_chunk)
    
    with open("", "w") as outfile:
       json.dump(combined_chunks, outfile, indent=2)

