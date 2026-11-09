"""The Sleepy Biographer - publishes due items from sleepy/queue.json (long videos and Shorts).

  python sleepy/yt.py due       -> prints how many items are due (used by the workflow to skip quickly)
  python sleepy/yt.py whoami    -> prints which YouTube channel the hook is connected to
  python sleepy/yt.py publish   -> uploads every due item: video, thumbnail, playlist, first comment

Needs env SLEEPY_HOOK = Apps Script web app URL with ?k=KEY (it hands out a 1-hour YouTube token for the channel),
and GH_TOKEN so `gh release download` can fetch the finished video from the (draft) release.

queue.json item:
 {"id": "franklin", "kind": "long"|"short", "publish_after": "2026-11-11T23:30:00Z", "release": "<release tag>",
  "video": "video.mp4", "thumbnail": "thumbnail.jpg" (long only), "title": "...", "description": "...", "tags": [...],
  "comment": "first comment text", "playlist": "<playlist title>" (optional), "category": "27", "done": false}
Policy built in: the 'altered or synthetic content' flag is ALWAYS on (AI voice), never made-for-kids, one item per slot.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
QUEUE = HERE / "queue.json"
API = "https://www.googleapis.com/youtube/v3"
MAX_PER_RUN = 2


def summary(text):
    print(text)
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p:
        with open(p, "a") as f:
            f.write(text + "\n")


def now():
    return dt.datetime.now(dt.timezone.utc)


def is_due(it):
    if it.get("done") or it.get("attempts", 0) >= 4:
        return False
    return dt.datetime.fromisoformat(it["publish_after"].replace("Z", "+00:00")) <= now()


def load():
    return json.loads(QUEUE.read_text())


def save(q):
    QUEUE.write_text(json.dumps(q, indent=2, ensure_ascii=False) + "\n")


def hook(action):
    r = requests.post(os.environ["SLEEPY_HOOK"], data=json.dumps({"action": action}),
                      headers={"Content-Type": "application/json"}, timeout=120, allow_redirects=True)
    try:
        j = r.json()
    except ValueError:
        raise SystemExit(f"Apps Script did not answer properly ({r.status_code}). Is the web app deployed with "
                         f"access 'Anyone'? Reply: {r.text[:200]}")
    if not j.get("ok"):
        raise SystemExit(f"Apps Script says: {j.get('error')}")
    return j


def whoami():
    summary(f"Connected to YouTube channel: **{hook('whoami')['channel']}**")


def tokentest():
    j = hook("token")
    h = {"Authorization": f"Bearer {j['token']}"}
    info = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": j["token"]}, timeout=30).json()
    scopes = [x.rsplit("/", 1)[-1] for x in info.get("scope", "").split()]
    ch = requests.get(f"{API}/channels", params={"part": "snippet,statistics", "mine": "true"}, headers=h, timeout=30)
    ok = ch.status_code == 200 and ch.json().get("items")
    name = ch.json()["items"][0]["snippet"]["title"] if ok else ch.text[:200]
    summary(f"Token test: scopes={scopes}; channels.list -> {ch.status_code}: {name}")
    if not ok or "youtube.upload" not in scopes:
        raise SystemExit("Token cannot upload - check appsscript.json scopes")


def upload_video(h, path, body, size):
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos",
                      params={"uploadType": "resumable", "part": "snippet,status"},
                      headers={**h, "Content-Type": "application/json; charset=UTF-8",
                               "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
                      data=json.dumps(body), timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Upload could not start ({r.status_code}): {r.text[:400]}")
    url = r.headers["Location"]
    chunk, pos = 32 * 1024 * 1024, 0
    with open(path, "rb") as f:
        while pos < size:
            f.seek(pos)
            data = f.read(chunk)
            end = pos + len(data) - 1
            rr = None
            for attempt in range(6):
                try:
                    rr = requests.put(url, data=data, timeout=600, headers={
                        "Content-Length": str(len(data)), "Content-Range": f"bytes {pos}-{end}/{size}"})
                except requests.RequestException as e:
                    print("retry after error:", e); time.sleep(5 * (attempt + 1)); continue
                if rr.status_code in (500, 502, 503, 504):
                    time.sleep(5 * (attempt + 1)); continue
                break
            if rr is None:
                raise RuntimeError("network kept dropping during upload")
            if rr.status_code in (200, 201):
                return rr.json()["id"]
            if rr.status_code == 308:
                rng = rr.headers.get("Range")
                pos = int(rng.split("-")[1]) + 1 if rng else pos
                print(f"uploaded {pos / size:.0%}", flush=True)
            else:
                raise RuntimeError(f"Upload failed ({rr.status_code}): {rr.text[:400]}")
    raise RuntimeError("upload ended without a video id")


def add_to_playlist(h, vid, title):
    pl = requests.get(f"{API}/playlists", params={"part": "snippet", "mine": "true", "maxResults": 50}, headers=h, timeout=30).json()
    pid = next((p["id"] for p in pl.get("items", []) if p["snippet"]["title"].strip().lower() == title.strip().lower()), None)
    if not pid:
        return f"playlist '{title}' not found"
    r = requests.post(f"{API}/playlistItems", params={"part": "snippet"}, headers={**h, "Content-Type": "application/json"},
                      data=json.dumps({"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}), timeout=30)
    return "added" if r.status_code in (200, 201) else f"failed {r.status_code}"


def fetch_parts(it, work):
    """Video was handed over as parts (<95 MB each) on a temporary branch: join them back into one file."""
    repo = os.environ["GITHUB_REPOSITORY"]
    tmp = work / "_parts"
    subprocess.run(["rm", "-rf", str(tmp)], check=True)
    subprocess.run(["git", "clone", "-q", "--depth", "1", "--single-branch", "--branch", it["parts_branch"],
                    f"https://x-access-token:{os.environ['GH_TOKEN']}@github.com/{repo}.git", str(tmp)], check=True)
    parts = sorted(tmp.glob(it["video"] + ".part*"))
    if not parts:
        raise RuntimeError("no video parts found on branch " + it["parts_branch"])
    with open(work / it["video"], "wb") as out:
        for pt in parts:
            with open(pt, "rb") as f:
                while True:
                    b = f.read(8 * 1024 * 1024)
                    if not b:
                        break
                    out.write(b)
    if it.get("sha256"):
        import hashlib
        h = hashlib.sha256()
        with open(work / it["video"], "rb") as f:
            for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
                h.update(b)
        if h.hexdigest() != it["sha256"]:
            raise RuntimeError("joined video does not match its checksum - parts damaged, not uploading")
    if it.get("thumbnail"):
        (work / it["thumbnail"]).write_bytes((tmp / it["thumbnail"]).read_bytes())
    subprocess.run(["rm", "-rf", str(tmp)], check=True)


def delete_branch(name):
    if name:
        subprocess.run(["git", "push", "-q", "origin", "--delete", name], check=False)


def publish_one(it, token):
    h = {"Authorization": f"Bearer {token}"}
    work = HERE / "work" / it["id"]
    work.mkdir(parents=True, exist_ok=True)
    files = [it["video"]] + ([it["thumbnail"]] if it.get("thumbnail") else [])
    if it.get("parts_branch"):
        fetch_parts(it, work)
    else:
        for fn in files:
            subprocess.run(["gh", "release", "download", it["release"], "--repo", os.environ["GITHUB_REPOSITORY"],
                            "-p", fn, "-D", str(work), "--clobber"], check=True)
    video = work / it["video"]
    size = video.stat().st_size
    title = it["title"]
    if it["kind"] == "short" and "#shorts" not in title.lower():
        title = (title[:88] + " #Shorts").strip()
    body = {
        "snippet": {"title": title, "description": it["description"], "tags": it.get("tags", []),
                    "categoryId": it.get("category", "27"), "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True, "embeddable": True},
    }
    if it.get("schedule_at"):   # upload now as private, YouTube makes it public by itself at that time
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = it["schedule_at"]
    vid = upload_video(h, video, body, size)
    notes = []
    if it.get("thumbnail"):
        with open(work / it["thumbnail"], "rb") as f:
            t = requests.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set", params={"videoId": vid},
                              headers={**h, "Content-Type": "image/jpeg"}, data=f.read(), timeout=60)
        notes.append("thumbnail " + ("set" if t.status_code == 200 else f"NOT set ({t.status_code}: verify the channel at youtube.com/verify)"))
    if it.get("playlist"):
        notes.append("playlist " + add_to_playlist(h, vid, it["playlist"]))
    if it.get("comment"):
        c = requests.post(f"{API}/commentThreads", params={"part": "snippet"}, headers={**h, "Content-Type": "application/json"},
                          data=json.dumps({"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": it["comment"]}}}}), timeout=60)
        notes.append("first comment " + ("posted" if c.status_code in (200, 201) else f"FAILED {c.status_code}"))
    for fn in files:
        (work / fn).unlink(missing_ok=True)
    if it.get("parts_branch"):
        delete_branch(it["parts_branch"])
        notes.append("parts branch deleted")
    if it.get("schedule_at"):
        notes.append("goes public at " + it["schedule_at"])
    return vid, notes


def publish():
    q = load()
    due = [it for it in q if is_due(it)][:MAX_PER_RUN]
    if not due:
        summary("Nothing due right now.")
        return
    token = None
    for it in due:
        try:
            if token is None:
                j = hook("token")
                token = j["token"]
                summary(f"Posting to **{j['channel']}**")
            vid, notes = publish_one(it, token)
            it["done"], it["video_id"], it["url"] = True, vid, f"https://youtu.be/{vid}"
            it["posted_at"] = now().isoformat(timespec="seconds")
            summary(f"✅ **{it['title']}** → https://youtu.be/{vid} ({', '.join(notes)})")
        except (RuntimeError, subprocess.CalledProcessError, SystemExit, requests.RequestException) as e:
            it["attempts"] = it.get("attempts", 0) + 1
            it["last_error"] = str(e)[:300]
            summary(f"❌ **{it['title']}** failed (attempt {it['attempts']}): {e}")
        save(q)
    save(q)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "due":
        print(sum(1 for it in load() if is_due(it)))
    else:
        {"whoami": whoami, "publish": publish, "tokentest": tokentest}[cmd]()
