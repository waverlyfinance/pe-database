import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_STRING,
  ssl: {
    rejectUnauthorized: false
  }
});

export default async function handler(req, res) {
    const { firm, industry, region, fund, status_current } = req.query;
    
    let baseQuery = "SELECT * FROM portcos_test";
    let conditions = [];
    let params = [];

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

    try {
      const results = await pool.query(baseQuery, params);
      res.status(200).json(results.rows);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
}