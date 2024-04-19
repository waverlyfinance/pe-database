from openai import OpenAI
import json
import os
from pydantic import BaseModel, Field
from langchain_text_splitters import RecursiveJsonSplitter

# Openai stuff
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# pre-process the files first. Extract only relevant fields to save on tokens
def pre_process(firm): 
    
    filename = firm + "_portcos"
    
    with open(f"_portcos_processed/{filename}.json", "r") as file:
        data = json.load(file)
    
    new_data = []

    for company in data:
        extracted_fields = {
            "company_name": company["company_name"],
            # "company_description": company["company_description"] if company["company_description"] else None,
            "industry": company["industry"] if company["industry"] else None,
            "region": company["region"] if company["region"] else None,
            "fund": company["fund"] if company["fund"] else None,
            "date_of_investment": company.get("date_of_investment") if company.get("date_of_investment") else None,
            "status_current": company.get("status_current") if company.get("status_current") else None,
        }

        new_data.append(extracted_fields)

    with open(f"_portcos_gpt/{filename}.json", "w") as outfile:
        json.dump(new_data, outfile, indent=2)

    return new_data


# Langchain chunking. Documents are too large (max 4096 output tokens)
def chunk(data):

    # data_string = json.dumps(data)

    splitter = RecursiveJsonSplitter(max_chunk_size=5000)

    chunks = splitter.split_text(json_data=data, convert_lists=True)

    print(chunks[0])
    print(chunks[1])
    return chunks


# STANDARDIZING FOR DATABASE
class standardized_fields(BaseModel):
    industry: str | None = Field(None, description="Must be only one of the following options: Technology, Healthcare, Industrials, Consumer, Financials, Real Estate, Infrastructure, Business Services, Natural Resources")
    date_of_investment: int | None = Field(None, description="Must be an integer in yyyy format. E.g. 2013 or 2017")
    region: str | None = Field(None, description="Must be one of: North America, Europe, LatAm, Asia Pacific, or Other")
    status_current: str | None = Field(None, description="Must be either 1 of 2 values: 'current' (e.g. active) or 'realized' (e.g. historical).")

# fields_schema = standardized_fields.schema()

class output_fields(BaseModel):
    output_fields: list[standardized_fields]

fields_schema = output_fields.schema()

# inputs are the original data
def transform_fields(data_string):

    completion = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {
            "role": "system",
            "content": """You will be provided data for a company, such as the company's industry, region, and date of investment.  
            You must transform the original inputs using your available tools.
            The output must be expressed as JSON.
            You MUST follow the rules in the description. E.g. "industry" can only be one of 9 options, and nothing else. 
            Here are some hints:
            Technology: E.g. Software, servers, computer chips, IT, etc. Note that software for specific industries (aka "vertical" software), like software for Healthcare or for Financials, should not be classified as Technology. But in the underlying industry.
            Healthcare: E.g. Hospitals, pharmaceuticals, biotech, insurance tech, vertical healthcare software (software specifically for healthcare), doctors
            Industrials: E.g. Construction, chemicals, waste management
            Consumer: E.g. Retail, e-commerce, direct-to-consumer, apparel, groceries
            Business Services: Document shredding, facilities cleaning, office supplies
            Financials: E.g. Payments, banks, lenders, insurance 
            Real Estate: E.g. Housing, commercial real estate
            Infrastructure: bridges, airports, shipping yards, roads, solar farms, wind turbines 
            Natural Resources: E.g. Energy, mining, oil & gas, metals

            
            """
        },
        {
            "role": "user", 
            "content": data_string
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



def main(firm):
    filename = firm + "_portcos"
    
    data = pre_process(firm)
    chunks = chunk(data)
    print(chunks)
    print(type(chunks))
    
    # data_string = json.dumps(data)

    output = []
    for item in chunks[:5]:
        # transformed_chunk = transform_fields(chunk)
        print(item)

        output.append(item)
        
    with open(f"_portcos_gpt/{filename}_test.json", "w") as outfile:
        json.dump(output, outfile, indent=2)

main("tpg")

# data = pre_process("tpg")
# chunks = chunk(data)

