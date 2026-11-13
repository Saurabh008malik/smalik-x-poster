"""Warm Mug Radio - YouTube login (one time) and upload.

  python warmmug/yt.py auth-start     -> asks Google for a sign-in code (shown in the run summary)
  python warmmug/yt.py auth-wait      -> waits until Saurabh approves on google.com/device, saves the
                                         login encrypted in warmmug/secret/yt_token.enc
  python warmmug/yt.py whoami         -> prints which YouTube channel the saved login posts to
  python warmmug/yt.py upload [dir]   -> uploads warmmug/<dir>/video.mp4 with meta.json (+ thumbnail.jpg if there)

Needs: warmmug/oauth_client.json (Google OAuth client, type "TVs and Limited Input devices")
       env WM_KEY (the key used to lock/unlock the saved login; the workflow passes a repo secret)
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
TOKEN_FILE = HERE / "secret" / "yt_token.enc"
STATE = HERE / "work" / "device.json"
SCOPE = "https://www.googleapis.com/auth/youtube"
API = "https://www.googleapis.com/youtube/v3"


def client():
    if os.environ.get("YT_CLIENT_ID"):
        return os.environ["YT_CLIENT_ID"], os.environ["YT_CLIENT_SECRET"]
    c = json.loads((HERE / "oauth_client.json").read_text())
    c = c.get("installed") or c.get("web") or c
    return c["client_id"], c["client_secret"]


def summary(text):
    print(text)
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p:
        with open(p, "a") as f:
            f.write(text + "\n")


def lock(plain):
    key = os.environ["WM_KEY"]
    TOKEN_FILE.parent.mkdir(exist_ok=True)
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-a", "-pass", "env:WM_KEY",
                    "-out", str(TOKEN_FILE)], input=plain.encode(), check=True, env={**os.environ, "WM_KEY": key})


def unlock():
    if os.environ.get("YT_REFRESH_TOKEN"):
        return os.environ["YT_REFRESH_TOKEN"]
    r = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-a", "-pass", "env:WM_KEY",
                        "-in", str(TOKEN_FILE)], capture_output=True, check=True)
    return r.stdout.decode().strip()


def access_token():
    cid, sec = client()
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": cid, "client_secret": sec, "refresh_token": unlock(), "grant_type": "refresh_token"}, timeout=30)
    if r.status_code != 200:
        raise SystemExit(f"YouTube login failed ({r.status_code}): {r.text[:300]}\n"
                         "If it says invalid_grant, run the 'Warm Mug Radio - connect YouTube' workflow again.")
    return r.json()["access_token"]


def auth_start():
    cid, _ = client()
    r = requests.post("https://oauth2.googleapis.com/device/code", data={"client_id": cid, "scope": SCOPE}, timeout=30)
    r.raise_for_status()
    d = r.json()
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(d))
    summary(f"## Connect Warm Mug Radio to YouTube\n\n"
            f"1. On your phone open **{d['verification_url']}**\n"
            f"2. Type this code: **{d['user_code']}**\n"
            f"3. Sign in, and when asked which account/channel, pick **Warm Mug Radio** (not your cricket channel).\n"
            f"4. Tap Allow. This run finishes by itself within a minute after that.\n\n"
            f"The code works for {d['expires_in']//60} minutes.")


def auth_wait():
    cid, sec = client()
    d = json.loads(STATE.read_text())
    deadline, wait = time.time() + d["expires_in"], d.get("interval", 5)
    while time.time() < deadline:
        time.sleep(wait)
        r = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": cid, "client_secret": sec, "device_code": d["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"}, timeout=30)
        j = r.json()
        if r.status_code == 200:
            if not j.get("refresh_token"):
                raise SystemExit("Google did not return a long-term login. Remove access at myaccount.google.com/permissions and retry.")
            lock(j["refresh_token"])
            ch = requests.get(f"{API}/channels", params={"part": "snippet", "mine": "true"},
                              headers={"Authorization": f"Bearer {j['access_token']}"}, timeout=30).json()
            name = (ch.get("items") or [{}])[0].get("snippet", {}).get("title", "unknown")
            summary(f"\n✅ Connected. Videos will be posted to the channel: **{name}**")
            return
        if j.get("error") == "slow_down":
            wait += 5
        elif j.get("error") != "authorization_pending":
            raise SystemExit(f"Sign-in failed: {j}")
    raise SystemExit("The code expired before it was approved. Run the workflow again.")


def hook_call(payload):
    """Send a request to Saurabh's Apps Script web app (secret WARMMUG_HOOK = web app URL with ?k=KEY)."""
    r = requests.post(os.environ["WARMMUG_HOOK"], data=json.dumps(payload),
                      headers={"Content-Type": "application/json"}, timeout=360, allow_redirects=True)
    try:
        j = r.json()
    except ValueError:
        raise SystemExit(f"Apps Script did not answer properly ({r.status_code}). Check the web app is deployed "
                         f"with access 'Anyone'. Reply: {r.text[:300]}")
    if not j.get("ok"):
        raise SystemExit(f"Apps Script says: {j.get('error')}")
    return j


def whoami():
    if os.environ.get("WARMMUG_HOOK"):
        name = hook_call({"action": "whoami"})["channel"]
        summary(f"Posting to YouTube channel: **{name}** (via Apps Script)")
        return name
    tok = access_token()
    ch = requests.get(f"{API}/channels", params={"part": "snippet", "mine": "true"},
                      headers={"Authorization": f"Bearer {tok}"}, timeout=30).json()
    name = (ch.get("items") or [{}])[0].get("snippet", {}).get("title", "unknown")
    summary(f"Posting to YouTube channel: **{name}**")
    return name


def upload(folder="out"):
    out = HERE / folder
    meta = json.loads((out / "meta.json").read_text())
    video = out / "video.mp4"
    if os.environ.get("WARMMUG_HOOK"):
        import base64
        if video.stat().st_size > 38 * 1024 * 1024:
            raise SystemExit("Video is too big for the Apps Script route (over 38 MB). Use a shorter mix.")
        thumb = out / "thumbnail.jpg"
        j = hook_call({"action": "upload", "title": meta["title"], "description": meta["description"],
                       "tags": meta["tags"], "privacy": os.environ.get("WM_PRIVACY", "public"),
                       "comment": meta.get("comment", ""),
                       "video": base64.b64encode(video.read_bytes()).decode(),
                       "thumbnail": base64.b64encode(thumb.read_bytes()).decode() if thumb.exists() else ""})
        (out / "result.json").write_text(json.dumps({"video_id": j["id"], "url": j["url"],
                                                     "thumbnail_set": j.get("thumbnail") in ("set", "none"),
                                                     "first_comment": j.get("comment", "none")}))
        summary(f"✅ Posted to {j['channel']}: **{meta['title']}** ({meta['minutes']} min) → {j['url']}"
                + f"\n\nFirst comment: {j.get('comment', 'none')}"
                + ("" if j.get("thumbnail") in ("set", "none") else
                   "\n\n⚠️ Custom thumbnail not set - verify the channel with your phone number at youtube.com/verify"))
        return
    tok = access_token()
    h = {"Authorization": f"Bearer {tok}"}
    body = {
        "snippet": {"title": meta["title"], "description": meta["description"], "tags": meta["tags"],
                    "categoryId": "10", "defaultLanguage": "en"},
        "status": {"privacyStatus": os.environ.get("WM_PRIVACY", "public"), "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True, "embeddable": True},
    }
    size = video.stat().st_size
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos",
                      params={"uploadType": "resumable", "part": "snippet,status"},
                      headers={**h, "Content-Type": "application/json; charset=UTF-8",
                               "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
                      data=json.dumps(body), timeout=60)
    if r.status_code != 200:
        raise SystemExit(f"Upload could not start ({r.status_code}): {r.text[:500]}")
    url = r.headers["Location"]

    chunk, pos, vid = 16 * 1024 * 1024, 0, None
    with open(video, "rb") as f:
        while pos < size:
            f.seek(pos)
            data = f.read(chunk)
            end = pos + len(data) - 1
            rr = None
            for attempt in range(5):
                try:
                    rr = requests.put(url, data=data, timeout=300, headers={
                        **h, "Content-Length": str(len(data)), "Content-Range": f"bytes {pos}-{end}/{size}"})
                except requests.RequestException as e:
                    print("retry after error:", e); time.sleep(5 * (attempt + 1)); continue
                if rr.status_code in (500, 502, 503, 504):
                    time.sleep(5 * (attempt + 1)); continue
                break
            if rr is None:
                raise SystemExit("Upload failed: network kept dropping. The next run will try again.")
            if rr.status_code in (200, 201):
                vid = rr.json()["id"]; pos = size
            elif rr.status_code == 308:
                rng = rr.headers.get("Range")
                pos = int(rng.split("-")[1]) + 1 if rng else pos
                print(f"uploaded {pos/size:.0%}")
            else:
                raise SystemExit(f"Upload failed ({rr.status_code}): {rr.text[:500]}")

    thumb_ok = True
    if (out / "thumbnail.jpg").exists():  # Shorts have no custom thumbnail
        with open(out / "thumbnail.jpg", "rb") as f:
            t = requests.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set", params={"videoId": vid},
                              headers={**h, "Content-Type": "image/jpeg"}, data=f.read(), timeout=60)
        if t.status_code != 200:
            thumb_ok = False
            print("Thumbnail not set:", t.status_code, t.text[:300])

    comment_state = "none"
    if meta.get("comment"):
        c = requests.post(f"{API}/commentThreads", params={"part": "snippet"},
                          headers={**h, "Content-Type": "application/json"},
                          data=json.dumps({"snippet": {"videoId": vid, "topLevelComment": {
                              "snippet": {"textOriginal": meta["comment"]}}}}), timeout=60)
        comment_state = "posted" if c.status_code in (200, 201) else f"failed: {c.status_code} {c.text[:150]}"

    link = f"https://youtu.be/{vid}"
    (out / "result.json").write_text(json.dumps({"video_id": vid, "url": link, "thumbnail_set": thumb_ok,
                                                 "first_comment": comment_state}))
    summary(f"✅ Posted: **{meta['title']}** ({meta['minutes']} min) → {link}"
            + f"\n\nFirst comment: {comment_state}"
            + ("" if thumb_ok else "\n\n⚠️ Custom thumbnail not set - verify the channel with your phone number at youtube.com/verify"))


def verify(max_min="25"):
    """After an upload: wait until YouTube has really processed the video (playable, full length).
    Exit code 1 if it is not playable in time, so the workflow does NOT log the mix as posted."""
    out = HERE / "out"
    res = json.loads((out / "result.json").read_text())
    meta = json.loads((out / "meta.json").read_text())
    want = float(meta["minutes"]) * 60
    url = f"https://www.youtube.com/watch?v={res['video_id']}"
    hdr = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
           "Accept-Language": "en-US,en;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"}
    import re
    deadline = time.time() + float(max_min) * 60
    last = "no answer"
    while time.time() < deadline:
        try:
            html = requests.get(url, headers=hdr, timeout=40).text
            st = re.search(r'"playabilityStatus":\{"status":"([A-Z_]+)"', html)
            ln = re.search(r'"lengthSeconds":"(\d+)"', html)
            last = f"status={st.group(1) if st else '?'} length={ln.group(1) if ln else '?'}s (expected about {want:.0f}s)"
            if st and st.group(1) == "LOGIN_REQUIRED":   # YouTube's bot check on GitHub's servers: cannot be checked from here
                summary(f"\u26a0\ufe0f Uploaded {res['url']} but YouTube blocks the automatic processing check from GitHub "
                        "(bot check). Check YouTube Studio that it shows a duration and is public.")
                print("cannot verify from here (LOGIN_REQUIRED); upload itself succeeded")
                return
            if st and st.group(1) == "OK" and ln and int(ln.group(1)) >= want * 0.9:
                summary(f"\u2705 YouTube finished processing the video ({last}) {res['url']}")
                print("verified:", last)
                return
        except Exception as e:  # network blip: try again
            last = f"check failed: {e}"
        print("waiting:", last, flush=True)
        time.sleep(60)
    summary(f"\u274c YouTube did NOT finish processing {res['url']} in {max_min} min ({last}). "
            "Not logged as posted. Delete that video in YouTube Studio; the mix can be rebuilt.")
    raise SystemExit(1)


if __name__ == "__main__":
    cmd = {"auth-start": auth_start, "auth-wait": auth_wait, "whoami": whoami, "upload": upload, "verify": verify}[sys.argv[1]]
    cmd(*sys.argv[2:])
