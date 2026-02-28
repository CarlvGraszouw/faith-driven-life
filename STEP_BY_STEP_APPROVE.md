# Step-by-step: Approve a submission and show it on the site

Follow these steps whenever you want to approve a comment, prayer request, or testimony so visitors can see it.

---

## Part 1: One-time setup (already done if you added your sheet URL)

- [x] Formspree form is set up and submissions go to your email.
- [x] Google Sheet has columns: **Type** | **Name** | **Date** | **Message**.
- [x] Sheet is published as CSV and the URL is in **approved-list-config.js**.

If any of that is not done, see **APPROVE_VIA_GOOGLE_SHEET.md**.

---

## Part 2: Each time you want to approve something

### Step 1: Open the submission

- Go to [Formspree](https://formspree.io) and sign in, **or**
- Open the email Formspree sent you.

Note:
- **Name** of the person  
- **Date** (e.g. today: 28 February 2026)  
- **Message** (the full comment, prayer request, or testimony)

### Step 2: Decide which section it belongs to

- Comment → you’ll use type **comment**
- Prayer request → you’ll use type **prayer**
- Testimony → you’ll use type **testimony**

### Step 3: Open your Google Sheet

- Go to [Google Sheets](https://sheets.google.com).
- Open the spreadsheet you use for approved submissions (the one whose CSV URL is in **approved-list-config.js**).

### Step 4: Add one new row

- Click the first empty row below the header (Row 2, then 3, then 4, etc.).
- Fill the cells in that row:

| Column   | What to type |
|----------|----------------|
| **Type** | Exactly one word: `comment` or `prayer` or `testimony` (lowercase). |
| **Name** | The person’s name (as they wrote it). |
| **Date** | The date, e.g. `28 February 2026`. |
| **Message** | The full message (copy from Formspree or the email). |

Example:

| Type     | Name  | Date            | Message                          |
|----------|-------|-----------------|----------------------------------|
| comment  | John  | 28 February 2026| Thank you, this encouraged me.   |

- The sheet will auto-save (or press **Ctrl+S** / **Cmd+S**).

### Step 5: Check the website

- Open your site’s **Comments**, **Prayer requests**, or **Testimonies** page (depending on the type you used).
- Refresh the page (F5 or Ctrl+R).
- The new row should appear in the “Published” list.

---

## Summary

1. Read the submission (Formspree or email).  
2. Open your Google Sheet.  
3. Add a row: **Type** = `comment` / `prayer` / `testimony`, then **Name**, **Date**, **Message**.  
4. Save the sheet (if needed).  
5. Refresh the relevant page on your site.

No HTML editing and no push to GitHub for each approval. The site loads the list from your sheet automatically.
