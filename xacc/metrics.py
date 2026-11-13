"""X performance tracker (13 Nov 2026): reads impressions / likes / replies / reposts / bookmarks of our recent posts and
writes status/perf-x-<acct>.md, a ranked "what worked" file that the post-writing prompts read before every new post.

  python3 xacc/metrics.py wsp|inf|smalik [--force]

wsp, inf  -> tokens from xacc/tokens (same as run.py), posts from xacc/posted/
smalik    -> @Smalik_wc (cricket only, kept completely separate) - tokens from X_ACCESS_TOKEN / X_ACCESS_TOKEN_SECRET,
             posts from posted/
Cost control: the file is refreshed at most every MIN_AGE_H hours (owned reads are about $0.001 per post) and only posts
from the last DAYS days are read (max 100 per call).
"""
import datetime as dt
import json
import os
import pathlib
import re
import sys

import requests

ROOT = pathlib.Path(__file__).parent
REPO = ROOT.parent
STATUS = REPO / "status"
API = "https://api.x.com"
DAYS = 10
MIN_AGE_H = 4
sys.path.insert(0, str(ROOT))


def get_auth(acct):
    if acct == "smalik":
        from requests_oauthlib import OAuth1
        return OAuth1(os.environ["X_CONSUMER_KEY"], os.environ["X_CONSUMER_SECRET"],
                      os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"])
    import run
    return run.auth(acct)


def local_offset(acct):
    if acct == "smalik":
        return 330  # IST
    return json.loads((ROOT / "accounts.json").read_text())[acct]["tz_offset_minutes"]


def collect(acct):
    folder = REPO / "posted" if acct == "smalik" else ROOT / "posted"
    handle = "Smalik_wc" if acct == "smalik" else json.loads((ROOT / "accounts.json").read_text())[acct]["handle"]
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=DAYS)
    rows = []
    for f in sorted(folder.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        url = d.get("x_url") or ""
        m = re.search(rf"/{handle}/status/(\d+)", url, re.I)
        if not m:
            continue
        ts = d.get("posted_at") or d.get("created_at")
        try:
            when = dt.datetime.fromisoformat(ts)
            if when.tzinfo is None:
                when = when.replace(tzinfo=dt.timezone.utc)
        except Exception:
            when = dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc)
        if when < cutoff:
            continue
        rows.append({"id": m.group(1), "text": d.get("text", ""), "when": when, "image": bool(d.get("image")),
                     "file": f.name})
    rows.sort(key=lambda r: r["when"], reverse=True)
    return rows[:100]


def fetch(rows, auth):
    ids = ",".join(r["id"] for r in rows)
    r = requests.get(f"{API}/2/tweets", params={"ids": ids, "tweet.fields": "public_metrics,created_at"},
                     auth=auth, timeout=40)
    if not r.ok:
        raise SystemExit(f"metrics read failed {r.status_code}: {r.text[:300]}")
    got = {t["id"]: t["public_metrics"] for t in r.json().get("data", [])}
    out = []
    for row in rows:
        pm = got.get(row["id"])
        if not pm:
            continue
        eng = sum(pm.get(k, 0) for k in ("like_count", "reply_count", "retweet_count", "quote_count", "bookmark_count"))
        imp = pm.get("impression_count", 0)
        out.append({**row, "imp": imp, "likes": pm.get("like_count", 0), "replies": pm.get("reply_count", 0),
                    "reposts": pm.get("retweet_count", 0) + pm.get("quote_count", 0),
                    "bookmarks": pm.get("bookmark_count", 0), "eng": eng,
                    "rate": (eng / imp * 100) if imp else 0.0})
    return out


def first_line(t, n=70):
    s = re.sub(r"\s+", " ", t.strip().split("\n")[0])
    return (s[:n] + "...") if len(s) > n else s


def kind(t):
    low = t.lower()
    if "?" in t and ("reply" in low or "drop" in low or "tell us" in low or "poll" in low or "👇" in t):
        return "question / poll"
    if "→" in t:
        return "news with → bullets"
    if "this week" in low or "recap" in low:
        return "weekly recap"
    return "other news / text"


def group(rows, keyf):
    g = {}
    for r in rows:
        g.setdefault(keyf(r), []).append(r)
    res = []
    for k, v in g.items():
        res.append((k, len(v), sum(x["imp"] for x in v) / len(v), sum(x["eng"] for x in v) / len(v)))
    return sorted(res, key=lambda x: -x[2])


def write(acct, rows):
    STATUS.mkdir(exist_ok=True)
    off = local_offset(acct)
    lines = [f"<!-- generated_at: {dt.datetime.now(dt.timezone.utc).isoformat()} -->",
             f"# X performance - {acct} (last {DAYS} days, {len(rows)} posts read)", ""]
    if len(rows) < 5:
        lines += ["Not enough data yet (fewer than 5 posts with numbers). Follow the normal rules in the prompt; "
                  "do not guess a pattern from this file.", ""]
    if rows:
        tot_imp = sum(r["imp"] for r in rows)
        lines += [f"Average per post: {tot_imp / len(rows):.0f} impressions, "
                  f"{sum(r['eng'] for r in rows) / len(rows):.1f} interactions "
                  f"(likes + replies + reposts + quotes + bookmarks).", ""]
        ranked = sorted(rows, key=lambda r: (-r["imp"], -r["eng"]))
        lines.append("## Best posts (by impressions) - REPEAT these patterns: topic type, hook, format, length")
        for r in ranked[:8]:
            lines.append(f"- {r['imp']} imp | {r['likes']} likes, {r['replies']} replies, {r['reposts']} reposts, "
                         f"{r['bookmarks']} saves | {r['rate']:.1f}% | {'card' if r['image'] else 'text'} | "
                         f"{first_line(r['text'])}")
        if len(rows) >= 10:
            lines += ["", "## Weakest posts - do NOT repeat these angles or formats"]
            for r in ranked[-4:]:
                lines.append(f"- {r['imp']} imp | {r['eng']} interactions | {first_line(r['text'])}")
        lines += ["", "## By format (average impressions / interactions per post)"]
        for k, n, i, e in group(rows, lambda r: kind(r["text"])):
            lines.append(f"- {k}: {n} posts, {i:.0f} imp, {e:.1f} interactions")
        for k, n, i, e in group(rows, lambda r: "with card image" if r["image"] else "text only"):
            lines.append(f"- {k}: {n} posts, {i:.0f} imp, {e:.1f} interactions")
        lines += ["", f"## By hour (account local time, UTC{off // 60:+d}h)"]
        for k, n, i, e in group(rows, lambda r: f"{((r['when'] + dt.timedelta(minutes=off)).hour):02d}:00"):
            lines.append(f"- {k}: {n} posts, {i:.0f} imp, {e:.1f} interactions")
    lines += ["", "How to use: keep the account's rules, but lean toward the formats, hooks and topics at the top of this "
              "file and away from the weakest. Never copy a post; repeat the pattern with new facts. Small samples "
              "(under ~5 posts per group) are hints, not proof."]
    (STATUS / f"perf-x-{acct}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:14]))


def main():
    acct = sys.argv[1]
    force = "--force" in sys.argv
    f = STATUS / f"perf-x-{acct}.md"
    if f.exists() and not force:
        m = re.search(r"generated_at: (\S+)", f.read_text(encoding="utf-8")[:200])
        if m:
            age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(m.group(1))).total_seconds() / 3600
            if age < MIN_AGE_H:
                print(f"perf-x-{acct}.md is {age:.1f}h old - fresh enough, skipping (saves API cost)")
                return
    rows = collect(acct)
    if not rows:
        print("no posted tweets in the window yet")
        write(acct, [])
        return
    write(acct, fetch(rows, get_auth(acct)))


if __name__ == "__main__":
    main()
