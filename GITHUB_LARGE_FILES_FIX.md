# Fixing GitHub Large-File and Repo-Size Issues

## What’s going on

1. **“See https://gh.io/lfs” warning**  
   One of your audio files (**The Supreme Commission.mp3**, ~69 MB) is over GitHub’s **50 MB** “warning” limit. The push still succeeds, but GitHub suggests using Git LFS for large files.

2. **~1.37 GiB**  
   An **Android Studio installer** (`downloads/android-studio-panda1-patch1-windows.exe`, ~1.28 GB) was committed earlier. It was removed from the **current** branch history with `git filter-branch`, but:
   - **Remote:** After a successful **force push**, the repo on GitHub only has the cleaned history (no exe).
   - **Local:** Your local clone can still show **size-pack: 1.37 GiB** because the old pack file may still contain the exe blob until the repo is fully repacked or re-cloned.

3. **Committer identity warning**  
   Git is using a name/email inferred from your machine. You can set them explicitly to get rid of the warning.

---

## 1. Fix committer identity (optional)

In **Git Bash**:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

To fix the **last** commit only:

```bash
git commit --amend --reset-author --no-edit
git push --force
```

---

## 2. Shrink your local repo (if it still shows ~1.37 GiB)

If `git count-objects -vH` still reports **size-pack: 1.37 GiB**, the smallest and safest fix is a **fresh clone** (your remote is already clean after force push):

```bash
cd /c/
mv "My Website" "My Website backup"
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git "My Website"
cd "My Website"
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub repo URL. The new clone will only have the cleaned history (~100–150 MB).

---

## 3. What to do about the LFS warning (69 MB audio file)

Your files are **under 100 MB**, so GitHub does **not** block the push; you only get a recommendation to use LFS.

You have three options:

### Option A: Do nothing (simplest)

- The warning is harmless; the site and repo keep working.
- Repo stays a bit larger and clones a bit slower.

### Option B: Host audio outside Git (no LFS, smaller repo)

1. **Upload the two MP3s elsewhere**, e.g.:
   - **GitHub Releases:** Repo → Releases → “Create a new release” → attach the two MP3s, then use the “attachment” URLs in your HTML.
   - Or Google Drive, OneDrive, or your own server (get a direct link).
2. **Remove the audio files from the repo** (and from history) and **point the site to the new URLs** in `audio.html`.
3. **Rewrite history** so the MP3s are gone from all commits, then **force push** (same idea as with the exe).

Result: no large files in Git, no LFS, no 50 MB warning.

### Option C: Use Git LFS for the audio files

1. Install Git LFS: <https://git-lfs.com/>  
2. In your repo (e.g. in Git Bash):

   ```bash
   git lfs install
   git lfs track "audio/*.mp3"
   git add .gitattributes
   git add audio/*.mp3
   git commit -m "Track audio with Git LFS"
   git push
   ```

3. If the MP3s are already in history, migrate them:

   ```bash
   git lfs migrate import --include="audio/*.mp3" --everything
   git push --force
   ```

Then future pushes use LFS for those files and the LFS warning from GitHub should no longer apply.

---

## 4. Prevent large files in the future

Your **`.gitignore`** already includes:

- `downloads/`
- `*.exe`, `*.dmg`, `*.pkg`

So the Android Studio installer (and similar) won’t be committed again. Keep audio in the repo, in LFS, or host it elsewhere—all are valid; choose what you prefer for size and simplicity.

---

## Quick reference

| Issue              | Action                                                                 |
|--------------------|------------------------------------------------------------------------|
| LFS warning        | Option A (ignore), B (host audio elsewhere), or C (use Git LFS).       |
| Local repo 1.37 GB | Fresh clone from GitHub (after force push) or keep as-is.              |
| Committer warning  | `git config --global user.name "..."` and `user.email "..."`.         |
| Avoid big files    | Keep `.gitignore` as-is; don’t commit `downloads/` or huge binaries.  |
