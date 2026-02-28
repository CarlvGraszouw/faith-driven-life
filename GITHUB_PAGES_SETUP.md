# Publish this website on GitHub Pages (free)

Follow these steps to put your site online at `https://YOUR_USERNAME.github.io/REPO_NAME/` or a custom URL.

---

## Step 1: Install Git (if you don’t have it)

1. Go to **https://git-scm.com/download/win**
2. Download and run the Windows installer
3. Use the default options and finish the install
4. **Close and reopen** any terminal/Cursor/PowerShell so Git is recognized

To check: open a new terminal and run `git --version`. You should see a version number.

---

## Step 2: Create a new repository on GitHub

1. Go to **https://github.com** and sign in (or create a free account)
2. Click the **+** (top right) → **New repository**
3. **Repository name:** e.g. `faith-driven-life` or `my-website`
4. **Public**
5. **Do not** check “Add a README” (your folder already has files)
6. Click **Create repository**

You’ll see a page with “Quick setup” and a URL like  
`https://github.com/YOUR_USERNAME/faith-driven-life.git`  
Keep this page open.

---

## Step 3: Push your website folder to GitHub

Open **PowerShell** or **Command Prompt** and run these commands **one at a time**.  
Replace `YOUR_USERNAME` and `faith-driven-life` with your GitHub username and repo name.

```powershell
cd "c:\My Website"
```

```powershell
git init
```

```powershell
git add .
```

```powershell
git commit -m "Initial commit - A Faith Driven Life website"
```

```powershell
git branch -M main
```

```powershell
git remote add origin https://github.com/YOUR_USERNAME/faith-driven-life.git
```

```powershell
git push -u origin main
```

- If it asks to log in, use your **GitHub username** and a **Personal Access Token** (not your normal password).  
  To create a token: GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**. Give it a name, tick **repo**, generate, then copy and paste it when the terminal asks for a password.

---

## Step 4: Turn on GitHub Pages

1. On GitHub, open your repository (e.g. `faith-driven-life`)
2. Click **Settings** → in the left sidebar click **Pages**
3. Under **Source**, choose **Deploy from a branch**
4. Under **Branch**: select **main**, folder **/ (root)**
5. Click **Save**

After 1–2 minutes your site will be live at:

**https://YOUR_USERNAME.github.io/faith-driven-life/**

(Use your real username and repo name.)

---

## Step 5 (important): Fix links so they work on GitHub Pages

GitHub Pages often serves the site from a **subpath** (e.g. `/faith-driven-life/`), so links like `href="blogs.html"` can break.

**Option A – Use a repo named exactly `YOUR_USERNAME.github.io`**

- Create a **new** repo named **exactly** your GitHub username + `.github.io`  
  Example: if your username is `carlwilma`, repo name: `carlwilma.github.io`
- Push your website files to that repo (same steps as above, but use this repo URL)
- Then the site is at **https://YOUR_USERNAME.github.io** (no extra path), and your current links will work as-is.

**Option B – Keep a repo like `faith-driven-life`**

- The site will be at `https://YOUR_USERNAME.github.io/faith-driven-life/`
- So the “root” of the site is not `/` but `/faith-driven-life/`.  
  I can add a small script or base tag so all links (Home, Blogs, etc.) work from that path. If you want this, say “fix links for GitHub subpath” and I’ll give you the exact code changes.

---

## Updating the site later

After you change files in `c:\My Website`:

```powershell
cd "c:\My Website"
git add .
git commit -m "Update site"
git push
```

GitHub will rebuild the site; changes usually appear within a minute.

---

## Summary

| Step | Action |
|------|--------|
| 1 | Install Git from git-scm.com |
| 2 | Create a new repo on GitHub (e.g. `faith-driven-life` or `USERNAME.github.io`) |
| 3 | In `c:\My Website` run: `git init`, `git add .`, `git commit -m "Initial commit"`, `git branch -M main`, `git remote add origin https://github.com/USERNAME/REPO.git`, `git push -u origin main` |
| 4 | Repo **Settings** → **Pages** → Source: **Deploy from a branch** → branch **main**, folder **/ (root)** → Save |
| 5 | Use repo name `USERNAME.github.io` for root URL, or ask for “fix links for GitHub subpath” |

Your site will be live at **https://YOUR_USERNAME.github.io/REPO_NAME/** (or **https://YOUR_USERNAME.github.io** if the repo is `USERNAME.github.io`).
