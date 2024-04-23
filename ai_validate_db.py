from openai import OpenAI
import anthropic
import json
import os
from pydantic import BaseModel, Field
from langchain_text_splitters import RecursiveJsonSplitter
import time
import psycopg2

# Openai stuff
api_key_oai = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key_oai)

# Anthropic
client = anthropic.Anthropic(
    api_key = os.getenv('ANTHROPIC_API_KEY'),
)

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
            "industry": company.get("industry") if company.get("industry") else None,
            "region": company.get("region") if company.get("region") else None,
            # "fund": company.get("fund") if company.get("fund") else None,
            "date_of_investment": company.get("date_of_investment") if company.get("date_of_investment") else None,
            "status_current": company.get("status_current") if company.get("status_current") else None,
            "hq": company.get("hq") if company.get("hq") else None,
        }

        new_data.append(extracted_fields)

    with open(f"_portcos_gpt/{filename}.json", "w") as outfile:
        json.dump(new_data, outfile, indent=2)

    return new_data


# # Langchain chunking. Documents are too large (max 4096 output tokens)
# def chunk(data):

#     # data_string = json.dumps(data)

#     splitter = RecursiveJsonSplitter(max_chunk_size=5000)

#     chunks = splitter.split_text(json_data=data, convert_lists=True)

#     print(chunks[0])
#     print(chunks[1])
#     return chunks


# STANDARDIZING FOR DATABASE
class standardized_fields(BaseModel):
    company_name: str = Field(None, description="Just repeat the exact same company name from the source data. Don't alter anything")
    industry_stan: str | None = Field(None, description="Must be only one of the following options: Technology, Healthcare, Industrials, Consumer, Financials, Real Estate, Infrastructure, Business Services, Natural Resources")
    date_of_investment_stan: int | None = Field(None, description="Must be an integer in yyyy format. E.g. 2013 or 2017")
    region_stan: str | None = Field(None, description="Must be ONLY one of the following options: North America, EMEA, LatAm, Asia Pacific, Africa")
    status_current_stan: str | None = Field(None, description="Must be either these 2 values: 'Current' (e.g. Active) or 'Realized' (e.g. Historical).")

fields_schema = standardized_fields.schema()


# inputs are the original data
def transform_fields(data_string):

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": """You will be provided data for a company, such as the company's industry, region, and date of investment.  
            You must transform the original inputs using your available tools.
            The output must be expressed as JSON.
            You MUST follow the rules in the description. E.g. "industry" can only be one of 9 options, and nothing else. 
            Here are some hints:
            Technology: E.g. Software, servers, computer chips, IT, media, telecom, etc. Note that software for specific industries (aka "vertical" software), like software for Healthcare or for Financials, should not be classified as Technology. But in the underlying industry.
            Healthcare: E.g. Hospitals, pharmaceuticals, biotech, insurance tech, vertical healthcare software (software specifically for healthcare), doctors
            Industrials: E.g. Construction, chemicals, waste management, aerospace, defence
            Consumer: E.g. Retail, e-commerce, direct-to-consumer, apparel, groceries
            Business Services: Document shredding, facilities cleaning, office supplies, government services, education
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


# Claude version
def transform_fields_claude(data):

    prompt= f"""You will be provided data for a company, such as the company's industry, region, and date of investment.  
            You must transform the original inputs using the transform_fields tool.
            The output MUST be expressed as JSON.
            You MUST follow the rules in the description of fields_schema. E.g. "industry" can only be one of 9 options, and nothing else 
            Here are some hints:
            Technology: E.g. Software, servers, computer chips, IT, media, telecom, etc. Note that software for specific industries (aka "vertical" software), like software for Healthcare or for Financials, should not be classified as Technology. But in the underlying industry.
            Healthcare: E.g. Hospitals, pharmaceuticals, biotech, insurance tech, vertical healthcare software (software specifically for healthcare), doctors
            Industrials: E.g. Construction, chemicals, waste management, aerospace, defence
            Consumer: E.g. Retail, e-commerce, direct-to-consumer, apparel, groceries
            Business Services: Document shredding, facilities cleaning, office supplies, government services, education
            Financials: E.g. Payments, banks, lenders, insurance 
            Real Estate: E.g. Housing, commercial real estate
            Infrastructure: bridges, airports, shipping yards, roads, solar farms, wind turbines 
            Natural Resources: E.g. Energy, mining, oil & gas, metals
            
            Use the transform_fields tool.
            If there is no good answer you are confident in, simply return 'null'
            
            Here is the data:
            {data}"""

    completion = client.beta.tools.messages.create(
    model="claude-3-haiku-20240307",
    #haiku-20240307
    #sonnet-20240229
    temperature=0.0,
    max_tokens=1000,
    
    tools = [
    {   
        "name": "transform_fields",
        "description": """Transform inputs from a company, into standardized JSON outputs. Per instructions provided in 'fields_schema'""",
        "input_schema": fields_schema
    },],
    messages=[
        {"role": "user", "content": prompt}
        ],
    )

    try:
        output = completion.content[0].input
        print(output)
    except:
        output = completion.content[1].input
        print(output)
    return output


def consolidate_fields(firm):
    filename = firm + "_portcos"
    
    # first file (original)
    with open(f"_portcos_processed/{filename}.json", "r") as file:
        data1 = json.load(file)
    
    # second file (LLM standardized)
    with open(f"_portcos_gpt/{filename}_output.json", "r") as file:
        data2 = json.load(file)

    # update first file with new fields
    for i in range(len(data1)):
        data1[i].update(data2[i]) # update all fields using 2nd file

    # output to new file
    with open(f"_portcos_output/{filename}.json", "w") as outfile:
        json.dump(data1, outfile, indent=2)


def update_db(firm):
    filename = firm.lower() + "_portcos"
    db_name = "portcos_test"

    # connect to Postgres db
    connection_string = os.getenv("DATABASE_STRING")
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()

    with open(f"_portcos_output/{filename}.json", "r", encoding="utf-8") as file:
        data = json.load(file)


    # SQL update query
    update_sql = f"""
    UPDATE {db_name} 
    SET 
        company_name = %s,
        industry_stan = %s,
        region_stan = %s,
        date_of_investment_stan = %s,
        status_current_stan = %s
    WHERE firm = %s AND website = %s; 
    """
    
    # Execute update statements for each company
    for company in data:
        cursor.execute(update_sql, (
            company.get("company_name"),
            company.get("industry_stan"),
            company.get("region_stan"),
            company.get("date_of_investment_stan"),
            company.get("status_current_stan"),
            company.get("firm"),
            company.get("website")
        ))
        # breakpoint()

    connection.commit()
    cursor.close()
    connection.close()



def main(firm):
    filename = firm + "_portcos"
    
    data = pre_process(firm)
    
    # data_string = json.dumps(data)

    output = []
    for company in data:
        # company_string = json.dumps(company)
        transformed_company = transform_fields_claude(company)
        output.append(transformed_company)
        time.sleep(1)
        
    with open(f"_portcos_gpt/{filename}_output.json", "w") as outfile:
        json.dump(output, outfile, indent=2)

# main("stonepoint")
# consolidate_fields("stonepoint")
update_db("clearlake") # case-sensitive. Must match actual firm name