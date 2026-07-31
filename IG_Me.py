#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
IG_Me.py -- Instagram Profile Scraper
======================================
Login priority:
  1. cookies.txt file  (Netscape format -- export from browser extension)
  2. Saved session     (auto-saved after first successful login)
  3. Secret.txt creds  (username + password -- last resort)

HOW TO GET cookies.txt:
  1. Install Chrome extension: "Get cookies.txt LOCALLY"
     https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
  2. Open instagram.com and make sure you are logged in
  3. Click the extension icon -> click "Export" (make sure domain is instagram.com)
  4. Save the file as  cookies.txt  inside this project folder
  5. Run this script

Usage:
    python IG_Me.py                          # interactive
    python IG_Me.py <username>               # scrape first 20 posts
    python IG_Me.py <username> <max_posts>   # scrape up to N posts

Requirements:
    pip install instaloader
"""

import instaloader
import time
import os
import pandas as pd
from http.cookiejar import MozillaCookieJar

# =====================================================================
#  CONFIG
# =====================================================================

COOKIES_FILE = "cookies.txt"     # Netscape cookie export from browser
SESSION_FILE = "ig_session"      # auto-saved session after first login
SECRET_FILE  = "Secret.txt"      # username line 1, password line 2

DIVIDER_THIN  = "-" * 62
DIVIDER_THICK = "=" * 62


def fmt(n: int) -> str:
    return f"{n:,}"


def print_banner():
    print()
    print(DIVIDER_THICK)
    print("   Instagram Profile Scraper")
    print(DIVIDER_THICK)
    print()


# =====================================================================
#  LOGIN METHOD 1 -- cookies.txt (Netscape format from browser extension)
# =====================================================================

def try_cookies_file(L: instaloader.Instaloader) -> bool:
    """Load a Netscape-format cookies.txt exported from the browser."""
    if not os.path.exists(COOKIES_FILE):
        print(f"  [1] {COOKIES_FILE} not found -- skipping")
        return False
    try:
        print(f"  [1] Loading {COOKIES_FILE} ... ", end="", flush=True)
        jar = MozillaCookieJar(COOKIES_FILE)
        jar.load(ignore_discard=True, ignore_expires=True)
        ig_cookies = [c for c in jar if "instagram" in c.domain]
        if not ig_cookies:
            print("SKIP (no Instagram cookies inside the file)")
            return False
        L.context._session.cookies.update(jar)
        print(f"OK  ({len(ig_cookies)} Instagram cookies loaded)")
        return True
    except Exception as e:
        print(f"FAIL  [{e}]")
        return False


# =====================================================================
#  LOGIN METHOD 2 -- saved session file
# =====================================================================

def try_saved_session(L: instaloader.Instaloader) -> bool:
    """Load a previously saved instaloader session."""
    if not os.path.exists(SESSION_FILE):
        print(f"  [2] No saved session found -- skipping")
        return False
    try:
        print(f"  [2] Loading saved session '{SESSION_FILE}' ... ", end="", flush=True)
        L.load_session_from_file(username="", filename=SESSION_FILE)
        print("OK")
        return True
    except Exception as e:
        print(f"FAIL  [{e}]")
        return False


# =====================================================================
#  LOGIN METHOD 3 -- username + password from Secret.txt
# =====================================================================

def try_password_login(L: instaloader.Instaloader) -> bool:
    """Log in using credentials. Saves session on success."""
    ig_user, ig_pass = None, None

    if os.path.exists(SECRET_FILE):
        try:
            data = pd.read_csv(SECRET_FILE, header=None)
            u = str(data.iloc[0][0]).strip()
            p = str(data.iloc[1][0]).strip()
            if u and u.lower() not in ("username", "") \
               and p and p.lower() not in ("password", ""):
                ig_user, ig_pass = u, p
        except Exception:
            pass

    if not ig_user:
        print("\n  [3] No valid credentials in Secret.txt.")
        print("      Enter your Instagram login:\n")
        ig_user = input("      Instagram username: ").strip()
        ig_pass = input("      Instagram password: ").strip()

    if not ig_user or not ig_pass:
        return False

    try:
        print(f"\n  [3] Logging in as @{ig_user} ... ", end="", flush=True)
        L.login(ig_user, ig_pass)
        print("OK")
        L.save_session_to_file(filename=SESSION_FILE)
        print(f"      Session saved to '{SESSION_FILE}' (next run will skip login)")
        return True
    except instaloader.exceptions.BadCredentialsException:
        print("FAIL  (wrong username or password)")
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("FAIL  (2FA is on -- use cookies.txt method instead)")
    except Exception as e:
        print(f"FAIL  [{e}]")
    return False


# =====================================================================
#  LOGIN ORCHESTRATOR
# =====================================================================

def login(L: instaloader.Instaloader) -> bool:
    print("Authenticating...\n")
    if try_cookies_file(L):
        return True
    if try_saved_session(L):
        return True
    return try_password_login(L)


# =====================================================================
#  CORE SCRAPER
# =====================================================================

def scrape(username: str, max_posts: int) -> None:
    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
    )

    if not login(L):
        print()
        print("[ERROR] All login methods failed.")
        print()
        print("  SOLUTION -- export cookies from Chrome:")
        print("  1. Install: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc")
        print("  2. Open instagram.com (logged in)")
        print("  3. Click the extension -> Export")
        print(f"  4. Save as '{COOKIES_FILE}' in this folder:")
        print(f"     {os.path.abspath('.')}")
        print("  5. Run this script again")
        sys.exit(1)

    print()

    # -- Fetch profile -------------------------------------------------------
    print(DIVIDER_THICK)
    print(f"  Fetching profile: @{username}")
    print(DIVIDER_THICK)

    try:
        profile = instaloader.Profile.from_username(L.context, username)

    except instaloader.exceptions.ProfileNotExistsException:
        print(f"\n[ERROR] Profile '@{username}' not found.")
        print("  - Check the username spelling on instagram.com")
        print("  - Profile may be private (need to follow them)")
        sys.exit(1)

    except instaloader.exceptions.LoginRequiredException:
        print(f"\n[ERROR] Login required to view '@{username}'.")
        sys.exit(1)

    except instaloader.exceptions.ConnectionException as e:
        print(f"\n[ERROR] Connection error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    # -- Profile overview ----------------------------------------------------
    bio = (profile.biography or "").replace("\n", " ")
    bio_display = bio[:80] + ("..." if len(bio) > 80 else "")

    print()
    print(f"  Full Name    : {profile.full_name or 'N/A'}")
    print(f"  Username     : @{profile.username}")
    print(f"  Bio          : {bio_display}")
    print(f"  Website      : {profile.external_url or 'N/A'}")
    print()
    print(DIVIDER_THIN)
    print(f"  {'STAT':<18}  VALUE")
    print(DIVIDER_THIN)
    print(f"  {'Total Posts':<18}  {fmt(profile.mediacount)}")
    print(f"  {'Followers':<18}  {fmt(profile.followers)}")
    print(f"  {'Following':<18}  {fmt(profile.followees)}")
    print(DIVIDER_THIN)

    if profile.mediacount == 0:
        print("\n  This profile has no posts.")
        return

    # -- Per-post table ------------------------------------------------------
    print()
    print(f"  Fetching up to {max_posts} post(s) for @{username}...")
    print()
    print(DIVIDER_THIN)
    print(f"  {'#':<5}  {'Likes':>10}  {'Comments':>10}  URL")
    print(DIVIDER_THIN)

    post_num = total_likes = total_comments = 0

    try:
        for post in profile.get_posts():
            post_num    += 1
            likes        = post.likes
            comments     = post.comments
            url          = f"https://www.instagram.com/p/{post.shortcode}/"

            total_likes    += likes
            total_comments += comments

            print(f"  {post_num:<5}  {fmt(likes):>10}  {fmt(comments):>10}  {url}")

            if post_num >= max_posts:
                leftover = profile.mediacount - post_num
                if leftover > 0:
                    print(f"\n  [Stopped at {max_posts}. {fmt(leftover)} more post(s) not fetched.]")
                break

            time.sleep(1.2)

    except instaloader.exceptions.TooManyRequestsException:
        print("\n[WARNING] Rate limited by Instagram. Wait a few minutes and try again.")
    except KeyboardInterrupt:
        print("\n[INFO] Cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] While reading posts: {e}")

    # -- Summary -------------------------------------------------------------
    print()
    print(DIVIDER_THICK)
    print(f"  SUMMARY -- @{username}")
    print(DIVIDER_THICK)
    print(f"  {'Posts Fetched':<22}: {fmt(post_num)}")
    print(f"  {'Total Likes':<22}: {fmt(total_likes)}")
    print(f"  {'Total Comments':<22}: {fmt(total_comments)}")
    if post_num > 0:
        print(f"  {'Avg Likes / Post':<22}: {fmt(total_likes    // post_num)}")
        print(f"  {'Avg Comments / Post':<22}: {fmt(total_comments // post_num)}")
    print(DIVIDER_THICK)
    print()


# =====================================================================
#  ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    print_banner()

    if len(sys.argv) >= 2:
        target = sys.argv[1].strip().lstrip("@")
    else:
        target = input("  Enter Instagram username to scrape (without @): ").strip().lstrip("@")

    if not target:
        print("[ERROR] Username cannot be empty.")
        sys.exit(1)

    if len(sys.argv) >= 3:
        try:
            max_p = int(sys.argv[2])
        except ValueError:
            max_p = 20
    else:
        raw = input("  How many posts to fetch? [press Enter for 20]: ").strip()
        max_p = int(raw) if raw.isdigit() and int(raw) > 0 else 20

    scrape(target, max_p)
