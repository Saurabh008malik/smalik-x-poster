"""YouTube helper queue for the two long-form channels (Lamplight Scripture, The Sleepy Biographer).

  python ytq/ytq.py due        -> prints how many items are due (comments + Shorts)
  python ytq/ytq.py run        -> posts first comments that are due, then at most one Short per channel
  python ytq/ytq.py whoami     -> checks both hooks

Files: ytq/comments.json  first comments: posted COMMENT_DELAY_MIN minutes after the long video is really public
       ytq/shorts.json    Shorts cut from the long videos: posted at their slot, each pointing to the long video
Hooks (GitHub secrets): LAMPLIGHT_HOOK, SLEEPY_HOOK = Apps Script web app URL with ?k=KEY (lends a 1-hour token).
Policy built in: altered/synthetic flag ON, never made for kids, one Short per channel per run, at least
MIN_GAP_MIN minutes between two Shorts of a channel, max 3 Shorts per channel per UTC day.
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
sys.path.insert(0, str(HERE.parent / "sleepy"))
from yt import upload_video  # noqa: E402  (resumable uploader already tested on the Sleepy channel)

API = "https://www.googleapis.com/youtube/v3"
CHANNELS = {"lamplight": "LAMPLIGHT_HOOK", "sleepy": "SLEEPY_HOOK"}
COMMENT_DELAY_MIN = 60
MIN_GAP_MIN = 90
MAX_SHORTS_PER_DAY = 3
COMMENTS = HERE / "comments.json"
SHORTS = HERE / "shorts.json"


def summary(text):
    print(text, flush=True)
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p:
        with open(p, "a") as f:
            f.write(text + "\n")


def now():
    return dt.datetime.now(dt.timezone.utc)


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def load(p):
    return json.loads(p.read_text()) if p.exists() else []


def save(p, data):
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def comment_due(it):
    return (not it.get("done")) and it.get("attempts", 0) < 8 and ts(it["go_live"]) + dt.timedelta(minutes=COMMENT_DELAY_MIN) <= now()


def short_due(it):
    return (not it.get("done")) and it.get("attempts", 0) < 4 and ts(it["publish_after"]) <= now()


def hook(chan, action="token"):
    url = os.environ.get(CHANNELS[chan], "")
    if not url:
        raise RuntimeError(f"secret {CHANNELS[chan]} is not set")
    r = requests.post(url, data=json.dumps({"action": action}), headers={"Content-Type": "application/json"},
                      timeout=120, allow_redirects=True)
    try:
        j = r.json()
    except ValueError:
        raise RuntimeError(f"Apps Script did not answer properly ({r.status_code}): {r.text[:160]}")
    if not j.get("ok"):
        raise RuntimeError(f"Apps Script says: {j.get('error')}")
    return j


class Chan:
    """One authorised channel: token, own channel id, list of own uploads."""

    def __init__(self, name):
        j = hook(name)
        self.name = name
        self.h = {"Authorization": f"Bearer {j['token']}"}
        self.title = j["channel"]
        r = requests.get(f"{API}/channels", params={"part": "id,contentDetails", "mine": "true"}, headers=self.h, timeout=30).json()
        it = r["items"][0]
        self.id = it["id"]
        self.uploads = it["contentDetails"]["relatedPlaylists"]["uploads"]
        self._videos = None

    def videos(self):
        if self._videos is None:
            ids, tok = [], None
            while True:
                p = {"part": "contentDetails", "playlistId": self.uploads, "maxResults": 50}
                if tok:
                    p["pageToken"] = tok
                r = requests.get(f"{API}/playlistItems", params=p, headers=self.h, timeout=30).json()
                ids += [x["contentDetails"]["videoId"] for x in r.get("items", [])]
                tok = r.get("nextPageToken")
                if not tok or len(ids) >= 200:
                    break
            out = []
            for i in range(0, len(ids), 50):
                r = requests.get(f"{API}/videos", params={"part": "snippet,status,contentDetails", "id": ",".join(ids[i:i + 50])},
                                 headers=self.h, timeout=30).json()
                out += r.get("items", [])
            self._videos = out
        return self._videos

    def find(self, contains):
        """Newest long video (not a Short) whose title contains the text."""
        for v in self.videos():
            if contains.lower() in v["snippet"]["title"].lower() and "#shorts" not in v["snippet"]["title"].lower():
                return v
        return None

    def has_own_comment(self, vid):
        r = requests.get(f"{API}/commentThreads", params={"part": "snippet", "videoId": vid, "maxResults": 100, "order": "time"},
                         headers=self.h, timeout=30)
        if r.status_code != 200:
            return False
        for t in r.json().get("items", []):
            a = t["snippet"]["topLevelComment"]["snippet"].get("authorChannelId", {}).get("value")
            if a == self.id:
                return True
        return False


def post_comment(ch, it):
    v = ch.find(it["title_contains"])
    if not v:
        return "video not found yet"
    vid = v["id"]
    if v["status"]["privacyStatus"] != "public":
        return f"video {vid} is not public yet ({v['status']['privacyStatus']})"
    it["video_id"] = vid
    if ch.has_own_comment(vid):
        it["done"] = True
        it["note"] = "channel already had a comment, nothing posted"
        return f"already has a channel comment ({vid})"
    c = requests.post(f"{API}/commentThreads", params={"part": "snippet"}, headers={**ch.h, "Content-Type": "application/json"},
                      data=json.dumps({"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": it["text"]}}}}), timeout=60)
    if c.status_code in (200, 201):
        it["done"] = True
        it["posted_at"] = now().isoformat(timespec="seconds")
        return f"first comment posted on {vid} (pin it by hand in Studio: the API cannot pin)"
    raise RuntimeError(f"comment failed {c.status_code}: {c.text[:200]}")


def short_comment_text(it):
    kind = "bedtime biographies" if it["channel"] == "sleepy" else "Bible stories"
    return (f"\u25b6 Watch the full video here: {it['long_url']}\n\n"
            f"Subscribe and tap the bell for new {kind}. \U0001F319")


def comment_on_short(ch, it):
    """First comment on a Short = link to the full video. Retries on later runs if YouTube is not ready yet."""
    vid = it["video_id"]
    if ch.has_own_comment(vid):
        it["comment_done"] = True
        return "already has a channel comment"
    last = ""
    for k in range(3):
        c = requests.post(f"{API}/commentThreads", params={"part": "snippet"}, headers={**ch.h, "Content-Type": "application/json"},
                          data=json.dumps({"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": short_comment_text(it)}}}}),
                          timeout=60)
        if c.status_code in (200, 201):
            it["comment_done"] = True
            return "full-video link comment posted (pin it by hand if you like)"
        last = f"{c.status_code}: {c.text[:160]}"
        time.sleep(20)
    it["comment_attempts"] = it.get("comment_attempts", 0) + 1
    it["comment_error"] = last
    return f"comment not posted yet, will retry ({last})"


def comment_pending(s):
    return bool(s.get("done") and s.get("video_id") and s.get("long_url") and not s.get("comment_done")
                and s.get("comment_attempts", 0) < 6)


def fetch_short(it, work):
    repo = os.environ["GITHUB_REPOSITORY"]
    tmp = work / ("_" + it["branch"])
    subprocess.run(["rm", "-rf", str(tmp)], check=True)
    subprocess.run(["git", "clone", "-q", "--depth", "1", "--single-branch", "--branch", it["branch"],
                    f"https://x-access-token:{os.environ['GH_TOKEN']}@github.com/{repo}.git", str(tmp)], check=True)
    src = tmp / it["file"]
    if not src.exists():
        raise RuntimeError("short file missing on branch " + it["branch"])
    dst = work / Path(it["file"]).name
    dst.write_bytes(src.read_bytes())
    subprocess.run(["rm", "-rf", str(tmp)], check=True)
    return dst


def post_short(ch, it):
    long_v = ch.find(it["link_title_contains"])
    if not long_v or long_v["status"]["privacyStatus"] != "public":
        return None, "long video not public yet, waiting"
    desc = it["description"].replace("{LONG_URL}", f"https://youtu.be/{long_v['id']}")
    work = HERE / "work"
    work.mkdir(exist_ok=True)
    path = fetch_short(it, work)
    title = it["title"]
    if "#shorts" not in title.lower():
        title = (title[:88] + " #Shorts").strip()
    body = {"snippet": {"title": title, "description": desc, "tags": it.get("tags", []), "categoryId": it.get("category", "27"),
                        "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True, "embeddable": True}}
    vid = upload_video(ch.h, path, body, path.stat().st_size)
    path.unlink(missing_ok=True)
    it["done"], it["video_id"], it["posted_at"] = True, vid, now().isoformat(timespec="seconds")
    it["long_url"] = f"https://youtu.be/{long_v['id']}"
    try:
        summary("   " + comment_on_short(ch, it))
    except Exception as e:  # noqa: BLE001
        summary(f"   comment on Short failed, will retry: {e}")
    return vid, "posted"


def delete_finished_branches(shorts):
    branches = {}
    for it in shorts:
        branches.setdefault(it["branch"], []).append(it.get("done") or it.get("attempts", 0) >= 4)
    for b, flags in branches.items():
        if all(flags):
            subprocess.run(["git", "push", "-q", "origin", "--delete", b], check=False)
            summary(f"branch {b} finished and removed")


def run():
    comments, shorts = load(COMMENTS), load(SHORTS)
    chans = {}

    def chan(n):
        if n not in chans:
            chans[n] = Chan(n)
            summary(f"Connected: **{chans[n].title}**")
        return chans[n]

    for it in [c for c in comments if comment_due(c)]:
        try:
            msg = post_comment(chan(it["channel"]), it)
            if not it.get("done"):
                it["attempts"] = it.get("attempts", 0)   # waiting is not a failure
            summary(f"💬 {it['channel']} / {it['title_contains']}: {msg}")
        except Exception as e:  # noqa: BLE001
            it["attempts"] = it.get("attempts", 0) + 1
            it["last_error"] = str(e)[:300]
            summary(f"❌ comment {it['channel']} / {it['title_contains']}: {e}")
        save(COMMENTS, comments)

    for it in [x for x in shorts if comment_pending(x)]:
        try:
            summary(f"\U0001F4AC short {it['id']}: {comment_on_short(chan(it['channel']), it)}")
        except Exception as e:  # noqa: BLE001
            it["comment_attempts"] = it.get("comment_attempts", 0) + 1
            summary(f"\u274c short comment {it['id']}: {e}")
        save(SHORTS, shorts)

    today = now().date().isoformat()
    for name in CHANNELS:
        mine = [s for s in shorts if s["channel"] == name]
        done_today = [s for s in mine if s.get("done") and s.get("posted_at", "")[:10] == today]
        last = max((ts(s["posted_at"]) for s in mine if s.get("done") and s.get("posted_at")), default=None)
        if len(done_today) >= MAX_SHORTS_PER_DAY:
            continue
        if last and now() - last < dt.timedelta(minutes=MIN_GAP_MIN):
            continue
        due = sorted([s for s in mine if short_due(s)], key=lambda s: s["publish_after"])
        if not due:
            continue
        it = due[0]
        try:
            vid, msg = post_short(chan(name), it)
            summary(f"🎬 {name}: {it['title']} -> {('https://youtube.com/shorts/' + vid) if vid else msg}")
        except Exception as e:  # noqa: BLE001
            it["attempts"] = it.get("attempts", 0) + 1
            it["last_error"] = str(e)[:300]
            summary(f"❌ short {name} / {it['id']} (attempt {it['attempts']}): {e}")
        save(SHORTS, shorts)
    save(COMMENTS, comments)
    save(SHORTS, shorts)
    delete_finished_branches(shorts)


def due():
    n = sum(1 for c in load(COMMENTS) if comment_due(c)) + sum(1 for s in load(SHORTS) if short_due(s) or comment_pending(s))
    print(n)


def whoami():
    for n in CHANNELS:
        try:
            summary(f"{n}: connected to **{hook(n, 'whoami')['channel']}**")
        except Exception as e:  # noqa: BLE001
            summary(f"{n}: not connected ({e})")


def uploadtest():
    """5-second black clip uploaded UNLISTED on the channel in env TEST_CHANNEL, checked after 90 s, then deleted.
    An API project that is not verified gets its uploads locked to private: this proves it is not."""
    n = os.environ.get("TEST_CHANNEL", "lamplight")
    ch = Chan(n)
    clip = HERE / "work" / "test.mp4"
    clip.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=640x360:d=5",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "5", "-c:v", "libx264", "-c:a", "aac",
                    "-shortest", str(clip)], check=True)
    body = {"snippet": {"title": "Pipeline test (will be deleted)", "description": "test", "categoryId": "27"},
            "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
    vid = upload_video(ch.h, clip, body, clip.stat().st_size)
    summary(f"{n}: test upload accepted on **{ch.title}**: {vid}")
    import time
    time.sleep(90)
    r = requests.get(f"{API}/videos", params={"part": "status", "id": vid}, headers=ch.h, timeout=30).json()
    st = r["items"][0]["status"] if r.get("items") else r
    summary(f"{n}: status after 90 s: {json.dumps(st)}")
    d = requests.delete(f"{API}/videos", params={"id": vid}, headers=ch.h, timeout=30)
    summary(f"{n}: test video deleted: HTTP {d.status_code}")


if __name__ == "__main__":
    {"due": due, "run": run, "whoami": whoami, "uploadtest": uploadtest}[sys.argv[1]]()
