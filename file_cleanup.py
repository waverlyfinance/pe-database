import json 
from ai_extract import transform_fields

#TODO: Probably need to redo these companies 
# L Cat
# Marlin
# Flexpoint
# NMC

# Add fields to existing files
def add_field(filename):
    firm = filename
    filename = filename + "_portcos"

    with open(f"_portcos_processed/{filename}.json", "r") as file:
        data = json.load(file)
    
    for company in data: 
        company["firm"] = firm

    with open(f"_portcos_processed/{filename}.json", "w") as outfile:
        json.dump(data, outfile, indent=2)
    
add_field("HIG")


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


remove_companies("vista")
# remove_json("tpg")





# Use GPT-4 to standardize fields
def transform(filename):
    filename = filename + "_portcos"

    with open(f"_portcos_raw/{filename}.json", "r") as file:
        content = json.load(file)

    #TODO: Some JSON files have different field names. E.g. "status_current" or "status"
    for company in content:
        company["industry"] = original_industry
        company["date_of_investment"] = original_date
        company["region"] = original_region
        company["status_current"] = original_status

#original_industry, original_date, original_region, original_status

# transform("vista")

