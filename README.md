Vercel deployment: https://pe-ohxl91h2u-michael-yuans-projects.vercel.app/  
<br>

**Business Context:**  
A frequent "sourcing" exercise in Private Equity is monitoring your competitors' portfolios.   
There's often a handful of firms that are most directly competing with you on deals. Particularly if you're focused on a certain "theme", such as "DevSecOps" or "Supply Chain Software"  
By monitoring other portcos, you'll know (1) what your competitors are focused on, and (2) which assets may be coming up for sale soon.  
E.g. A typical PE investment is 3-5 years. So if Competitor A owns a DevSecOps company that is 4 years old, I know they are selling soon. I'd want to position myself for that sale ahead of time, so I'm in a better competitive position  
  
<br>

**Step 1: Scraping portcos**  
File: portcos.py and ai_extract.py

Tried 3 approaches here: 
1. Writing Beautifulsoup scripts myself to extract values from websites
2. Asking GPT-4 to extract key information, after passing a processed version of the raw HTML
3. Asking GPT-4 to write the Beautifulsoup code to do (1). This approach worked the best

4. [In the future] Ask GPT-4 to extract just the URL links from a website. Then, loop through each URL and extract the key fields.  

Note: Currently have 12 firms uploaded to the web app. Another 8 that are scraped but need some adjustments

<br>

**Step 2: Standardizing portcos**  
The web scraping outputs are JSON files (e.g. "tpg_portcos.json") stored in different folders. 
- _portcos_raw folder: Contains just the raw files
- _portcos_processed folder: Passed a manual review in order to standardize the files. I used file_cleanup.py to do some standardization tasks. E.g. Firm A might call it "name", Firm B might call it "company_name"  

I then used a LLM (most recently Claude Haiku or sometimes Sonnet) to standardize the files further. The problem is: Firm A may call an industry "Financial Services", Firm B calls it "Financials", Firm C calls it "Asset Management & Insurance"  
These need to be standardized to 1 label, "Financials", in order to be used as a filter by the user  
File: ai_validate_db.py contains this script  
- _portcos_gpt folder contains the LLM's answers
- _portcos_output folder contains the final consolidated outputs. I check every one manually, and sometimes have to correct hallucinations

<br>

**Step 3: Database + embeddings**  
Using a Postgres db hosted via Neon.tech (Nasr's suggestion!)  
File: db.py

There are currently ~2,000 companies in the db.  
This script uploads to the db and generates embeddings based on the company_description field.  
Note: In the future, I think I need to re-do the embeddings to capture other fields. For example, if a firm describes their sector as "Enterprise Software", that is relevant.  
Or, if they have a custom field called "transaction_type" and the label is "Corporate Divestiture", that's interesting.  
Or, in the future: Press release info  

<br>

**Step 4: Frontend**  
"frontend" folder contains the React / Next app  
Currently, it's just a database with filters + semantic search  
Upon loading, data is fetched from the PG database. If the user performs semantic search, the SQL query is run again, ordering results by vector similarity.   
If filters are selected, the API endpoint is not hit. The data array is just filtered on the client side  

I'm currently spending time improving the UI on the frontend using ShadCN.  

<br>

**Next steps: **
I'm really excited by the idea of enriching this db with press releases.  
Additionally, I think it'd be really cool to set up an agent loop: Imagine the user selects 100 companies and says "This is great. But now, my boss is asking me to highlight which of these companies are still founder-owned?" Or "Which of these were corporate divestitures?"  
That is a super common workflow, and it requires Googling every single company. It would be awesome if we could automate that using our database


