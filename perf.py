"""Performance tracker: which posts/reels got the most engagement, so the content robots can repeat the pattern.

Run: python perf.py cricket|money|adda   -> writes status/perf-<page>.md (read by the content prompts)
Uses the Page token (likes, comments, shares; views/reach when the token has insights permission).
"""
import datetime as dt
import json
import os
import pathlib
import sys

import requests

GRAPH = "https://graph.facebook.com/v26.0"
ROOT = pathlib.Path(__file__).parent
DAYS = 14
PAGES = {
    "cricket": (ROOT, "FB_PAGE_ID", "FB_PAGE_TOKEN", None),
    "money": (ROOT / "money", "MONEY_FB_PAGE_ID", "MONEY_FB_PAGE_TOKEN", None),
    "adda": (ROOT / "adda", "ADDA_FB_PAGE_ID", "ADDA_FB_PAGE_TOKEN", "61594820314272"),
}


def get(path, tok, **params):
    try:
        r = requests.get(f"{GRAPH}/{path}", params={**params, "access_token": tok}, timeout=30)
        return r.json() if r.ok else {"_error": r.text[:200]}
    except requests.RequestException as e:
        return {"_error": str(e)}


def page_token(pid, tok):
    d = get(pid, tok, fields="access_token")
    return d.get("access_token") or tok


def fb_stats(url, tok):
    oid = url.split(" ")[0].rstrip("/").split("/")[-1]
    s = {"likes": 0, "comments": 0, "shares": 0, "views": None}
    if "/reel/" in url:
        d = get(oid, tok, fields="likes.summary(true).limit(0),comments.summary(true).limit(0)")
        s["likes"] = ((d.get("likes") or {}).get("summary") or {}).get("total_count", 0)
        s["comments"] = ((d.get("comments") or {}).get("summary") or {}).get("total_count", 0)
        ins = get(f"{oid}/video_insights", tok, metric="total_video_views")
        for m in ins.get("data", []):
            s["views"] = (m.get("values") or [{}])[0].get("value")
    else:
        d = get(oid, tok, fields="reactions.summary(true).limit(0),comments.summary(true).limit(0),shares")
        s["likes"] = ((d.get("reactions") or {}).get("summary") or {}).get("total_count", 0)
        s["comments"] = ((d.get("comments") or {}).get("summary") or {}).get("total_count", 0)
        s["shares"] = (d.get("shares") or {}).get("count", 0)
        ins = get(f"{oid}/insights", tok, metric="post_impressions_unique")
        for m in ins.get("data", []):
            s["views"] = (m.get("values") or [{}])[0].get("value")
    return s


def ig_media(pid, tok):
    acc = (get(pid, tok, fields="instagram_business_account").get("instagram_business_account") or {}).get("id")
    if not acc:
        return {}
    d = get(f"{acc}/media", tok, fields="permalink,like_count,comments_count,media_type", limit=50)
    out = {}
    for m in d.get("data", []):
        views = None
        ins = get(f"{m['id']}/insights", tok, metric="reach,saved,shares")
        vals = {x["name"]: (x.get("values") or [{}])[0].get("value") for x in ins.get("data", [])}
        if vals:
            views = vals.get("reach")
        out[m["permalink"].rstrip("/").replace("/reels/", "/reel/")] = {
            "likes": m.get("like_count", 0), "comments": m.get("comments_count", 0),
            "saves": vals.get("saved", 0) or 0, "shares": vals.get("shares", 0) or 0, "views": views}
    return out


def describe(d):
    fb = d.get("facebook") or {}
    cap = (fb.get("caption") or d.get("caption") or d.get("text") or "").strip().split("\n")[0]
    kind = "reel" if (d.get("video") or fb.get("video")) else ("card" if (d.get("image") or fb.get("image")) else "text")
    card = d.get("card") or {}
    return kind, cap[:110], card.get("theme") or card.get("kicker") or ""


def main(name):
    folder, id_env, tok_env, default_id = PAGES[name]
    pid, tok = os.environ.get(id_env) or default_id, os.environ.get(tok_env)
    lines = [f"# What performed best on this page (last {DAYS} days, updated {dt.date.today()})", ""]
    if not pid or not tok:
        lines.append("No data yet (Page keys missing).")
    else:
        tok = page_token(pid, tok)
        igm = ig_media(pid, tok)
        since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=DAYS)
        rows, have_views = [], False
        for f in sorted((folder / "posted").glob("*.json")):
            d = json.loads(f.read_text())
            when = d.get("done_at") or d.get("posted_at")
            if not when or dt.datetime.fromisoformat(when) < since:
                continue
            tot = {"likes": 0, "comments": 0, "shares": 0, "saves": 0, "views": 0}
            if d.get("facebook_url"):
                for k, v in fb_stats(d["facebook_url"], tok).items():
                    if v is not None:
                        tot[k] = tot.get(k, 0) + v
                        have_views |= k == "views"
            iu = (d.get("instagram_url") or "").split(" ")[0].rstrip("/").replace("/reels/", "/reel/")
            for k, v in (igm.get(iu) or {}).items():
                if v is not None:
                    tot[k] = tot.get(k, 0) + v
                    have_views |= k == "views"
            kind, hook, theme = describe(d)
            score = tot["likes"] + 3 * tot["comments"] + 2 * tot["shares"] + 2 * tot["saves"] + tot["views"] / 100
            rows.append((score, f.stem, kind, hook, theme, tot))
        rows.sort(reverse=True)
        if not rows:
            lines.append("No posts in this window yet.")
        else:
            lines.append("Score = likes + 3×comments + 2×shares + 2×saves + views/100 (Facebook + Instagram together).")
            if not have_views:
                lines.append("Views/reach not available yet (token lacks insights permission) — ranking uses engagement only.")
            lines += ["", "## Top performers — repeat these patterns (hook style, topic, format)", ""]
            for s, n, k, h, t, tot in rows[:5]:
                lines.append(f"- [{k}] score {s:.1f} | {h} | likes {tot['likes']}, comments {tot['comments']}, shares {tot['shares']}, saves {tot['saves']}, views {tot['views'] or '-'} | {n}")
            lines += ["", "## Weakest — avoid repeating these patterns", ""]
            for s, n, k, h, t, tot in rows[-3:][::-1]:
                lines.append(f"- [{k}] score {s:.1f} | {h} | {n}")
            by = {}
            for s, n, k, *_ in rows:
                by.setdefault(k, []).append(s)
            lines += ["", "## Average score by format", ""]
            lines += [f"- {k}: {sum(v) / len(v):.1f} over {len(v)} posts" for k, v in sorted(by.items(), key=lambda x: -sum(x[1]) / len(x[1]))]
    (ROOT / "status").mkdir(exist_ok=True)
    (ROOT / "status" / f"perf-{name}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
