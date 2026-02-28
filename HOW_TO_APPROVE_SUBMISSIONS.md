# How to approve a submission and show it on the website

When someone submits a comment, prayer request, or testimony, it arrives in **Formspree** (and in your email). To approve it and show it to all visitors:

## Step 1: Decide to approve

In Formspree (or your email), read the submission. When you want to publish it, note:
- **Name** (to show on the site)
- **Date** (e.g. 28 February 2026)
- **Message** (the comment, prayer request, or testimony text)

## Step 2: Open the right file

- **Comments** → open `comments.html`
- **Prayer requests** → open `prayer-requests.html`
- **Testimonies** → open `testimonies.html`

## Step 3: Add a new “approved” block

Find the section that looks like this (the **Published comments** / **Published prayer requests** / **Published testimonies** list):

```html
<div class="approved-list">
  <div class="approved-item">
    <strong>Visitor name</strong> <span class="approved-meta">— Date (example – replace or delete)</span>
    <p>Approved comment text. ...</p>
  </div>
</div>
```

**Add a new block** inside `<div class="approved-list">`, **above** any existing items (so newest appears first). Copy this and fill in the brackets:

```html
<div class="approved-item">
  <strong>[Name of person]</strong> <span class="approved-meta">— [Date, e.g. 28 February 2026]</span>
  <p>[Their message – copy from Formspree. Keep it on one line or use line breaks as needed.]</p>
</div>
```

**Example** (for a comment):

```html
<div class="approved-item">
  <strong>John</strong> <span class="approved-meta">— 28 February 2026</span>
  <p>Thank you for this site. It encouraged me today.</p>
</div>
```

- Replace **name**, **date**, and **message** with the real submission.
- If the message contains **<** or **>** or **&** or **"**, write them in HTML: `&lt;` `&gt;` `&amp;` `&quot;` so the page displays correctly.

## Step 4: Save and push to GitHub

1. Save the file (e.g. `comments.html`).
2. Commit and push to GitHub (same as when you update the site).
3. After GitHub Pages updates (a minute or two), the new item will appear on the live site for all visitors.

---

**Summary:** Approve = add the submission as a new `approved-item` block in the right HTML file, then push. There is no “approve” button; you edit the page and publish what you want visitors to see.
