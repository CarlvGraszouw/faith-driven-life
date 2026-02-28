# Approve submissions via Google Sheet (no HTML editing)

Approved comments, prayer requests, and testimonies are now **loaded from a Google Sheet**. When you approve a submission from Formspree, you only add a row to the sheet — no code or push needed. The site fetches the sheet and shows the list.

---

## One-time setup

### 1. Create the Google Sheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet.
2. Name it (e.g. "A Faith Driven Life – Approved").
3. In the **first row**, put these column headers exactly:
   - **Type** | **Name** | **Date** | **Message**
4. (Optional) Add one test row to check:
   - `comment` | `Test User` | `28 February 2026` | `This is a test.`

### 2. Publish the sheet to the web

1. In the sheet: **File → Share → Publish to web**.
2. Under "Link", choose **Entire document** or the sheet tab that has your table.
3. Format: **Comma-separated values (.csv)**.
4. Click **Publish**. Copy the URL (it looks like  
   `https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=0`).

### 3. Put the URL in your site

1. Open **`approved-list-config.js`** in your project.
2. Replace the placeholder URL with your published CSV URL:
   ```js
   window.APPROVED_SHEET_CSV_URL = 'https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=0';
   ```
   (Use the URL you copied; the part after `/d/` is your sheet ID.)
3. Save and push to GitHub so the live site uses this file.

---

## How to approve a submission

1. You receive the submission in **Formspree** (or by email).
2. Open your **Google Sheet** (the one you published).
3. Add a **new row**:
   - **Type:** `comment`, `prayer`, or `testimony` (one word, lowercase).
   - **Name:** their name.
   - **Date:** e.g. `28 February 2026`.
   - **Message:** what they wrote (copy from Formspree).
4. Save the sheet (Ctrl+S or it auto-saves).

The site loads the sheet when someone visits Comments, Prayer requests, or Testimonies. New rows appear there within a short time (visitors may need to refresh). No HTML editing and no push to GitHub for each approval.

---

## Notes

- **Type** must be exactly: `comment`, `prayer`, or `testimony`.
- The **Comments** page shows rows where Type = `comment`; **Prayer requests** shows `prayer`; **Testimonies** shows `testimony`.
- If you don’t set up the sheet or leave the URL as `YOUR_SHEET_ID`, the “Published” lists will stay empty and the site will still work.
