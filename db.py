import os
import json
import psycopg2

#TODO: Clean up TPG, KKR, AmSec, Platinum. Then export to Neon

# grab values from JSON file
with open("_portcos_raw/courtsquare_portcos.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Connect to Postgres
connection_string = "postgresql://portcos_test_owner:6wrlIDbXz9qP@ep-rough-dream-a5c4u78v.us-east-2.aws.neon.tech/portcos_test?sslmode=require"
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
    ceo TEXT
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
    "ceo"
    ]

column_names_sql = ", ".join(column_names) # concatenate the list above into 1 string to pass into a SQL command


def create_db():
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_name} ({columns})")
    # insert query
    insert_query = f"INSERT INTO {db_name} ({column_names_sql}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # programmatically loop through column names + values 
    for company in data:
        values = []
        for column in column_names:
            value = company.get(column) # in the JSON file, some are missing fields for "fund", etc.
            values.append(value) 
        
        cursor.execute(insert_query, values)

    # commit and close
    connection.commit()
    cursor.close()
    connection.close()

create_db()
