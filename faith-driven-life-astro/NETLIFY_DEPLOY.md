# Deploy A Faith Driven Life (Astro) on Netlify

This folder is a **separate project** from your current site. Your existing site (e.g. on GitHub Pages) stays live until you are ready to switch.

## 1. Copy assets from your current site

Copy these from `c:\My Website\` into `faith-driven-life-astro\public\`:

- **logo.png** → `public/logo.png` (required for the nav logo)
- **favicon.svg** (optional; the template has one in `public/`)

If you have audio or study PDFs:

- **audio/** → `public/audio/`
- **study-material/** → `public/study-material/`

## 2. Install and run locally

```bash
cd faith-driven-life-astro
pnpm install
pnpm run dev
```

Open http://localhost:4321 to preview. Structure and look should match your current site (dark theme, gold accent, same nav and pages).

## 3. Deploy on Netlify (separate site)

1. **Push this project to its own repo** (so the current site repo is unchanged):
   - Create a new GitHub repo, e.g. `faith-driven-life-astro` or `faith-driven-life-netlify`.
   - Remove the existing git remote and add the new one:
     ```bash
     cd faith-driven-life-astro
     git remote remove origin
     git remote add origin https://github.com/YOUR_USERNAME/faith-driven-life-astro.git
     git push -u origin main
     ```

2. **In Netlify:**
   - Log in at [netlify.com](https://www.netlify.com).
   - **Add new site** → **Import an existing project** → **GitHub** → choose the new repo.
   - Netlify will use the repo’s `netlify.toml`: build command `pnpm run build`, publish directory `dist`.
   - Click **Deploy site**.

3. Your Astro site will get a URL like `https://something.netlify.app`. Your current GitHub Pages site is unchanged.

## 4. When the new site is ready

- Point your custom domain to the Netlify site (in Netlify: **Domain settings**), or
- Keep both: e.g. GitHub Pages for the old site and Netlify for the new one until you switch.

## Build / tech

- **Framework:** Astro (template: Astrofy / Astro Modern Personal Website).
- **Styling:** Tailwind CSS + DaisyUI, custom “faith” theme (dark blue + gold).
- **Build output:** `dist/` (static).
