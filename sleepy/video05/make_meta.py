import json
tl = json.load(open('/home/claude/marcus/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = ["Welcome, and a Boy on the Caelian Hill", "A Rough Cloak and a Plank Bed", "A Sudden Heir", "Letters to Fronto",
         "Faustina, and a House Full of Children", "The Quiet Years of Antoninus", "Two Emperors, and a War in the East",
         "A Sickness from the East", "Winters by the Danube", "A Rumour from Syria", "Athens, and a Gift to Philosophy",
         "The Setting Sun, and Goodnight"]
def ts(s):
    s = int(s); h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
lines = []; t = tl['lead']
for n in range(1, 13):
    lines.append(f"{'0:00' if n == 1 else ts(t)} {n}. {names[n-1]}"); t += durs[n]
mins = round(tl['total'] / 60)
title = "Marcus Aurelius: The Emperor Who Wrote to Himself | Biography for Sleep"
desc = f"""Fall asleep to the true story of Marcus Aurelius, the Roman emperor who wrote the Meditations. In this calm, slow biography we follow him from a quiet childhood on the Caelian Hill in Rome in 121 AD, through his teachers, his letters to Fronto, his marriage to Faustina and the peaceful years beside Antoninus Pius, to two decades on the throne: floods, plague, the long winters by the Danube where he wrote his private notebook by lamplight, the burned letters of a rebel, Athens, and his last days in 180 AD. About {mins} minutes of gentle narration over a quiet fireside sound.

🌙 CHAPTERS
""" + "\n".join(lines) + """

📚 SOURCES
- Marcus Aurelius, Meditations, translated by George Long (1862, public domain; text from Standard Ebooks)
- Letters of Marcus Aurelius and Fronto (letter on a day at the grape harvest, Ad M. Caes. 4.6; romanletters.org)
- Cassius Dio, Roman History, books 71-72 (Avidius Cassius, the burned letters, Athens, "a kingdom of gold")
- Historia Augusta, Life of Marcus Aurelius and Life of Antoninus Pius (a later and less reliable source; stories from it are marked as later accounts in the narration)
- Encyclopaedia Britannica: Marcus Aurelius; Antoninus Pius; Stanford Encyclopedia of Philosophy: Marcus Aurelius
- Livius.org: Marcus Aurelius
Short lines from the Meditations are quoted in George Long's public-domain translation. Where a story comes only from a later account (for example the plank bed at twelve, the nickname Verissimus, Antoninus's last word, the palace auction, the last words to the officer), the narration says so.

🎙 Narration: AI-generated voice (Kokoro, open source). Research, script writing, fact-checking and production: The Sleepy Biographer. This video is labelled as altered/synthetic content.
🖼 Images: public-domain and CC0 photographs, paintings and prints from Wikimedia Commons (including the Capitoline equestrian statue, works from the Rijksmuseum, the J. Paul Getty Museum and the British Library, and Eugène Delacroix's The Last Words of Marcus Aurelius). Fireside sound: synthesized by us.

This is a calm history story for rest and sleep. It is not medical, legal or financial advice.

New biography every Tuesday and Friday. Subscribe for more calm history for sleep.

#HistoryForSleep #BiographyForSleep #MarcusAurelius"""
tags = "marcus aurelius, marcus aurelius biography, meditations marcus aurelius, stoicism, stoic philosophy, roman emperor, ancient rome for sleep, history for sleep, biography for sleep, fall asleep to history, sleep story for adults, bedtime history, calm biography, history documentary, relaxing history, ancient history for sleep, boring history for sleep, sleepy history"
comment = "Welcome, and goodnight. 🌙 Marcus Aurelius wrote his notebook for no one but himself. If you keep a journal, or have one line from the Meditations that stays with you, share it below. And who should The Sleepy Biographer tell next?"
txt = f"""TITLE
{title}

DESCRIPTION
{desc}

TAGS (comma separated)
{tags}

FIRST COMMENT (post from the channel 60 minutes after it goes public; pin it by hand in Studio)
{comment}

PLAYLIST
Ancient Lives for Sleep

UPLOAD CHECKLIST
- Visibility: Schedule, Sat 28 Nov 2026 05:30 IST (= Fri 27 Nov 2026 7:00 PM New York = 2026-11-28T00:00:00Z)
- Altered or synthetic content: Yes
- Made for kids: No
- Category: Education; Language: English
- Thumbnail: thumbnail.jpg
- Playlist: Ancient Lives for Sleep
- Chapters: on (first at 0:00)
- End screen: Subscribe + best video
- First comment: queued in ytq/comments.json (posts 60 min after public); pin it by hand

SLOT
sleepy 2026-11-28 05:30 IST (2026-11-28T00:00:00Z)

FILES
Video backup: branch backup-sleepy-marcus (90 MB parts; join with: cat sleepy_v05_marcus.mp4.part* > video.mp4)
Duration: {ts(tl['total'])}
"""
open('/home/claude/marcus/metadata.txt', 'w').write(txt)
json.dump({'title': title, 'comment': comment}, open('/home/claude/marcus/meta_short.json', 'w'))
print(len(desc), 'chars desc;', ts(tl['total']))
