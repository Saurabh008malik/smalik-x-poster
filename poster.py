"""Smalik Cricket Poster — posts queued items to X (@Smalik_wc) and the Cricket Ki Baat Facebook Page.

Queue format: queue/<name>.json
{
  "text": "tweet text",                     # X post
  "image": "<name>.png",                    # X card (16:9)
  "created_at": "ISO-8601 with timezone",
  "platforms": ["x", "facebook"],           # optional, default ["x"]
  "facebook": {                             # needed when "facebook" is in platforms
    "caption": "Hinglish caption",
    "first_comment": "optional first comment",
    "image": "<name>-fb.jpg"                # portrait card (4:5)
  }
}

Rules: posts after DELAY_MINUTES (0 = right away); one item per run; max MAX_POSTS_PER_DAY items per IST day.
Each platform is attempted independently. Item -> posted/ if at least one platform worked, else failed/.
"""
import base64
import datetime as dt
import json
import os
import pathlib
import shutil
import sys

import requests
from requests_oauthlib import OAuth1

import igpost

DELAY_MINUTES = 0
MAX_POSTS_PER_DAY = 20
X_MAX_AGE_MINUTES = 360   # X never gets old news: anything queued longer than this is skipped, not posted late
GRAPH = "https://graph.facebook.com/v26.0"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

ROOT = pathlib.Path(__file__).parent
QUEUE, POSTED, FAILED = ROOT / "queue", ROOT / "posted", ROOT / "failed"


# ---------------- X ----------------
def x_auth():
    return OAuth1(os.environ["X_CONSUMER_KEY"], os.environ["X_CONSUMER_SECRET"],
                  os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"])


def post_x(text, image):
    payload = {"text": text}
    if image and image.exists():
        up = requests.post("https://api.x.com/2/media/upload", auth=x_auth(), timeout=60,
                           json={"media": base64.b64encode(image.read_bytes()).decode(),
                                 "media_category": "tweet_image"})
        if not up.ok:
            raise RuntimeError(f"X image upload failed {up.status_code}: {up.text}")
        payload["media"] = {"media_ids": [up.json()["data"]["id"]]}
    r = requests.post("https://api.x.com/2/tweets", auth=x_auth(), json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"X post failed {r.status_code}: {r.text}")
    tid = r.json()["data"]["id"]
    return f"https://x.com/Smalik_wc/status/{tid}"


# ---------------- Facebook ----------------
def page_token():
    """Return a Page token. If the saved secret is a User token, swap it for the Page's own token."""
    page_id, token = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
    if not page_id or not token:
        raise RuntimeError("FB_PAGE_ID / FB_PAGE_TOKEN secrets are missing")
    r = requests.get(f"{GRAPH}/{page_id}", params={"fields": "access_token", "access_token": token}, timeout=30)
    if r.ok and r.json().get("access_token"):
        return page_id, r.json()["access_token"]
    return page_id, token


def post_fb_reel(fb, base_dir, page_id, token):
    import time
    video = base_dir / fb["video"]
    r = requests.post(f"{GRAPH}/{page_id}/video_reels", timeout=60, data={"upload_phase": "start", "access_token": token})
    if not r.ok:
        raise RuntimeError(f"Reel start failed {r.status_code}: {r.text}")
    vid, upload_url = r.json()["video_id"], r.json()["upload_url"]
    blob = video.read_bytes()
    u = requests.post(upload_url, timeout=300, data=blob,
                      headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(blob))})
    if not u.ok:
        raise RuntimeError(f"Reel upload failed {u.status_code}: {u.text}")
    f = requests.post(f"{GRAPH}/{page_id}/video_reels", timeout=60,
                      data={"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                            "description": fb["caption"], "access_token": token})
    if not f.ok:
        raise RuntimeError(f"Reel publish failed {f.status_code}: {f.text}")
    note = ""
    if fb.get("first_comment"):
        time.sleep(20)
        c = requests.post(f"{GRAPH}/{vid}/comments", timeout=30, data={"message": fb["first_comment"], "access_token": token})
        note = "" if c.ok else f" (first comment skipped: {c.status_code})"
    return f"https://www.facebook.com/reel/{vid}{note}"


def post_facebook(fb, base_dir):
    page_id, token = page_token()
    if fb.get("video"):
        return post_fb_reel(fb, base_dir, page_id, token)
    image = base_dir / fb["image"]
    with image.open("rb") as f:
        r = requests.post(f"{GRAPH}/{page_id}/photos", timeout=90,
                          data={"message": fb["caption"], "access_token": token},
                          files={"source": (image.name, f, "image/jpeg")})
    if not r.ok:
        raise RuntimeError(f"Facebook post failed {r.status_code}: {r.text}")
    res = r.json()
    post_id = res.get("post_id") or res.get("id")
    note = ""
    if fb.get("first_comment"):
        c = requests.post(f"{GRAPH}/{post_id}/comments", timeout=30,
                          data={"message": fb["first_comment"], "access_token": token})
        note = "" if c.ok else f" (first comment skipped: {c.status_code})"
    return f"https://www.facebook.com/{post_id}{note}"


# ---------------- helpers ----------------
def move(item, files, dest, extra):
    dest.mkdir(exist_ok=True)
    data = json.loads(item.read_text())
    data.update(extra)
    (dest / item.name).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    item.unlink()
    for f in files:
        if f and f.exists():
            shutil.move(str(f), dest / f.name)


def posted_today():
    today = dt.datetime.now(IST).date().isoformat()
    if not POSTED.exists():
        return 0
    return sum(1 for f in POSTED.glob("*.json")
               if json.loads(f.read_text()).get("posted_at", "").startswith(today))


def check_keys():
    ok = True
    r = requests.get("https://api.x.com/2/users/me", auth=x_auth(), timeout=30)
    print("X:", r.status_code, ("✅ @" + r.json()["data"]["username"]) if r.ok else ("❌ " + r.text))
    ok &= r.ok
    if os.environ.get("FB_PAGE_ID") and os.environ.get("FB_PAGE_TOKEN"):
        page_id, token = page_token()
        r = requests.get(f"{GRAPH}/{page_id}", params={"fields": "id,name,instagram_business_account{id,username}", "access_token": token}, timeout=30)
        print("Facebook:", r.status_code, ("✅ " + r.json().get("name", "")) if r.ok else ("❌ " + r.text))
        print("Instagram:", r.json().get("instagram_business_account") if r.ok else None)
        raw = os.environ["FB_PAGE_TOKEN"]
        d = requests.get(f"{GRAPH}/debug_token", params={"input_token": raw, "access_token": raw}, timeout=30).json().get("data", {})
        (ROOT / "status").mkdir(exist_ok=True)
        (ROOT / "status" / "fb_token.txt").write_text(
            f"saved token type: {d.get('type')}\nexpires_at: {d.get('expires_at')}\n"
            f"data_access_expires_at: {d.get('data_access_expires_at')}\nscopes: {d.get('scopes')}\n"
            f"page call ok: {r.ok}\ninstagram: {r.json().get('instagram_business_account') if r.ok else None}\n")
        ok &= r.ok
    else:
        print("Facebook: ❌ FB_PAGE_ID / FB_PAGE_TOKEN secrets missing")
        ok = False
    if not ok:
        sys.exit(1)


def retry_comment():
    """Retry the Facebook first comment on the newest posted item where it was skipped."""
    _, token = page_token()
    items = sorted(POSTED.glob("*.json"), key=lambda f: json.loads(f.read_text()).get("posted_at", ""))
    done = 0
    for f in reversed(items):
        data = json.loads(f.read_text())
        url = data.get("facebook_url", "")
        if "first comment skipped" not in url:
            continue
        post_id = url.split("facebook.com/")[1].split(" ")[0]
        msg = (data.get("facebook") or {}).get("first_comment")
        c = requests.post(f"{GRAPH}/{post_id}/comments", timeout=30, data={"message": msg, "access_token": token})
        print("Comment:", c.status_code, c.text[:300])
        if not c.ok:
            dbg = requests.get(f"{GRAPH}/debug_token", timeout=30,
                               params={"input_token": token, "access_token": token}).json()
            scopes = (dbg.get("data") or {}).get("scopes")
            ttype = (dbg.get("data") or {}).get("type")
            (ROOT / "status").mkdir(exist_ok=True)
            (ROOT / "status" / "last_error.txt").write_text(
                f"comment {c.status_code}: {c.text[:500]}\ntoken type: {ttype}\nscopes: {scopes}\n")
            sys.exit(1)
        data["facebook_url"] = f"https://www.facebook.com/{post_id}"
        data["first_comment_id"] = c.json().get("id")
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print("✅ First comment added:", post_id)
        done += 1
    print(f"Done - {done} comment(s) added.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        return check_keys()
    if len(sys.argv) > 1 and sys.argv[1] == "comment":
        return retry_comment()
    if len(sys.argv) > 2 and sys.argv[1] == "instagram":
        return backfill_instagram(sys.argv[2:])

    now = dt.datetime.now(dt.timezone.utc)
    flash_only = len(sys.argv) > 1 and sys.argv[1] == "flash"   # news-flash runs only touch *-flash-* items
    due = []
    for item in sorted(QUEUE.glob("*.json")):
        if ("-flash-" in item.name) != flash_only:
            continue
        data = json.loads(item.read_text())
        if (now - dt.datetime.fromisoformat(data["created_at"])).total_seconds() / 60 >= DELAY_MINUTES - 15:  # items stamped a few minutes ahead still count
            due.append((data["created_at"], item, data))
    if not due:
        print("Nothing due.")
        return
    if posted_today() >= MAX_POSTS_PER_DAY:
        print("Daily cap reached — waiting.")
        return

    due.sort(key=lambda x: x[0])
    slots_left = MAX_POSTS_PER_DAY - posted_today()
    any_error = False
    for _, item, data in due[:max(1, slots_left)]:
        any_error |= post_item(item, data)
    if any_error:
        sys.exit(1)


def post_instagram(data, base_dir):
    fb = data.get("facebook") or {}
    ig = data.get("instagram") or {}
    page_id, token = page_token()
    caption = ig.get("caption") or fb["caption"]
    comment = ig.get("first_comment") or fb.get("first_comment")
    if fb.get("video"):
        return igpost.post_ig_reel(page_id, token, base_dir / fb["video"], caption, comment)
    return igpost.post_ig_image(page_id, token, base_dir / fb["image"], caption, comment)


def backfill_instagram(names):
    """python poster.py instagram <posted-json-name>...  -> publish already-posted items to Instagram."""
    for name in names:
        f = POSTED / name
        data = json.loads(f.read_text())
        if data.get("instagram_url"):
            print("Already on Instagram:", name); continue
        try:
            data["instagram_url"] = post_instagram(data, POSTED)
            data.pop("instagram_error", None)
            print("✅", name, data["instagram_url"])
        except Exception as e:
            data["instagram_error"] = str(e); print("❌", name, e)
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def post_item(item, data):
    platforms = data.get("platforms", ["x"])
    x_image = QUEUE / data["image"] if data.get("image") else None
    fb = data.get("facebook") or {}
    fb_image = QUEUE / fb["image"] if fb.get("image") else None
    fb_video = QUEUE / fb["video"] if fb.get("video") else None
    print("Posting", item.name, "to", platforms)

    results, errors, notes = {}, {}, {}
    age_min = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(data["created_at"])).total_seconds() / 60
    max_age = data.get("max_age_minutes", X_MAX_AGE_MINUTES)
    if "x" in platforms:
        if age_min > max_age:
            # Rule (10 Nov 2026): a missed post is left out. Old news is never posted on X.
            notes["x_skipped"] = f"stale ({int(age_min)} min old, limit {max_age}) - not posted"
            print("⏭️  X skipped, stale:", item.name)
        else:
            try:
                results["x_url"] = post_x(data["text"], x_image)
                print("✅ X:", results["x_url"])
            except Exception as e:
                errors["x_error"] = str(e); print("❌ X:", e)
    if "facebook" in platforms:
        try:
            results["facebook_url"] = post_facebook(fb, QUEUE)
            print("✅ Facebook:", results["facebook_url"])
        except Exception as e:
            errors["facebook_error"] = str(e); print("❌ Facebook:", e)

    if "facebook" in platforms and (fb_image or fb_video) and data.get("instagram", {}).get("skip") is not True:
        try:
            results["instagram_url"] = post_instagram(data, QUEUE)
            print("✅ Instagram:", results["instagram_url"])
        except Exception as e:  # Instagram problems never block X/Facebook
            errors["instagram_error"] = str(e); print("❌ Instagram:", e)

    stamp = dt.datetime.now(IST).isoformat()
    files = [x_image, fb_image, fb_video]
    if results:
        move(item, files, POSTED, {"posted_at": stamp, **results, **errors, **notes})
    else:
        move(item, files, FAILED, {"failed_at": stamp, **errors, **notes})
    return bool(errors)


if __name__ == "__main__":
    main()
