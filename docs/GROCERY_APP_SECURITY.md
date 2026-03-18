# Security – Grocery app on Oracle (and when you sell it)

Do these **as you go** through the walkthrough. Nothing here is optional if you care about security and selling the app.

---

## 1. Oracle server

### SSH

- **Use key-based login only.** You already did this (Generate key pair for me). Do **not** enable password authentication for SSH.
- **Restrict SSH by IP (optional but strong):** In the Security List, instead of Source `0.0.0.0/0` for port 22, use your home/office IP (e.g. `YOUR_IP/32`). Then only that IP can SSH. If your IP changes often, skip this or use a VPN.

### Firewall (Security List)

- Open **only** 22 (SSH), 80 (HTTP), 443 (HTTPS). No other ports to `0.0.0.0/0`.
- Gunicorn is bound to **127.0.0.1:5000** (see systemd unit), so the app is **not** directly exposed; only Nginx is public. Keep it that way.

### Updates

- After SSH works, run once (and periodically):
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
- Reboot if the kernel was updated.

### User

- Run the app as **ubuntu** (non-root). Your systemd unit already does this. Never run the app as root.

---

## 2. Secrets (API keys, Stripe, etc.)

- **Never commit secrets.** No API keys, Stripe secret key, or JWT secrets in git. Use `.gitignore` (e.g. `.env`, `.env.rapidapi`); the repo already ignores these.
- **Server:** Keep RapidAPI key in:
  - **systemd:** `Environment="RAPIDAPI_KEY=..."` in the service file, or
  - **File:** `~/grocery-api/.env.rapidapi` with `export RAPIDAPI_KEY="..."` and `chmod 600 .env.rapidapi`.
- **Stripe:** When you add payments, use **environment variables** or a similar file for `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`; never in code or frontend. Only **publishable** key goes in the frontend.
- **Flask:** When you add auth, set a strong `SECRET_KEY` (e.g. `openssl rand -hex 32`) in env; never hardcode it.

---

## 3. App and API

- **HTTPS:** As soon as you have a domain, add **HTTPS with Certbot** (Step 3.5). Use **https://** for the API and frontend so passwords, tokens, and payment data are encrypted in transit.
- **No secrets in client:** The browser/frontend must never see RapidAPI key, Stripe secret key, or server-side secrets. Only the **public** API URL (and later Stripe publishable key) are fine in the frontend.
- **Stripe webhook:** Verify webhook signatures with `STRIPE_WEBHOOK_SECRET` before trusting events; never skip this.
- **Auth:** Hash passwords (e.g. bcrypt); never store plain-text passwords. Use HTTPS for login/signup.

---

## 4. When you sell (auth + payments + data)

- **User data:** Store only what you need. In your Privacy Policy, say what you collect and how you use it. In South Africa, consider **POPIA** (Protection of Personal Information Act).
- **Payments:** Use Stripe (or another PCI-compliant provider); never store full card numbers. Stripe handles cards; you store only subscription status and Stripe customer/session IDs as needed.
- **Sessions / JWT:** Use short-lived tokens; secure cookies if using session-based auth (e.g. `Secure`, `HttpOnly`, `SameSite`).

---

## 5. Quick checklist

| Area | Action |
|------|--------|
| Server | SSH key-only; only ports 22, 80, 443 open |
| Server | Gunicorn on 127.0.0.1; Nginx reverse proxy |
| Server | `apt update && apt upgrade` periodically; run app as ubuntu |
| Secrets | No keys in git; use env or restricted files (chmod 600) |
| API | HTTPS once you have a domain; no secrets in frontend |
| Auth (later) | Hash passwords; HTTPS for login |
| Stripe (later) | Secret key + webhook secret in env only; verify webhook signatures |
| Legal | Privacy Policy; POPIA if applicable |

Security is not a one-time step: do the server and secrets parts **now**, and the rest **when** you add auth, payments, and a domain.
