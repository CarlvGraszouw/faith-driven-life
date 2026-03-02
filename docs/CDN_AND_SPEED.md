# CDN and speed (Website Checker – "Enable CDN")

Some website checkers report **"Enable CDN"** or "No CDN active" for GitHub Pages sites. Here’s what that means and what you can do.

## Does my site use a CDN?

**Yes.** GitHub Pages serves your site over a global CDN (Fastly). Your content is cached at edge locations, so many visitors are served from a nearby node. The site is already:

- **Gzip compressed** (transfer size reduced)
- **Served from a CDN** (GitHub’s infrastructure)
- **Compact** (small page size helps speed)

Some checkers don’t detect GitHub’s CDN and still show “Enable CDN” or “No CDN active.” That’s a **detection limitation**, not proof that you have no CDN.

## If the checker still says "Enable CDN"

1. **Use the checker’s own help**  
   Many tools have a link like **“Website Checker Does Not Recognize an Activated CDN”** or similar. Use it to report that the site is on GitHub Pages (and thus already behind a CDN).

2. **Optional: Put the site behind Cloudflare**  
   If you use a **custom domain** (e.g. `faithdrivenlife.com`) instead of `carlvgraszouw.github.io/faith-driven-life`, you can:
   - Add the domain to **Cloudflare** (free plan).
   - Point the domain to GitHub Pages (via CNAME or DNS).
   - Enable the Cloudflare proxy (orange cloud).
   - Cloudflare will act as a second, often “recognized” CDN in front of GitHub Pages and can improve “Be fast” and “Enable CDN” in checkers that look for it.

   If you keep using **only** the `*.github.io` URL, you cannot add Cloudflare in front of that domain; in that case, the only way to “fix” the warning is the checker’s “does not recognize” option or similar.

## What we’ve done in the repo for speed

- **Preconnect** to Google Fonts so the browser can start the connection early.
- **Compression** is handled by GitHub Pages (Gzip).
- **Small payload**: minimal scripts and inline CSS, no heavy frameworks.
- **PWA and caching**: service worker caches key pages for repeat visits.

Re-run the Website Checker after deploying; “Be fast” and “Be online” often improve. If “Enable CDN” remains, treat it as a recognition issue unless you add a custom domain and Cloudflare.
