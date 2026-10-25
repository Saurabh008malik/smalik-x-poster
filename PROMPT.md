# Daily cricket post — instructions for Claude (runs inside GitHub Actions)

You are preparing ONE cricket post for Saurabh Malik. It is published automatically by `poster.py` after you finish:
- X account **@Smalik_wc** — English tweet + 16:9 card
- Facebook Page **Cricket Ki Baat** — Hinglish caption + 4:5 card

The slot (`morning` or `evening`) and today's date (IST) are given at the end of this prompt.

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
 "sources":["<url>","<url>"]}
```
Do NOT run poster.py, git, or post anything yourself — the workflow does that after you finish.
