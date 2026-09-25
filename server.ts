import express from 'express';
import { createServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';
import duckdb from 'duckdb';
import axios from 'axios';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

const app = express();
app.use(express.json());

const HF_TOKEN = process.env.HF_TOKEN || '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';
const DATASET_REPO = 'Cyber-insight-309/paytm';

let cachedDatasetUrl: string | null = null;

// Initialize DuckDB
const db = new duckdb.Database(':memory:');
const conn = db.connect();

async function resolveDatasetUrl() {
  if (cachedDatasetUrl) return cachedDatasetUrl;
  try {
    const hfApiUrl = `https://huggingface.co/api/datasets/${DATASET_REPO}/parquet`;
    const response = await axios.get(hfApiUrl, {
      headers: (HF_TOKEN && HF_TOKEN !== 'hf_...') ? { Authorization: `Bearer ${HF_TOKEN}` } : {}
    });
    const configs = response.data;
    const firstConfig = Object.keys(configs)[0];
    const firstSplit = Object.keys(configs[firstConfig])[0];
    cachedDatasetUrl = configs[firstConfig][firstSplit][0];
    return cachedDatasetUrl;
  } catch (err) {
    console.error('Failed to resolve dataset URL:', err);
    return null;
  }
}

// Utility to run queries
const runQuery = (sql: string): Promise<any[]> => {
  return new Promise((resolve, reject) => {
    if (!conn) return reject(new Error('Database connection lost'));
    conn.all(sql, (err, res) => {
      if (err) {
        console.error('Query execution error:', err);
        reject(err);
      } else {
        resolve(res);
      }
    });
  });
};

// Install and load the httpfs extension for remote file access
async function initDuckDB() {
  try {
    console.log('Starting DuckDB initialization...');
    await runQuery('INSTALL httpfs;');
    await runQuery('LOAD httpfs;');
    
    if (HF_TOKEN && HF_TOKEN !== 'hf_...') {
      console.log('Creating HF secret...');
      await runQuery(`
        CREATE SECRET hf_secret (
          TYPE HTTP,
          EXTRA_HTTP_HEADERS MAP { 'Authorization': 'Bearer ${HF_TOKEN}' }
        );
      `);
    }
    
    const url = await resolveDatasetUrl();
    if (url) {
      console.log('DuckDB ready with dataset:', url);
    }
  } catch (err) {
    console.error('Failed to initialize DuckDB:', err);
  }
}

initDuckDB();

// Search API
app.post('/api/search', async (req, res) => {
  const { query, limit = 25, offset = 0 } = req.body;
  
  try {
    const url = await resolveDatasetUrl();
    if (!url) {
      throw new Error('Could not connect to Hugging Face dataset. Please check token/repo.');
    }

    let sql = `SELECT * FROM read_parquet('${url}')`;
    if (query) sql += ` WHERE ${query}`;
    sql += ` LIMIT ${limit} OFFSET ${offset}`;

    console.log('Running query:', sql);

    const startTime = Date.now();
    const rows = await runQuery(sql);
    const duration = Date.now() - startTime;

    // Total count query
    const countRes = await runQuery(`SELECT count(*) as total FROM read_parquet('${url}')`);
    const total = countRes[0]?.total || 0;

    res.json({
      rows,
      total,
      duration,
      columns: rows.length > 0 ? Object.keys(rows[0]) : []
    });
  } catch (err: any) {
    console.error('API Search error:', err);
    res.status(500).json({ error: err.message || 'Search failed' });
  }
});

async function startServer() {
  const isDev = process.env.NODE_ENV !== 'production';
  
  if (isDev) {
    const vite = await createServer({
      server: { middlewareMode: true },
      appType: 'custom',
    });
    app.use(vite.middlewares);
    app.use('*', async (req, res, next) => {
      const url = req.originalUrl;
      try {
        const fs = await import('fs');
        let template = fs.readFileSync(path.resolve(__dirname, 'index.html'), 'utf-8');
        template = await vite.transformIndexHtml(url, template);
        res.status(200).set({ 'Content-Type': 'text/html' }).end(template);
      } catch (e) {
        vite.ssrFixStacktrace(e as Error);
        next(e);
      }
    });
  } else {
    app.use(express.static(path.join(__dirname, 'dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.join(__dirname, 'dist', 'index.html'));
    });
  }

  const port = process.env.PORT || 3000;
  app.listen(port, () => {
    console.log(`Server started on port ${port}`);
  });
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
});
