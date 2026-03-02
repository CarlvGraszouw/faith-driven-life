# Neon database – step-by-step guide

Use this guide to set up and use your Neon PostgreSQL database safely with this project.

---

## Step 1: Rotate your database password (if you shared it)

Because the connection string was shared in chat, create a new password so the old one is no longer valid.

### Option A: From the Neon Console UI

1. Go to **https://console.neon.tech** and open your project **A FAITH DRIVEN LIFE**.
2. **Click on the branch name** (e.g. **production**) in the left sidebar under **BRANCH** — or click the **production** row on the Branches page — so you’re **inside** the branch (you should see **Overview**, **SQL Editor**, **Tables**, etc.).
3. Look for one of these:
   - A **Roles**, **Roles & Databases**, or **Connection details** tab or section.
   - Or on the **Dashboard**, click **Connect** and see if there’s a **Reset password** / **Regenerate password** link next to the connection string.
4. If you see a **role** (e.g. **neondb_owner**), open its **menu** (⋮ or dropdown) and choose **Reset password**. Copy the new password and use it in your connection string.

If you still don’t see any of that, use **Option B** below.

### Option B: Reset password with SQL (always works)

1. In the Neon Console, under **BRANCH**, click **production** so you’re in the branch.
2. Open the **SQL Editor** tab.
3. Run this (replace `YourNewSecurePassword123` with a strong password you choose):

   ```sql
   ALTER USER neondb_owner WITH PASSWORD 'YourNewSecurePassword123';
   ```

4. Click **Run**. The password for `neondb_owner` is now updated.
5. Build your new connection string: use your **existing** connection string and replace only the **password** part (between the first `:` and the `@`) with `YourNewSecurePassword123`. Example format:
   `postgresql://neondb_owner:YourNewSecurePassword123@ep-polished-cell-a8lepn0g-pooler.eastus2.azure.neon.tech/neondb?sslmode=require`

---

## Step 2: Create a `.env` file in your project

The connection string must stay only on your computer and **never** be committed to Git.

1. Open your project folder in File Explorer: **`C:\My Website`**
2. In that folder (same level as `index.html`), create a new file named exactly: **`.env`**
   - In Notepad: Save As → File name: `.env` → Save as type: **All Files** → Encoding: UTF-8.
   - In Cursor/VS Code: Right‑click in the file list → New File → name it `.env`
3. Open `.env` and add **one line** (replace the value with your **new** connection string from Step 1):

   ```
   DATABASE_URL=postgresql://neondb_owner:YOUR_NEW_PASSWORD@ep-polished-cell-a8lepn0g-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require
   ```

   - Replace `YOUR_NEW_PASSWORD` with the password you set in Step 1.
   - There should be **no spaces** around the `=`.
   - Do not add quotes around the value unless your app explicitly expects them.

4. Save the file and close it.

---

## Step 3: Confirm `.env` is not committed to Git

1. In a terminal (Command Prompt or PowerShell), go to your project:
   ```bat
   cd "C:\My Website"
   ```
2. Run:
   ```bat
   git status
   ```
3. **Check:** `.env` should **not** appear in the list of changed or untracked files.  
   If it does **not** appear, you’re good — `.env` is ignored.  
   If it **does** appear, do **not** run `git add .env` or `git add .`; the project’s `.gitignore` should already include `.env`. Tell your developer or re-check `.gitignore`.

---

## Step 4: Use the database (options)

### Option A: Neon extension in Cursor

1. In Cursor, open the **Neon** extension (sidebar or Extensions).
2. It will use its own login; you don’t need to paste the connection string there.
3. You can run SQL, create tables, and browse data from the extension.

### Option B: Local script (Node.js)

1. Install the Postgres client (in your project folder):
   ```bat
   npm init -y
   npm install pg
   ```
2. Create a file e.g. `scripts/test-db.js` that reads `DATABASE_URL` from `process.env` (e.g. using `dotenv`) and connects.  
   Run it with:
   ```bat
   node scripts/test-db.js
   ```
   Never commit the connection string inside the script; always use `.env` and keep `.env` out of Git.

### Option C: Use from a backend later

When you add a backend (e.g. serverless functions on Vercel/Netlify), set **DATABASE_URL** in that platform’s environment variables (dashboard → Settings → Environment variables) and use the same connection string there. Do not put it in front-end code or in the HTML/JS that runs in the browser.

---

## Quick checklist

- [ ] Step 1: New password set in Neon Console; new connection string copied
- [ ] Step 2: `.env` created in `C:\My Website` with `DATABASE_URL=...` (new password)
- [ ] Step 3: `git status` does **not** show `.env`
- [ ] Step 4: Using Neon via extension, a local script, or a backend — never in browser code

---

## If something goes wrong

- **“Password authentication failed”**  
  Use the connection string that Neon shows **after** you reset the password in Step 1.

- **`.env` still appears in `git status`**  
  Ensure the file is named exactly `.env` (with the leading dot) and is in `C:\My Website`. Check that `.gitignore` contains a line with `.env`.

- **Using the database from your website forms**  
  The current site is static (GitHub Pages). To save form data to Neon you need a small backend (e.g. serverless functions) that receives the form and writes to Postgres; the connection string stays only in that backend’s environment.
