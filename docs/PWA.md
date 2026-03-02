# Progressive Web App (PWA) setup

Your site is set up as a **Progressive Web App**. Users can install it on their phone or desktop and use it like an app, with basic offline support.

## What was added

- **`manifest.webmanifest`** – App name, theme color, icons, and “standalone” display so it opens without the browser chrome.
- **`sw.js`** – Service worker that caches the main pages and assets so the site can load when offline (or from cache when online).
- **Manifest link** on all main HTML pages so “Add to Home Screen” / “Install” works from any page.
- **Apple meta tags** on the home page for iOS “Add to Home Screen” (app name, status bar style).
- **Service worker registration** on every main page so the worker is registered no matter which page is visited first.

## How users install it

### On Android (Chrome/Edge)
- Open your site, then tap the **menu** (⋮) → **“Install app”** or **“Add to Home screen”**.
- Or accept the install prompt if the browser shows one.

### On iPhone/iPad (Safari)
- Open your site in **Safari**, tap the **Share** button, then **“Add to Home Screen”**. Name it and tap Add.

### On desktop (Chrome/Edge)
- Open your site; an **install** icon may appear in the address bar, or use the menu → **“Install A Faith Driven Life”** (or similar).

## Testing locally

1. Serve the site over **HTTPS** (or `localhost`). GitHub Pages is HTTPS, so once deployed it will work.
2. For local testing, use a simple HTTPS server or run from `localhost`; the service worker requires a secure context.
3. In Chrome DevTools → **Application** → **Manifest** you can check the manifest; under **Service Workers** you can see if the worker is registered.

## Optional: better PWA icons

The manifest uses **logo.png** for both 192×192 and 512×512. For best results you can add dedicated icon files:
- `icon-192.png` (192×192)
- `icon-512.png` (512×512)

Then update `manifest.webmanifest` so each `icons` entry uses the correct file and size. Until then, the browser will scale `logo.png`.

## Cache updates

When you change the site, update the cache version in **`sw.js`**: change `CACHE_NAME = 'faith-driven-life-v1'` to `v2` (etc.). Existing users will get the new cache on their next visit.
