"""Status report: posted on time? every platform + first comment OK? any comments? GitHub minutes? tokens?

Run: python report.py [days]   -> prints and writes status/report.md
Env: FB_PAGE_ID/TOKEN, MONEY_FB_PAGE_ID/TOKEN, ADDA_FB_PAGE_ID/TOKEN, X_* keys, GH_TOKEN + GH_REPO (minutes)
"""
import datetime as dt
import json
import math
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
FREE_MINUTES = 2000  # only applies to private repos; this repo is PUBLIC so Actions minutes are free and unlimited
DEFAULT_IDS = {"ADDA_FB_PAGE_ID": "61594820314272"}
IG_START = dt.datetime(2026, 10, 26, 7, 10, tzinfo=dt.timezone.utc)  # Instagram posting switched on
OK, BAD, WAIT, NA = "✅", "❌", "⏳", "—"
# Fixed expiry dates that cannot be read live (renew before these)
STATIC_EXPIRY = [("GitHub timer token (inside cron-job.org)", dt.date(2027, 9, 29)),
                 ("Claude login token (CLAUDE_CODE_OAUTH_TOKEN)", dt.date(2027, 10, 1))]
out = []


def p(line=""):
    print(line)
    out.append(line)


def ist(t):
    return t.astimezone(IST).strftime("%d %b %H:%M")


def page(id_env, tok_env):
    pid, tok = os.environ.get(id_env) or DEFAULT_IDS.get(id_env), os.environ.get(tok_env)
    if not pid or not tok:
        return None, None
    r = requests.get(f"{GRAPH}/{pid}", params={"fields": "access_token", "access_token": tok}, timeout=30)
    if r.ok and r.json().get("access_token"):
        tok = r.json()["access_token"]
    return pid, tok


def fb_id(url):
    return url.split(" ")[0].rstrip("/").split("/")[-1] if url else None


def fb_comments(obj_id, tok, own_id):
    r = requests.get(f"{GRAPH}/{obj_id}/comments", timeout=30,
                     params={"fields": "from,message,created_time", "limit": 50, "access_token": tok})
    if not r.ok:
        return None
    return [c for c in r.json().get("data", []) if (c.get("from") or {}).get("id") != own_id]


def ig_comments(page_id, tok):
    d = requests.get(f"{GRAPH}/{page_id}", params={"fields": "instagram_business_account{id,username}", "access_token": tok}, timeout=30).json()
    acc = d.get("instagram_business_account")
    if not acc:
        return None, []
    r = requests.get(f"{GRAPH}/{acc['id']}/media", timeout=40,
                     params={"fields": "permalink,timestamp,comments.limit(50){text,username,timestamp}",
                             "limit": 25, "access_token": tok})
    if not r.ok:
        return acc["username"], None
    found = []
    for m in r.json().get("data", []):
        for c in (m.get("comments") or {}).get("data", []):
            if c.get("username") != acc["username"]:
                found.append((m.get("permalink"), c.get("username"), c.get("text")))
    return acc["username"], found


# ---------- per-item platform status ----------
def platform_status(d, kind):
    """Return dict of icons: fb, fbc, ig, igc, x."""
    fb = d.get("facebook") or {}
    has_media = bool(d.get("image") or d.get("video") or fb.get("image") or fb.get("video"))
    fb_comment_wanted = bool(fb.get("first_comment") or d.get("first_comment"))
    s = {}
    fu = d.get("facebook_url") or ""
    s["fb"] = OK if fu else (BAD if d.get("facebook_error") or "facebook" in d.get("platforms", ["facebook"]) else NA)
    s["fbc"] = NA if not fb_comment_wanted or not fu else (BAD if "comment skipped" in fu else OK)
    posted = dt.datetime.fromisoformat(d.get("done_at") or d.get("posted_at") or NOW.isoformat())
    iu = d.get("instagram_url") or ""
    if not has_media or (posted < IG_START and not iu):
        s["ig"] = s["igc"] = NA
    else:
        s["ig"] = OK if iu else BAD
        s["igc"] = NA if not iu else (BAD if "comment skipped" in iu else OK)
    if kind == "cricket":
        if "x" in d.get("platforms", []):
            s["x"] = OK if d.get("x_url") else BAD
        else:
            s["x"] = NA
    return s


def table(rows, kind):
    head = "| Post | Planned (IST) | Posted (IST) | On time | Facebook | FB 1st comment | Instagram | IG 1st comment |"
    sep = "|---|---|---|---|---|---|---|---|"
    if kind == "cricket":
        head += " X |"
        sep += "---|"
    p(head)
    p(sep)
    for r in rows:
        line = f"| {r['name']} | {r['planned']} | {r['posted']} | {r['time']} | {r['fb']} | {r['fbc']} | {r['ig']} | {r['igc']} |"
        if kind == "cricket":
            line += f" {r.get('x', NA)} |"
        p(line)


def section(name, folder, id_env, tok_env, scheduled, kind, expected):
    p(f"## {name}")
    rows, problems = [], []
    for sub, state in (("posted", "posted"), ("failed", "failed"), ("queue", "queue")):
        d_ = folder / sub
        for f in sorted(d_.glob("*.json")) if d_.exists() else []:
            d = json.loads(f.read_text())
            when = scheduled(f, d)
            if not when or when < SINCE:
                continue
            r = {"name": f.stem, "planned": ist(when), "when": when}
            if state == "posted":
                done = dt.datetime.fromisoformat(d.get("done_at") or d.get("posted_at"))
                delay = (done - when).total_seconds() / 60
                r["posted"] = ist(done)
                r["time"] = OK if delay <= LATE_MIN else f"{BAD} {delay:+.0f} min"
                r.update(platform_status(d, kind))
                if any(v == BAD for k, v in r.items() if k in ("fb", "fbc", "ig", "igc", "x")) or delay > LATE_MIN:
                    problems.append(f.stem)
            elif state == "failed":
                r.update(posted=f"{BAD} failed", time=BAD, fb=BAD, fbc=NA, ig=BAD, igc=NA, x=BAD if kind == "cricket" else NA)
                problems.append(f.stem)
            else:  # still in the queue
                overdue = (NOW - when).total_seconds() / 60 > 60
                r.update(posted=f"{BAD} not posted" if overdue else f"{WAIT} scheduled", time=BAD if overdue else WAIT,
                         fb=BAD if overdue else WAIT, fbc=NA, ig=BAD if overdue else WAIT, igc=NA,
                         x=(BAD if overdue else WAIT) if kind == "cricket" and "x" in d.get("platforms", []) else NA)
                if overdue:
                    problems.append(f.stem)
            rows.append(r)
    # slots that should exist but have no file at all (job never triggered)
    for label, when in expected():
        if SINCE <= when <= NOW - dt.timedelta(minutes=60) and not any(label == r["name"] or (kind != "cricket" and r["name"].startswith(label + "-")) for r in rows):
            rows.append({"name": label, "planned": ist(when), "when": when, "posted": f"{BAD} not triggered", "time": BAD,
                         "fb": BAD, "fbc": NA, "ig": BAD, "igc": NA, "x": BAD if kind == "cricket" else NA})
            problems.append(label)
    rows.sort(key=lambda r: r["when"])
    posted_n = sum(1 for r in rows if r.get("posted", "")[:1].isdigit())
    p(f"{posted_n} posted · {len(problems)} with a problem {OK if not problems else BAD}")
    p()
    table(rows, kind)
    pid, tok = page(id_env, tok_env)
    p()
    p("**Comments from other people** (your own first comments excluded):")
    if not tok:
        p(f"- {BAD} Could not read (Facebook keys missing)")
        return tok
    n = 0
    for sub in ("posted",):
        for f in sorted((folder / sub).glob("*.json")) if (folder / sub).exists() else []:
            d = json.loads(f.read_text())
            when = scheduled(f, d)
            if not when or when < SINCE:
                continue
            oid = fb_id(d.get("facebook_url"))
            if oid:
                for c in fb_comments(oid, tok, pid) or []:
                    n += 1
                    p(f"- Facebook | {f.stem} | {(c.get('from') or {}).get('name', 'someone')}: {c.get('message', '')[:200]}")
    user, igc = ig_comments(pid, tok)
    for link, who, text in igc or []:
        n += 1
        p(f"- Instagram | {link} | @{who}: {(text or '(emoji/sticker)')[:200]}")
    if n == 0:
        p("- None yet.")
    return tok


def x_section():
    p("## X (@Smalik_wc) replies")
    try:
        from requests_oauthlib import OAuth1
        auth = OAuth1(os.environ["X_CONSUMER_KEY"], os.environ["X_CONSUMER_SECRET"],
                      os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"])
        me = requests.get("https://api.x.com/2/users/me", auth=auth, timeout=30).json()["data"]
        r = requests.get(f"https://api.x.com/2/users/{me['id']}/mentions", auth=auth, timeout=30,
                         params={"max_results": 20, "start_time": SINCE.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "tweet.fields": "created_at,author_id", "expansions": "author_id", "user.fields": "username"})
        if not r.ok:
            p(f"- {BAD} Could not read replies: {r.status_code} {r.text[:150]}")
            return
        users = {u["id"]: u["username"] for u in r.json().get("includes", {}).get("users", [])}
        data = r.json().get("data", [])
        for t in data:
            p(f"- X | @{users.get(t['author_id'], '?')}: {t['text'][:200]}")
        if not data:
            p("- None yet.")
    except Exception as e:  # noqa: BLE001
        p(f"- {BAD} Could not read X: {e}")


# ---------- GitHub minutes ----------
def minutes_section():
    p("## GitHub minutes (public repo: unlimited, free)")
    tok, repo = os.environ.get("GH_TOKEN"), os.environ.get("GH_REPO")
    if not tok or not repo:
        p(f"- {BAD} Could not read (no GitHub token in this run)")
        return
    start = NOW.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    nxt = (start + dt.timedelta(days=32)).replace(day=1)
    used, last3, page_n = 0, 0, 1
    while True:
        r = requests.get(f"https://api.github.com/repos/{repo}/actions/runs", timeout=30,
                         headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"},
                         params={"per_page": 100, "page": page_n, "created": f">={min(start, NOW - dt.timedelta(days=3)):%Y-%m-%d}"})
        if not r.ok:
            p(f"- {BAD} Could not read runs: {r.status_code}")
            return
        runs = r.json().get("workflow_runs", [])
        for run in runs:
            if not run.get("run_started_at") or not run.get("updated_at"):
                continue
            a = dt.datetime.fromisoformat(run["run_started_at"].replace("Z", "+00:00"))
            b = dt.datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
            m = max(1, math.ceil((b - a).total_seconds() / 60))
            if a >= start:
                used += m
            if a >= NOW - dt.timedelta(days=3):
                last3 += m
        if len(runs) < 100:
            break
        page_n += 1
    per_day = last3 / 3 if last3 else 0
    p("| Used this month | Pace (last 3 days) | Limit | |")
    p("|---|---|---|---|")
    p(f"| {used:,} min | {per_day:.0f} min/day | none (public repo) | {OK} no limit, nothing can run out |")
    p("Estimated from this repo's run times. If the repo is ever made private, the free plan is 2,000 minutes a month.")


# ---------- tokens ----------
def tokens_section():
    p("## Keys and expiry dates")
    p("| Key | Expires | Days left | |")
    p("|---|---|---|---|")
    for label, env in (("Cricket Ki Baat Page token", "FB_PAGE_TOKEN"), ("Paycheck Truths Page token", "MONEY_FB_PAGE_TOKEN"),
                       ("Creator Adda Page token", "ADDA_FB_PAGE_TOKEN"),
                       ("Credit Score Truths Page token", "CREDIT_FB_PAGE_TOKEN")):
        raw = os.environ.get(env)
        if not raw:
            p(f"| {label} | not set | — | {BAD} |")
            continue
        d = requests.get(f"{GRAPH}/debug_token", params={"input_token": raw, "access_token": raw}, timeout=30).json().get("data", {})
        if not d.get("is_valid", True):
            p(f"| {label} | invalid | 0 | {BAD} |")
            continue
        exp = d.get("data_access_expires_at") or d.get("expires_at")
        if not exp:
            p(f"| {label} | never | — | {OK} |")
            continue
        when = dt.datetime.fromtimestamp(exp, dt.timezone.utc)
        left = (when - NOW).days
        p(f"| {label} (Meta data access) | {when:%d %b %Y} | {left} | {OK if left > 30 else BAD + ' renew soon'} |")
    for label, day in STATIC_EXPIRY:
        left = (day - NOW.date()).days
        p(f"| {label} | about {day:%d %b %Y} | {left} | {OK if left > 30 else BAD + ' renew soon'} |")


def cricket_when(f, d):
    day, slot = f.stem[:10], f.stem[11:]
    hm = {"morning": "08:41", "evening": "19:41", "late": "19:41"}.get(slot.split("-")[0])
    if not hm:
        return None
    return dt.datetime.fromisoformat(f"{day}T{hm}:00+05:30")


def money_when(f, d):
    return dt.datetime.fromisoformat(d["publish_at"]) if d.get("publish_at") else None


def days_in_window():
    d = SINCE.astimezone(IST).date()
    while d <= NOW.astimezone(IST).date():
        yield d
        d += dt.timedelta(days=1)


def cricket_expected():
    for d in days_in_window():
        yield f"{d}-morning", dt.datetime.fromisoformat(f"{d}T08:41:00+05:30")
        yield f"{d}-evening", dt.datetime.fromisoformat(f"{d}T19:41:00+05:30")
        yield f"{d}-evening-reel", dt.datetime.fromisoformat(f"{d}T19:41:00+05:30")


def batch_expected(first_hm, start=None, skip=()):
    def gen():
        for d in days_in_window():
            if (start and str(d) < start) or str(d) in skip:
                continue
            yield f"{d}", dt.datetime.fromisoformat(f"{d}T{first_hm}:00+05:30")
    return gen


if __name__ == "__main__":
    p(f"# Status report - {NOW.astimezone(IST):%d %b %Y %H:%M} IST (last {DAYS} days)")
    p(f"{OK} done · {BAD} problem (failed, late, not posted or not triggered) · {WAIT} scheduled, not due yet · {NA} not needed")
    p()
    section("Cricket Ki Baat (Facebook + Instagram + X)", ROOT, "FB_PAGE_ID", "FB_PAGE_TOKEN", cricket_when, "cricket", cricket_expected)
    p()
    x_section()
    p()
    section("Paycheck Truths (Facebook + Instagram)", ROOT / "money", "MONEY_FB_PAGE_ID", "MONEY_FB_PAGE_TOKEN", money_when, "page", batch_expected("16:30"))
    p()
    section("Creator Adda (Facebook + Instagram)", ROOT / "adda", "ADDA_FB_PAGE_ID", "ADDA_FB_PAGE_TOKEN", money_when, "page", batch_expected("17:30"))
    p()
    # Credit Score Truths: started 4 Nov; 5 Nov was missed (daily job was blocked, fixed 6 Nov) and is deliberately not backfilled
    section("Credit Score Truths (Facebook + Instagram)", ROOT / "usfin" / "credit", "CREDIT_FB_PAGE_ID", "CREDIT_FB_PAGE_TOKEN", money_when, "page",
            batch_expected("17:30", start="2026-11-04", skip=("2026-11-05",)))
    if SINCE.astimezone(IST).date() <= dt.date(2026, 11, 5):
        p("_Note: 05 Nov (US day) was skipped on purpose - the daily job was blocked until 06 Nov and Saurabh chose not to backfill._")
    p()
    minutes_section()
    p()
    tokens_section()
    (ROOT / "status").mkdir(exist_ok=True)
    (ROOT / "status" / "report.md").write_text("\n".join(out) + "\n")
