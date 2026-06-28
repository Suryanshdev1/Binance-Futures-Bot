# 🌐 Web Demo

This folder contains a web wrapper around the existing CLI trading bot.  
The original `cli.py` and `bot/` package remain completely untouched.

## 📁 Structure

```
web_demo/
├── app.py              # Streamlit web interface (RECOMMENDED)
├── api.py              # FastAPI REST API (alternative)
└── requirements.txt    # Extra dependencies for web deployment
```

---

## 🚀 Option A: Streamlit (Recommended for Demos)

### Local Run

```bash
# From project root
pip install -r web_demo/requirements.txt
streamlit run web_demo/app.py
```

Open `http://localhost:8501` in your browser.

### What You Get
- Clean web form to place orders
- Real-time validation
- Order history table
- No terminal needed

---

## 🚀 Option B: FastAPI (For API/Portfolio)

### Local Run

```bash
# From project root
pip install -r web_demo/requirements.txt
uvicorn web_demo.api:app --reload --port 8000
```

Open `http://localhost:8000/docs` for interactive Swagger UI.

### Example API Call

```bash
curl -X POST "http://localhost:8000/order" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 0.001
  }'
```

---

## 🌍 Deploy to Render (Free)

### Step 1: Add Files to Your Repo

Copy these files from this folder into your main project:

```
├── web_demo/              (this folder)
├── render.yaml            (from the root output)
├── requirements.txt       (your existing one)
└── .env.example           (your existing one)
```

### Step 2: Push to GitHub

```bash
git add web_demo/ render.yaml
git commit -m "Add web demo wrapper"
git push origin main
```

### Step 3: Connect to Render

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **New +** → **Blueprint**
3. Select your repo
4. Render reads `render.yaml` and creates the service automatically
5. Go to **Environment** tab → Add your `.env` variables:
   - `BINANCE_API_KEY`
   - `BINANCE_SECRET_KEY`
6. Click **Deploy**

Your site will be live at: `https://binance-bot-streamlit.onrender.com`

---

## 🚂 Deploy to Railway (Free Tier)

### Step 1: Add Files to Your Repo

Copy these files from this folder into your main project:

```
├── web_demo/              (this folder)
├── railway.json           (from the root output)
├── Dockerfile             (optional, from the root output)
├── requirements.txt       (your existing one)
└── .env.example           (your existing one)
```

### Step 2: Push to GitHub

```bash
git add web_demo/ railway.json
git commit -m "Add web demo for Railway deploy"
git push origin main
```

### Step 3: Connect to Railway

1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repo
4. Railway auto-detects `railway.json`
5. Go to **Variables** tab → Add:
   - `BINANCE_API_KEY`
   - `BINANCE_SECRET_KEY`
6. Click **Deploy**

Your site will be live at: `https://your-project.up.railway.app`

---

## ⚠️ Important Security Notes

1. **Never commit `.env`** — it is already in `.gitignore`
2. **Set API keys in the platform dashboard**, not in code
3. **This is Testnet only** — no real money is at risk
4. **The CLI version (`cli.py`) still works exactly as before** — nothing was changed

---

## 🔄 Switching Between Streamlit and FastAPI

| Platform | Streamlit Command | FastAPI Command |
|----------|-------------------|-----------------|
| Local | `streamlit run web_demo/app.py` | `uvicorn web_demo.api:app --reload` |
| Render | `streamlit run web_demo/app.py --server.port $PORT` | `uvicorn web_demo.api:app --host 0.0.0.0 --port $PORT` |
| Railway | Same as above | Same as above |

Just update the `startCommand` in `render.yaml` or `railway.json` to switch.
