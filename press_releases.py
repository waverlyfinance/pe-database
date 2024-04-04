from ai_extract import *
import os
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup

headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"} 

# Vista
def vista_pr(): 
    pr_url = "https://www.thomabravo.com/press-releases"
    pr_response = requests.get(pr_url, headers=headers)
    soup = BeautifulSoup(pr_response.text, "html.parser")
    pr_html = soup.body.find_all("a", class_="post-detail-link")


   
    pr_html_test = "https://www.thomabravo.com/press-releases/hcss-to-be-acquired-by-thoma-bravo"
    response = requests.get(pr_html_test, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    body_text = soup.body.get_text(separator = " ", strip=True)

extract_pr(body_text)



