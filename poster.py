"""Smalik Cricket Poster — posts queued tweets (text + image) to X for @Smalik_wc.

Queue format: queue/<name>.json  ->  {"text": "...", "image": "<name>.png", "created_at": "ISO-8601 with timezone"}
              queue/<name>.png   ->  the tweet card image (optional)

Rules:
- A queued tweet is posted only after DELAY_MINUTES have passed since created_at (safety window).
- Delete its files from queue/ before then to cancel it.
- One tweet per run, max MAX_POSTS_PER_DAY per IST day.
- Posted items move to posted/, failed ones to failed/ (never retried automatically).
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

DELAY_MINUTES = 0
MAX_POSTS_PER_DAY = 3
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

ROOT = pathlib.Path(__file__).parent
QUEUE, POSTED, FAILED = ROOT / "queue", ROOT / "posted", ROOT / "failed"


def auth():
    return OAuth1(
        os.environ["X_CONSUMER_KEY"], os.environ["X_CONSUMER_SECRET"],
        os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"],
    )


def move(item, image, dest, extra=None):
    dest.mkdir(exist_ok=True)
    data = json.loads(item.read_text())
    if extra:
        data.update(extra)
    (dest / item.name).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    item.unlink()
    if image and image.exists():
        shutil.move(str(image), dest / image.name)


def posted_today():
    today = dt.datetime.now(IST).date().isoformat()
    if not POSTED.exists():
        return 0
    n = 0
    for f in POSTED.glob("*.json"):
        if json.loads(f.read_text()).get("posted_at", "").startswith(today):
            n += 1
    return n


def check_keys():
    r = requests.get("https://api.x.com/2/users/me", auth=auth(), timeout=30)
    print("Status:", r.status_code)
    if r.ok:
        print("✅ Keys work! Connected to @" + r.json()["data"]["username"])
    else:
        print("❌", r.text)
        sys.exit(1)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        return check_keys()

    now = dt.datetime.now(dt.timezone.utc)
    due = []
    for item in sorted(QUEUE.glob("*.json")):
        data = json.loads(item.read_text())
        created = dt.datetime.fromisoformat(data["created_at"])
        if (now - created).total_seconds() / 60 >= DELAY_MINUTES:
            due.append((created, item, data))
    if not due:
        print("Nothing due.")
        return
    if posted_today() >= MAX_POSTS_PER_DAY:
        print("Daily cap reached — waiting.")
        return

    due.sort(key=lambda x: x[0])
    _, item, data = due[0]
    image = QUEUE / data["image"] if data.get("image") else None
    print("Posting", item.name)

    try:
        payload = {"text": data["text"]}
        if image and image.exists():
            up = requests.post(
                "https://api.x.com/2/media/upload", auth=auth(), timeout=60,
                json={"media": base64.b64encode(image.read_bytes()).decode(),
                      "media_category": "tweet_image"},
            )
            if not up.ok:
                raise RuntimeError(f"Image upload failed {up.status_code}: {up.text}")
            payload["media"] = {"media_ids": [up.json()["data"]["id"]]}

        r = requests.post("https://api.x.com/2/tweets", auth=auth(), json=payload, timeout=30)
        if not r.ok:
            raise RuntimeError(f"Post failed {r.status_code}: {r.text}")
        tweet_id = r.json()["data"]["id"]
        move(item, image, POSTED, {"posted_at": dt.datetime.now(IST).isoformat(), "tweet_id": tweet_id,
                                   "url": f"https://x.com/Smalik_wc/status/{tweet_id}"})
        print(f"✅ Posted: https://x.com/Smalik_wc/status/{tweet_id}")
    except Exception as e:  # keep failed items out of the queue so they are never retried by accident
        move(item, image, FAILED, {"failed_at": dt.datetime.now(IST).isoformat(), "error": str(e)})
        print("❌", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
