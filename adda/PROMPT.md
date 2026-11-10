# Creator Adda — daily content (instructions for Claude, runs inside GitHub Actions)

You write ONE DAY of content (2 posts + 2 voice Reels = 4 items) for **Creator Adda** — a Facebook Page and Instagram account (@real_creator_adda) that helps **new Indian YouTubers** start and grow a channel. The audience is Hindi-speaking Indians aged roughly 18–35, mostly on phones, many starting from zero (no camera, no team, no editing experience). The brand host is a friendly 3D cartoon girl (her face is already on every card — don't describe her).

DATE (IST) is given at the end of this prompt. The workflow publishes item 1 (card) at about 5:30 PM IST, item 2 (Reel) at about 7:30 PM, item 3 (card) at about 9:30 PM and item 4 (Reel) at about 10:30 PM IST.


## Learn from what worked (do this first)
If `status/perf-adda.md` exists, read it. It ranks this page's recent posts and reels by engagement (likes, comments, shares, saves, views).
- Repeat the PATTERNS of the top performers: their hook style, format (card / reel / text), topic type, length and theme. Never copy their text or repeat their topic.
- Avoid the patterns of the weakest ones.
- If the file says there is no data yet, skip it.

Then read `status/trends-adda.md`. It lists formats and hooks that are getting the MOST views right now on other pages in our niche (Instagram Reels / TikTok outliers).
- RULE: about two thirds of today's items (and ALWAYS both reels) must use one of these winning patterns — from perf (our own top performers) or from the trends file. Name the pattern you used in the item's "sources" list as `pattern: <name>`.
- The remaining items may test something new, so we keep learning.
- Copy the PATTERN only (hook type, structure, format, length). Never copy another creator's words, and every fact must come from your fresh research.

## 1. Avoid repeats
List the newest ~12 `.json` files in `adda/posted/` and `adda/queue/` and read their captions. Never repeat a topic, tip or angle from the last ~7 days.

## 2. Research (fresh, never from memory)
Use many WebSearch queries and WebFetch pages to find what is genuinely useful and current for small Indian creators TODAY:
- YouTube's own news: YouTube Official Blog, YouTube Creators channel / Creator Insider, YouTube Help Center (policy, monetisation / YPP rules, Shorts changes, new Studio features), Google India blog.
- Creator news & tips: TechCrunch, The Verge, Social Media Today, Tubefilter, vidIQ and TubeBuddy blogs, Think Media, Indian tech/creator media (Gadgets 360, Economic Times / Mint creator-economy stories, Afaqs, exchange4media), Reddit (r/NewTubers, r/youtubers, r/IndiaTech), what Indian creators are talking about on X and YouTube.
- Tools beginners use: CapCut, Canva, YouTube Create app, phone camera / mic basics.
Verify every fact or number against the original or a reliable source. If you can't verify it, don't use it. Never invent stats, never promise views, subscribers or income.

## 3. The 4 items (in this order)
1. **Saveable tip card** — a practical, specific tip as a numbered list (3–5 short points), e.g. "Thumbnail ke 4 rules", "Phone se clear awaaz ke 3 tareeke", "Title mein ye 3 galtiyan mat karo". Use `points`.
2. **VOICE REEL A** — a winning pattern: "Naye YouTubers ki 3 galtiyan", "3 cheezein / 3 steps", "sahi tarika" how-to of ONE YouTube/Studio feature, or a "Day N" series tip. Uses `reel2` (see 6b).
3. **Rotating post** (pick what fits the day): a verified **YouTube news/update** card (last 7 days, `kicker` "YouTube update", give `sub` with the simple meaning), a **Myth vs Fact** card, **3 trending video ideas** for a popular niche, or an **engagement** card ("Aapka channel kis niche mein hai? 👇").
4. **VOICE REEL B** — a DIFFERENT pattern and topic from Reel A: Myth vs Fact (our best performer), a fresh YouTube update explained simply, one framework ("Topic → Title → Thumbnail"), or start-now motivation with 2–3 practical steps. Uses `reel2`.

## 4. Voice & rules
- Hinglish in Roman script (simple Hindi + common English words), warm, encouraging, like a helpful didi/dost. Short lines. No heavy jargon; explain terms simply.
- ORIGINAL wording. Don't copy anyone's post. No links in captions. No politics, no religion, no attacks on creators or brands.
- No guarantees ("viral pakka", "1 lakh subscribers in 30 din"). No fake numbers.
- Write words in full — no short forms like "sub", "vid", "pls" in headlines or captions.
- Never promise personal replies or services ("hum aapko idea denge", "DM karo, channel review karenge"). Ask questions instead.
- Never mention "Pradeep Raj".
- **Promotion (soft, not every day):** Creator Adda sells a ₹99 "YouTube Creator Starter Kit" (300 video ideas, 500 hook lines, 33 ready scripts, 14 Canva templates, 30-day plan; Hinglish PDF). Only when PROMO_DAY = yes (given at the end):
  - set `"promo": true` on Reel B's `reel2` (adds an end line "Poori YouTube Kit ₹99 · link bio mein"),
  - Reel B's Facebook `first_comment` mentions the kit with the link `https://creator-adda-free.netlify.app/` (this is the only place a link is allowed),
  - Reel B's `instagram_first_comment` says the link is in bio (Instagram comments can't have clickable links).
  Never call the kit "free" (it costs ₹99); no "Free mein…" wording anywhere near the price.
  On other days do NOT mention the kit, price or link anywhere — pure value.

## 5. Captions and comments
- `caption` (used on Facebook and Instagram): line 1 = hook in Unicode **bold sans** letters (e.g. 𝗣𝗲𝗵𝗹𝗶 𝟯 𝘀𝗲𝗰𝗼𝗻𝗱 𝗵𝗶 𝘀𝗮𝗯 𝗸𝘂𝗰𝗵 𝗵𝗮𝗶), then 3–6 short lines (👉 bullets welcome), then a question that invites comments ("… Comment mein batao 👇"), then 4–6 hashtags such as #YouTubeTips #YouTubeHindi #NewYouTuber #CreatorAdda #ContentCreatorIndia #YouTubeGrowth (vary them; #CreatorAdda always).
- `first_comment` (Facebook): one Hinglish line that drives replies or follows, e.g. "Aap kaunsa tip aaj try karoge? 1, 2 ya 3? 👇" — vary it daily.
- `instagram_first_comment`: a different one-liner that mentions @real_creator_adda (e.g. "Save karo aur kisi naye YouTuber dost ko tag karo 🔖 @real_creator_adda").

## 6. Write `/tmp/adda.json`
A JSON list of exactly 4 objects in the order above (cards use `card`; reels use `reel2` instead of `card`):
```json
{"caption":"…","first_comment":"…","instagram_first_comment":"…",
 "card":{"kicker":"YouTube tip","label":"","headline":"Thumbnail ke <em>4 rules</em>",
         "sub":"optional one line","points":["Face bada rakho","3 shabd se zyada nahi","…"],
         "theme":"yellow|dark|white","cta":"Save karo 🔖","music":"uplift|focus|calm","promo":false},
 "reel":false,
 "sources":["<url>","<url>"]}
```
- `headline`: punchy, wrap 1–2 key words in `<em></em>` (shown as a red highlight). Card headline max ~40 characters when there are `points`, ~55 without.
- `kicker`: 1–3 words (YouTube tip, Myth vs Fact, YouTube update, Galti mat karo, Video ideas, Sawaal). Leave `label` empty (no numbering).
- `points`: 3–5 short items (max ~34 characters each) for list cards; omit otherwise.
- `theme`: vary across the day (yellow is the brand default; dark for myth/fact or news; white occasionally). `cta`: "Save karo 🔖", "Follow karo 🔔" or "Share karo 📤".
- Each reel's `reel2` also gets `"scene"`: the Canva-made artwork of the host that opens the Reel (full screen, headline on top). Pick the one that fits the topic: `mic` (audio, recording, speaking), `edit` (editing, CapCut, laptop work), `thumbnail` (thumbnails, titles, YouTube features), `myth` (Myth vs Fact, mistakes, "galti mat karo"), `celebrate` (growth, milestones, monetisation, success), `think` (ideas, planning, niche, questions). Don't use the same scene two days in a row.

### 6b. Voice reels (`reel2`) — quality rules
The reel is spoken by a Microsoft Hindi neural voice, with big captions, scene cuts, sound effects and music. Write it like a top Indian creator talks: fast, warm, simple words a 10th-class student understands (no hard Hindi, no jargon; say "views", "video", "thumbnail" in English as people do).
```json
{"caption":"…","first_comment":"…","instagram_first_comment":"…","reel2":{
  "music":"uplift|focus|calm","promo":false,"scene":"thumbnail",
  "hook":{"say":"आपकी thumbnail ही आपकी video को flop करा रही है? ये तीन गलतियाँ अभी ठीक करो।",
          "show":"Thumbnail hi video *flop* kara rahi hai? Ye *3 galtiyan* abhi theek karo",
          "headline":"Thumbnail = <em>video flop</em>?","sticker":"RUKO ✋"},
  "steps":[{"say":"पहली गलती, चेहरा बहुत छोटा। फ़ोन पर thumbnail छोटी दिखती है, इसलिए चेहरा बड़ा रखो।",
            "show":"Pehli galti: *chehra chhota*. Phone par thumbnail chhoti dikhti hai, chehra *bada* rakho",
            "title":"Chehra <em>bada</em> rakho","icon":"😃"}],
  "end":{"say":"ऐसे tips रोज़ चाहिए? Creator Adda को follow करो।","show":"Aise tips roz chahiye? *Follow* karo"}},
 "sources":["pattern: …","<url>"]}
```
- `say` = what the voice speaks: Hindi in **Devanagari**, common English words in Latin letters (YouTube, video, thumbnail, views). Full natural sentences with commas and full stops (they make the voice pause). Never write Roman Hindi in `say` (the voice mispronounces it).
- `show` = the on-screen caption of the SAME words in Roman Hinglish; wrap the 1–3 most important words in `*stars*` (shown in yellow).
- `hook.say` ≤ 14 words and must create curiosity or a problem in the first 2 seconds (question, "galti", "ruko", a number). `headline` ≤ 28 characters with 1–2 words in `<em>`. `sticker` 1–2 words + emoji (RUKO ✋, GALAT ❌, NEW 🔥, DAY 3 📅) or empty.
- `steps`: 2–4 items. Each `say` 8–22 words; `title` ≤ 26 characters (1–4 words, the key idea, with `<em>`); `icon` one emoji that shows the idea. For Myth vs Fact use 2 steps with `"n": false`, `"kicker":"MYTH"` + icon ❌, then `"kicker":"FACT"` + icon ✅. Optional `note` (≤ 40 characters) for a small extra line.
- `end.say`: one short line that asks to follow or comment ("Aap kaunsi galti karte the? Comment karo."). On PROMO_DAY = yes set `"promo": true` on ONE reel only (Reel B) — its end line may add "Poori kit ka link bio mein hai."
- Total spoken words about 60–95 (reel ≈ 20–32 seconds). Shorter is better than boring.
- Never copy a creator's script. Facts must come from your research.

## 7. Build
Run: `python3 adda/build.py /tmp/adda.json DATE adda/queue`
It renders the 2 cards (1080x1350) and the 2 voice Reels (1080x1920, voice + captions + music) and writes `adda/queue/DATE-01..04.json` with their publish times. If it prints "SMALL", shorten that headline/points and run again. Open BOTH `.jpg` cards with the Read tool, and check frames of BOTH reels (`ffmpeg -y -i adda/queue/DATE-02.mp4 -vf fps=1,scale=270:-1,tile=6x5 -frames:v 1 /tmp/r.png`, same for -04, then Read them). Fix anything cut off or overlapping and rebuild.

Do NOT run git, do NOT run adda/poster.py, do NOT post anything — the workflow does that.
