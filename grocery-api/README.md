# Grocery price comparison (API + optional crowdsourcing)

Uses **iGrosa** (or similar) via **RapidAPI** to get SA store prices, then saves the best deal per item to a JSON file. Optional SQLite DB for crowdsourced prices to fill gaps.

## 1. Get an API key

1. Sign up at [RapidAPI](https://rapidapi.com).
2. Find and subscribe to **iGrosa** (or the grocery API you want).
3. Copy your RapidAPI key from the dashboard.

## 2. Set the key (don’t commit it)

**Option A – Environment variable (recommended)**  
In PowerShell (current session only):

```powershell
$env:RAPIDAPI_KEY = "your_actual_key_here"
```

Or: Windows **System Properties → Environment Variables** → add `RAPIDAPI_KEY` for your user.

**Option B – .env file**  
Copy `.env.example` to `.env`, put your key in `.env`, and load it before running (e.g. `pip install python-dotenv` and add `from dotenv import load_dotenv; load_dotenv(SCRIPT_DIR / ".env")` at the top of the script). Do **not** commit `.env`.

## 3. Install and run

```powershell
cd "c:\My Website\grocery-api"
pip install -r requirements.txt
python compare_prices.py
```

Output: `best_deals_YYYY-MM-DD.json` in the same folder. If the API params/response differ from the script, adjust `API_ENDPOINT` and the parsing in `get_price()` to match [iGrosa’s RapidAPI docs](https://rapidapi.com).

## 4. Optional: crowdsourcing

- **Add a price:** `add_crowdsourced_price("white bread 700g", "Pick n Pay", 14.50, "user123")`
- The script already uses `get_crowdsourced_price()` to fill missing API results with the last 24h average from `grocery_prices.db`.
- For a real app: expose a small Flask/FastAPI endpoint where users POST `item`, `store`, `price` (with auth) and call `add_crowdsourced_price()`.

## 5. Run daily (cron on server)

```text
0 6 * * * /usr/bin/python3 /path/to/grocery-api/compare_prices.py
```

Set `RAPIDAPI_KEY` in the server environment (e.g. in crontab or in a small wrapper script that exports it then runs the script).

## 6. Host on Oracle Linux and sell the app

- **API:** Run `gunicorn -w 1 -b 0.0.0.0:5000 app:app` (or use the systemd + Nginx steps in the doc).
- **Step-by-step (Oracle + auth + payments + legal):** See **`docs/GROCERY_APP_ORACLE_HOST_AND_SELL.md`** for full instructions: deploy on Oracle, add auth, Stripe, domain/HTTPS, and disclaimers so you can sell the app.

## Notes

- API response shape may differ; adapt the `data["price"]` parsing in `get_price()` to the real response.
- Watch RapidAPI usage/costs; reduce `items` or call frequency if needed.
- Disclaim in your app: “Prices approximate; sourced from third-party APIs and/or user inputs.”
