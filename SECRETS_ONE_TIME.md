# One-time setup (about 3 minutes)

After this, **every `git push` to `main`** deploys the site via GitHub Actions. You do **not** need Cloudflare’s “Connect Git” build or a deploy command in the Pages UI.

## 1. Get your Cloudflare Account ID

- Log in to [dash.cloudflare.com](https://dash.cloudflare.com).
- Open **Workers & Pages** (or any account page). The **Account ID** is in the **right-hand sidebar** on Workers & Pages, or in the URL: `dash.cloudflare.com/<THIS_IS_ACCOUNT_ID>/...`

Copy that 32-character hex string.

## 2. Create an API token

1. Open **[API Tokens](https://dash.cloudflare.com/profile/api-tokens)**.
2. **Create token** → **Create Custom Token**.
3. **Permissions:**
   - **Account** → **Cloudflare Pages** → **Edit**
   - **Account** → **Account Settings** → **Read** (if available; helps Wrangler resolve the account)
4. **Account resources:** Include → **This account** (your account).
5. **Create token**, then **copy the token** (shown once).

## 3. Pages project name

The workflow deploys to **`faith-driven-life`**. If you need another name, edit `.github/workflows/deploy-cloudflare-pages.yml` (`--project-name=...`).

If the first deploy fails with “project not found”, either:

- Create an empty **Pages** project named `faith-driven-life` (**Workers & Pages** → **Create**), **or**
- Run once on your PC (after `npx wrangler login`):  
  `npx wrangler pages project create faith-driven-life --production-branch=main`

## 4. Add GitHub Actions secrets (only two)

Repo: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Name | Value |
|------|--------|
| `CLOUDFLARE_API_TOKEN` | Paste the API token from step 2 |
| `CLOUDFLARE_ACCOUNT_ID` | Paste Account ID from step 1 |

## 5. Turn off duplicate Cloudflare Git builds (important)

If you previously connected **this repo** to Cloudflare Pages **Git integration**, open that Pages project → **Settings** → **Builds** / **Git** → **Disconnect** the repository.

Otherwise you may get **two** deploys per push (Cloudflare build + GitHub Action).

## 6. Custom domain (one-time)

Still one dashboard step: **Workers & Pages** → your project → **Custom domains** → add `www` / apex. DNS can stay at Cloudflare or your registrar per Cloudflare’s wizard.

After that, **push to `main`** and watch **Actions** → **Deploy Cloudflare Pages**.
