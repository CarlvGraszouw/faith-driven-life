# Full walkthrough: Grocery app on Oracle → app you can sell

Follow this **from top to bottom**. Do one section, check the “You’re done when…” line, then move to the next. Replace any placeholders (e.g. `YOUR_PUBLIC_IP`, paths to your key) with your real values.

---

## Before you start

- You need: a **RapidAPI** account and an **iGrosa** (or similar) API key for grocery prices.
- On your PC: **PowerShell** (or Terminal). On the server: **SSH** into Ubuntu.

---

## Security (do this as you go)

- **Server:** Use SSH keys only (no password login). Open only ports **22, 80, 443**. Keep the system updated (`sudo apt update && sudo apt upgrade`). Run the app as **ubuntu** (non-root).
- **Secrets:** Never put API keys or Stripe keys in git. Use env vars or a restricted file (e.g. `.env.rapidapi` with `chmod 600`) on the server.
- **API:** Once you have a domain, use **HTTPS** (Certbot). When you add auth, hash passwords and use HTTPS for login. When you add Stripe, keep the secret key and webhook secret server-side only and verify webhook signatures.

Full list: **`docs/GROCERY_APP_SECURITY.md`**.

---

# Phase 1 – Oracle server (get SSH working)

## Step 1.1 – Oracle account and VM

1. Go to **https://www.oracle.com/cloud/free/** → **Start for free**.
2. Sign up (country, email, password). Verify email and complete payment verification (card for identity; use Always Free only to avoid charges).
3. Log in at **https://cloud.oracle.com**.
4. Menu **(≡)** → **Compute** → **Instances** → choose your region → **Create Instance**.
5. Fill in:
   - **Name:** e.g. `grocery-app`.
   - **Image:** Click **Change Image** → choose **Canonical Ubuntu**, **22.04**.
   - **Shape:** Click **Change shape** → **Always free-eligible** → **VM.Standard.E2.1.Micro** → **Select shape**.
   - **Networking:** Leave default; ensure **Assign a public IPv4 address** is checked.
   - **SSH keys:** **Generate a key pair for me** → **Save private key** and **Save public key**. Put the private key somewhere safe (e.g. `C:\Users\YourName\.ssh\oracle-grocery.key`).
6. Click **Create**. Wait until the instance is **Running**.
7. Note the **Public IP address** (e.g. `123.45.67.89`). You’ll use this as `YOUR_PUBLIC_IP` everywhere below.

**You’re done when:** The instance shows **Running** and you have the **public IP** and the **private key** file.

---

## Step 1.2 – Open ports 22, 80, and 443

1. In Oracle Cloud: **Networking** → **Virtual cloud networks**.
2. Click the VCN used by your instance (e.g. the one created with it).
3. Click the **Subnet** (e.g. “Public subnet-…”).
4. Click **Default Security List**.
5. **Add Ingress Rules** so you have **three** rules (add any that are missing):

   | Source        | IP Protocol | Destination port range |
   |---------------|-------------|-------------------------|
   | 0.0.0.0/0     | TCP         | 22                      |
   | 0.0.0.0/0     | TCP         | 80                      |
   | 0.0.0.0/0     | TCP         | 443                     |

6. Save (e.g. **Add Ingress Rules**).

**You’re done when:** All three ports (22, 80, 443) appear in the Security List Ingress rules.

---

## Step 1.3 – SSH in from your PC

1. Open **PowerShell**.
2. Run (use **your** key path and **your** public IP):

   ```powershell
   ssh -i "C:\path\to\your-private-key.key" ubuntu@YOUR_PUBLIC_IP
   ```

   Example:

   ```powershell
   ssh -i "$env:USERPROFILE\.ssh\oracle-grocery.key" ubuntu@123.45.67.89
   ```

3. If asked “Are you sure you want to continue connecting?”, type `yes` and Enter.
4. You should see a prompt like: `ubuntu@grocery-app:~$`.

**You’re done when:** You are at the `ubuntu@...:~$` prompt. If it times out, double-check the key path, IP, and that port 22 is open (Step 1.2).

---

## Step 1.4 – Install Python, Nginx, and Git on the server

In the same SSH session, run:

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx
```

**You’re done when:** The command finishes without errors.

---

# Phase 2 – Deploy the grocery app on the server

## Step 2.1 – Copy the app from your PC to the server

1. **On your PC**, open a **new** PowerShell window (leave SSH open in the other).
2. Run (replace the key path and IP; the path after `-r` must point to your `grocery-api` folder):

   ```powershell
   scp -i "C:\path\to\your-private-key.key" -r "c:\My Website\grocery-api" ubuntu@YOUR_PUBLIC_IP:~/
   ```

   Example:

   ```powershell
   scp -i "$env:USERPROFILE\.ssh\oracle-grocery.key" -r "c:\My Website\grocery-api" ubuntu@123.45.67.89:~/
   ```

3. Wait for the copy to finish.

**You’re done when:** No error. You can check on the server (in your SSH session) with: `ls ~/grocery-api` and you see `app.py`, `compare_prices.py`, `requirements.txt`, etc.

---

## Step 2.2 – Set up Python and the API key on the server

In your **SSH session** on the server, run these one after the other:

```bash
cd ~/grocery-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then set your RapidAPI key (replace with your **real** key):

```bash
export RAPIDAPI_KEY="your_actual_rapidapi_key_here"
```

To keep the key for later logins (optional), add it to your shell profile:

```bash
echo 'export RAPIDAPI_KEY="your_actual_rapidapi_key_here"' >> ~/.bashrc
```

**You’re done when:** `pip install` finishes and `echo $RAPIDAPI_KEY` prints your key (or nothing if you didn’t export it yet).

---

## Step 2.3 – Test the price script and create the first deals file

Still in SSH, with the same shell (and venv active if you had it):

```bash
cd ~/grocery-api && source venv/bin/activate && python compare_prices.py
```

- If the API key and API are correct, you’ll see “Best deals for today:” and a file `best_deals_YYYY-MM-DD.json` in `~/grocery-api`.
- If you see “No prices returned”, the key or API might be wrong; the script still creates a JSON file (possibly empty). You can continue; fix the key/API later.

**You’re done when:** No Python errors and a file `best_deals_*.json` exists. Check with: `ls ~/grocery-api/best_deals_*.json`.

---

## Step 2.4 – Schedule daily price updates (cron)

On the server, store your API key in a file (so cron can use it; don’t commit this file):

```bash
nano ~/grocery-api/.env.rapidapi
```

Type this one line (replace with your **real** key):

```bash
export RAPIDAPI_KEY="your_actual_rapidapi_key_here"
```

Save: **Ctrl+O**, Enter, **Ctrl+X**. Then:

```bash
chmod 600 ~/grocery-api/.env.rapidapi
chmod +x ~/grocery-api/run_compare_prices.sh
crontab -e
```

If asked to choose an editor, pick **nano** (usually 1). Add this **one line** at the end (6:00 AM every day):

```text
0 6 * * * /home/ubuntu/grocery-api/run_compare_prices.sh
```

Save: **Ctrl+O**, Enter, **Ctrl+X**. Verify:

```bash
crontab -l
```

**You’re done when:** `crontab -l` shows the line above.

---

## Step 2.5 – Run the web API (Gunicorn) and test it

In SSH:

```bash
cd ~/grocery-api && source venv/bin/activate && gunicorn -w 1 -b 0.0.0.0:5000 app:app
```

Leave this running. On **your PC**, open a browser and go to:

**http://YOUR_PUBLIC_IP:5000/api/deals**

You should see JSON (with `"deals"` and maybe `"disclaimer"`). If you see “No deals file yet”, that’s OK for now; the API is working.

Stop the server on the server with **Ctrl+C**.

**You’re done when:** The browser shows JSON from `http://YOUR_PUBLIC_IP:5000/api/deals`.

---

## Step 2.6 – Run the API as a service (starts on boot)

On the server:

```bash
sudo nano /etc/systemd/system/grocery-app.service
```

Paste the following. **Replace** `your_actual_rapidapi_key_here` with your real key:

```ini
[Unit]
Description=Grocery best-deals API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/grocery-api
Environment="RAPIDAPI_KEY=your_actual_rapidapi_key_here"
Environment="PATH=/home/ubuntu/grocery-api/venv/bin"
ExecStart=/home/ubuntu/grocery-api/venv/bin/gunicorn -w 1 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Save: **Ctrl+O**, Enter, **Ctrl+X**. Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable grocery-app
sudo systemctl start grocery-app
sudo systemctl status grocery-app
```

Status should say **active (running)**. If not, check the path and key.

**You’re done when:** `systemctl status grocery-app` shows **active (running)**.

---

## Step 2.7 – Put Nginx in front (so you can use port 80 and add HTTPS later)

On the server:

```bash
sudo nano /etc/nginx/sites-available/grocery-app
```

Paste (replace `YOUR_PUBLIC_IP` with your server’s IP, e.g. `123.45.67.89`):

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

Save: **Ctrl+O**, Enter, **Ctrl+X**. Then:

```bash
sudo ln -sf /etc/nginx/sites-available/grocery-app /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

On your PC, open:

**http://YOUR_PUBLIC_IP/api/deals**

You should get the same JSON as before (now on port 80, no `:5000`).

**You’re done when:** **http://YOUR_PUBLIC_IP/api/deals** returns JSON. Your app is **hosted on Oracle Linux**.

---

# Phase 3 – Turn it into an app you can sell

Do these when you’re ready to charge users. Order is flexible; many people do: frontend → auth → payments → legal → domain.

---

## Step 3.1 – Simple frontend (so people can “see” the app)

- Build a small page (HTML/JS or React/Vue) that calls `GET http://YOUR_PUBLIC_IP/api/deals` and shows “Best deals today” with a short disclaimer.
- Host that page either:
  - On the **same server** (e.g. put the built files in `/var/www/html` or a folder and point Nginx at it), or
  - On **Vercel/Netlify** and have the frontend call your Oracle API URL.

This gives you something to show and sell (“see where each item is cheapest”).

---

## Step 3.2 – User accounts (auth)

- Add **signup** and **login** (e.g. Flask-Login or JWT with a User table in SQLite/Postgres).
- Protect `/api/deals` (or a “premium” endpoint) so only logged-in (or subscribed) users get data.
- The app already has placeholder routes: `/api/register` and `/api/login` in `app.py`; implement them and add a check before returning deals.

---

## Step 3.3 – Payments (Stripe)

- Create a **Stripe** account and add **Products/Prices** (e.g. “Monthly” and “Yearly”).
- In the app: `POST /api/create-checkout-session` → redirect user to Stripe Checkout.
- Stripe **webhook** → on successful payment, set the user’s plan in your DB.
- When serving deals, check subscription; if not active, return “Subscribe” or 402.

`app.py` has placeholders: `/api/create-checkout-session` and `/api/webhook`; implement them with Stripe’s docs.

---

## Step 3.4 – Legal (required for selling)

- **Terms of Service** – What the app does, acceptable use, no guarantee of price accuracy.
- **Privacy Policy** – What you collect (email, payment), how you use it, where it’s stored.
- **Disclaimer** – e.g. “Prices are approximate; confirm at the store.”
- **Refund policy** – When you refund (e.g. within 14 days).

Add these as pages or links in the app and in checkout. In South Africa, consider POPIA and consumer law.

---

## Step 3.5 – Domain and HTTPS (recommended for a paid app)

1. Buy a **domain** (e.g. Namecheap, Freenom).
2. In the domain’s DNS, add an **A record** pointing to **YOUR_PUBLIC_IP**.
3. On the server:
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo nano /etc/nginx/sites-available/grocery-app
   ```
   Change `server_name YOUR_PUBLIC_IP;` to `server_name yourdomain.com;`, save.
4. Run:
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```
5. Use **https://yourdomain.com** for the app and API.

---

# Checklist – where you are

| Phase | Step | Done |
|-------|------|------|
| **Security** | Secrets not in git; SSH key-only; only 22/80/443 open | ☐ |
| **Security** | HTTPS + auth/Stripe security when you add them (see GROCERY_APP_SECURITY.md) | ☐ |
| **1** | Oracle VM created, ports 22/80/443 open | ☐ |
| **1** | SSH works; Python, pip, venv, Nginx installed | ☐ |
| **2** | App copied to server; venv + pip install | ☐ |
| **2** | RAPIDAPI_KEY set; compare_prices.py runs and creates JSON | ☐ |
| **2** | Cron runs daily (run_compare_prices.sh) | ☐ |
| **2** | Gunicorn + systemd service running | ☐ |
| **2** | Nginx reverse proxy; **http://YOUR_IP/api/deals** works | ☐ |
| **3** | Frontend that shows deals | ☐ |
| **3** | User auth (register/login) | ☐ |
| **3** | Stripe subscriptions + webhook | ☐ |
| **3** | Terms, Privacy, Disclaimer, Refund | ☐ |
| **3** | Domain + HTTPS | ☐ |

Once Phase 2 is complete, the app is **hosted on Oracle**. Phase 3 is what makes it an app you can **sell**.
