from ai_extract import *
import os
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
import time

headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"} 


# pre-process html. OPTION 1: Extract ONLY the classes, links, and text
def process_html_classes(url, scrape_id):
    try:
        response = requests.get(url, headers=headers).text
    except requests.exceptions.RequestException as error:
        print(f"error fetching data: {error}")
    
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
    
    # transform into string, so it can be passed to a LLM
    processed_html = ", ".join(str(item) for item in clean_html)

    # print(processed_html)
    return processed_html

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
    output = []

    for node in nodes:
        company = {
            "company_name": node["title"],
            "id": node["id"],
            "company_description": node["content"].strip("\n"),
            "region": node["geography"]["nodes"][0]["name"] if node["geography"]["nodes"] else None,
            "fund": node["product"]["nodes"][0]["name"] if node["product"]["nodes"] else None,
            "industry": node["sector"]["nodes"][0]["name"] if node["sector"]["nodes"] else None,
            "status_current": node["status"].get("nodes")[0]["name"] if node["status"]["nodes"] else None,
        }
        output.append(company)
    print(output)
    
    # export the results into a JSON file
    with open("_portcos_raw/tpg_portcos.json", "w") as outfile:
        json.dump(output, outfile, indent=2)

    return output

    # need to run update_keys function to the output (from file_cleanup file)

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

    updated_data = []

    for company in combined_results:

        updated_company = {
            "company_name": company["name"],
            "company_description": company["description"],
            "date_of_investment": company["yoi"] if company["yoi"] is not None else None,
            "country": company["country"] if company["country"] is not None else None,
            "region": company["region"] if company["region"] is not None else None,
            "fund": company["assetClass"] if company["assetClass"] is not None else None,
            "hq": company["hq"] if company["hq"] is not None else None,
            "industry": company["industry"] if company["industry"] is not None else None,
            "website": company["url"] if company["url"] is not None else None,
        }
        
        updated_data.append(updated_company)

    with open("_portcos_raw/kkr_portcos.json", "w") as outfile:
        json.dump(updated_data, outfile, indent=2)

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

# TODO: Looks like quality is a bit low. Should redo
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

# TODO: Need to finish this later
def flexpoint_portcos():
    url = "https://flexpointford.com/investments/"
    scrape_id = "body"

    processed_html = process_html_classes(url, scrape_id)
    print(processed_html)

    # schema = identify_schema(processed_html)

    # json_output = extract_html(processed_html, schema)

    # with open("flexpoint_portcos.json", "w") as outfile:
    #     json.dump(json_output, outfile, indent=2)

# flexpoint_portcos()


def clearlake_portcos():
    url = "https://clearlake.com/portfolio/"
    
    # grab all URLs
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.find("div", id="js-grid-lightbox-gallery")

    links = []
    for a in soup("a", href=True):
        links.append(a["href"])

    # take first URL, and identify the schema
    processed_html = process_html_classes(links[0], "body")
    schema = identify_schema(processed_html)
    
    # loop through each URL, and extract the relevant data 
    portcos = []
    for link in links:
        processed_html = process_html_classes(link, "body")
        json_output = extract_html(processed_html, schema)
        portcos.append(json_output)

    with open("clearlake_portcos2.json", "w") as outfile:
        json.dump(portcos, outfile, indent=2)


# Use GPT-4 to write the scraping code for me:
def clearlake_portcos_test():
    url = "https://clearlake.com/portfolio/"
    
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.find("body")

    portfolio_companies = []

    # Iterate over each portfolio item
    for item in soup.select('.cbp-item'):
        company_info = {
            'company_name': '',
            'industry': '',
            'status_current': '',
            'website': ''
        }
    
        # Extract company name
        company_name = item.select_one('.cbp-caption-image img')
        if company_name and company_name.has_attr('alt'):
            company_info['company_name'] = company_name['alt'].upper().replace("”", "")
        
        # Industry and current status are embedded within the class names of '.cbp-item'
        class_list = item.get('class', [])
        if 'Software' in class_list:
            company_info['industry'] = 'Software & Technology'
        elif 'Energy' in class_list:
            company_info['industry'] = 'Energy & Industrials'
        elif 'Food' in class_list:
            company_info['industry'] = 'Food & Consumer Services'
        
        if 'Current' in class_list:
            company_info['status_current'] = 'Current Investment'
        elif 'Prior' in class_list:
            company_info['status_current'] = 'Prior Investment'
        
        # Extract company detail page URL
        company_page = item.select_one('a.cbp-caption')
        if company_page and company_page.has_attr('href'):
            company_info['website'] = company_page['href']
        
        # Add the extracted info to the list
        portfolio_companies.append(company_info)

    # Assuming you would like to print or use the extracted data
    for company in portfolio_companies:
        print(company)


def hig_portcos():
    url = "https://hig.com/portfolio/?status=active"
    
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.find("body")

    portcos = []

    # GPT-4 generated the following code: 
    # Iterate over each portfolio item in the HTML file (where the relevant details are)
    for item in soup.select('.portfolio--item'):
        company_info = {
            'company_name': None,
            'company_description': None,
            'industry': None,
            'region': None,
            'status_current': None,
            'website': None,
            'fund': None
        }
        
        # Extract company name
        company_name = item.select_one('h4')
        if company_name:
            company_info['company_name'] = company_name.text.strip()
        
        # Extract company description
        company_description = item.select_one('.portfolio--item-content > p:nth-of-type(1)')
        if company_description:
            company_info['company_description'] = company_description.text.encode().decode("unicode-escape")
        
        # Website URL
        website = item.select_one('a.portfolio--item-link')
        if website and website.has_attr('href'):
            company_info['website'] = website['href']
        
        # Sector, Region, Status, and Fund are contained within the class list
        class_list = item['class']
        industries = ['business-services', 'chemicals', 'consumer-retail', 'healthcare', 'industrials', 'technology-media-and-telecom']
        regions = ['north-america', 'europe', 'latin-america']
        statuses = ['active', 'realized']
        funds = ['private-equity-united-states', 'private-equity-europe', 'private-equity-latin-america', 'growth', 'infrastructure', 'biohealth']
        
        # Extract fund
        company_info['fund'] = next((fund for fund in funds if fund in class_list), None)

        # Extract sector
        company_info['industry'] = next((industry for industry in industries if industry in class_list), None)
        
        # Extract region
        company_info['region'] = next((region for region in regions if region in class_list), None)
        
        # Extract status
        company_info['status'] = next((status for status in statuses if status in class_list), None)
        
        portcos.append(company_info)

    # STEP 2: Loop through each individual website, and extract the investment date (missing from HTML from previous step)

    urls = [portco.get("website") for portco in portcos]

    for url in urls:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        soup = soup.find("div", class_="wrap", role="document")
        soup = soup.find("strong", string="Invested") 
        if soup:
            date_of_investment = soup.find_next("span").text.strip() 
        else: 
            date_of_investment = None
        time.sleep(1)

        for portco in portcos:
            portco.update({"date_of_investment": date_of_investment})
    
    print(portcos)

    with open("_portcos_raw/hig_portcos.json", "w") as outfile:
        json.dump(portcos, outfile, indent=2)

# NOTE: Court Square uses Javascript to render the actual content, so would need Puppeteer or Selenium to actually scrape the detailed content
def courtsquare_portcos():
    url = "https://www.courtsquare.com/portfolio/"
    firm = "Court Square"
    
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.find("body")

    # Find all portfolio items
    portfolio_items = soup.find_all('div', class_='portfolio_tile--outer')

    portcos = []

    for item in portfolio_items:
        portco = {}
        
        # Extract the link to the company's detailed profile
        link_tag = item.find('a', class_='base_link')
        if link_tag:
            portco['website'] = "www.courtsquare.com" + link_tag.get('href')

        # Extract the company name
        name_tag = item.find('h2', class_='typo_header')
        if name_tag:
            portco['company_name'] = name_tag.get_text(strip=True)
        
        # Extract the industry (sector)
        sector_tag = item.find('span', class_='portfolio_tile--sector_item')
        if sector_tag:
            portco['industry'] = sector_tag.get_text(strip=True)
        
        portco["firm"] = firm

        portcos.append(portco)

    # Printing the result
    print(portcos)


    with open("_portcos_raw/courtsquare_portcos.json", "w") as file:
        json.dump(portcos, file, indent=2)


def charlesbank_portcos():
    url = "https://www.charlesbank.com/portfolio/portfolio-list/"
    firm = "Charlesbank"
    
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.find("body")

    # Step 1: Extract URLs for each company from the total portfolio page
    urls = [] 
    
    total_links = soup.select('#investment-list p a')

    for link in total_links:
        url = link.get("href")
        urls.append(url)

    # Step 2: Loop through each URL and then extract the relevant fields 
    portcos = []
    
    for url in urls:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        soup = soup.find("body")
        
        portco = {}

        company_name = soup.find('h1').text.strip() if soup.find('h1') else None
        company_description = soup.find(string="Business").find_next('p').text.strip() if soup.find(string="Business") else None
        date_of_investment = soup.find(string="Year of Investment:").find_next('p').text if soup.find(string="Year of Investment:") else None
        fund = soup.find(string="Strategy").find_next('p').text if soup.find(string="Strategy") else None
        industry = soup.find(string="Industry").find_next('p').text.strip() if soup.find(string="Industry") else None
        headquarters = soup.find(string="Headquarters").find_next('p').text.strip() if soup.find(string="Headquarters") else None
        status_current = soup.find(string="Status").find_next('p').text.strip() if soup.find(string="Status") else None
        website = soup.find(string="Website").find_next('a')['href'] if soup.find(string="Website") else None
        ceo = soup.find(string="CEO").find_next('p').text.strip() if soup.find(string="CEO") else None
        employees = soup.find(string="Employees").find_next('p').text.strip() if soup.find(string="Employees") else None

        portco.update({
            "company_name": company_name, 
            "company_description": company_description,
            "date_of_investment": date_of_investment, 
            "fund": fund, 
            "industry": industry, 
            "headquarters": headquarters, 
            "status_current": status_current, 
            "website": website, 
            "ceo": ceo, 
            "employees": employees,
            "firm": firm
            })
        
        portcos.append(portco)

    # output into a file
    with open("_portcos_raw/charlesbank_portcos.json", "w") as file:
        json.dump(portcos, file, indent=2)


def kelso_portcos():
    url = "https://www.kelso.com/investments"
    firm = "Kelso"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    soup = soup.find("body")

    # Step 1: Extract URLs for each company from the total portfolio page
    urls = [] 

    links = soup.find_all('div', class_='kelso-investment-image')
    
    for a in links:
        if a.find("a"):
            url = "https://www.kelso.com" + a.find("a").get("href")
            urls.append(url)
        else:
            None
    
    # Step 2: Loop through each company and extract the data
    portcos = []
    
    for url in urls:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        soup = soup.find("body")
        
        portco = {}

        company_name = soup.find('h1', class_='kelso-investment-company-name').text.strip()
        company_description = soup.find('p', class_='kelso-investment-company-description').text.strip()
        
        # Extracting other details which are inside labels
        details = soup.find('div', class_='kelso-investment-company-data')
        
        # Extracting details from labeled sections
        labels = soup.find_all('label')
        details = {label.text.strip(' :'): label.find_next_sibling('span').text.strip() for label in labels if label.find_next_sibling('span')}

        date_of_investment = details.get('Investment Date')
        industry = details.get('Sector')
        headquarters = details.get('Headquarters')
        status = details.get('Status')

        # Compile all extracted data into a dictionary
        portco.update({
            "company_name": company_name, 
            "company_description": company_description,
            "date_of_investment": date_of_investment, 
            "industry": industry, 
            "region": headquarters, 
            "status": status,
            "firm": firm
        })
    
        portcos.append(portco)

    # delete duplicates 
    unique_portcos = []
    seen = set()

    for portco in portcos:
        # Create a tuple of the dictionary values
        identifier = tuple(portco.items())
        if identifier not in seen:
            seen.add(identifier)
            unique_portcos.append(portco)
    print(unique_portcos)
        
    # output into a file
    with open("_portcos_raw/kelso_portcos2.json", "w") as file:
        json.dump(unique_portcos, file, indent=2)

def abry_portcos():
    url = "https://abry.com/companies/"
    firm = "Abry"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    soup = soup.find("body")

    # Step 1: Extract URLs for each company from the total portfolio page
    company_links = soup.select(".company-grid a")
    urls = []

    for link in company_links: 
        if 'href' in link.attrs:
            urls.append(link['href'])
        else:
            None

    # Step 2: Loop through each company and extract the data
    portcos = []
    
    for url in urls:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        soup = soup.find("body")
        
        portco = {}

        company_name = soup.find('h1').text if soup.find('h1') else None
        company_description = soup.find('div', class_='summary').p.text if soup.find('div', class_='summary') else None
        details = {li.strong.text.strip(':'): li.span.text for li in soup.find_all('li') if li.strong and li.span}

        # Extracted details
        status_current = details.get('Status')
        industry = details.get('Sector')
        date_of_investment = details.get('Investment Year')
        hq = details.get('Headquarters')
        fund = details.get('Fund')
        website = details.get("Website")


        # Compile all extracted data into a dictionary
        portco.update({
            "company_name": company_name, 
            "company_description": company_description,
            "date_of_investment": date_of_investment, 
            "industry": industry, 
            "hq": hq, 
            "status_current": status_current,
            "website": website,
            "firm": firm
        })
    
        portcos.append(portco)

    # output into a file
    with open("_portcos_raw/abry_portcos.json", "w") as file:
        json.dump(portcos, file, indent=2)

# TODO: Need Selenium or Puppeteer? HTML missing many companies
def stonepoint_portcos():
    url = "https://www.stonepoint.com/private-equity/companies/"
    firm = "Stone Point"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    soup = soup.find("body")

    # Step 1: Extract URLs for each company from the total portfolio page
    company_links = soup.find_all('a', href=True)
    urls = []

    for link in company_links: 
        href = link['href']
        # Filter out any links that do not lead to specific company pages or irrelevant links
        if 'company' in href:
            urls.append(href)

    # the following companies are somehow missing from the HTML. Maybe Javascript rendering?? Adding manually below.  
    urls.extend([
        "https://www.stonepoint.com/company/businessolver/",
        "https://www.stonepoint.com/company/citco/",
        "https://www.stonepoint.com/company/clearpoint-health/",
        "https://www.stonepoint.com/company/crea/",
        "https://www.stonepoint.com/company/cross-ocean-partners/",
        "https://www.stonepoint.com/company/dmg-bancshares/",
        "https://www.stonepoint.com/company/everbank/",
        "https://www.stonepoint.com/company/hyphen-solutions/",
        "https://www.stonepoint.com/company/ieq-capital/",
        "https://www.stonepoint.com/company/lincoln-property-company/",
        "https://www.stonepoint.com/company/lone-wolf-technologies/",
        "https://www.stonepoint.com/company/onboard-partners/",
        "https://www.stonepoint.com/company/prima-capital-advisors/",
        "https://www.stonepoint.com/company/prismhr/",
        "https://www.stonepoint.com/company/private-client-select-insurance-services/",
        "https://www.stonepoint.com/company/sabal-capital-holdings/",
        "https://www.stonepoint.com/company/sambasafety/",
        "https://www.stonepoint.com/company/sunfire/",
        "https://www.stonepoint.com/company/ten-x/",
        "https://www.stonepoint.com/company/tree-line-capital/",
        "https://www.stonepoint.com/company/truist-insurance-holdings/",
        "https://www.stonepoint.com/company/verisys/",
        "https://www.stonepoint.com/company/vervent/",
    ])

    # Step 2: 
    portcos = []

    for url in urls:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        soup = soup.find("body")
        
        portco = {}

        # Locate the container that holds the informati
        company_container = soup.find('div', class_='company-modal')
        company_name = company_container.find('h2', class_='company-modal-title').text if company_container.find('h2', class_='company-modal-title') else None
        
        details = {item.text.split(':')[0]: item.find('span').text.strip() for item in company_container.find_all('li') if ':' in item.text}
        date_of_investment = details.get('Investment Year')
        hq = details.get('HQ')
        status_current = details.get('Status')
        website = company_container.find('a', class_='company-modal-link')['href'] if company_container.find('a', class_='company-modal-link') else None
     
        #company description
        paragraphs = company_container.find_all('p')[:2] if company_container.find('div', class_='markdown-content') else None
        company_description = ' '.join(p.get_text(strip=True) for p in paragraphs)

        # industry extraction
        sector_div = company_container.find('h4', class_='company-modal-detail-title', string='Sector(s)')
        if sector_div:
            sector_list = sector_div.find_next_sibling('ul')
            industry = ', '.join([li.text.strip() for li in sector_list.find_all('li')]) if sector_list else None
        else:
            industry = None

        portco = {
            "company_name": company_name,
            "company_description": company_description,
            "date_of_investment": date_of_investment,
            "industry": industry,
            "hq": hq,
            "status_current": status_current,
            "website": website,
            "firm": firm
        }

        # Append the dictionary to the list
        portcos.append(portco)

    # output into a file
    with open("_portcos_raw/stonepoint_portcos.json", "w") as file:
        json.dump(portcos, file, indent=2)


