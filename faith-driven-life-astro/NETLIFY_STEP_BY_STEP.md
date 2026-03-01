# Step-by-step: Deploy the Astro site on Netlify (second site)

Your **current site** stays live on GitHub Pages. This guide deploys the **Astro version** as a **second site** on Netlify so you can compare them.

---

## Before you start

- You need a **Netlify account** (free): [https://app.netlify.com/signup](https://app.netlify.com/signup)
- Your repo **faith-driven-life** is already on GitHub with the **faith-driven-life-astro** folder inside it (same repo as your current site).

---

## Step 1: Log in to Netlify

1. Go to **https://app.netlify.com**
2. Sign in (or sign up with GitHub, email, etc.)

---

## Step 2: Add a new site from Git

1. Click **“Add new site”** (or **“Sites”** in the top nav, then **“Add new site”**).
2. Choose **“Import an existing project”**.

---

## Step 3: Connect to GitHub

1. Click **“Deploy with GitHub”** (or **“Connect to Git provider”** → **GitHub**).
2. If Netlify asks for permission to access GitHub, click **“Authorize Netlify”** (or **“Authorize”**).
3. If asked to **“Install”** or **“Configure Netlify”** on your GitHub account, choose:
   - **“All repositories”** or  
   - **“Only select repositories”** and pick **faith-driven-life**.
4. Click **“Install”** / **“Save”** so Netlify can read your repo.

---

## Step 4: Pick the repository

1. In the list of repos, find **“faith-driven-life”**.
2. Click **“faith-driven-life”** to select it.

---

## Step 5: Set build settings (important)

Netlify will show **“Branch to deploy”**, **“Build command”**, **“Publish directory”**, and sometimes **“Base directory”**. Set them like this:

| Setting            | Value                    |
|--------------------|--------------------------|
| **Branch to deploy** | `main` (or your default branch) |
| **Base directory**   | `faith-driven-life-astro` |
| **Build command**   | `pnpm run build` (or `npm run build`) |
| **Publish directory** | `dist` |

How to set them:

1. **Base directory**
   - Find **“Base directory”** (or **“Advanced build settings”** → **“Base directory”**).
   - Enter: **`faith-driven-life-astro`**
   - This tells Netlify to build only from that folder (your current site at the repo root is not built).

2. **Build command**
   - In **“Build command”**, enter: **`pnpm run build`**
   - If you prefer npm or Netlify doesn’t use pnpm, use: **`npm run build`**

3. **Publish directory**
   - In **“Publish directory”**, enter: **`dist`**
   - With **Base directory** set to **faith-driven-life-astro**, Netlify will use **faith-driven-life-astro/dist** as the built site. You do **not** need to type **faith-driven-life-astro/dist** here; **`dist`** is correct.

4. Leave other options as default (no need to add env vars unless you use them).

---

## Step 6: Deploy

1. Click **“Deploy site”** (or **“Deploy faith-driven-life”**).
2. Netlify will clone the repo, go into **faith-driven-life-astro**, run **pnpm install** (or **npm install**) and **pnpm run build** (or **npm run build**), then publish the **dist** folder.
3. Wait until the deploy finishes (usually 1–3 minutes). You’ll see **“Published”** or **“Site is live”**.

---

## Step 7: Open your second site

1. At the top of the deploy summary, Netlify shows a link like **“https://random-name-12345.netlify.app”**.
2. Click it to open your **Astro** site (second site).
3. Your **original** site is still at: **https://carlvgraszouw.github.io/faith-driven-life/** (or your custom domain). Nothing there has changed.

---

## Summary

| Site            | URL / Where it lives |
|-----------------|----------------------|
| **Current site** (unchanged) | GitHub Pages, e.g. **https://carlvgraszouw.github.io/faith-driven-life/** |
| **Second site** (Astro)      | Netlify, e.g. **https://something.netlify.app** |

---

## If the build fails

- **“Base directory”** must be exactly **`faith-driven-life-astro`** (no leading slash, no trailing slash).
- **Publish directory** must be **`dist`** (not `faith-driven-life-astro/dist` when Base directory is set).
- If you see **“pnpm: command not found”**, change **Build command** to **`npm run build`** and try again (Netlify will use npm).
- Check the **Deploy log** (click the deploy, then **“Deploy log”**) for the exact error.

---

## Optional: custom subdomain

To use a name like **faith-driven-life-astro.netlify.app**:

1. In Netlify: **Site configuration** (or **Site settings**) → **Domain management** → **Options** → **Edit site name**.
2. Change the random name to **faith-driven-life-astro** (or any available name).
3. Your second site will be at **https://faith-driven-life-astro.netlify.app**.
