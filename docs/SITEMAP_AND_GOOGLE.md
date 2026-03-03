# Sitemap and Google – use the full URL

Your site is hosted on **GitHub Pages as a project site**. That means it does **not** live at the root of the domain. It lives at a **subpath**.

## The one URL to use everywhere

Use this exact address for everything (checkers, Google, links, sharing):

**https://www.afaithdrivenlife.com/**

Not:
- ~~carlvgraszouw.github.io~~
- ~~carlvgraszouw.github.io/~~ (root of the domain)
- ~~faith-driven-life.github.io~~

## Why the checker says “No sitemap.xml was found”

Many tools ask for a “domain” and then look for:

- `https://<domain>/sitemap.xml`
- `https://<domain>/robots.txt`

If you enter **carlvgraszouw.github.io**, they look at:

- `https://carlvgraszouw.github.io/sitemap.xml` → **does not exist** (your site is not at the root)
- `https://carlvgraszouw.github.io/robots.txt` → **does not exist** there

Your real files are here:

- **Sitemap:** https://www.afaithdrivenlife.com/sitemap.xml  
- **Robots:** https://www.afaithdrivenlife.com/robots.txt  

So the checker **must** be run with the **full** URL:

**https://www.afaithdrivenlife.com/**

If the tool only has a “domain” field, try putting the full URL in that field, or use a checker that lets you enter the full page URL.

If it still says “sitemap not found”, use the tool’s option: **“My sitemap.xml is Not Being Recognized”** and tell them the sitemap URL is:

**https://www.afaithdrivenlife.com/sitemap.xml**

---

## Why “A FAITH DRIVEN LIFE” doesn’t show in Google

Google only shows sites it has **crawled and indexed**. For a new or project site, that often doesn’t happen until you **add the site and sitemap in Google Search Console**.

### Step 1: Open Google Search Console

1. Go to: **https://search.google.com/search-console**
2. Sign in with the Google account you want to use.

### Step 2: Add your property (your site)

1. Click **“Add property”**.
2. Choose **“URL prefix”**.
3. Enter exactly: **https://www.afaithdrivenlife.com/**
4. Click **Continue**.

### Step 3: Prove you own the site

Google will ask you to verify ownership. For GitHub Pages you can use:

- **HTML tag:** Add a meta tag they give you in the `<head>` of `index.html`, then click “Verify” in Search Console.  
  **Or**
- **HTML file:** Download the file they give you, put it in the root of your repo (e.g. `faith-driven-life/xxxxx.html`), push to GitHub, then click “Verify”.

After it says “Ownership verified”, you’re done with verification.

### Step 4: Submit the sitemap

1. In Search Console, open your property: **https://www.afaithdrivenlife.com/**
2. In the left menu, go to **“Sitemaps”**.
3. Under “Add a new sitemap”:
   - **First try:** enter **sitemap.xml** and click **Submit**.
   - **If you see “Couldn’t fetch”:** remove that sitemap, then in the same field paste the **full** URL and submit:
     **https://www.afaithdrivenlife.com/sitemap.xml**
4. The property URL must be exactly **https://www.afaithdrivenlife.com/** (with trailing slash). If you added a different property (e.g. without `/faith-driven-life/`), add a new property with the full URL above, verify it, then submit the sitemap again.

### Step 5: Ask Google to index the homepage (optional but useful)

1. At the top of Search Console, use the **URL inspection** / “Inspect any URL” box.
2. Enter: **https://www.afaithdrivenlife.com/**
3. Click **Request indexing** (or “Submit to index”) so Google queues the homepage for crawling.

---

## What to expect

- **Sitemap:** Once you use the **full** URL in checkers and in Search Console, the “no sitemap” warning should go away (or you use “My sitemap is not being recognized” and give them the sitemap URL above).
- **Google:** Indexing can take from a few days to a few weeks. After you add the property, verify, submit the sitemap, and optionally request indexing for the homepage, keep using the same full URL everywhere. Searching **“A FAITH DRIVEN LIFE”** may start showing your site once Google has crawled and indexed it.

---

## Short checklist

| Task | Use this URL |
|------|-------------------------------|
| Website Checker / any audit | https://www.afaithdrivenlife.com/ |
| Google Search Console property | https://www.afaithdrivenlife.com/ |
| Sitemap (for “not recognized” forms) | https://www.afaithdrivenlife.com/sitemap.xml |
| Share your site with others | https://www.afaithdrivenlife.com/ |

Using the full URL everywhere is what fixes both “sitemap not found” and “site not in Google”.
