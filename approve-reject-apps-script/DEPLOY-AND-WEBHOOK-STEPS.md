# Step-by-step: Deploy as Web app + Add Formspree webhook

Do this **after** you’ve pasted the full script into Apps Script and set **SPREADSHEET_ID** and **OWNER_EMAIL** in CONFIG.

---

## Part 1: Deploy as Web app

### Step 1: Save the script
- In the Apps Script editor, press **Ctrl+S** (or click the disk icon).

### Step 2: Open the Deploy menu
- Click **Deploy** (top right).
- Click **New deployment**.

### Step 3: Choose Web app
- Next to “Select type”, click the **gear icon** (⚙️).
- Choose **Web app**.
- Click **OK** or continue.

### Step 4: Set deployment options
- **Description:** e.g. `Approve Reject v1` (optional).
- **Execute as:** **Me** (your Google account).
- **Who has access:** **Anyone** (so the Approve/Reject links work without login).
- Click **Deploy**.

### Step 5: Authorize (first time only)
- If Google asks to authorize the app:
  - Click **Authorize access**.
  - Choose your Google account.
  - If you see “Google hasn’t verified this app”: click **Advanced** → **Go to [project name] (unsafe)** → **Allow**.

### Step 6: Copy the Web app URL
- When deployment finishes, a dialog shows **Web app URL**.
- Copy the **entire URL**. It looks like:
  ```text
  https://script.google.com/macros/s/AKfycbx...long_string.../exec
  ```
- Click **Done** (or **Copy** if there is one, then **Done**).

### Step 7: Put the URL in CONFIG
- Back in the Apps Script editor, find **CONFIG** at the top.
- Replace `'YOUR_WEB_APP_URL'` with your copied URL **in quotes**, e.g.:
  ```javascript
  WEB_APP_URL: 'https://script.google.com/macros/s/AKfycbx.../exec'
  ```
- **Save** again (Ctrl+S).

### Step 8: Deploy a new version (so CONFIG is used)
- Click **Deploy** → **Manage deployments**.
- Next to your deployment, click the **pencil icon** (Edit).
- Under **Version**, choose **New version**.
- Optionally change **Description** (e.g. `With WEB_APP_URL set`).
- Click **Deploy**.
- Close the dialog.

Part 1 is done. The Web app is live and the email links will use this URL.

---

## Part 2: Add webhook in Formspree

### Step 1: Open Formspree
- Go to [https://formspree.io](https://formspree.io) and sign in.

### Step 2: Open your form
- Click your form (e.g. **“A Faith Driven Life - Submissions”**).

### Step 3: Go to Webhooks / Integrations
- In the form’s menu, click **Settings** or **Integrations** or **Webhooks** (the exact name depends on Formspree’s current layout).
- Find the **Webhooks** section (where you can add a URL that receives form submissions).

### Step 4: Add the webhook URL
- Click **Add webhook** or **New webhook** (or similar).
- In the **URL** or **Webhook URL** field, paste your **Web app URL** (the same one you put in CONFIG):
  ```text
  https://script.google.com/macros/s/AKfycbx.../exec
  ```
- **Important:** Use the **exec** URL, not a **dev** URL. It must end with `/exec`.
- If there is an option for **Method**, leave it as **POST** (or choose POST).
- If there is an option for **Events**, choose something like “Form submission” or “New submission”.
- Save (e.g. **Save**, **Add**, or **Create**).

### Step 5: Test
- On your site, submit a test comment (or prayer request / testimony).
- Within a short time you should get an email with **Approve** and **Reject** links.
- Click **Approve**. You should see an “Approved” page, and the submission should appear in your Google Sheet’s approved tab and on your site after refresh.

---

## Quick checklist

- [ ] Script saved with SPREADSHEET_ID and OWNER_EMAIL set.
- [ ] Deploy → New deployment → Web app.
- [ ] Execute as: **Me**. Who has access: **Anyone**. Deploy.
- [ ] Authorize if asked.
- [ ] Copy Web app URL, put it in CONFIG as WEB_APP_URL, save.
- [ ] Deploy → Manage deployments → Edit → New version → Deploy.
- [ ] Formspree → your form → Webhooks → Add webhook → paste same URL → Save.
- [ ] Test: submit form → check email → click Approve → check sheet and site.

If something doesn’t work, check **SETUP_APPROVE_REJECT.md** for troubleshooting.
