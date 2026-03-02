# WebScore.AI / audit score improvements

This doc summarizes changes made to improve your site’s audit score (e.g. WebScore.AI, Lighthouse, SEO tools) and what to do next.

## Changes made

### 1. **SEO – robots.txt**
- **File:** `robots.txt` at site root
- Tells crawlers they can index the whole site and where to find the sitemap.
- Commonly checked by audit tools.

### 2. **SEO – sitemap.xml**
- **File:** `sitemap.xml` at site root
- Lists main pages (index, blogs, resources, book, audio, bible, comments, prayer-requests, testimonies) with priorities and change frequency.
- Helps search engines discover and rank your pages.

### 3. **SEO – canonical URLs**
- **Added:** `<link rel="canonical" href="...">` on index, blogs, and resources.
- Defines the preferred URL for each page and reduces duplicate-content issues.

### 4. **SEO – Open Graph and Twitter Card meta tags**
- **Added on index, blogs, resources:** `og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `og:site_name`, and Twitter card equivalents.
- Improves how links look when shared on social media and is often part of “SEO” and “best practices” checks.

### 5. **SEO – structured data (JSON-LD)**
- **Added on index:** A `WebSite` schema with name, url, and description.
- Gives search engines clear information about your site and can improve rich results and SEO scores.

### 6. **Performance**
- Fonts already use `display=swap` in the Google Fonts URL; `preconnect` and `crossorigin` are in place on index to keep font loading efficient.

## What to do next

1. **Re-run the audit**  
   After deploying these changes, run WebScore.AI (and optionally Lighthouse) again. Scores often improve once crawlers see the new meta tags, sitemap, and structured data.

2. **Add the same SEO meta to other pages**  
   For consistency and better scores on deep links, add canonical + Open Graph + Twitter Card to:
   - `book.html`
   - `audio.html`
   - `bible.html`
   - `comments.html`
   - `prayer-requests.html`
   - `testimonies.html`
   - `post.html` (with dynamic title/description if you have a template).

3. **Image optimization**  
   If `logo.png` is large, export a smaller version (e.g. 1200×630 for social) and use that in `og:image` and `twitter:image` for faster loads and better social previews.

4. **Core Web Vitals**  
   Use [PageSpeed Insights](https://pagespeed.web.dev/) to check LCP, FID/INP, CLS. Your site is mostly static, so scores can be high; any heavy script or large image will show up there.

5. **Accessibility**  
   You already have skip link, focus styles, and semantic HTML. Run an accessibility audit (e.g. Lighthouse “Accessibility”) and fix any reported contrast or ARIA issues.

6. **Security headers**  
   You already use a Content-Security-Policy meta tag. If you ever move to a server where you can set HTTP headers, adding headers like `X-Content-Type-Options: nosniff` and `Referrer-Policy` can improve security/audit checks.

Deploy, re-run the audit, and then iterate on any remaining suggestions from the tool.
