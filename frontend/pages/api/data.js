import { Pool } from 'pg';
import { OpenAI } from "openai";

const pool = new Pool({
  connectionString: process.env.DATABASE_STRING,
  ssl: {
    rejectUnauthorized: false
  }
});

// Generate embeddings function

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function generate_embeddings(query) {
  try {
    const response = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: query,
      encoding_format: "float",
    });
    // console.log("API response:", response);

    
    const output = response?.data[0]?.embedding; 
    if (!output) {
      throw new Error("No embedding found in response")
    }
    console.log(output)
    return output
  } catch (error) {
    console.error("Error in generating embeddings:", error);
  }
}


// function to define SQL query
export default async function handler(req, res) {
    const { firm, industry_stan, region_stan, status_current_stan, searchQuery } = req.query;
    
    let baseQuery = "SELECT firm, company_name, industry_stan, region_stan, fund, date_of_investment_stan, company_description, status_current_stan, website FROM portcos_test";
    let conditions = [];
    let params = [];

    // standard filters
    if (firm) {
      conditions.push(`firm = $${params.length + 1}`);
      params.push(firm);
    }

    if (industry_stan) {
      conditions.push(`industry_stan = $${params.length + 1}`);
      params.push(industry_stan);
    }

    if (region_stan) {
      conditions.push(`region_stan = $${params.length + 1}`);
      params.push(region_stan);
    }

    if (status_current_stan) {
      conditions.push(`status_current_stan = $${params.length + 1}`);
      params.push(status_current_stan);
    }
    
    if (conditions.length > 0) {
      baseQuery += " WHERE " + conditions.join(" AND ");
    }

    
    // If user inputs a searchQuery: Adjust the SQL query
    if (searchQuery) {
      let searchEmbedding = await generate_embeddings(searchQuery);
      // const numericEmbeddings = searchEmbedding.map(parseFloat);

      // let indexEmbedding = params.length + 1;
      baseQuery += ` ORDER BY embedding <-> ARRAY[${searchEmbedding}]::vector LIMIT 15`;
      // params.push(searchEmbedding);
      // console.log("Updated SQL query:", baseQuery)
      console.log("Conditions: ", conditions);
    }

    // call the SQL query
    try {
      const results = await pool.query(baseQuery, params);
      console.log("SQL query:", baseQuery, params);
      console.log("Conditions: ", conditions);
      
      res.status(200).json(results.rows);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
}

