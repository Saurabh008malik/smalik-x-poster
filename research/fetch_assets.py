"""Download public-domain assets (text files + Wikimedia Commons images) inside GitHub Actions.
config: {"urls": {"name.ext": "https://..."}, "commons": [{"q": "search", "n": 40, "tag": "genesis"}], "min_width": 900, "thumb": 1600}
Writes research/assets/<name>/ (files, img/*.jpg, sources.json).
"""
import json, sys, pathlib, re, time, requests

cfg = json.load(open(sys.argv[1])); out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "LamplightResearch/1.0 (contact: saurabh6041@gmail.com)"}
for name, url in cfg.get("urls", {}).items():
    try:
        r = requests.get(url, headers=H, timeout=120); r.raise_for_status()
        (out / name).write_bytes(r.content); print("OK url", name, len(r.content))
    except Exception as e:
        print("ERR url", name, e)

OK_LIC = re.compile(r"public domain|cc0|pd-|no restrictions|pd ", re.I)
img = out / "img"; img.mkdir(exist_ok=True); sources = []
seen = set()
for job in cfg.get("commons", []):
    q, n, tag = job["q"], job.get("n", 40), job.get("tag", "x")
    try:
        api = "https://commons.wikimedia.org/w/api.php"
        params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": min(50, n * 2),
                  "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": cfg.get("thumb", 1600)}
        r = requests.get(api, params=params, headers=H, timeout=60); r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
    except Exception as e:
        print("ERR commons", q, e); continue
    got = 0
    for pid, p in pages.items():
        if got >= n: break
        ii = (p.get("imageinfo") or [{}])[0]; em = ii.get("extmetadata", {})
        lic = (em.get("LicenseShortName", {}).get("value", "") + " " + em.get("License", {}).get("value", "") + " " + em.get("Copyrighted", {}).get("value", ""))
        if not (OK_LIC.search(lic) or em.get("Copyrighted", {}).get("value", "").lower() == "false"): continue
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/tiff"): continue
        if (ii.get("width") or 0) < cfg.get("min_width", 900): continue
        title = p["title"]
        if title in seen: continue
        seen.add(title)
        turl = ii.get("thumburl") or ii.get("url")
        fn = f"{tag}_{len(sources):03d}.jpg"
        try:
            d = requests.get(turl, headers=H, timeout=120); d.raise_for_status()
            (img / fn).write_bytes(d.content)
        except Exception as e:
            print("ERR img", title, e); continue
        sources.append({"file": fn, "title": title, "page": f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}",
                        "license": em.get("LicenseShortName", {}).get("value", ""), "artist": re.sub("<[^>]+>", "", em.get("Artist", {}).get("value", ""))[:120],
                        "query": q, "width": ii.get("width"), "height": ii.get("height")})
        got += 1; time.sleep(0.3)
    print("OK commons", q, got)
json.dump(sources, open(out / "sources.json", "w"), indent=1)
print("images:", len(sources))
