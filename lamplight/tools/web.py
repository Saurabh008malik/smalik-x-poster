"""Extract World English Bible verses (Gutenberg plain text) without footnotes.
Usage: python3 tools/web.py genesis 1:1-2:3   -> prints verses as plain prose
"""
import re, sys, pathlib
SRC = {"genesis": "/home/claude/lamplight/a1/web_genesis.txt", "psalms": "/home/claude/lamplight/a1/web_psalms.txt"}
def load(book):
    t = pathlib.Path(SRC[book]).read_text(encoding="utf-8", errors="ignore")
    t = t.split("*** START")[1].split("*** END")[0]
    verses = {}
    cur = None
    for line in t.splitlines():
        m = re.match(r"^(\d{3}):(\d{3})\s(.*)$", line)
        if m:
            cur = (int(m.group(1)), int(m.group(2))); verses[cur] = m.group(3).strip()
        elif cur and line.startswith("        "):
            verses[cur] += " " + line.strip()
    for k, v in verses.items():
        v = re.sub(r"\{[^}]*\}", "", v)
        verses[k] = re.sub(r"\s+", " ", v).strip()
    return verses
def passage(book, ref):
    vs = load(book)
    a, b = ref.split("-") if "-" in ref else (ref, ref)
    c1, v1 = map(int, a.split(":"))
    if ":" in b: c2, v2 = map(int, b.split(":"))
    else: c2, v2 = c1, int(b)
    out = [v for (c, n), v in sorted(vs.items()) if (c, n) >= (c1, v1) and (c, n) <= (c2, v2)]
    return " ".join(out)
if __name__ == "__main__":
    print(passage(sys.argv[1], sys.argv[2]))
