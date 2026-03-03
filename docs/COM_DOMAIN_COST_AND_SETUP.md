# Hosting on a .com Domain — Cost and How to Get It Done

Using your own .com (e.g. **afaithdrivenlife.com**) fixes the Google “standalone” and sitemap issues: your site is no longer under github.io, and Search Console is straightforward.

---

**Done in this repo:** CNAME and all site URLs are set to **www.afaithdrivenlife.com**. Push only after you (1) buy **afaithdrivenlife.com**, (2) set DNS (CNAME www → carlvgraszouw.github.io), (3) set custom domain in GitHub Settings → Pages. If you use a different domain, edit CNAME and replace www.afaithdrivenlife.com everywhere.

## 1. How much will it cost?

| Item | Cost |
|------|------|
| **Domain (.com)** | About **$10–15 per year** (sometimes less with first-year deals) |
| **GitHub Pages hosting** | **Free** (unchanged) |
| **SSL (HTTPS)** | **Free** (GitHub provides it when you use a custom domain) |

**Total: roughly $10–15 per year** — you only pay for the domain.

### Where to buy the domain (examples)

- **Cloudflare** — often ~$9–10/year, no markup, simple DNS.
- **Namecheap** — often ~$8–14/year, first year sometimes cheaper.
- **Google Domains (now Squarespace Domains)** — around $12/year.
- **Porkbun** — often ~$9–11/year.
- **GoDaddy** — often higher; check for coupons.

Pick any registrar you like; the steps are the same. If you want the simplest DNS and low cost, Cloudflare or Namecheap are common choices.

### Domain name ideas

- **afaithdrivenlife.com**
- **faithdrivenlife-site.com** or **faithdrivenlifepage.com** (if “faithdrivenlife.com” is taken)

Check availability on the registrar’s site before buying.

---

## 2. How to get it done (step-by-step)

### Step 1: Buy the domain

1. Go to a registrar (e.g. cloudflare.com, namecheap.com).
2. Search for the name you want (e.g. **afaithdrivenlife.com**).
3. Add it to cart and complete checkout. You’ll get a login to manage DNS for that domain.

---

### Step 2: Add a CNAME file to your repo

So GitHub Pages knows which domain to use:

1. In your repo root (same folder as `index.html`), create a file named **`CNAME`** (no extension, all caps).
2. Put **one line** in it — the address you want people to use:
   - If you want **www**:  
     `www.afaithdrivenlife.com`
   - If you want **no www** (e.g. afaithdrivenlife.com):  
     `afaithdrivenlife.com`
3. Save, commit, and push. The repo root must contain only this one line in `CNAME`.

**Recommendation:** Use **www** (e.g. `www.afaithdrivenlife.com`) — it’s easier with GitHub Pages (one CNAME in DNS).

---

### Step 3: Set DNS at your registrar

Log in where you bought the domain and open the DNS settings.

**If you use www (recommended):**

| Type | Name | Value / Target |
|------|------|----------------|
| **CNAME** | `www` | `carlvgraszouw.github.io` |

So: **www** → **carlvgraszouw.github.io**.  
(Some registrars ask for “Host” = `www`, “Points to” = `carlvgraszouw.github.io`.)

**If you use the apex/root (e.g. afaithdrivenlife.com with no www):**

You need **A** records to GitHub’s IPs. As of 2024, GitHub documents these; check:  
[https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages)  
for the current IPs (often 4 A records). This is a bit more work than using www.

Save the DNS changes. It can take from a few minutes up to 24–48 hours to propagate.

---

### Step 4: Tell GitHub Pages your domain

1. On GitHub, open your repo → **Settings** → **Pages** (under “Code and automation” or “Build and deployment”).
2. Under **“Custom domain”**, type the domain exactly as in `CNAME` (e.g. `www.afaithdrivenlife.com`).
3. Click **Save**.
4. When the option appears, turn on **Enforce HTTPS**.

GitHub will then issue a free SSL certificate. Wait until the domain shows as verified and HTTPS works when you open the site in the browser.

---

### Step 5: Update the site to use the new URL

After the site loads at your .com (e.g. https://www.afaithdrivenlife.com/), every reference to the old github.io URL should be updated so search engines and links use the new domain. That means:

- **Canonical tags** in all HTML pages
- **og:url**, **og:image**, **og:site_name** (and any other OG/Twitter meta)
- **sitemap.xml** — all `<loc>` URLs
- **robots.txt** — the Sitemap line
- **JSON-LD** (WebSite, Organization) — `url` and any sameAs
- **Internal links** (if any point to the full github.io URL)
- **Google Search Console** — add a new property for the .com and submit the new sitemap

You can do this by hand or ask for help: once you tell me the exact domain (e.g. **https://www.afaithdrivenlife.com**), I can outline or apply the exact changes (canonicals, sitemap, robots, meta, schema) in your project.

---

## 3. Quick checklist

| Step | Action |
|------|--------|
| 1 | Buy .com at a registrar (~$10–15/year) |
| 2 | Add **CNAME** file in repo: one line = your domain (e.g. `www.afaithdrivenlife.com`), push |
| 3 | At registrar DNS: CNAME **www** → **carlvgraszouw.github.io** (Namecheap: Domain List → Manage → Advanced DNS → Add Record → CNAME, Host: www, Value: carlvgraszouw.github.io) |
| 4 | GitHub → Settings → Pages → Custom domain → your domain → Save → Enforce HTTPS |
| 5 | When the site loads on the .com, update canonicals, sitemap, robots, meta, schema (and GSC) to the new URL |

---

## 4. What you get

- A proper .com address (e.g. **www.afaithdrivenlife.com**).
- Google can list your site as its own result (not under “GitHub”).
- Simpler Search Console (one property for the .com, sitemap works without “Couldn’t fetch”).
- Same free hosting and HTTPS; you only pay for the domain each year.

If you tell me the exact .com you bought (e.g. **www.afaithdrivenlife.com**), I can give you the exact CNAME content and then the list of files/lines to change for canonicals, sitemap, robots, and meta/schema.
