# Paytm Mobile Search - Hugging Face Parquet Explorer (7.3M+ Rows)

Fast real-time mobile number search engine querying large Parquet datasets (7,345,462 rows) hosted on Hugging Face using embedded in-memory **DuckDB** and HTTP range requests.

---

## 🛠️ Kya-Kya Install Aur Configure Kiya Gaya Hai?

1. **`duckdb` (^1.4.4)**:
   - High-performance analytical database engine.
   - Pura 170MB file download karne ke bajaye **HTTP Range Requests (`httpfs`)** ke zariye sirf wahi data read karta hai jo query ke liye zaroori hai.
   - Private Hugging Face datasets ke liye `CREATE SECRET` ke zariye `Authorization: Bearer <TOKEN>` configure kiya gaya hai.
   - Numbers ko `CAST(mobile AS VARCHAR)` karke fast pattern match karta hai.

2. **`axios`**:
   - Hugging Face datasets API (`https://huggingface.co/api/datasets/.../parquet`) se direct parquet file URLs resolve karne ke liye.

3. **`express` & `tsx`**:
   - Node.js backend server (`server.ts`) jo frontend ke saath serve hota hai.
   - Port 3000 ya Render ke dynamic `PORT` env var par listen karta hai.

4. **Frontend UI (`React 19` + `Tailwind CSS 4` + `Lucide Icons`)**:
   - Simple, fast aur clean mobile number search interface.
   - Real-time result table with pagination.
   - Dataset repository aur token details user interface se completely hidden hain.

---

## 🚀 Render Par Host Karne Ka Step-by-Step Tarika

### Step 1: Code Ko GitHub Par Push Karein
Agar aapka code abhi tak GitHub par nahi hai:
1. GitHub par ek naya private ya public repository banayein.
2. Apne computer par project folder me terminal khol kar ye commands chalayein:
   ```bash
   git init
   git add .
   git commit -m "Paytm dataset explorer ready for Render"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
   git push -u origin main
   ```

---

### Step 2: Render Par Account Banayein
1. [https://render.com](https://render.com) par jayein aur login/signup karein (GitHub se connect kar sakte hain).

---

### Step 3: Naya Web Service Banayein
1. Render Dashboard me **"New +"** button par click karein aur **"Web Service"** chunein.
2. Apne GitHub repository ko select karein (e.g. `paytm-search`).

---

### Step 4: Settings Fill Karein

Render aapse basic settings poochega, ye exact values fill karein:

| Setting Field | Value |
|---|---|
| **Name** | `paytm-search` (ya jo aapko pasand ho) |
| **Language / Runtime** | `Node` |
| **Branch** | `main` |
| **Root Directory** | *(Khali chhod dein)* |
| **Build Command** | `npm install && npm run build` |
| **Start Command** | `npm start` |
| **Instance Type** | `Free` (0.5 CPU, 512 MB RAM) |

---

### Step 5: Environment Variables Add Karein (Sabse Zaroori)

Neeche **"Environment Variables"** section me jayein aur ye variables add karein:

1. **`HF_TOKEN`**
   - Value: `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` (Aapka Hugging Face Access Token)
2. **`NODE_VERSION`**
   - Value: `20.18.0`
3. **`NODE_ENV`**
   - Value: `production`

---

### Step 6: Deploy Par Click Karein
- **"Deploy Web Service"** button par click karein.
- Render automatically:
  1. Dependencies install karega (`npm install`)
  2. Vite frontend build karega (`npm run build`)
  3. Server start karega (`npm start`)
- 2-3 minute me aapko ek live URL mil jayega:
  `https://paytm-search-xxxx.onrender.com`

---

## ⚙️ Project Scripts

- `npm run dev`: Local development server chalu karne ke liye (`tsx server.ts`).
- `npm run build`: Production bundle (`dist/`) create karne ke liye.
- `npm start`: Production server start karne ke liye (`NODE_ENV=production tsx server.ts`).
