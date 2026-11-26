"""Instagram publishing helpers (Instagram API with Facebook Login), shared by both robots.

Uses the Facebook Page token. The Instagram account is found through the Page it is linked to.
Images are first uploaded (unpublished) to the Page to get a public URL; reels use resumable upload.
"""
import time

import requests

GRAPH = "https://graph.facebook.com/v26.0"


def _check(r, what):
    if not r.ok:
        raise RuntimeError(f"{what} failed {r.status_code}: {r.text[:400]}")
    return r.json()


def ig_account(page_id, token):
    d = _check(requests.get(f"{GRAPH}/{page_id}", timeout=30,
                            params={"fields": "instagram_business_account", "access_token": token}), "Find Instagram account")
    acc = (d.get("instagram_business_account") or {}).get("id")
    if not acc:
        raise RuntimeError("No Instagram account linked to this Page")
    return acc


def public_image_url(page_id, token, image_path):
    with open(image_path, "rb") as f:
        up = _check(requests.post(f"{GRAPH}/{page_id}/photos", timeout=90,
                                  data={"published": "false", "access_token": token},
                                  files={"source": (image_path.name, f, "image/jpeg")}), "Image hosting upload")
    info = _check(requests.get(f"{GRAPH}/{up['id']}", timeout=30,
                               params={"fields": "images", "access_token": token}), "Image URL lookup")
    return info["images"][0]["source"]


def _wait_ready(container, token, tries=40):
    for _ in range(tries):
        d = _check(requests.get(f"{GRAPH}/{container}", timeout=30,
                                params={"fields": "status_code", "access_token": token}), "Container status")
        if d.get("status_code") == "FINISHED":
            return
        if d.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram processing failed: {d}")
        time.sleep(6)
    raise RuntimeError("Instagram processing timed out")


def _publish(ig_id, container, token, first_comment):
    pub = _check(requests.post(f"{GRAPH}/{ig_id}/media_publish", timeout=60,
                               data={"creation_id": container, "access_token": token}), "Instagram publish")
    media_id = pub["id"]
    link = _check(requests.get(f"{GRAPH}/{media_id}", timeout=30,
                               params={"fields": "permalink", "access_token": token}), "Permalink").get("permalink", media_id)
    note = ""
    if first_comment:
        time.sleep(5)
        c = requests.post(f"{GRAPH}/{media_id}/comments", timeout=30,
                          data={"message": first_comment, "access_token": token})
        note = "" if c.ok else f" (first comment skipped: {c.status_code} {c.text[:200]})"
    return f"{link}{note}"


def post_ig_image(page_id, token, image_path, caption, first_comment=None):
    ig_id = ig_account(page_id, token)
    url = public_image_url(page_id, token, image_path)
    cont = _check(requests.post(f"{GRAPH}/{ig_id}/media", timeout=60,
                                data={"image_url": url, "caption": caption, "access_token": token}), "Instagram image container")["id"]
    _wait_ready(cont, token)
    return _publish(ig_id, cont, token, first_comment)


def post_ig_reel(page_id, token, video_path, caption, first_comment=None):
    """Instagram sometimes rejects a reel upload with a one-off processing error: try up to 3 times."""
    last = None
    for attempt in range(3):
        try:
            return _post_ig_reel_once(page_id, token, video_path, caption, first_comment)
        except RuntimeError as e:
            last = e
            if "upload failed" not in str(e) and "processing failed" not in str(e).lower():
                raise
            time.sleep(30)
    raise last


def _post_ig_reel_once(page_id, token, video_path, caption, first_comment=None):
    ig_id = ig_account(page_id, token)
    c = _check(requests.post(f"{GRAPH}/{ig_id}/media", timeout=60,
                             data={"media_type": "REELS", "upload_type": "resumable", "caption": caption,
                                   "share_to_feed": "true", "access_token": token}), "Instagram reel container")
    blob = open(video_path, "rb").read()
    u = requests.post(c["uri"], data=blob, timeout=300,
                      headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(blob))})
    if not u.ok:
        raise RuntimeError(f"Instagram reel upload failed {u.status_code}: {u.text[:300]}")
    _wait_ready(c["id"], token, tries=60)
    return _publish(ig_id, c["id"], token, first_comment)


IG_IMAGES_PER_DAY = 2  # 27 Nov 2026: Instagram flagged image posting as spam (2207051) on 3 accounts; reels are not capped


def image_budget_ok(posted_dir, cap=IG_IMAGES_PER_DAY, hours=24):
    """True while fewer than `cap` IMAGE posts reached Instagram from this account in the last `hours`.
    Keeps image volume low so Instagram does not flag the account; Facebook is not affected."""
    import datetime as _dt
    import json as _json
    import pathlib as _pl
    now = _dt.datetime.now(_dt.timezone.utc)
    n = 0
    for f in _pl.Path(posted_dir).glob("*.json"):
        try:
            d = _json.loads(f.read_text())
        except Exception:  # noqa: BLE001
            continue
        if d.get("video") or (d.get("facebook") or {}).get("video") or not d.get("instagram_url"):
            continue
        ts = d.get("posted_at") or d.get("done_at")
        try:
            t = _dt.datetime.fromisoformat(ts)
            if t.tzinfo is None:
                t = t.replace(tzinfo=_dt.timezone.utc)
        except Exception:  # noqa: BLE001
            continue
        if (now - t).total_seconds() < hours * 3600:
            n += 1
    return n < cap
