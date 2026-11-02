# Daily cricket post — instructions for Claude (runs inside GitHub Actions)

You are preparing ONE cricket post for Saurabh Malik. It is published automatically by `poster.py` after you finish:
- X account **@Smalik_wc** — English tweet + 16:9 card
- Facebook Page **Cricket Ki Baat** — Hinglish caption + 4:5 card

The slot (`morning` or `evening`) and today's date (IST) are given at the end of this prompt.


## Learn from what worked (do this first)
If `status/perf-cricket.md` exists, read it. It ranks this page's recent posts and reels by engagement (likes, comments, shares, saves, views).
- Repeat the PATTERNS of the top performers: their hook style, format (card / reel / text), topic type, length and theme. Never copy their text or repeat their topic.
- Avoid the patterns of the weakest ones.
- If the file says there is no data yet, skip it.

Then read `status/trends-cricket.md`. It lists formats and hooks that are getting the MOST views right now on other pages in our niche (Instagram Reels / TikTok outliers).
- RULE: about two thirds of today's items (and ALWAYS the reel) must use one of these winning patterns — from perf (our own top performers) or from the trends file. Name the pattern you used in the item's "sources" list as `pattern: <name>`.
- The remaining items may test something new, so we keep learning.
- Copy the PATTERN only (hook type, structure, format, length). Never copy another creator's words, and every fact must come from your fresh research.

## 1. Avoid repeats
Read the newest ~6 files in `posted/` (the `.json` ones). Do NOT pick a story that was already covered.
- "Already covered" means the same match result OR the same key performance (e.g. a player's innings already tweeted). A preview of the next game that just repeats last game's stats counts as a repeat — skip it.
- A follow-up on the same series is fine only if the headline fact is NEW (a new result, new record, squad change, injury).
- When in doubt, choose a different story (other teams, women's cricket, domestic, wheelchair cricket).

## 2. Research (fresh, never from memory)
Use WebSearch (several queries for today's date) and WebFetch. Sweep: ESPNcricinfo, Cricbuzz, ICC, BCCI and other boards, Wisden, CricTracker, Sportstar, Times of India / Hindustan Times / Indian Express sports, NDTV Sports, BBC Sport cricket, what cricket fans are talking about, plus wheelchair / para cricket news (India wheelchair team, DCCI, IWPL).
- **morning**: the biggest result, record or moment from the last ~24 hours (overnight + yesterday).
- **evening**: what happened TODAY (IST) — a result, big performance, team selection / injury / record story, or a big match tonight/tomorrow. Don't reuse yesterday's results.
- Prioritise India (men and women) and big international games. Prefer real wheelchair-cricket news when there is some.
- Verify every number (scores, overs, records, names) against at least one reliable source. Never invent stats. If unsure of a detail, leave it out.
- Never mention the name "Pradeep Raj".

## 3. Write three texts
a) **X tweet (English)**: ≤ 250 characters as X counts them (Unicode-bold letters and emoji count as 2). Hook in Unicode bold sans letters (e.g. 𝗛𝗜𝗦𝗧𝗢𝗥𝗜𝗖!), 2–3 short lines of key facts, a punchy closer, 2 evergreen hashtags (#Cricket #TeamIndia #WomensCricket #WheelchairCricket, or a simple match tag like #INDvNZ). Original wording. **No links.**
b) **Facebook caption (Hinglish, Roman script)**: first line = hook in Unicode bold sans letters, then 3–6 short lines with 👉 bullets, a fan question ("… Comment karo 👇"), hashtags #CricketKiBaat + 2 relevant. No links.
c) **Facebook first comment (Hinglish, one line)**, e.g. "Aisi hi daily cricket updates ke liye Cricket Ki Baat ko Follow karo 🔔🏏" — vary it.

## 4. Make both cards
Write `/tmp/card.json`:
```json
{"pill":"SERIES · VENUE/MATCH · DD Mon YYYY","tag":"Big win","headline":"SHORT CAPS <em>KEY</em>",
 "accent":"#FF9933","glow":"rgba(255,153,51,.28)",
 "teams":[{"name":"Team A","score":"180/5","overs":"20 ov","color":"#9AA4B2"},
          {"name":"Team B","score":"181/6","overs":"19.5 ov","color":"#FF9933","win":true}],
 "result":"One line result",
 "stats":[{"big":"51* off 26","small":"short explanation"},{"big":"…","small":"…"},{"big":"…","small":"…"}],
 "source":"Data: ESPNcricinfo"}
```
- `tag`: 2 words ("Big win", "Record alert", "Match day", "Upset alert", "History made").
- `headline`: max ~20 characters so it fits on one line.
- accent/glow = the winning or featured team's colour. Exactly 3 stats. If it isn't a finished match, the two rows can be key facts (name = label, score = value).

Render: `python3 cards/render.py /tmp/card.json queue/DATE-SLOT`
→ creates `queue/DATE-SLOT.png` (X) and `queue/DATE-SLOT-fb.jpg` (Facebook).
Open BOTH images with the Read tool and check nothing overlaps or is cut off. Fix the JSON and re-render if needed.

## 5. Queue it
Write `queue/DATE-SLOT.json` (UTF-8, keep the bold letters and emoji as-is):
```json
{"text":"<tweet>","image":"DATE-SLOT.png","created_at":"<now, UTC ISO-8601 with +00:00>",
 "platforms":["x","facebook"],
 "facebook":{"caption":"<caption>","first_comment":"<first comment>","image":"DATE-SLOT-fb.jpg"},
 "instagram":{"first_comment":"<different Hinglish one-liner that mentions @realcricketkibaat>"},
 "sources":["<url>","<url>"]}
```
## 6. Reel (ONLY when SLOT = evening) — REQUIRED every evening
The reel is not optional: budget your research so you always reach this step. Keep research to what the post needs.

Also make ONE short animated Reel for the Facebook Page (not for X). Same brand design and same music as everything else.
- Pick the most exciting fact/moment of the day (can be the same story as the post but a different angle, e.g. a stat reveal). Never invent facts.
- Write `/tmp/reel.json`: `{"brand":"ckb","theme":"saffron","music":"uplift","kicker":"Record alert","headline":"ERASMUS <em>156*</em> OFF 125","sub":"Namibia 321/6, Ireland all out 290","source":"Data: ESPNcricinfo"}` — headline max ~40 characters (caps, key number in `<em>`), sub max ~60 characters, `source` optional.
- Render: `python3 money/reel.py /tmp/reel.json queue/DATE-SLOT-reel.mp4` (about 40 seconds). Optionally view a frame with `ffmpeg -ss 5 -i queue/DATE-SLOT-reel.mp4 -frames:v 1 /tmp/f.png` and Read it.
- Write `queue/DATE-SLOT-reel.json`:
```json
{"text":"","created_at":"<now, UTC ISO-8601 with +00:00, 1 minute AFTER the main post's created_at>",
 "platforms":["facebook"],
 "facebook":{"caption":"<Hinglish caption, bold Unicode hook, 👉 bullets, fan question, #CricketKiBaat>","first_comment":"<Hinglish one-liner>","video":"DATE-SLOT-reel.mp4"},
 "instagram":{"first_comment":"<different Hinglish one-liner that mentions @realcricketkibaat>"},
 "sources":["<url>"]}
```
The same card/reel and caption are also published to Instagram (@realcricketkibaat) automatically. Do NOT run poster.py, git, or post anything yourself — the workflow does that after you finish.
