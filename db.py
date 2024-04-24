import os
from dotenv import load_dotenv
import json
import psycopg2
from openai import OpenAI




#TODO: Clean up KKR. Then export
#TODO: Date of investment for HIG is wrong
#TODO: Scrape individual pages for Carlyle


# Connect to Postgres
# load_dotenv()
connection_string = os.getenv("DATABASE_STRING")
connection = psycopg2.connect(connection_string)
cursor = connection.cursor()

# db definition
db_name = "portcos_test"

columns = """
    id SERIAL PRIMARY KEY,
    firm TEXT,
    company_name TEXT, 
    company_description TEXT,
    industry TEXT, 
    date_of_investment TEXT,
    status_current TEXT, 
    region TEXT, 
    fund TEXT,
    hq TEXT,  
    website TEXT,
    follow_on TEXT, 
    ceo TEXT,
    industry_stan TEXT,
    date_of_investment_stan INT,
    region_stan TEXT,
    status_current_stan TEXT
"""

column_names = [
    "firm",
    "company_name", 
    "company_description",
    "industry", 
    "date_of_investment",
    "status_current", 
    "region", 
    "fund",
    "hq",  
    "website",
    "follow_on",
    "ceo",
    "industry_stan",
    "date_of_investment_stan",
    "region_stan",
    "status_current_stan"
    ]

column_names_sql = ", ".join(column_names) # concatenate the list above into 1 string to pass into a SQL command


def create_db(firm):
    # grab values from JSON file
    with open(f"_portcos_output/{firm}_portcos.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    # cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_name} ({columns})")
    
    # insert query
    insert_query = f"INSERT INTO {db_name} ({column_names_sql}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # programmatically loop through column names + values 
    for company in data:
        values = []
        for column in column_names:
            value = company.get(column) # in the JSON file, some are missing fields for "fund", etc.
            values.append(value)
        
        cursor.execute(insert_query, values)

    # commit and close
    connection.commit()
    # cursor.close()
    # connection.close()

# Update table 
def update_db(data):
    
    # grab values from JSON file
    with open("_portcos_processed/tpg_portcos.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    update_sql = f"""
        UPDATE {db_name} 
        SET 
            company_description = %s
            region = %s,
            fund = %s,
            industry = %s,
            status_current = %s,
            company_name = %s
        WHERE id BETWEEN ; 
        """
    # Need to update the ID numbers manually^ 


    # Execute update statements for each company
    for company in data:
        cursor.execute(update_sql, (
            company["company_description"],
            company["region"],
            company["fund"],
            company["industry"],
            company["status_current"],
            company["company_name"],
        ))

        connection.commit()
    
    cursor.close()
    connection.close()


# Generate embeddings
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

def generate_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    output = response.data[0].embedding
    return output

# Add embeddings to db
def embeddings_db(firm):
    
    filename = firm + "_portcos"

    # grab firm name first
    with open(f"_portcos_output/{filename}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    firm_name = data[0]["firm"]

    # Tell it which companies to update using a query
    cursor.execute(f"SELECT id, company_description FROM portcos_test WHERE firm = '{firm_name}'")
    records = cursor.fetchall()

    for record in records:
        text = record[1] # record[0] is id and record[1] is company_description
        if text:  
            embedding = generate_embedding(text)
            cursor.execute(
                "UPDATE portcos_test SET embedding = %s WHERE id = %s", 
                (embedding, record[0])
            )

    connection.commit()  
    cursor.close()
    connection.close()

# For companies where the company_description field is empty. Use the other values to generate an embedding instead
def embeddings_no_desc(firm):
    filename = firm + "_portcos"
    firm_name = "Platinum Equity"

    with open(f"_portcos_processed/{filename}.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Tell it which companies to update using a query
    cursor.execute(f"SELECT id, company_name FROM portcos_test WHERE firm = '{firm_name}'")
    records = cursor.fetchall()

    for company in data:
        for record in records:
            if company["company_name"] == record[1]:
                print(company["company_name"])
                embedding = generate_embedding(company)
                
                cursor.execute(
                "UPDATE portcos_test SET embedding = %s WHERE id = %s", 
                (embedding, record[0])
                )

    connection.commit()  
    cursor.close()
    connection.close()


def main(firm):
    create_db(firm) 
    embeddings_db(firm) 
    # embeddings_no_desc(firm) 
    
main("kkr") # name needs to match filename
