# Selling your book on the website

Your site has a **Book** page (`book.html`). To sell your book, you do two things: (1) put it on a sales platform and get a link, (2) put that link (and your cover + description) on the Book page.

---

## Option 1: Gumroad (good for digital or print)

- **Site:** [gumroad.com](https://gumroad.com)
- **Free to start.** They take a small fee per sale.
- **Steps:**
  1. Sign up, create a product (your book).
  2. Upload a PDF (ebook) or set it as a physical product and connect shipping.
  3. Set your price. Gumroad gives you a link like `https://gumroad.com/l/YourBook`.
  4. In `book.html`, set the **“Buy now”** button `href` to that link.
  5. Add your book title, description, and cover image (e.g. `book-cover.jpg` in the same folder as `book.html`).

---

## Option 2: Payhip (similar to Gumroad)

- **Site:** [payhip.com](https://payhip.com)
- Create a product, set price, get a checkout link.
- Put that link in the **“Buy now”** button in `book.html`.

---

## Option 3: Amazon (KDP)

- **Site:** [kdp.amazon.com](https://kdp.amazon.com)
- Publish your book as ebook and/or paperback. Amazon handles payment and (for print) printing and shipping.
- When the book is live, copy its Amazon product page URL (e.g. `https://www.amazon.com/dp/XXXXXXXX`).
- In `book.html`, you can:
  - Make **“Buy now”** point to that Amazon link, or
  - Keep **“Buy now”** for Gumroad/Payhip and set **“Also on Amazon”** to the Amazon link.

---

## What to edit in `book.html`

1. **Cover image**  
   Add a file named `book-cover.jpg` (or `.png`) in the same folder as `book.html`, or put it in an `images` folder and set:  
   `src="images/book-cover.jpg"`.

2. **Title**  
   Replace “Your Book Title Here” with your real book title.

3. **Byline and format**  
   Replace “By Carl and Wilma · Paperback / eBook” with your name(s) and format (e.g. “Paperback & Kindle”).

4. **Description**  
   Replace the placeholder paragraph with a short blurb for your book.

5. **Buy links**  
   - **Buy now:** set `href="#"` to your Gumroad, Payhip, or Amazon link.  
   - **Also on Amazon:** set that `href` to your Amazon link, or remove the button if you’re not using Amazon.

---

## Summary

| Step | Action |
|------|--------|
| 1 | Choose Gumroad, Payhip, and/or Amazon and create your book product. |
| 2 | Get the checkout or product URL. |
| 3 | In `book.html`, add your cover image, title, description, and paste the link(s) into the button(s). |
| 4 | Push the updated `book.html` (and any new image) to GitHub so the live site updates. |

No backend or payment code is needed on your site; the sales platform handles payments and delivery.
