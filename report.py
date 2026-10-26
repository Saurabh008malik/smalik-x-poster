"""Status report: were posts on time, and did anyone comment (Facebook, Instagram, X)?

Run: python report.py [days]   -> prints and writes status/report.md
Secrets (env): FB_PAGE_ID, FB_PAGE_TOKEN, MONEY_FB_PAGE_ID, MONEY_FB_PAGE_TOKEN, X_* keys
"""
import datetime as dt
import json
import os
import pathlib
import sys

import requests

GRAPH = "https://graph.facebook.com/v26.0"
ROOT = pathlib.Path(__file__).parent
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
NOW = dt.datetime.now(dt.timezone.utc)
SINCE = NOW - dt.timedelta(days=DAYS)
LATE_MIN = 30
out = []


def p(line=""):
    print(line)
    out.append(line)


def page(id_env, tok_env):
    pid, tok = os.environ.get(id_env), os.environ.get(tok_env)
    if not pid or not tok:
        return None, None
    r = requests.get(f"{GRAPH}/{pid}", params={"fields": "access_token", "access_token": tok}, timeout=30)
    if r.ok and r.json().get("access_token"):
        tok = r.json()["access_token"]
    return pid, tok


def fb_id(url):
    if not url:
        return None
    u = url.split(" ")[0]
    return u.rstrip("/").split("/")[-1]


def fb_comments(obj_id, tok, own_id):
    r = requests.get(f"{GRAPH}/{obj_id}/comments", timeout=30,
                     params={"fields": "from,message,created_time", "limit": 50, "access_token": tok})
    if not r.ok:
        return None
    return [c for c in r.json().get("data", []) if (c.get("from") or {}).get("id") != own_id]


def ig_comments(page_id, tok, since):
    """Comments by other people on recent Instagram media of the account linked to the Page."""
    d = requests.get(f"{GRAPH}/{page_id}", params={"fields": "instagram_business_account{id,username}", "access_token": tok}, timeout=30).json()
    acc = d.get("instagram_business_account")
    if not acc:
        return None, []
    r = requests.get(f"{GRAPH}/{acc['id']}/media", timeout=40,
                     params={"fields": "permalink,timestamp,comments_count,comments.limit(50){text,username,timestamp}",
                             "limit": 25, "access_token": tok})
    if not r.ok:
        return acc["username"], None
    found = []
    for m in r.json().get("data", []):
        for c in (m.get("comments") or {}).get("data", []):
            if c.get("username") != acc["username"]:
                found.append((m.get("permalink"), c.get("username"), c.get("text"), c.get("timestamp")))
    return acc["username"], found


def section(name, folder, id_env, tok_env, scheduled):
    p(f"## {name}")
    posted = folder / "posted"
    failed = folder / "failed"
    items = []
    for f in sorted(posted.glob("*.json")) if posted.exists() else []:
        d = json.loads(f.read_text())
        when = scheduled(f, d)
        if when and when >= SINCE:
            items.append((f, d, when))
    p(f"Posts in the last {DAYS} day(s): {len(items)}")
    late = []
    for f, d, when in items:
        done = d.get("done_at") or d.get("posted_at")
        if not done:
            continue
        done = dt.datetime.fromisoformat(done)
        delay = (done - when).total_seconds() / 60
        errs = [k for k in d if k.endswith("_error")]
        flag = "LATE" if delay > LATE_MIN else "on time"
        p(f"- {f.stem}: planned {when.astimezone(IST):%d %b %H:%M} IST, posted {done.astimezone(IST):%H:%M} IST ({delay:+.0f} min, {flag})"
          + (f"  ERRORS: {', '.join(errs)}" if errs else ""))
        if delay > LATE_MIN or errs:
            late.append(f.stem)
    fails = list(failed.glob("*.json")) if failed.exists() else []
    if fails:
        p(f"Failed items on record: {len(fails)} ({', '.join(x.stem for x in fails[-5:])})")
    pid, tok = page(id_env, tok_env)
    p("")
    p("Comments from other people (your own first comments are excluded):")
    if not tok:
        p("- Could not read (Facebook keys missing)")
        return
    n = 0
    for f, d, when in items:
        oid = fb_id(d.get("facebook_url"))
        if oid:
            cs = fb_comments(oid, tok, pid)
            if cs is None:
                p(f"- Facebook {f.stem}: could not read comments")
            for c in cs or []:
                n += 1
                p(f"- Facebook | {f.stem} | {(c.get('from') or {}).get('name', 'someone')}: {c.get('message', '')[:200]}")
    user, igc = ig_comments(pid, tok, SINCE)
    if igc is None:
        p(f"- Instagram @{user}: could not read comments")
    for link, who, text, ts in igc or []:
        n += 1
        p(f"- Instagram | {link} | @{who}: {(text or '')[:200]}")
    if n == 0:
        p("- None yet on Facebook or Instagram.")
    return n


def x_section():
    p("## X (@Smalik_wc)")
    try:
        from requests_oauthlib import OAuth1
        auth = OAuth1(os.environ["X_CONSUMER_KEY"], os.environ["X_CONSUMER_SECRET"],
                      os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"])
        me = requests.get("https://api.x.com/2/users/me", auth=auth, timeout=30).json()["data"]
        r = requests.get(f"https://api.x.com/2/users/{me['id']}/mentions", auth=auth, timeout=30,
                         params={"max_results": 20, "start_time": SINCE.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "tweet.fields": "created_at,author_id,conversation_id", "expansions": "author_id",
                                 "user.fields": "username"})
        if not r.ok:
            p(f"- Could not read replies/mentions: {r.status_code} {r.text[:150]}")
            return
        users = {u["id"]: u["username"] for u in r.json().get("includes", {}).get("users", [])}
        data = r.json().get("data", [])
        for t in data:
            p(f"- X | @{users.get(t['author_id'], '?')}: {t['text'][:200]}")
        if not data:
            p("- No replies or mentions yet.")
    except Exception as e:  # noqa: BLE001
        p(f"- Could not read X: {e}")


def cricket_when(f, d):
    day = f.stem[:10]
    slot = f.stem[11:]
    hm = {"morning": "08:41", "evening": "19:41", "reel": "19:42"}.get(slot.split("-")[0])
    if not hm:
        return None
    return dt.datetime.fromisoformat(f"{day}T{hm}:00+05:30")


def money_when(f, d):
    return dt.datetime.fromisoformat(d["publish_at"]) if d.get("publish_at") else None


if __name__ == "__main__":
    p(f"# Status report - {NOW.astimezone(IST):%d %b %Y %H:%M} IST (last {DAYS} days)")
    p()
    section("Cricket Ki Baat (Facebook + Instagram + X)", ROOT, "FB_PAGE_ID", "FB_PAGE_TOKEN", cricket_when)
    p()
    x_section()
    p()
    section("Paycheck Truths (Facebook + Instagram)", ROOT / "money", "MONEY_FB_PAGE_ID", "MONEY_FB_PAGE_TOKEN", money_when)
    (ROOT / "status").mkdir(exist_ok=True)
    (ROOT / "status" / "report.md").write_text("\n".join(out) + "\n")
