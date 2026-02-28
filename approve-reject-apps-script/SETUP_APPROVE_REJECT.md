# Set up automated Approve / Reject by email

When someone submits a comment, prayer request, or testimony, you get an **email with two links: Approve** and **Reject**. Click **Approve** → it appears on the site. Click **Reject** → it does not. No manual sheet editing.

---

## What you need

- Your **Google Sheet** (the one already used for the approved list) with:
  - One tab that has **Type | Name | Date | Message** (this is the one published as CSV). Note its tab name (e.g. `Sheet1`).
  - A second tab named **Pending** (you will create this in Step 2).
- Your **Formspree** form ID (already in use on the site).
- About 15 minutes.

---

## Step 1: Get your Spreadsheet ID

1. Open your Google Sheet (the one with Type, Name, Date, Message).
2. Look at the URL in the browser. It looks like:
   ```text
   https://docs.google.com/spreadsheets/d/1a2B3c4D5e6F7g8H9i0J/edit
   ```
3. Copy the part between `/d/` and `/edit`. That is your **Spreadsheet ID** (e.g. `1a2B3c4D5e6F7g8H9i0J`).

---

## Step 2: Add the Pending tab

1. In the same spreadsheet, click the **+** at the bottom to add a new sheet.
2. Name it **Pending** (right‑click the tab → Rename).
3. You can leave it empty; the script will add headers and rows.

---

## Step 3: Create the Apps Script project

1. In the spreadsheet menu: **Extensions → Apps Script**.
2. If asked, name the project (e.g. "Approve Reject").
3. You’ll see a file `Code.gs`. **Select all** (Ctrl+A) and **delete**.
4. Open the file **`approve-reject-apps-script/Code.gs`** from your website project folder (in Cursor/VS Code). Copy **all** its contents and paste into the Apps Script editor.
5. At the top of the pasted code, edit **CONFIG**:

   - **SPREADSHEET_ID**  
     Paste the ID you copied in Step 1 (replace `YOUR_SPREADSHEET_ID`).

   - **OWNER_EMAIL**  
     Your email where you want the Approve/Reject emails (replace `YOUR_EMAIL@gmail.com`).

   - **APPROVED_SHEET_NAME**  
     The exact name of the tab that has Type, Name, Date, Message (e.g. `Sheet1`). This is the tab you publish as CSV for the site.

   - **PENDING_SHEET_NAME**  
     Leave as `Pending` if you named the new tab that.

   - **WEB_APP_URL**  
     Leave as `YOUR_WEB_APP_URL` for now. You’ll come back after the first deploy.

6. Click **Save** (disk icon or Ctrl+S).

---

## Step 4: Deploy as Web App

1. In Apps Script: **Deploy → New deployment**.
2. Click the gear icon next to "Select type", choose **Web app**.
3. Set:
   - **Description:** e.g. "Approve Reject"
   - **Execute as:** **Me** (your Google account)
   - **Who has access:** **Anyone** (so the links in the email work without login)
4. Click **Deploy**.
5. If asked to authorize the app, click **Authorize access**, choose your Google account, then **Advanced** → "Go to [project name] (unsafe)" → **Allow**.
6. When the deployment is done, copy the **Web app URL**. It looks like:
   ```text
   https://script.google.com/macros/s/AKfycbx.../exec
   ```
7. Go back to **Code.gs**, set **WEB_APP_URL** to this URL (in quotes), then **Save**.
8. **Deploy → Manage deployments** → open the three dots next to your deployment → **Edit** → set **Version** to **New version** → **Deploy**. (So the updated CONFIG is used.)

---

## Step 5: Add Formspree webhook

1. Go to [Formspree.io](https://formspree.io) and sign in.
2. Open your form (**"A Faith Driven Life - Submissions"** or the one you use).
3. Go to **Settings** (or **Integrations**).
4. Find **Webhooks** (or **Webhook**). Add a new webhook:
   - **URL:** paste your **Web app URL** from Step 4 (the `https://script.google.com/.../exec` one).
   - **Events:** if there is an option, choose “Form submission” or “New submission”.
5. Save.

From now on, when someone submits the form, Formspree will send the data to your script. The script will add the submission to the Pending sheet and send you an email with **Approve** and **Reject** links.

---

## Step 6: Test

1. Submit a test comment (or prayer request / testimony) from your site.
2. Check your inbox. You should get an email with:
   - The submission details
   - A green **Approve** link and a red **Reject** link
3. Click **Approve**. The browser should show “Approved” and the submission should appear in the **Approved** tab (the one with Type, Name, Date, Message).
4. Refresh your site’s Comments (or Prayer requests / Testimonies) page. The new row should appear in the published list.

---

## Troubleshooting

- **No email**  
  Check Formspree webhook is set to your Web app URL. Check spam. In Apps Script, **Executions** (left sidebar) shows if `doPost` ran and any errors.

- **“Sheet not found”**  
  Check CONFIG: **APPROVED_SHEET_NAME** and **PENDING_SHEET_NAME** match the tab names exactly (case-sensitive).

- **Approve link does nothing or error**  
  Make sure **WEB_APP_URL** in CONFIG is the full `.../exec` URL and you deployed a **new version** after changing it.

- **Submission appears with wrong type**  
  The script infers type from the form’s subject line (“New comment”, “Prayer request”, “Testimony”). Your hidden `_subject` fields on the site already set these; no change needed unless you use different wording.

---

## Summary

1. Spreadsheet ID and Pending tab in the sheet.  
2. Apps Script: paste `Code.gs`, set CONFIG (sheet ID, your email, tab names, then Web app URL after first deploy).  
3. Deploy as Web app, **Anyone** can access, copy the URL.  
4. Put that URL in CONFIG, save, deploy **new version**.  
5. Formspree → Webhooks → add that same URL.  
6. Test: submit → email → Approve → row appears on sheet and on site.

After this, approving is just clicking **Approve** in the email; no manual sheet editing.
