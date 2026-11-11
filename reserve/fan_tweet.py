"""Last-resort X tweet so a slot is never empty. It is a fan question, NOT news, so it can never be old news.

Usage: python3 reserve/fan_tweet.py DATE KEY
Writes queue/DATE-flash-KEY.json (X only). Used by xflash.yml only after the normal attempts for the slot failed.
"""
import datetime as dt, json, pathlib, sys

HERE = pathlib.Path(__file__).parent
date, key = sys.argv[1], sys.argv[2]
pool = json.loads((HERE / "fan_questions.json").read_text(encoding="utf-8"))
day = dt.date.fromisoformat(date).toordinal()
idx = (day * 7 + int(key[:2])) % len(pool)
q = HERE.parent / "queue"
q.mkdir(exist_ok=True)
out = {"text": pool[idx], "created_at": dt.datetime.now(dt.timezone.utc).isoformat(), "platforms": ["x", "facebook"],
       "kind": "flash", "max_age_minutes": 90, "last_resort": True,
       # Cricket Ki Baat Page gets the same question as a text post (no card, so Instagram is skipped for this one)
       "facebook": {"caption": pool[idx].split("#")[0].rstrip() + "\n\nAapka jawab comment karo 👇\n\n#CricketKiBaat #Cricket",
                    "first_comment": "Roz ki cricket baatein ke liye Cricket Ki Baat ko Follow karo 🔔🏏"}}
(q / f"{date}-flash-{key}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("Fan-question tweet queued for", date, key, "index", idx)
