from portcos import *
import json
import sqlite3

# grab values from JSON file
with open("lcat_portcos.json", "r") as file:
    data = json.load(file)

# Connect to SQLite
connection = sqlite3.connect("portcos_test.db")
cursor = connection.cursor()

# db definition
db_name = "portcos2"

columns = """
    company_name TEXT PRIMARY KEY, 
    company_description TEXT,
    industry TEXT, 
    date_of_investment INTEGER,
    status_current TEXT, 
    region TEXT, 
    fund TEXT,
    hq TEXT,  
    website TEXT
"""

column_names = [
    "company_name", 
    "company_description",
    "industry", 
    "date_of_investment",
    "status_current", 
    "region", 
    "fund",
    "hq",  
    "website"
    ]

# concatenate the list above into 1 string to pass into a SQL command
column_names_sql = ", ".join(column_names)

# create table 
cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_name} ({columns})")

# insert query
insert_query = f"INSERT INTO {db_name} ({column_names_sql}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

# programmatically loop through column names + values 
for company in data:
    values = []
    for column in column_names:
        value = company.get(column) # in the JSON file, some are missing fields for "fund", etc.
        values.append(value) 
    
    # Bypasses duplicate errors. Can't insert values into a table that already exists
    try:
        cursor.execute(insert_query, values)
    except sqlite3.IntegrityError as error:
        print(f"An error occured: {error}")

connection.commit()

# query
query = f"SELECT * FROM {db_name}"

# print
rows = cursor.execute(query).fetchall()
for row in rows:
    print(row)

