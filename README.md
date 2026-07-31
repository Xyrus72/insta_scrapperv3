# Instagram Profile Scraper

A Python scraper that logs in using **your existing browser cookies** (Chrome / Firefox / Edge) — no password file, no Selenium, no ChromeDriver needed.

Given any **public** Instagram username it returns:

- Total Posts, Followers, Following
- Per-post **Likes** and **Comments** count
- Average Likes & Comments across all fetched posts

---

## Requirements

```
Python 3.8+
instaloader
browser-cookie3
```

Install dependencies:

```bash
pip install instaloader browser-cookie3
```

---

## How It Works

1. Reads your Instagram session straight from **Chrome / Firefox / Edge** cookies
2. No password is stored anywhere
3. Uses the [instaloader](https://instaloader.github.io/) library to fetch profile data via Instagram's API

---

## Run

**Interactive (prompts you for everything):**

```bash
python IG_Me.py
```

**Pass username directly:**

```bash
python IG_Me.py cristiano
```

**Pass username + how many posts to fetch:**

```bash
python IG_Me.py cristiano 50
```

---

## Important Notes

- You must be **logged into Instagram** in Chrome, Firefox, or Edge on this PC
- **Close Chrome** before running (Chrome locks its cookie database while open)
- Works on **public profiles** only
- On Windows you may need to run as **Administrator** if cookies can't be read
- Instagram may rate-limit after many requests — a 1.2 s delay per post is built in

---

## Output Example

```
╔════════════════════════════════════════════════════════════╗
║          Instagram Profile Scraper — Cookie Auth           ║
║       No password needed  |  Public profiles only          ║
╚════════════════════════════════════════════════════════════╝

Loading Instagram session from browser cookies...
  Trying Chrome cookies ... OK

══════════════════════════════════════════════════════════════
  Fetching: @cristiano
══════════════════════════════════════════════════════════════

  Full Name    : Cristiano Ronaldo
  Username     : @cristiano
  Bio          : ...
  Website      : N/A

  STAT              VALUE
  ──────────────────────────────────────────────────────────
  Total Posts       913
  Followers         649,191,284
  Following         572
  ──────────────────────────────────────────────────────────

  #      Likes    Comments  URL
  ──────────────────────────────────────────────────────────
  1      4,812,003      14,302  https://www.instagram.com/p/...
  2      3,901,221      11,100  https://www.instagram.com/p/...
  ...

══════════════════════════════════════════════════════════════
  SUMMARY — @cristiano
══════════════════════════════════════════════════════════════
  Posts Fetched         : 20
  Total Likes           : 68,000,000
  Total Comments        : 200,000
  Avg Likes / Post      : 3,400,000
  Avg Comments / Post   : 10,000
══════════════════════════════════════════════════════════════
```
