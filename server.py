#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
server.py -- Flask backend for Instagram Profile Scraper
Run:  python server.py
Then open:  http://localhost:5000
"""

from flask import Flask, request, jsonify, send_from_directory
import instaloader
import time
import os
from http.cookiejar import MozillaCookieJar

app = Flask(__name__, static_folder=".")

COOKIES_FILE = "cookies.txt"
SESSION_FILE = "ig_session"

# ─────────────────────────────────────────────────────────────
#  Auth helpers
# ─────────────────────────────────────────────────────────────

def build_loader():
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
    return L


def load_session(L):
    # Try cookies.txt first
    if os.path.exists(COOKIES_FILE):
        try:
            jar = MozillaCookieJar(COOKIES_FILE)
            jar.load(ignore_discard=True, ignore_expires=True)
            ig = [c for c in jar if "instagram" in c.domain]
            if ig:
                L.context._session.cookies.update(jar)
                return True
        except Exception:
            pass

    # Try saved session
    if os.path.exists(SESSION_FILE):
        try:
            L.load_session_from_file(username="", filename=SESSION_FILE)
            return True
        except Exception:
            pass

    return False


# ─────────────────────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/scrape", methods=["POST"])
def scrape():
    data      = request.get_json()
    username  = (data.get("username") or "").strip().lstrip("@")
    max_posts = int(data.get("max_posts") or 20)

    if not username:
        return jsonify({"error": "Username is required"}), 400

    L = build_loader()
    if not load_session(L):
        return jsonify({
            "error": "Not authenticated. Make sure cookies.txt is in the project folder."
        }), 401

    # Fetch profile
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        return jsonify({"error": f"Profile '@{username}' not found or is private."}), 404
    except instaloader.exceptions.LoginRequiredException:
        return jsonify({"error": "Login required. Your session may have expired — re-export cookies.txt."}), 401
    except instaloader.exceptions.TooManyRequestsException:
        return jsonify({"error": "Instagram rate limit hit. Please wait a few minutes and try again."}), 429
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Fetch posts
    posts = []
    try:
        for post in profile.get_posts():
            posts.append({
                "number":   len(posts) + 1,
                "likes":    post.likes,
                "comments": post.comments,
                "url":      f"https://www.instagram.com/p/{post.shortcode}/",
                "date":     post.date_utc.strftime("%Y-%m-%d"),
                "caption":  (post.caption or "")[:120],
            })
            if len(posts) >= max_posts:
                break
            time.sleep(1.2)
    except instaloader.exceptions.TooManyRequestsException:
        pass  # Return whatever we got so far
    except Exception:
        pass

    total_likes    = sum(p["likes"]    for p in posts)
    total_comments = sum(p["comments"] for p in posts)

    return jsonify({
        "profile": {
            "username":    profile.username,
            "full_name":   profile.full_name or "",
            "biography":   profile.biography or "",
            "external_url": profile.external_url or "",
            "mediacount":  profile.mediacount,
            "followers":   profile.followers,
            "followees":   profile.followees,
        },
        "posts": posts,
        "summary": {
            "posts_fetched":    len(posts),
            "total_likes":      total_likes,
            "total_comments":   total_comments,
            "avg_likes":        total_likes    // len(posts) if posts else 0,
            "avg_comments":     total_comments // len(posts) if posts else 0,
        }
    })


if __name__ == "__main__":
    print("=" * 50)
    print("  Instagram Scraper Server")
    print("  Open:  http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, port=5000)
