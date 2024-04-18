import { Pool } from 'pg';
import OpenAI from "openai";

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

    console.log("API response:", response);

    // check if embeddings are available in the response
    if (response.data && response.data.embeddings.length > 0) {
      const output = response.data.embeddings[0].embedding; 
      console.log("Embeddings output:", output);
      console.log(output);
      return output
    } else {
      console.error("No embeddings returned", query);
    }
  } catch (error) {
    console.error("Error in generating embeddings:", error);
  }
}

generate_embeddings("Testing testing. I am testing!")


// function to define SQL query
export default async function handler(req, res) {
    const { firm, industry, region, fund, status_current, searchQuery } = req.query;
    
    let baseQuery = "SELECT * FROM portcos_test";
    let conditions = [];
    let params = [];

    // standard filters
    if (firm) {
      conditions.push("firm = $1");
      params.push(firm);
    }

    if (industry) {
      conditions.push("industry = $2");
      params.push(industry);
    }

    if (region) {
      conditions.push("region = $3");
      params.push(region);
    }

    if (fund) {
      conditions.push("fund = $4");
      params.push(fund);
    }

    if (status_current) {
      conditions.push("status_current = $5");
      params.push(status_current);
    }
    
    if (conditions.length > 0) {
      baseQuery =+ " WHERE " + conditions.join(" AND ");
    }

    
    // If user inputs a searchQuery: Adjust the SQL query
    if (searchQuery) {
      const searchEmbedding = await generate_embeddings(searchQuery);
      baseQuery += `ORDER BY embedding <-> $6::float8[] LIMIT 15`
      console.log("Search query: ", searchQuery);
      params.push(searchEmbedding);
    }

    // call the SQL query
    try {
      const results = await pool.query(baseQuery, params);
      console.log(baseQuery, params);
      
      res.status(200).json(results.rows);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
}

