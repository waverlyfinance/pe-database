import os
from dotenv import load_dotenv
import json
import psycopg2
from embeddings import generate_embedding


#TODO: Clean up TPG, KKR, AmSec, Platinum. Then export to Neon
#TODO: Date of investment for HIG is wrong



# Connect to Postgres
load_dotenv()
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


def create_db(firm):
    # grab values from JSON file
    with open(f"_portcos_processed/{firm}_portcos.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    # cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_name} ({columns})")
    
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



# Add embeddings to db
def embeddings_db():
    # Tell it which companies to update using a query
    cursor.execute("SELECT id, company_description FROM portcos_test")
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

# semantic search query
def semantic_search(query, threshold):
    query_embedding = generate_embedding(query)

    # just returns the top 10 results
    cursor.execute("SELECT company_name, company_description FROM portcos_test ORDER BY embedding <-> %s::vector LIMIT 15", (query_embedding,)) 

    # Searches based on cosine similarity between (1) query and (2) company_description. Sorts by distance threshold (similarity)
    # cursor.execute("SELECT company_name, company_description FROM portcos_test WHERE embedding <-> %s::vector < %s ORDER BY embedding <-> %s::vector", (query_embedding, threshold, query_embedding)) 
    
    results = cursor.fetchall()
    print(results)
    print(len(results))

    cursor.close()
    connection.close()

def main():
    create_db("tpg")
    # embeddings_db()
    # semantic_search("waste management services", 1.0)
    # update_db(data)
    
main()
