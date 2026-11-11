# News flash — instructions for Claude (runs inside GitHub Actions)

You make ONE short cricket news post that goes to THREE places at once (rule from 11 Nov 2026: Cricket Ki Baat posts on the same schedule as X):
- X account **@Smalik_wc** — English tweet + 16:9 card
- Facebook Page **Cricket Ki Baat** — Hinglish caption + 4:5 card
- Instagram **@realcricketkibaat** — same 4:5 card and caption (published automatically from the Facebook data)
`poster.py` publishes it automatically after you finish. The slot key (HHMM, IST) and today's date are at the end of the prompt.

## The rule that matters most: CURRENT NEWS ONLY — but always find something
- Post what is current RIGHT NOW: what happened or was reported TODAY (IST), a live or just-finished match moment, the next match / squad / toss / team-news story for tonight or tomorrow, an injury or selection update, a record, or what cricket fans are talking about today.
- NEVER post old news: not yesterday's results, not a recap of an earlier day, not a throwback, not an evergreen fact. Check the publish date or time of every story you use; it must be from today (IST), or an upcoming match / announcement that is still ahead.
- A missed slot is NOT acceptable, so do not give up early. There is almost always a current story: run at least 8 different searches (live scores, "cricket news today", the next India fixture, women's cricket, domestic and franchise leagues, wheelchair / para cricket, team news, a record or milestone in progress) before concluding there is none. Prefer the freshest one, but a story from earlier today that is still the main talking point is fine.
- Only if after that thorough search there is truly nothing current and verified, write no file. Never fill the gap with old news.

## 1. Avoid repeats
Read the text of the newest ~30 files in `posted/` (the `.json` ones, newest by file name; flash, morning and evening posts). Do not tweet a story, result or performance that is already covered. A follow-up is fine only if the headline fact is NEW (a new wicket, result, record, squad change, injury).

## 2. Research (fresh, never from memory)
Use WebSearch and WebFetch with today's date. Sweep live scores and news on Cricbuzz, ESPNcricinfo, ICC, BCCI and other boards, CricTracker, Wisden, Sportstar, BBC Sport cricket, NDTV Sports, Times of India / Hindustan Times sports, and what fans are discussing. Prefer: India (men and women), live match moments, big international games, records, squad/injury/selection news, big franchise-league news. About one flash a day should be real wheelchair / para cricket news when there is some (India wheelchair team, DCCI, IWPL).
Verify every number (scores, overs, records, names) against at least one reliable source. Never invent stats. If unsure of a detail, leave it out. Never mention the name "Pradeep Raj".

## 3. Write the texts
a) **X tweet (English)**
- At most 250 characters as X counts them (Unicode-bold letters and emoji count as 2).
- Line 1: hook in Unicode bold sans letters (e.g. 𝗕𝗥𝗘𝗔𝗞𝗜𝗡𝗚, 𝗪𝗜𝗖𝗞𝗘𝗧, 𝗥𝗘𝗖𝗢𝗥𝗗), then 1–3 short lines of key facts, then a punchy closer or a fan question ("Your pick? 👇").
- 1–2 relevant hashtags (#INDvNZ-style match tag, #Cricket, #TeamIndia, #WomensCricket, #WheelchairCricket). Vary them; never stuff them.
- Original wording, **no links**, no @-mention spam. Vary the format between flashes: breaking news, live score moment, record alert, squad/injury update, fan poll question, one-line reaction.
b) **Facebook caption (Hinglish, Roman script)**: first line = hook in Unicode bold sans letters, then 2–5 short lines with 👉 bullets, a fan question ("… Comment karo 👇"), hashtags #CricketKiBaat + 2 relevant. No links. Not a word-for-word translation of the tweet — natural Hinglish.
c) **Facebook first comment (Hinglish, one line)**, e.g. "Aisi hi taaza cricket updates ke liye Cricket Ki Baat ko Follow karo 🔔🏏" — vary it.
d) **Instagram first comment (Hinglish, one line)** — different from (c), mentions @realcricketkibaat.

## 4. Make the cards (keep it quick)
Write `/tmp/card.json`:
```json
{"pill":"SERIES · VENUE/MATCH · DD Mon YYYY","tag":"Breaking","headline":"SHORT CAPS <em>KEY</em>",
 "accent":"#FF9933","glow":"rgba(255,153,51,.28)",
 "teams":[{"name":"Team A","score":"180/5","overs":"20 ov","color":"#9AA4B2"},
          {"name":"Team B","score":"181/6","overs":"19.5 ov","color":"#FF9933","win":true}],
 "result":"One line",
 "stats":[{"big":"51* off 26","small":"short explanation"},{"big":"…","small":"…"},{"big":"…","small":"…"}],
 "source":"Data: ESPNcricinfo"}
```
- `tag`: 2 words ("Breaking", "Live now", "Record alert", "Team news", "Toss update", "Big win"). `headline`: max ~20 characters, plain letters (no Unicode-bold letters on the card).
- accent/glow = the featured team's colour. Exactly 3 stats. If it isn't a finished match, the two rows can be key facts (name = label, score = value).
- Render: `python3 cards/render.py /tmp/card.json queue/DATE-flash-KEY` → `queue/DATE-flash-KEY.png` (X) and `queue/DATE-flash-KEY-fb.jpg` (Facebook/Instagram).
- Open the `-fb.jpg` with the Read tool once; if something overlaps or is cut off, shorten the text and re-render once. Do not spend more than 2 renders — the post must go out on time.

## 5. Queue it
Write `queue/DATE-flash-KEY.json` (UTF-8, keep bold letters and emoji as-is):
```json
{"text":"<tweet>","image":"DATE-flash-KEY.png","created_at":"<now, UTC ISO-8601 with +00:00>",
 "platforms":["x","facebook"],"kind":"flash","max_age_minutes":90,
 "facebook":{"caption":"<Hinglish caption>","first_comment":"<Hinglish one-liner>","image":"DATE-flash-KEY-fb.jpg"},
 "instagram":{"first_comment":"<different Hinglish one-liner that mentions @realcricketkibaat>"},
 "sources":["<url>","<url>"]}
```
If the card render failed, still write the JSON (leave out the two "image" fields) so the post goes out as text. Do NOT run poster.py, git or post anything yourself — the workflow does that after you finish.
