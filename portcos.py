import os
import requests
from collections import defaultdict
import json
from pprint import pprint

# Grab portco info from the TPG website
def tpg_portcos():
    url="https://www.tpg.com/page-data/sq/d/3768513084.json"
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    } 

    response = requests.get(url, headers=headers)
    nodes = response.json()["data"]["allWpPortfolio"]["nodes"] #239 nodes per the JSON file

    # extract relevant fields
    output_dict = defaultdict(dict)

    for node in nodes:
        name = node["title"] 

        output_dict[name] = {
            "id": node["id"],
            "desc": node["content"].strip("\n"),
            "geo": node["geography"]["nodes"][0]["name"] if node["geography"]["nodes"] else None,
            "product": node["product"]["nodes"][0]["name"] if node["product"]["nodes"] else None,
            "sector": node["sector"]["nodes"][0]["name"] if node["sector"]["nodes"] else None,
            "status": node["status"].get("nodes")[0]["name"] if node["status"]["nodes"] else None,
        }


    # print function
    for company, details in output_dict.items():
        print(company)
        for key, value in details.items():
            print(value)
        print()
    
    # export the results into a JSON file
    with open("tpg_portcos.json", "w") as outfile:
        json.dump(output_dict, outfile, indent=2)

    return output_dict


# FOR KKR
def kkr_portcos():

    # KKR has portcos spread out over 6 pages of JSON. Need to combine them first   
    urls = [f"https://www.kkr.com/content/kkr/sites/global/en/invest/portfolio/jcr:content/root/main-par/bioportfoliosearch.bioportfoliosearch.json?page={i}" for i in range(1,7)] 
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    combined_results = [] # what we want is in a list object called "results"

    for url in urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            combined_results.extend(data.get("results"))
        else:
            print(f"failed to fetch data from {url}")

    #pprint(combined_results)
    with open("kkr_portcos.json", "w") as outfile:
        json.dump(combined_results, outfile, indent=2)


    # TODO: Is the below extraction step necessary? Maybe we just use the total data, and extract at a later step? 
    # Now, extract only the fields we're interested in
    output_dict = {}
    keys_to_extract = ["hq", "region", "assetClass", "industry", "yoi", "url", "description"] # these are per the kkr_portcos.json file

    for company in combined_results:
        name = company["name"]
        
        update_dict = {key: company.get(key) for key in keys_to_extract}
        
        if name:
            output_dict[name] = update_dict

    pprint(output_dict)
    
    with open("kkr_portcos_extracted.json", "w") as outfile:
        json.dump(output_dict, outfile, indent=2)

    return output_dict


# FOR PERMIRA
def permira_portcos():
    # STEP 1: Permira has a JSON file spread across 6 pages. The following code combines them into 1 page 
    urls = [f"https://www.permira.com/api/portfolio?page={i}&sort=a_z" for i in range(0,5)]
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    combined_list = []

    for url in urls: 
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            combined_list.extend(data.get("data"))
        else:
            print(f"failed to fetch data from {url}")

    # output the JSON file into the "permira_portcos sub-folder"
    filename = os.path.join("permira_portcos", "permira_portcos.json") 
    with open(filename, "w") as outfile:
        json.dump(combined_list, outfile, indent=2)

    # STEP 2: now extract only the fields we care about
    output_dict = {}

    keys_to_extract = ["name", "description", ]

    # extracts the Name, Description, and the URL
    for company in combined_list:
        name = company["name"]
        output_dict[name] = {
            "description": company["description"],
            "url": "https://www.permira.com" + company["cta"]["link"]["url"]
        }

    filename = os.path.join("permira_portcos", "permira_portcos_extracted.json") 
    with open(filename, "w") as outfile:
        json.dump(output_dict, outfile, indent=2)

    #pprint(output_dict)

    # STEP 3: Now send a GET request to each portco's URL. Returns HTML files 
    portco_urls = [values["url"] for values in output_dict.values()]
    
    for url in portco_urls[:5]:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response = response.text
            
            filename_part = url.split('/')[-2] + ".html"
            filename = os.path.join("permira_portcos\html", filename_part) 
            with open(filename, "w", encoding="utf-8") as file:
                file.write(response)
        else:
            print(f"failed to fetch data from {url}")

    # TODO: Extract the relevant fields from the HTML files


# FOR EQT
def eqt_portcos():
    # STEP 1: EQT has a JSON file containing the paths for each portco. NOTE: This is only for CURRENT portcos 
    url = "https://eqtgroup.com/page-data/current-portfolio/page-data.json"
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    data = requests.get(url, headers=headers).json()["result"]["data"]["allSanityCompanyPage"]

    # output the JSON file into the subfolder 
    filename = os.path.join("eqt_portcos", "eqt_portcos.json")
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=2)

    # STEP 2: Extract the relevant fields
    output_dict = {}

    for node in data["nodes"]:
        name = node["title"]

        output_dict[name] = {
            "country": node["country"],
            "entryDate": node.get("entryDate"),
            "url": "https://eqtgroup.com" + node["path"],
            "sector": node["sector"],
            "fund": []
        }

        # there can be 1, 2, 3, or multiple entries for "fund" if there are multiple investments. So need to handle that here: 
        if node["fund"]:
            for item in node["fund"]:
                output_dict[name]["fund"].append(item["title"])
    
    # confirm that there are 212 companies, which matches the nodes per Tree Viewer 
    #len(output_dict.keys()))

    # output as a JSON file
    filename = os.path.join("eqt_portcos", "eqt_portcos_extracted.json")
    with open(filename, "w") as outfile:
        json.dump(output_dict, outfile, indent=2)





# Carlyle only has HTML 


# TODO: Grabbing press releases from TPG's website is probably not the best approach. 492 articles. Not a good way to search through them based on company
def grab_releases():
    url="https://www.tpg.com/page-data/sq/d/1324487864.json"
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    } 

    response = requests.get(url, headers=headers)
    response = response.json()["data"]["allWpPost"]["nodes"] #492 nodes in the JSON file



def main():
    eqt_portcos()

main()
