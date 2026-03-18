# Step-by-step: Host grocery app on Oracle Linux and prepare to sell

This guide takes you from zero to a **grocery best-deals app** running on your **Oracle Cloud Linux server**, then through the steps to **turn it into a product you can sell** (API, auth, payments, legal).

---

## Phase 1: Get your Oracle server running and reachable

### Step 1.1 – Create the server (if you don’t have one)

Follow **`docs/ORACLE_AND_INSTAGRAM_POSTER_SETUP.md`** (Part 1 only):

1. Sign up at [Oracle Cloud Free](https://www.oracle.com/cloud/free/).
2. Create a VM: Ubuntu 22.04, shape **VM.Standard.E2.1.Micro** (Always Free).
3. Open **port 22** (SSH) and **port 80** (HTTP) and **port 443** (HTTPS) in the VCN **Security List** → Ingress rules:
   - TCP 22, 0.0.0.0/0  
   - TCP 80, 0.0.0.0/0  
   - TCP 443, 0.0.0.0/0  
4. Save your **private key** and note the instance **public IP**.

### Step 1.2 – SSH into the server

From your PC (PowerShell):

```powershell
ssh -i "C:\path\to\your-private-key.key" ubuntu@YOUR_PUBLIC_IP
```

If SSH times out: check the security list (ports 22, 80, 443), confirm the instance is **Running**, and that you’re using the correct key and IP. Once you see `ubuntu@...:~$`, continue.

### Step 1.3 – Install basics on the server

On the server (SSH session):

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx
```

---

## Phase 2: Deploy the grocery app on Oracle

### Step 2.1 – Copy the app to the server

**Option A – From your PC (if you have the project on your machine)**  
In PowerShell (from a folder that contains your private key and the project):

```powershell
scp -i "C:\path\to\your-private-key.key" -r "c:\My Website\grocery-api" ubuntu@YOUR_PUBLIC_IP:~/
```

**Option B – Using Git (if the project is in a repo)**  
On the server:

```bash
# If your repo is public or you use deploy keys:
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
# Then copy or symlink the grocery-api folder to ~/grocery-api (or adjust paths below)
```

### Step 2.2 – Set up Python and env on the server

On the server:

```bash
cd ~/grocery-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set your RapidAPI key (replace with your real key):

```bash
export RAPIDAPI_KEY="your_rapidapi_key_here"
```

To make it permanent, add that line to `~/.bashrc` or use a small script that exports it and then runs the app (see Step 2.5).

### Step 2.3 – Test the price script and cron

```bash
cd ~/grocery-api && source venv/bin/activate && python compare_prices.py
```

Check that `best_deals_YYYY-MM-DD.json` is created. Then schedule it daily:

```bash
crontab -e
```

Add (one line):

```text
0 6 * * * cd /home/ubuntu/grocery-api && /home/ubuntu/grocery-api/venv/bin/python compare_prices.py
```

(If you set `RAPIDAPI_KEY` in `~/.bashrc`, cron may not load it; then use a wrapper script that exports `RAPIDAPI_KEY` and runs `compare_prices.py`.)

### Step 2.4 – Run the web API (Flask + Gunicorn)

From `~/grocery-api` with venv active:

```bash
gunicorn -w 1 -b 0.0.0.0:5000 app:app
```

From your PC browser open: `http://YOUR_PUBLIC_IP:5000/api/deals`  
You should see JSON (best deals). Stop with Ctrl+C once confirmed.

### Step 2.5 – Run the API as a service (so it survives reboot)

Create a systemd unit:

```bash
sudo nano /etc/systemd/system/grocery-app.service
```

Paste (adjust paths if your app is elsewhere):

```ini
[Unit]
Description=Grocery best-deals API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/grocery-api
Environment="RAPIDAPI_KEY=your_rapidapi_key_here"
Environment="PATH=/home/ubuntu/grocery-api/venv/bin"
ExecStart=/home/ubuntu/grocery-api/venv/bin/gunicorn -w 1 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Replace `your_rapidapi_key_here` with your real key. Save (Ctrl+O, Enter, Ctrl+X). Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable grocery-app
sudo systemctl start grocery-app
sudo systemctl status grocery-app
```

### Step 2.6 – Put Nginx in front (reverse proxy + optional SSL later)

```bash
sudo nano /etc/nginx/sites-available/grocery-app
```

Paste (replace `YOUR_PUBLIC_IP` with your server IP or, later, your domain):

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/grocery-app /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Visit **http://YOUR_PUBLIC_IP/api/deals** – you should get the same JSON. The app is now **hosted on Oracle Linux**.

---

## Phase 3: Turn it into an app you can sell

### Step 3.1 – Add a simple frontend (optional but good for selling)

- Build a small **web app** (e.g. React, Vue, or plain HTML/JS) that calls `GET /api/deals` and shows “Best deals today” with a clear disclaimer.
- Host the frontend: either on the **same Oracle server** (Nginx serves static files or a build) or on **Vercel/Netlify** pointing to your Oracle API.
- This gives you something visible to show and sell (e.g. “See where each item is cheapest”).

### Step 3.2 – Add user accounts (auth)

To sell access you need **who is logged in** and **who has a valid subscription**.

- **Option A – Backend auth (recommended)**  
  Add **Flask-Login** or **JWT** (e.g. PyJWT): signup, login, logout; protect `/api/deals` (or a “premium” endpoint) so only logged-in or subscribed users get data.
- **Option B – Third-party**  
  Use **Firebase Auth**, **Auth0**, or **Supabase** and validate tokens in your Flask app.

Implementation steps:

1. Add a **User** model (e.g. SQLite or Postgres: email, password hash, plan).
2. Endpoints: `POST /api/register`, `POST /api/login` (return JWT or session).
3. Middleware: for paid routes, check JWT/session and that the user’s plan is active.

### Step 3.3 – Add payments (subscriptions)

To **charge** customers:

1. **Stripe** (recommended): create a Stripe account, add **Stripe** to your app (`pip install stripe`), create Products/Prices for “Monthly” and “Yearly”.
2. Endpoints:
   - `POST /api/create-checkout-session` → redirect user to Stripe Checkout.
   - `POST /api/webhook` (Stripe webhook) → on `checkout.session.completed` or `customer.subscription.updated`, set the user’s plan in your DB.
3. When serving `/api/deals`, check if the user has an active subscription; if not, return 402 or a “Subscribe” message.

### Step 3.4 – Legal and disclaimers (required for selling)

- **Terms of Service** – What the app does, acceptable use, no guarantee of price accuracy.
- **Privacy Policy** – What data you collect (email, payment), how you use it, where it’s stored.
- **Disclaimer** – e.g. “Prices are approximate and from third-party sources; always confirm at the store.”
- **Refund policy** – Under what conditions you refund (e.g. within 14 days, no refund after download/access).

Add these as pages or links in the app and in the checkout flow. If you sell in South Africa, consider POPIA and any consumer-law requirements.

### Step 3.5 – Domain and HTTPS (recommended for a commercial app)

1. Buy a **domain** (e.g. from Freenom, Namecheap, or your registrar).
2. Point the domain **A record** to your Oracle instance **public IP**.
3. On the server, install **Certbot** and get a free SSL cert:
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo nano /etc/nginx/sites-available/grocery-app
   ```
   Set `server_name yourdomain.com;` then:
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```
4. Your app is then served over **https://yourdomain.com** and looks professional for paying users.

---

## Quick checklist (summary)

| Phase | Step | Done |
|-------|------|------|
| 1 | Oracle server created, SSH works, ports 22/80/443 open | ☐ |
| 1 | Python, pip, venv, Nginx installed on server | ☐ |
| 2 | App copied to server; venv + `pip install -r requirements.txt` | ☐ |
| 2 | `RAPIDAPI_KEY` set; `compare_prices.py` runs and creates JSON | ☐ |
| 2 | Cron runs `compare_prices.py` daily | ☐ |
| 2 | `gunicorn` runs `app:app`; systemd service + Nginx reverse proxy | ☐ |
| 2 | **http://YOUR_IP/api/deals** returns JSON → **Hosted on Oracle** | ☐ |
| 3 | Frontend (web or mobile) that uses `/api/deals` | ☐ |
| 3 | User auth (signup/login, JWT or sessions) | ☐ |
| 3 | Stripe (or other) subscriptions; webhook updates user plan | ☐ |
| 3 | Terms, Privacy, Disclaimer, Refund policy | ☐ |
| 3 | Domain + HTTPS (Certbot) | ☐ |

Once all are done, you have a **grocery best-deals app hosted on Linux Oracle** and the core of a **sellable product** (auth + payments + legal). You can then add more features (alerts, favourites, more stores) and market it.
