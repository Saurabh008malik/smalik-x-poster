"""Publishes due money-page posts to the Paycheck Truths Facebook Page.

Run: python money/poster.py          -> post due items (max MAX_PER_RUN)
     python money/poster.py check    -> test the Page token, write status/money_token.txt
Secrets (env): MONEY_FB_PAGE_ID, MONEY_FB_PAGE_TOKEN
"""
import datetime as dt
import json
import os
import pathlib
import shutil
import sys

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import igpost  # noqa: E402

GRAPH = "https://graph.facebook.com/v26.0"
ROOT = pathlib.Path(__file__).parent
QUEUE, POSTED, FAILED = ROOT / "queue", ROOT / "posted", ROOT / "failed"
MAX_PER_RUN = 2


def page_token():
    page_id, token = os.environ["MONEY_FB_PAGE_ID"], os.environ["MONEY_FB_PAGE_TOKEN"]
    r = requests.get(f"{GRAPH}/{page_id}", params={"fields": "access_token", "access_token": token}, timeout=30)
    if r.ok and r.json().get("access_token"):
        return page_id, r.json()["access_token"]
    return page_id, token


def post_reel(item, page_id, token):
    video = QUEUE / item["video"]
    r = requests.post(f"{GRAPH}/{page_id}/video_reels", timeout=60,
                      data={"upload_phase": "start", "access_token": token})
    if not r.ok:
        raise RuntimeError(f"Reel start failed {r.status_code}: {r.text}")
    vid, upload_url = r.json()["video_id"], r.json()["upload_url"]
    data = video.read_bytes()
    u = requests.post(upload_url, timeout=300, data=data,
                      headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(data))})
    if not u.ok:
        raise RuntimeError(f"Reel upload failed {u.status_code}: {u.text}")
    f = requests.post(f"{GRAPH}/{page_id}/video_reels", timeout=60,
                      data={"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                            "description": item["caption"], "access_token": token})
    if not f.ok:
        raise RuntimeError(f"Reel publish failed {f.status_code}: {f.text}")
    note = ""
    if item.get("first_comment"):
        import time
        time.sleep(20)
        c = requests.post(f"{GRAPH}/{vid}/comments", timeout=30,
                          data={"message": item["first_comment"], "access_token": token})
        note = "" if c.ok else f" (first comment skipped: {c.status_code})"
    return f"https://www.facebook.com/reel/{vid}{note}"


def post_one(item, page_id, token):
    if item.get("video"):
        return post_reel(item, page_id, token)
    if item.get("image"):
        img = QUEUE / item["image"]
        with img.open("rb") as f:
            r = requests.post(f"{GRAPH}/{page_id}/photos", timeout=90,
                              data={"message": item["caption"], "access_token": token},
                              files={"source": (img.name, f, "image/jpeg")})
    else:
        r = requests.post(f"{GRAPH}/{page_id}/feed", timeout=60,
                          data={"message": item["caption"], "access_token": token})
    if not r.ok:
        raise RuntimeError(f"Facebook post failed {r.status_code}: {r.text}")
    res = r.json()
    post_id = res.get("post_id") or res.get("id")
    note = ""
    if item.get("first_comment"):
        c = requests.post(f"{GRAPH}/{post_id}/comments", timeout=30,
                          data={"message": item["first_comment"], "access_token": token})
        note = "" if c.ok else f" (first comment skipped: {c.status_code})"
    return f"https://www.facebook.com/{post_id}{note}"


def post_instagram(item, base_dir, page_id, token):
    ig = item.get("instagram") or {}
    caption = ig.get("caption") or item["caption"]
    comment = ig.get("first_comment") or item.get("first_comment")
    if item.get("video"):
        return igpost.post_ig_reel(page_id, token, base_dir / item["video"], caption, comment)
    return igpost.post_ig_image(page_id, token, base_dir / item["image"], caption, comment)


def backfill_instagram(names):
    page_id, token = page_token()
    for name in names:
        f = POSTED / name
        data = json.loads(f.read_text())
        if data.get("instagram_url"):
            print("Already on Instagram:", name)
            continue
        if not (data.get("image") or data.get("video")):
            print("Text-only, skipped:", name)
            continue
        try:
            data["instagram_url"] = post_instagram(data, POSTED, page_id, token)
            data.pop("instagram_error", None)
            print("OK", name, data["instagram_url"])
        except Exception as e:  # noqa: BLE001
            data["instagram_error"] = str(e)
            print("FAIL", name, e)
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def check():
    page_id, token = page_token()
    r = requests.get(f"{GRAPH}/{page_id}", params={"fields": "id,name,instagram_business_account{id,username}", "access_token": token}, timeout=30)
    print("Page:", r.status_code, r.text[:200])
    raw = os.environ["MONEY_FB_PAGE_TOKEN"]
    d = requests.get(f"{GRAPH}/debug_token", params={"input_token": raw, "access_token": raw}, timeout=30).json().get("data", {})
    status = ROOT.parent / "status"
    status.mkdir(exist_ok=True)
    (status / "money_token.txt").write_text(
        f"page call: {r.status_code} {r.text[:300]}\ntype: {d.get('type')}\nexpires_at: {d.get('expires_at')}\n"
        f"data_access_expires_at: {d.get('data_access_expires_at')}\nscopes: {d.get('scopes')}\n")
    sys.exit(0 if r.ok else 1)


def delete(target):
    page_id, token = page_token()
    r = requests.delete(f"{GRAPH}/{target}", params={"access_token": token}, timeout=30)
    print("Delete:", r.status_code, r.text[:300])
    sys.exit(0 if r.ok else 1)


def ig_images_blocked():
    """Instagram answers 'Action is blocked' (2207051) when it flags image posting as spam.
    Hammering a blocked action risks the account, so after such a failure pause image posts and probe once every 12h."""
    now = dt.datetime.now(dt.timezone.utc)
    recs = []
    for f in POSTED.glob("*.json"):
        try:
            recs.append(json.loads(f.read_text()))
        except Exception:  # noqa: BLE001
            continue
    recs.sort(key=lambda d: d.get("done_at", ""), reverse=True)
    for d in recs[:30]:
        if d.get("video") or not d.get("image"):
            continue
        err = d.get("instagram_error") or ""
        if "2207051" in err and not err.startswith("paused"):
            return (now - dt.datetime.fromisoformat(d["done_at"])).total_seconds() < 12 * 3600
        if d.get("instagram_url"):
            return False
    return False


def main():
    if not os.environ.get("MONEY_FB_PAGE_ID") or not os.environ.get("MONEY_FB_PAGE_TOKEN"):
        print("Money page secrets not set yet - nothing to do.")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        return check()
    if len(sys.argv) > 2 and sys.argv[1] == "instagram":
        return backfill_instagram(sys.argv[2:])
    if len(sys.argv) > 2 and sys.argv[1] == "delete":
        return delete(sys.argv[2])
    now = dt.datetime.now(dt.timezone.utc)
    due = []
    for f in sorted(QUEUE.glob("*.json")):
        data = json.loads(f.read_text())
        if dt.datetime.fromisoformat(data["publish_at"]) <= now:
            due.append((data["publish_at"], f, data))
    due.sort(key=lambda x: x[0])
    if not due:
        print("Nothing due.")
        return
    page_id, token = page_token()
    failed = False
    for _, f, data in due[:MAX_PER_RUN]:
        extra = {}
        try:
            extra["facebook_url"] = post_one(data, page_id, token)
            dest = POSTED
            print("OK", f.name, extra["facebook_url"])
            if (data.get("image") or data.get("video")) and (data.get("instagram") or {}).get("skip") is not True:
                if not data.get("video") and ig_images_blocked():
                    extra["instagram_error"] = "paused: Instagram blocked image posts (2207051); one probe every 12h, reels still post"
                    print("SKIP Instagram image (circuit breaker)")
                else:
                  try:
                      extra["instagram_url"] = post_instagram(data, QUEUE, page_id, token)
                      print("OK Instagram", extra["instagram_url"])
                  except Exception as e:  # noqa: BLE001  (never blocks Facebook)
                      extra["instagram_error"] = str(e)
                      print("FAIL Instagram", e)
        except Exception as e:  # noqa: BLE001
            extra["error"] = str(e)
            dest = FAILED
            failed = True
            print("FAIL", f.name, e)
        dest.mkdir(exist_ok=True)
        data.update(extra, done_at=dt.datetime.now(dt.timezone.utc).isoformat())
        (dest / f.name).write_text(json.dumps(data, ensure_ascii=False, indent=2))
        f.unlink()
        for key in ("image", "video"):
            if data.get(key) and (QUEUE / data[key]).exists():
                shutil.move(str(QUEUE / data[key]), dest / data[key])
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
