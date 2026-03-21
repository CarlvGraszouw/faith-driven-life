# Cloudflare Pages (website + PWA)

This repo is configured for **Cloudflare Pages** with **Pages Functions** (Workers runtime) for `/api/blog-feed`.

## What was migrated from Vercel

| Vercel | Cloudflare |
|--------|------------|
| `vercel.json` headers | Root `_headers` |
| `vercel.json` rewrites | Root `_redirects` (200 rewrites) |
| `api/blog-feed.js` (Node serverless) | `functions/api/blog-feed.js` (Pages Function) |
| Vercel Analytics script | Removed — use **Google Analytics** (already in pages) and/or **Cloudflare Web Analytics** in the dashboard |

## Connect GitHub → Pages

1. [Cloudflare Dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Select **`CarlvonGraszouw/faith-driven-life`**, branch **`main`**.
3. **Build settings:**
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/` or `.` (repository root — same folder as `index.html`)
4. **Save and Deploy.**

## Custom domain & SSL

1. In the Pages project → **Custom domains** → add **`www.afaithdrivenlife.com`** and **`afaithdrivenlife.com`**.
2. Follow Cloudflare’s DNS instructions (often CNAME `www` → `*.pages.dev` or your assigned Pages hostname).
3. SSL is automatic once the domain validates.

## PWA

- **`manifest.webmanifest`**, **`sw.js`**, and **`/sw.js`** cache rules in `_headers` are set so the service worker can update after deploys.
- After go-live, open the site once; users get **`faith-driven-life-v8`** cache from `sw.js`.

## Optional: Cloudflare Web Analytics

Dashboard → **Web Analytics** → add site → paste the lightweight beacon snippet into `index.html` `<head>` if you want Cloudflare’s privacy-friendly metrics alongside GA4.

## Delete Vercel (manual)

The repo cannot remove your Vercel account. In [Vercel](https://vercel.com):

1. Remove **Git** integration from duplicate projects (`faith-driven-life`, `faith-driven-life-hlzj`).
2. **Domains** → remove `afaithdrivenlife.com` / `www` from Vercel (after Cloudflare serves production).
3. **Delete** unused projects or the whole team if you no longer need Vercel.

## Local preview (optional)

```bash
npx wrangler pages dev . --compatibility-date=2024-11-01
```

Requires Node and a Cloudflare login (`npx wrangler login`).
