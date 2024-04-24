import json 
from bs4 import BeautifulSoup

#TODO: Probably need to redo these companies 
# L Cat
# Marlin
# Flexpoint
# NMC

# Add fields to existing files
def add_field(firm):
    filename = firm.lower() + "_portcos"

    with open(f"_portcos_processed/{filename}.json", "r") as file:
        data = json.load(file)
    
    for company in data: 
        company["firm"] = firm

    with open(f"_portcos_processed/{filename}.json", "w") as outfile:
        json.dump(data, outfile, indent=2)
    
# add_field("american_securities")

# Update just 1 key-value pair
def update_1key(firm):
    filename = firm + "_portcos"

    with open(f"_portcos_processed/{filename}.json", "r") as file:
        data = json.load(file)
    

    for company in data: 
        company["company_description"] = company["company_description"].replace("<p>", "").replace("</p>", "").strip() # strip p tags
        
    with open(f"_portcos_processed/{filename}.json", "w") as outfile:
        json.dump(data, outfile, indent=2)

# update_1key("tpg")

# Update keys in order to standardize for SQL database
def update_keys(firm):
    filename = firm + "_portcos"

    with open(f"_portcos_raw/{filename}.json", "r") as file:
        data = json.load(file)
    
    updated_data = []

    for company in data: 
        description = company["company_description"].replace("<p>", "").replace("</p>", "").strip() # strip p tags

        updated_company = {
            "id": company["id"],
            "company_description": description,
            "region": company["geo"] if company["geo"] is not None else None,
            "fund": company["product"] if company["product"] is not None else None,
            "industry": company["sector"] if company["sector"] is not None else None,
            "status_current": company["status"] if company["status"] is not None else None,
            "company_name": company["company_name"]
        }
        
        updated_data.append(updated_company)


    with open(f"_portcos_processed/{filename}.json", "w") as outfile:
        json.dump(updated_data, outfile, indent=2)

# update_keys("tpg")

# Applied to files that are: Lists of dicts. Each dict starts with an unnecessary "companies = {}" section
def remove_companies(filename):
    filename = filename + "_portcos"
    
    with open(f"_portcos_raw/{filename}.json", "r") as file:
        content = json.load(file)

    new_list = []
    for section in content:
        for company in section["companies"]:
            new_list.append(company)
    print(new_list)

    with open(f"_portcos_processed/{filename}.json", "w") as outfile:
        json.dump(new_list, outfile, indent=2)


# Applied to JSON files structured as: Dicts. Each
def remove_json(filename):
    filename = filename + "_portcos"
    
    with open(f"_portcos_raw/{filename}.json", "r") as file:
        content = json.load(file)

    new_list = []

    # Loop through each company. Append the key (company_name) as another field in the dictionary 
    for company_name, fields in content.items():
        fields.update({"company_name": company_name})

        new_list.append(fields)

    print(new_list)

    with open(f"_portcos_processed/{filename}.json", "w") as outfile:
        json.dump(new_list, outfile, indent=2)


# remove_json("tpg")



def main(firm):
    add_field(firm)

main("KKR")