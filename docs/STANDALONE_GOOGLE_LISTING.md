# How to Get Your Site Listed as Standalone in Google (Not Under GitHub)

## Why it shows under "GitHub" or "GitHub Pages"

With a custom domain, your site lives at **https://www.afaithdrivenlife.com/**. Google treats it as its own site. (If you were still on **carlvgraszouw.github.io/faith-driven-life/**, Google would group it under "GitHub" or "GitHub Pages" in search.)

Your pages already have strong identity (title "A Faith Driven Life", `og:site_name`, WebSite schema). The main thing that decides “standalone vs under GitHub” is the **domain**, not the meta tags.

---

## Reliable way to get a standalone listing: use a custom domain

When your site is served from **your own domain** (e.g. `www.afaithdrivenlife.com` or `faithdrivenlife.com`), Google treats it as its own site and can show it as a **standalone** result with your site name and favicon, not under GitHub.

### 1. Get a domain

- Buy a domain from a registrar (e.g. Namecheap, Google Domains, Cloudflare, etc.), e.g. **afaithdrivenlife.com** or **faithdrivenlife.com**.

### 2. Point the domain to GitHub Pages

**Option A – Subdomain (e.g. www.afaithdrivenlife.com)**  
- In your repo: add a file named **`CNAME`** in the root (same level as `index.html`) with one line:  
  `www.afaithdrivenlife.com`  
- In your registrar’s DNS for **afaithdrivenlife.com**:
  - Add a **CNAME** record:  
    Name: `www` (or `www.afaithdrivenlife.com`) → Target: `carlvgraszouw.github.io`

**Option B – Apex/root domain (e.g. afaithdrivenlife.com)**  
- In the repo: **CNAME** file with:  
  `afaithdrivenlife.com`  
- In DNS you typically use **A** records to GitHub’s IPs (see [GitHub Pages custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)) or a CNAME flattening / ALIAS if your DNS supports it.

### 3. Turn on the custom domain in GitHub

- Repo → **Settings** → **Pages**
- Under "Custom domain", enter your domain (e.g. `www.afaithdrivenlife.com`)
- Enable **Enforce HTTPS** when it’s offered

### 4. Update your site to use the new URL

After the domain works in the browser, update the site so everything uses the new URL:

- **Canonical tags** – point to `https://www.afaithdrivenlife.com/` (and per-page canonicals)
- **og:url**, **og:image** – use the new domain
- **sitemap.xml** – all `<loc>` URLs with the new domain
- **robots.txt** – Sitemap URL with the new domain
- **JSON-LD (WebSite, Organization)** – `url` and any sameAs/homepage with the new domain

Then redeploy.

### 5. Tell Google about the new site

- In **Google Search Console**, add a **Property** for the new URL (e.g. `https://www.afaithdrivenlife.com`).
- Verify ownership (HTML file, DNS, or Google Analytics).
- Submit the sitemap for the new domain.
- Optionally set the **old** property (github.io/faith-driven-life) to a permanent redirect (301) to the new domain so Google moves signals to the new standalone site.

---

## Summary

| Current (github.io path)        | With custom domain              |
|--------------------------------|---------------------------------|
| Often shown under "GitHub"     | Shown as its own site           |
| URL: …github.io/faith-driven-life | URL: your domain (e.g. www.afaithdrivenlife.com) |
| Identity is strong in meta/schema, but host is GitHub | Host is your brand → standalone listing |

**Bottom line:** To get a **standalone** link in Google (not under GitHub), use a **custom domain** and then point canonicals, sitemap, and structured data to that domain. If you tell me the exact domain you choose, I can outline the exact CNAME/canonical/sitemap changes for your repo.
