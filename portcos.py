from ai_extract import *
import os
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"} 

# pre-process html. OPTION 1: Extract ONLY the classes, links, and text
def process_html_classes(url, scrape_id):
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    
    # narrow down the HTML using the given identifier. Like body. Or a div class
    if soup.find(scrape_id):
        soup = soup.find(scrape_id)
    else:
        soup = soup

    clean_html = []
    for tag in soup.find_all(True):
        classes = tag.get("class")
        if classes:
            clean_html.append(classes)
    
        if tag.name == "a":
            link = tag.get("href")
            clean_html.append(link)

        if not tag.find(True) and tag.get_text(strip=True):
            text = tag.get_text(strip=True)
            clean_html.append(text)

    print(clean_html)
    return clean_html

process_html_classes("https://www.carlyle.com/portfolio", "'div', class_='section section--content'")
# https://www.marlinequity.com/portfolio/ #Difficult because 2 sections. 1st section is just URLs. 2nd contains actual data, but in the class tags
# https://www.american-securities.com/en/companies/list #Difficult because only provide name, desc, and URL. Need to actually go through the URLs yourself and then further scrape
# https://www.lcatterton.com/Investments.html #Difficult because only provide end part of URL


# pre-processing of HTML. OPTION 2: Only extracts the text
def process_html_text(url, scrape_id):
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    
    # narrow down the HTML using the given identifier. Like body. Or a div class
    if soup.find(scrape_id):
        soup = soup.find(scrape_id)
    else:
        soup = soup

    clean_html = soup.get_text(separator=" ", strip=True)

    print(clean_html)
    return clean_html


# pre-processing of HTML. OPTION 3: Only extracts the url links
def process_html_links(url, scrape_id):
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    
    # narrow down the HTML using the given identifier. Like body. Or a div class
    if soup.find(scrape_id):
        soup = soup.find(scrape_id)
    else:
        soup = soup
    
    links = []
    for a in soup("a", href=True):
        links.append(a["href"])

    print(links)
    return links




# Generic class. Fields to be extracted per portco
class Portco(BaseModel):
    company_name: str | None = Field(None, description="E.g. Exactech, winc, Anaplan, etc.")
    company_description: str | None = Field(None, description="Short description of company. Must be 50 words or less. Don't use marketing language") # takes up too many tokens. Grab this anyways from the press release??
    industry: str | None = Field(None, description="E.g. Consumer, Technology, Industrials, Healthcare, Real Estate, etc.")
    date_of_investment: str | None = Field(None, description="E.g. January 2022, or 2022, or 1/19/2022 are all acceptable")
    status_current: str | None = Field(None, description="Whether the company is current / active, or realized / former")
    region: str | None = Field(None, description="E.g. North America, Asia, Europe, etc.")
    fund: str | None = Field(None, description="Which sub-fund this company belongs to. E.g. Growth, Buyout, Rise, Real Estate, etc.")
    hq: str | None 
    website: str | None = Field(None, description="url or path to the portfolio company's website")
    PE_firm: str = Field(None, description="Name of the private equity firm. E.g. TPG, KKR, Bain Capital, etc.")

company_schema = Portco.schema()

# We want a list of multiple companies
class Portcos(BaseModel):
    companies: list[Portco]

companies_schema = Portcos.schema()


# COMPANIES

# For TPG
def tpg_portcos():
    url="https://www.tpg.com/page-data/sq/d/3768513084.json"

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
    pprint(output_dict)
    
    # export the results into a JSON file
    with open("tpg_portcos.json", "w") as outfile:
        json.dump(output_dict, outfile, indent=2)

    return output_dict


# FOR KKR
def kkr_portcos():

    # KKR has portcos spread out over 6 pages of JSON. Need to combine them first   
    urls = [f"https://www.kkr.com/content/kkr/sites/global/en/invest/portfolio/jcr:content/root/main-par/bioportfoliosearch.bioportfoliosearch.json?page={i}" for i in range(1,7)] 

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

    # extracts the Name, Description, and the URL
    for company in combined_list:
        name = company["name"]
        output_dict[name] = {
            "description": company["description"],
            "url": "https://www.permira.com" + company["cta"]["link"]["url"] # the url path is contained within these fields 
        }

    filename = os.path.join("permira_portcos", "permira_portcos_extracted.json") 
    with open(filename, "w") as outfile:
        json.dump(output_dict, outfile, indent=2)

    # STEP 3: Now send a GET request to each portco's URL. Returns HTML, which needs to be parsed 
    for name in output_dict.keys():

        url = output_dict[name]["url"]
        response = requests.get(url, headers=headers)

        # STEP 4: Use BeautifulSoup to scrape the portco's specific page and extract more data
        soup = BeautifulSoup(response.content, "html.parser")
        co_desc = soup.find('div', class_="CaseStudyScrollHijack_companyDescription__fwvXg").get_text(separator=" ", strip=True)
        
        co_date = soup.find('div', class_="CaseStudyScrollHijack_statsTitle__6RvPS") 
        co_date = co_date.get_text(strip=True) if co_date else None # cleans up text if the value exists. Otherwise, returns None
        
        # this code didn't work. Tried to validate whether the date existed. For some reason, returned the wrong results (e.g. "2021" when should have been None)
        """date_section = soup.find('div', class_="CaseStudyScrollHijack_stats__9ib02")
        date_check = date_section.find('div', class_="CaseStudyScrollHijack_statsDesc__qt5bR")
        date_check = date_check.get_text(separator=" ", strip=True) if date_check else None

        if date_check == "Investment year": """

        # co_details_messy is tricky. We need to extract 3 different fields from here
        co_details_messy = soup.find_all('div', class_="CaseStudyScrollHijack_companyDetailsRow__mHKu1") # this one needs further processing due to messy nature
        co_details_clean = {}

        for detail in co_details_messy[:3]: #first 3 elements are what we want. Last element is website, which is already in the output_dict
            # strip out all the unnecessary mess outside of the <p></p> tags
            p_tag1 = detail.find("p").get_text(strip=True)
            p_tag2 = detail.find("p").find_next_sibling("p").get_text(strip=True)
             
            co_details_clean.update({p_tag1: p_tag2})

        # Append these newly extracted fields to output_dict
        output_dict[name].update(co_details_clean)
        output_dict[name].update({
        "description": co_desc,
        "investment date": co_date
        })

    # output final dictionary into new JSON file
    filename = os.path.join("permira_portcos", "permira_portcos_final.json") 
    with open(filename, "w") as outfile:
        json.dump(output_dict, outfile, indent=2)
    #pprint(output_dict)
        

# FOR EQT
def eqt_portcos():
    # STEP 1: EQT has a JSON file containing the paths for each portco. NOTE: This is only for CURRENT portcos 
    url = "https://eqtgroup.com/page-data/current-portfolio/page-data.json"

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
    
    # Note: there are 212 companies 

    # output as a JSON file
    filename = os.path.join("eqt_portcos", "eqt_portcos_extracted.json")
    with open(filename, "w") as outfile:
        json.dump(output_dict, outfile, indent=2)


# FOR CARLYLE
def carlyle_portcos():
    url = "https://www.carlyle.com/portfolio"
    response = requests.get(url, headers=headers).text
    main(url)
    return response 


# Thoma Bravo
def thoma_portcos():
    url ="https://www.thomabravo.com/companies"
    response = requests.get(url, headers=headers).text
    return response


# Vista 
def vista_portcos():
    url = "https://www.vistaequitypartners.com/companies/portfolio/"
    
    # Vista uniquely has many follow on companies, which I want to add to the PortCo BaseModel
    class VistaPortco(Portco):
        follow_on: str | None = Field(None, "If a certain company gets acquired by another portfolio company, this is denoted by text like 'follow-on' or 'add-on' acquisition. In these cases, fill out the 'follow_on' field with the name of the acquiring portfolio company.")
    class VistaPortcos(BaseModel):
        companies: list[VistaPortco]
    schema = VistaPortcos.schema()

    # pre-process the HTML to eliminate unnecessary tags
    processed_html = process_html(url)

    # from ai_extract.py file. Chunk the document, then pass into LLM for extraction
    splits = chunk_html(processed_html)
    combined_chunks = []
    for chunk in splits:
        extracted_chunk = extract_html(chunk, schema)
        combined_chunks.append(extracted_chunk)
    
    with open("vista_portcos2.json", "w") as outfile:
       json.dump(combined_chunks, outfile, indent=2)


# New Mountain Capital
def new_mountain_portcos():
    url = "https://www.newmountaincapital.com/our-strategies/private-equity/portfolio/"
    schema = Portco.schema()
    
    # STEP 1: NMC doesn't provide details beyond URL links here. So clean up the HTML to isolate the URL links 
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    links = [] 
    for a in soup.main.find_all("a", href=True):
        links.append(a["href"])

    # STEP 2: Loop through each url, grab the HTML, and send it to the LLM for extraction
    portcos = []
    for link in links:
        processed_html = process_html(link) # only take the text within <body> tags
        json_output = extract_html(processed_html, schema)
        portcos.append(json_output)

    with open("nmc_portcos.json2", "w") as outfile:
        json.dump(portcos, outfile, indent=2)

# Platinum Equity Partners
def platinum_portcos():
    class PlatinumPortco(Portco):
        transaction_type: str | None = Field(None, description="E.g. Corporate Divestiture, Private Transaction, Private to Public, etc.")
    
    schema = PlatinumPortco.schema()
    
    #STEP 1: Process + scrape urls. Their HTML is split into 3 pages. And they only provide the URL links
    urls = [
    "https://www.platinumequity.com/our-companies/",
    "https://www.platinumequity.com/our-companies/?pagination=2",
    "https://www.platinumequity.com/our-companies/?pagination=3"
    ]
    
    links = [] 
    for url in urls:
        response = requests.get(url, headers=headers).text
        soup = BeautifulSoup(response, "html.parser")
        soup = soup.find("div", class_="companies-logo-section") # contained within the companies-logo-section
        
        for a in soup("a", href=True):
            links.append(a["href"])
    
    # STEP 2: Loop through each URL and extract the relevant fields
    portcos = []
    for link in links:
        processed_html = process_html(link)
        json_output = extract_html(processed_html, schema)
        portcos.append(json_output)
    
    with open("platinum_portcos2.json", "w") as outfile:
        json.dump(portcos, outfile, indent=2)

# American Securities
def american_securities_portcos():
    
    # Their portfolio page lists all the URLs. So we have to collect all the URLs, then scrape each company
    portfolio = "https://www.american-securities.com/en/companies/list"
    class AmsecPortco(Portco):
        exit_status: str | None = Field(None, description="Date and type of exit, if any. E.g. IPO in 2014, transferred to lenders in 2023, etc.")
    
    schema = AmsecPortco.schema()

    # STEP 1: Collect URLs 
    response = requests.get(portfolio, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    
    links = []
    for a in soup("a", class_=False, href=True):
        links.append(a["href"])

    # STEP 2: Loop through and scrape data
    urls = ["https://www.american-securities.com" + link for link in links]
    
    portcos = []
    for url in urls:
        processed_html = process_html(url)
        json_output = extract_html(processed_html, schema)
        portcos.append(json_output)

    with open("american_securities_portcos2.json", "w") as outfile:
         json.dump(portcos, outfile, indent=2)


# TODO: quality of this list is poor. Need to do better 
# Marlin Equities
def marlin_portcos():
    # Their portfolio page is super weird. 1 section contains company, desc, hq, and investment date. Then another section contains industry, status, and fund 
    
    url = "https://www.marlinequity.com/portfolio/"
    
    class MarlinPortco(Portco):
        fund: str | None = None
        region: str | None = None
        status_current: str | None = None
    
    class MarlinPortcos(BaseModel):
        companies: list[MarlinPortco]
    
    schema = MarlinPortcos.schema()

    # STEP 1: Just extract what we can from the first HTML section
    processed_html = process_html(url)
    json_output = extract_html(processed_html, schema)

    with open("marlin_portcos.json", "w") as outfile:
        json.dump(json_output, outfile, indent=2)


# TODO: Quality not great. Should re-run using GPT-4
# L Catterton
def lcatterton_portcos():
    portfolio = "https://www.lcatterton.com/Investments.html"
    Portco.PE_firm = "L Catterton"
     
    class LCatPortco(Portco):
        fund: str | None = Field(None, description="Must be one of: Flagship Buyout, Growth, Europe, Asia, Latin America, Real Estate, RMB")

    schema = LCatPortco.schema()

    # STEP 1: Collect URLs 
    response = requests.get(portfolio, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.find("div", class_="brands-holder")
    
    links = []
    for a in soup("a", href=True):
        name = a["href"].split('/')[-1]
        links.append("https://www.lcatterton.com/Investments-" + name + ".html")

    # STEP 2: Loop through URLs and extract data
    final_json = []
    for link in links:
        processed_html = process_html(link)
        json_output = extract_html(processed_html, schema)
        final_json.append(json_output)
        
    with open("lcat_portcos2.json", "w") as outfile:
        json.dump(final_json, outfile, indent=2)
