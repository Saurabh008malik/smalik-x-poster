"""Publishes due Creator Adda posts to the Creator Adda Facebook Page + Instagram (@real_creator_adda).

Run: python adda/poster.py          -> post due items (max MAX_PER_RUN)
     python adda/poster.py check    -> test the Page token, write status/adda_token.txt
Secrets (env): ADDA_FB_PAGE_ID, ADDA_FB_PAGE_TOKEN
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


DEFAULT_PAGE_ID = "61594820314272"  # Creator Adda Facebook Page (public id, not a secret)
TOKEN_SOURCES = ("ADDA_FB_PAGE_TOKEN", "MONEY_FB_PAGE_TOKEN", "FB_PAGE_TOKEN")


def resolve():
    """Return (page_id, page_token, source_name) or (page_id, None, report)."""
    page_id = os.environ.get("ADDA_FB_PAGE_ID") or DEFAULT_PAGE_ID
    notes = []
    for name in TOKEN_SOURCES:
        tok = os.environ.get(name)
        if not tok:
            notes.append(f"{name}: not set")
            continue
        r = requests.get(f"{GRAPH}/{page_id}", params={"fields": "access_token", "access_token": tok}, timeout=30)
        if r.ok and r.json().get("access_token"):
            return page_id, r.json()["access_token"], name
        if name == "ADDA_FB_PAGE_TOKEN":
            r2 = requests.get(f"{GRAPH}/{page_id}", params={"fields": "id,name", "access_token": tok}, timeout=30)
            if r2.ok:
                return page_id, tok, name
        notes.append(f"{name}: {r.status_code} {r.text[:160]}")
    return page_id, None, " | ".join(notes)


def page_token():
    page_id, token, info = resolve()
    if not token:
        raise RuntimeError(f"No working token for Creator Adda: {info}")
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
    page_id, token, info = resolve()
    status = ROOT.parent / "status"
    status.mkdir(exist_ok=True)
    lines = [f"page id: {page_id}", f"token source: {info if token else 'NONE'}"]
    if token:
        r = requests.get(f"{GRAPH}/{page_id}", params={"fields": "id,name,instagram_business_account{id,username}", "access_token": token}, timeout=30)
        lines.append(f"page call: {r.status_code} {r.text[:300]}")
        d = requests.get(f"{GRAPH}/debug_token", params={"input_token": token, "access_token": token}, timeout=30).json().get("data", {})
        lines += [f"type: {d.get('type')}", f"expires_at: {d.get('expires_at')}",
                  f"data_access_expires_at: {d.get('data_access_expires_at')}", f"scopes: {d.get('scopes')}"]
    else:
        lines.append(f"details: {info}")
    (status / "adda_token.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(0 if token else 1)


def delete(target):
    page_id, token = page_token()
    r = requests.delete(f"{GRAPH}/{target}", params={"access_token": token}, timeout=30)
    print("Delete:", r.status_code, r.text[:300])
    sys.exit(0 if r.ok else 1)


def main():
    if not any(os.environ.get(n) for n in TOKEN_SOURCES):
        print("No Facebook token available - nothing to do.")
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
