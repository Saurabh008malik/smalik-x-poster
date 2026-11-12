"""Automation for the extra X accounts (Wall St Pulse = wsp, Bollywood Ki Baat = bkb). 13 Nov 2026.

  python xacc/run.py slot ACCT [dry]        -> decides which slot to fill now (writes GITHUB_OUTPUT lines)
  python xacc/run.py fallback ACCT DATE KEY -> writes a simple current-question post (last try, so a slot is never empty)
  python xacc/run.py post ACCT DATE KEY     -> publishes xacc/queue/ACCT-DATE-KEY.json to X
  python xacc/run.py auth-start ACCT        -> prints the X authorize link (log in as the NEW account, press Authorize, copy the PIN)
  python xacc/run.py auth-finish ACCT PIN   -> stores the account's token (encrypted) and sets go_live = today
  python xacc/run.py whoami ACCT            -> checks the stored token

Tokens never appear in logs: they are stored in xacc/tokens/ACCT.enc, encrypted with a key derived from the
X_CONSUMER_SECRET GitHub secret (the repo is public, so nothing secret is ever written in plain text).
Posts never contain links (X charges $0.20 for a post with a URL vs $0.015 without).
"""
import base64
import datetime as dt
import hashlib
import json
import os
import pathlib
import random
import sys
import time

ROOT = pathlib.Path(__file__).parent
CFG_PATH = ROOT / "accounts.json"
CFG = json.loads(CFG_PATH.read_text())
Q, POSTED, FAILED, DRAFTS, TOK = (ROOT / d for d in ("queue", "posted", "failed", "drafts", "tokens"))
API = "https://api.x.com"


def out(**kv):
    lines = "".join(f"{k}={v}\n" for k, v in kv.items())
    print(lines, end="")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(lines)


def now_local(acct):
    return dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=CFG[acct]["tz_offset_minutes"])


def active_slots(acct, today):
    c = CFG[acct]
    if not c.get("go_live"):
        return []
    days = (today - dt.date.fromisoformat(c["go_live"])).days
    if days < 0:
        return []
    n = next(n for d, n in c["ramp"] if days < d)
    if today.weekday() >= 5:
        n = max(2, round(n * c.get("weekend_factor", 1)))
    return sorted(c["slots"][:n])


def slot(acct, dry=False):
    now = now_local(acct)
    date = now.strftime("%Y-%m-%d")
    if dry:
        return out(date=date, key=now.strftime("%H%M"), skip="no", dry="true", **{"try": 1})
    nowm = now.hour * 60 + now.minute
    for s in active_slots(acct, now.date()):
        h, m = map(int, s.split(":"))
        sm = h * 60 + m
        if nowm < sm:
            break
        if nowm - sm > 150:
            continue
        key = f"{h:02d}{m:02d}"
        name = f"{acct}-{date}-{key}"
        if (POSTED / f"{name}.json").exists() or (Q / f"{name}.json").exists():
            continue
        tries_f = FAILED / f"{name}.tries"
        tries = len(tries_f.read_text().split()) if tries_f.exists() else 0
        if tries >= 3:
            continue
        FAILED.mkdir(exist_ok=True)
        with open(tries_f, "a") as f:
            f.write(dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")
        return out(date=date, key=key, skip="no", dry="false", **{"try": tries + 1})
    reason = "account not live yet (no token)" if not CFG[acct].get("go_live") else "every due slot is posted"
    print("Nothing to do:", reason)
    out(date=date, key="", skip="yes", dry="false", **{"try": 0})


FALLBACK = {
    "wsp": [
        "𝗤𝗨𝗘𝗦𝗧𝗜𝗢𝗡 𝗢𝗙 𝗧𝗛𝗘 𝗗𝗔𝗬\n\nWhich stock are you watching most closely this week, and why?\n\nDrop the ticker below 👇",
        "𝗣𝗢𝗟𝗟 𝗧𝗜𝗠𝗘\n\nWhat moves markets more right now:\n\n📈 Earnings\n🏦 The Fed\n🛢️ Oil\n🤖 AI spending\n\nReply with yours 👇",
        "𝗤𝗨𝗜𝗖𝗞 𝗤𝗨𝗘𝗦𝗧𝗜𝗢𝗡\n\nAre you adding to stocks, holding cash, or waiting for a dip this month?\n\nTell us below 👇",
        "𝗬𝗢𝗨𝗥 𝗧𝗔𝗞𝗘\n\nWhich sector wins the next 12 months: tech, energy, healthcare or banks?\n\nReply 👇",
    ],
    "bkb": [
        "आज का सवाल 🎬\n\nइस हफ़्ते आप कौन-सी फ़िल्म या वेब सीरीज़ देखने वाले हैं?\n\nकमेंट में बताइए 👇",
        "सवाल 🍿\n\nइस साल की आपकी फ़ेवरेट हिंदी फ़िल्म कौन-सी है?\n\nनाम लिखिए 👇",
        "आप बताइए 🎥\n\nथिएटर या OTT, नई फ़िल्में आप कहाँ देखना पसंद करते हैं?\n\nजवाब दीजिए 👇",
        "फ़िल्मी सवाल ⭐\n\nकिस एक्टर की अगली फ़िल्म का आपको सबसे ज़्यादा इंतज़ार है?\n\nकमेंट करें 👇",
    ],
}


def fallback(acct, date, key):
    used = {json.loads(p.read_text()).get("text") for p in sorted(POSTED.glob(f"{acct}-*.json"))[-20:]}
    options = [t for t in FALLBACK[acct] if t not in used] or FALLBACK[acct]
    Q.mkdir(exist_ok=True)
    (Q / f"{acct}-{date}-{key}.json").write_text(json.dumps({
        "text": random.choice(options), "kind": "question",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat()}, ensure_ascii=False, indent=1))
    print("Fallback question queued for", acct, date, key)


# ---------- tokens ----------
def fernet(acct):
    from cryptography.fernet import Fernet
    k = hashlib.sha256((os.environ["X_CONSUMER_SECRET"] + ":xacc:" + acct).encode()).digest()
    return Fernet(base64.urlsafe_b64encode(k))


def save_enc(path, data, acct):
    TOK.mkdir(exist_ok=True)
    path.write_bytes(fernet(acct).encrypt(json.dumps(data).encode()))


def load_enc(path, acct):
    return json.loads(fernet(acct).decrypt(path.read_bytes()))


def auth(acct):
    from requests_oauthlib import OAuth1
    t = load_enc(TOK / f"{acct}.enc", acct)
    return OAuth1(os.environ["X_CONSUMER_KEY"], os.environ["X_CONSUMER_SECRET"], t["token"], t["secret"])


def auth_start(acct):
    from requests_oauthlib import OAuth1Session
    s = OAuth1Session(os.environ["X_CONSUMER_KEY"], client_secret=os.environ["X_CONSUMER_SECRET"], callback_uri="oob")
    r = s.fetch_request_token(API + "/oauth/request_token")
    save_enc(TOK / f"{acct}.pending.enc", {"token": r["oauth_token"], "secret": r["oauth_token_secret"]}, acct)
    print("\nOPEN THIS LINK while logged in to X as the NEW account, press 'Authorize app', copy the PIN:\n")
    print(f"https://api.x.com/oauth/authorize?oauth_token={r['oauth_token']}\n")
    url = f"https://api.x.com/oauth/authorize?oauth_token={r['oauth_token']}"
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(f"## Connect @{CFG[acct]['handle']}\n\n1. Log in to X as **@{CFG[acct]['handle']}**\n2. Open: {url}\n3. Press **Authorize app**, copy the PIN\n4. Run this workflow again with step = finish and the PIN\n")


def auth_finish(acct, pin):
    import requests
    from requests_oauthlib import OAuth1, OAuth1Session
    p = load_enc(TOK / f"{acct}.pending.enc", acct)
    s = OAuth1Session(os.environ["X_CONSUMER_KEY"], client_secret=os.environ["X_CONSUMER_SECRET"],
                      resource_owner_key=p["token"], resource_owner_secret=p["secret"], verifier=pin.strip())
    r = s.fetch_access_token(API + "/oauth/access_token")
    save_enc(TOK / f"{acct}.enc", {"token": r["oauth_token"], "secret": r["oauth_token_secret"],
                                   "screen_name": r.get("screen_name"), "user_id": r.get("user_id")}, acct)
    (TOK / f"{acct}.pending.enc").unlink(missing_ok=True)
    print("Connected X account:", "@" + str(r.get("screen_name")))
    if str(r.get("screen_name", "")).lower() != CFG[acct]["handle"].lower():
        print(f"WARNING: expected @{CFG[acct]['handle']} - check that the right account was logged in.")
    if not CFG[acct].get("go_live"):
        CFG[acct]["go_live"] = now_local(acct).strftime("%Y-%m-%d")
        CFG_PATH.write_text(json.dumps(CFG, ensure_ascii=False, indent=2) + "\n")
        print("go_live set to", CFG[acct]["go_live"])


def whoami(acct):
    import requests
    r = requests.get(API + "/2/users/me", auth=auth(acct), timeout=30)
    print(r.status_code, r.json().get("data", {}).get("username") if r.ok else r.text[:300])


# ---------- posting ----------
def post(acct, date, key):
    import requests
    name = f"{acct}-{date}-{key}"
    qf = Q / f"{name}.json"
    d = json.loads(qf.read_text(encoding="utf-8"))
    age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(d["created_at"])).total_seconds() / 60
    if age > d.get("max_age_minutes", 120):
        raise SystemExit(f"Too old to post ({age:.0f} min) - never post stale news")
    if "http://" in d["text"] or "https://" in d["text"] or "www." in d["text"]:
        raise SystemExit("Post contains a link - links are not allowed (cost and reach)")
    payload = {"text": d["text"]}
    img = Q / d["image"] if d.get("image") else None
    a = auth(acct)
    if img and img.exists():
        up = requests.post(API + "/2/media/upload", auth=a, timeout=60,
                           json={"media": base64.b64encode(img.read_bytes()).decode(), "media_category": "tweet_image"})
        if up.ok:
            payload["media"] = {"media_ids": [up.json()["data"]["id"]]}
        else:
            print("Image upload failed, posting text only:", up.status_code, up.text[:200])
    r = requests.post(API + "/2/tweets", auth=a, json=payload, timeout=30)
    if not r.ok:
        raise SystemExit(f"X post failed {r.status_code}: {r.text[:400]}")
    tid = r.json()["data"]["id"]
    time.sleep(4)
    g = requests.get(f"{API}/2/tweets/{tid}", auth=a, timeout=30)
    live = g.ok and g.json().get("data", {}).get("id") == tid
    d["x_url"] = f"https://x.com/{CFG[acct]['handle']}/status/{tid}"
    d["posted_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    d["confirmed_live"] = live
    POSTED.mkdir(exist_ok=True)
    (POSTED / f"{name}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    if img and img.exists():
        img.rename(POSTED / img.name)
    qf.unlink()
    print("Posted:", d["x_url"], "| confirmed live:", live)


if __name__ == "__main__":
    cmd, acct = sys.argv[1], sys.argv[2]
    assert acct in CFG, f"unknown account {acct}"
    if cmd == "slot":
        slot(acct, dry=len(sys.argv) > 3 and sys.argv[3] == "true")
    elif cmd == "fallback":
        fallback(acct, sys.argv[3], sys.argv[4])
    elif cmd == "post":
        post(acct, sys.argv[3], sys.argv[4])
    elif cmd == "auth-start":
        auth_start(acct)
    elif cmd == "auth-finish":
        auth_finish(acct, sys.argv[3])
    elif cmd == "whoami":
        whoami(acct)
