"""Last-resort post: used when all Claude attempts failed, so the slot is never missed.

Usage: python3 reserve/fallback.py DATE SLOT
Takes the next unused evergreen item from reserve/items, copies its cards into queue/ under the normal
names (queue/DATE-SLOT.json/.png/-fb.jpg) so the normal `python poster.py` step publishes it.
reserve/used.json remembers the order used; when every item has been used, the least recently used goes first.
"""
import datetime as dt, json, pathlib, shutil, sys

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
date, slot = sys.argv[1], sys.argv[2]
name = f"{date}-{slot}"

FAN = json.loads((HERE / "fan_questions.json").read_text(encoding="utf-8"))
items = sorted(p.stem for p in (HERE / "items").glob("*.json"))
used_file = HERE / "used.json"
used = json.loads(used_file.read_text()) if used_file.exists() else []
used = [u for u in used if u in items]
unused = [i for i in items if i not in used]
pick = unused[0] if unused else used[0]
used = [u for u in used if u != pick] + [pick]

d = json.loads((HERE / "items" / f"{pick}.json").read_text(encoding="utf-8"))
q = ROOT / "queue"
q.mkdir(exist_ok=True)
shutil.copy(HERE / "cards" / f"{pick}.png", q / f"{name}.png")   # kept so the daily check passes; X does not use it
shutil.copy(HERE / "cards" / f"{pick}-fb.jpg", q / f"{name}-fb.jpg")
out = {
    "text": FAN[(dt.date.fromisoformat(date).toordinal() * 7 + (0 if slot == "morning" else 1)) % len(FAN)],   # X gets a fan question, never old news
    "image": "",
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "platforms": ["x", "facebook"],
    "facebook": {**d["facebook"], "image": f"{name}-fb.jpg"},
    "instagram": d["instagram"],
    "reserve_id": pick,
}
(q / f"{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
used_file.write_text(json.dumps(used, indent=1))
print(f"Reserve post used for {name}: {pick}")
