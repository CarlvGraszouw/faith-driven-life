# Site security (static site on GitHub Pages)

Your site is **already in a good security position** because:

- **Static HTML** — No server-side code, database, or admin login to compromise.
- **HTTPS** — GitHub Pages serves your site over HTTPS by default (encrypted traffic).
- **No plugins** — This isn’t WordPress; there are no installable “security plugins.” Security is handled by the host and by the code on the site.

## What’s in place

1. **Content-Security-Policy (CSP)** on the home page  
   - Limits where scripts, styles, fonts, and connections can load from (e.g. only your domain, Google Fonts, Bible API, visit counter).  
   - Helps reduce the impact of any future XSS or injected scripts.

2. **Safe external links**  
   - All `target="_blank"` links use `rel="noopener noreferrer"` so the new tab can’t access your page or referrer (helps prevent tab-nabbing and limits tracking).

3. **Trusted scripts only**  
   - Scripts are same-origin (`visit-counter.js`, `scripture-rotator-data.js`, etc.) or from known APIs (Bible, visit counter). No random third-party script tags.

## Free ways to improve further

- **Keep dependencies minimal** — Don’t add script tags from unknown sites.
- **Forms** — If comments/prayer/testimonies post to Google Apps Script or another service, use **HTTPS** URLs only and never put API keys or secrets in the page (keep them in the backend/Apps Script).
- **GitHub** — Use a strong password and 2FA on your GitHub account so only you can change the repo.
- **Optional: Cloudflare** — Put the site behind [Cloudflare](https://www.cloudflare.com) (free) for extra DDoS protection and optional security headers; you’d point your domain to Cloudflare and then to GitHub Pages.

## Summary

The site is **secure for a static brochure-style site**: HTTPS, no server to hack, and CSP + safe links add an extra layer. There are no “free security plugins” to install; the improvements above are built into the code and hosting.
