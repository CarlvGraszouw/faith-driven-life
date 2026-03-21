# Host large audio on Cloudflare R2 (same account as Pages)

Your MP3 is valid; **Cloudflare Pages** only limits **each file to 25 MiB**. **R2** is object storage in the same Cloudflare account—good for **~70 MB** files and simple **upload** in the dashboard.

## 1. Create a bucket

1. Open **R2** in the dashboard: [Workers & Pages → R2](https://dash.cloudflare.com/?to=/:account/r2/overview) (or **Storage → R2**).
2. **Create bucket**.
3. Name it something clear, e.g. **`faith-driven-life-audio`** (names must be unique on your account).

## 2. Make the bucket readable on the web (public URL)

1. Open the bucket → **Settings**.
2. Under **Public Development URL**, click **Enable** (Cloudflare shows a warning; this URL is rate‑limited and meant for light / dev-style traffic; for heavy production traffic, use a **custom domain** on the same bucket—see [Public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/)).
3. Confirm with **`allow`** when asked.
4. Note the **Public Bucket URL** (looks like `https://pub-….r2.dev`). You will append the **object path** after it.

## 3. (Recommended) CORS so your site can use the file

If the audio is loaded from a **different hostname** than the MP3 (e.g. site on `pages.dev` and file on `r2.dev`), add a **CORS policy** on the bucket:

1. Bucket → **Settings** → **CORS policy** → **Add CORS policy**.
2. Open **`docs/r2-cors-policy.example.json`** in this repo, replace the example origins with your real site origins (no trailing slash), save, paste the JSON into the dashboard **JSON** tab, then **Save**.

Include at least:

- `https://faith-driven-life.pages.dev`
- Your custom domain(s), e.g. `https://www.afaithdrivenlife.com` and `https://afaithdrivenlife.com` once DNS is on Cloudflare.

## 4. Upload the MP3

**Option A — Dashboard (easiest)**

1. Open the bucket → **Objects** → **Upload**.
2. Upload your file. Prefer a **simple key** without spaces, e.g. `audio/the-supreme-commission.mp3` (create an `audio` “folder” by typing that path in the upload name/path field if the UI asks).
3. After upload, open the object; copy the **public URL** if the UI offers it, or build it as:

   **`{Public Bucket URL from step 2}` + `/` + `object key`**

   Example: `https://pub-xxxxx.r2.dev/audio/the-supreme-commission.mp3`

**Option B — Wrangler CLI (from your PC)**

1. Install/use Wrangler: `npx wrangler@4 login` (browser auth).
2. Run (adjust bucket name and paths):

   ```bash
   npx wrangler@4 r2 object put "faith-driven-life-audio/audio/the-supreme-commission.mp3" --file="audio/The Supreme Commission.mp3" --content-type="audio/mpeg" --remote
   ```

3. Your public URL is still **`{Public Bucket URL}/audio/the-supreme-commission.mp3`**.

See also: `scripts/upload-audio-to-r2.ps1` in this repo.

## 5. Point the website at the file

1. Open **`audio.html`** in this repo.
2. Find the script block that sets **`REMOTE_SUPREME_COMMISSION_MP3_URL`**.
3. Paste your **full HTTPS URL** to the MP3 (one line, in quotes).
4. Commit and push; GitHub Actions will deploy the updated page.

For **local testing only**, leave that variable **empty** so the page keeps using the file under **`audio/`** on disk.

## Optional: Production custom domain for audio

For production, Cloudflare recommends attaching your **own domain** to the bucket instead of relying only on `r2.dev`. See [Connect a bucket to a custom domain](https://developers.cloudflare.com/r2/buckets/public-buckets/#connect-a-bucket-to-a-custom-domain) (domain must be on the same Cloudflare account).
