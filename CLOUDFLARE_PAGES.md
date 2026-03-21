# Cloudflare Pages (website + PWA)

This repo is configured for **Cloudflare Pages** with **Pages Functions** (Workers runtime) for `/api/blog-feed`.

## Dashboard UI (exact labels — do not mix these up)

### Cloudflare (`https://dash.cloudflare.com`)

Select your **account** (top bar) if you have more than one.

| Where | What it is |
|--------|------------|
| **Account home** → card **Domains** with button **Onboard a domain** | **DNS zones only** — domains whose **nameservers** you set to Cloudflare. **If this list is empty, Cloudflare is not yet your DNS provider for `afaithdrivenlife.com`.** This is **not** the Pages project list. |
| Left sidebar → **Domains** | Same: **DNS** (records per domain/zone). |
| Left sidebar → **Workers & Pages** | **Deployed projects.** Your site is **`faith-driven-life`** (Pages). This can show updates **even when Domains is empty** — the site still lives at **`https://faith-driven-life.pages.dev`**. |
| **Workers & Pages** → **`faith-driven-life`** → **Custom domains** | Attach **`www.afaithdrivenlife.com`** / apex to **this** project. The wizard shows **exact DNS records** to add. |

**In short:** **Domains** = “we host DNS for this domain.” **Workers & Pages → faith-driven-life** = “the website files deploy here.” You need **onboarding + DNS** for the public domain, **and** the **Custom domains** tab on the project.

### Namecheap

**Domain List** → **Manage** → **Nameservers** → **Custom DNS** → paste **only** Cloudflare’s **two** nameservers (from onboarding). Remove **Vercel** `*.vercel-dns.com` entries.

### Vercel

**Domains** (account) or **Project → Settings → Domains**. If delete says nameservers must change: fix **Namecheap** first, then delete again.

---

## Automated deploy (no Cloudflare “build” dashboard)

Push to **`main`** runs **`.github/workflows/deploy-cloudflare-pages.yml`**, which stages into **`deploy-upload/`** and runs **`wrangler pages deploy deploy-upload …`** (static site + `functions/`).

**One-time:** add **`CLOUDFLARE_API_TOKEN`** and **`CLOUDFLARE_ACCOUNT_ID`** to GitHub **Actions secrets** — see **`README.md`** (repo homepage).

The token must be a **Custom API token** with **Account → Cloudflare Pages → Edit**. If `wrangler pages deploy` fails with **`Unable to authenticate` (code 10001)**, the token is missing that permission, is for the wrong account, or the **Account ID** secret does not match the account the token can access. See **`SETUP.txt`** for step-by-step token creation.

Do **not** set a Cloudflare Pages **build command** to `npx wrangler deploy` (that is for Workers). If you use **only** GitHub Actions to deploy, **disconnect** Cloudflare’s **Git** integration for this repo to avoid double deploys.

## File size limit (25 MiB per asset)

Cloudflare Pages rejects uploads where **any single file is larger than 25 MiB**. The workflow stages the site into `deploy-upload/` and **does not upload** `audio/The Supreme Commission.mp3` (~70&nbsp;MB).

**Step-by-step:** create an R2 bucket, upload the MP3, enable a public URL, optional CORS — see **`docs/HOST_AUDIO_R2.md`**. Then set **`REMOTE_SUPREME_COMMISSION_MP3_URL`** in **`audio.html`** to the public `https://…` URL (or leave it empty for local-only playback from `audio/`).

## Site layout (Cloudflare)

| Concern | How it’s handled |
|--------|------------------|
| HTTP headers | Root `_headers` |
| Pretty URLs | Root `_redirects` (200 rewrites) |
| `/api/blog-feed` | `functions/api/blog-feed.js` (Pages Function) |
| Analytics | **Google Analytics** (in pages) and/or **Cloudflare Web Analytics** (dashboard) |

## Connect GitHub → Pages

1. [Cloudflare Dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Select **`CarlvGraszouw/faith-driven-life`**, branch **`main`**.
3. **Build settings (critical):**
   - **Framework preset:** None
   - **Build command:** **leave completely empty** — do **not** use `npx wrangler deploy` (that is for **Workers**, not static **Pages**; it will fail with “Missing entry-point”).
   - **Build output directory:** `/` or `.` (repository root — same folder as `index.html`)
4. **Save and Deploy.**

### If the build log shows `Executing user deploy command: npx wrangler deploy`

That is wrong. Open the project → **Settings** → **Builds & deployments** → **Edit configuration** → clear **Build command** (and **Deploy command** if present) → save → **Retry deployment**. This repo does **not** commit `wrangler.toml` so Cloudflare won’t treat the site as a Worker bundle.

## Custom domain & SSL

1. In **Workers & Pages** → your **`faith-driven-life`** project → **Custom domains** → **Set up a domain** → add **`www.afaithdrivenlife.com`** and **`afaithdrivenlife.com`** (add both if you use apex + www).
2. If the domain’s DNS is already in **this Cloudflare account**, Cloudflare can often attach the records automatically. If not, add the **CNAME** / **A** records the wizard shows (commonly `www` → `faith-driven-life.pages.dev` as CNAME target).
3. SSL certificates issue automatically after DNS validates.

### If the site still shows errors or “Vercel” in response headers

DNS or an old integration can still send traffic to **another host**. Check from your PC: `curl -sI https://www.afaithdrivenlife.com` — if you see **`Server: Vercel`**, the name is not yet routed to Pages.

**Fix:**

1. **Cloudflare:** Ensure the domain **`afaithdrivenlife.com`** uses the DNS records Cloudflare Pages shows for this project (no leftover `A`/`CNAME` records pointing at old providers).
2. **Remove the domain from any previous host** (e.g. delete **`www`** / apex from old dashboard projects) so only Cloudflare Pages owns the hostname.
3. Wait a few minutes for DNS/SSL, then hard-refresh or try a private window.

The live Pages URL without a custom domain is always: **`https://faith-driven-life.pages.dev`**.

### If your domain is **not** in this Cloudflare account (DNS still goes to Vercel)

The GitHub Action **Point DNS to Cloudflare Pages** only works when **`afaithdrivenlife.com`** exists as a **zone** under the **same** Cloudflare account as your Pages project (nameservers pointed at Cloudflare). If the API returns “no zone,” DNS is managed **elsewhere** (registrar, another Cloudflare account, or only Vercel).

**Fix (must be done where DNS is controlled):**

1. **Remove** `www` and apex from any **Vercel** project (**Settings → Domains**), or Vercel will keep answering for that hostname.
2. At your **DNS host** (registrar or DNS panel), replace old records with what Cloudflare Pages expects. Typical values:
   - **`www`** → **CNAME** → **`faith-driven-life.pages.dev`** (often **proxied** if using Cloudflare DNS).
   - **Apex** `afaithdrivenlife.com` → follow the **Custom domains** wizard in **Workers & Pages → faith-driven-life → Custom domains** (apex may use CNAME flattening or the targets Cloudflare shows).
3. Wait for propagation, then check: `curl -sI https://www.afaithdrivenlife.com` — you want **`server: cloudflare`**, not **`Server: Vercel`**.

Optional: **add the site to Cloudflare** (same account as Pages) by changing **nameservers** at the registrar to the pair Cloudflare gives you; then DNS can be edited in one place and the **Point DNS to Cloudflare Pages** workflow can work on future runs.

## PWA

- **`manifest.webmanifest`**, **`sw.js`**, and **`/sw.js`** cache rules in `_headers` are set so the service worker can update after deploys.
- After go-live, open the site once; users get **`faith-driven-life-v9`** cache from `sw.js`.

## Optional: Cloudflare Web Analytics

Dashboard → **Web Analytics** → add site → paste the lightweight beacon snippet into `index.html` `<head>` if you want Cloudflare’s privacy-friendly metrics alongside GA4.

## Local preview (optional)

```bash
npx wrangler pages dev . --compatibility-date=2024-11-01
```

Use **`wrangler pages dev`** (Pages), not `wrangler deploy` (Workers). Optionally copy `wrangler.toml.example` to `wrangler.toml` locally only; do not set the dashboard build step to wrangler deploy.

Requires Node and a Cloudflare login (`npx wrangler login`).
