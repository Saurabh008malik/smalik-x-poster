import json
tl = json.load(open('/home/claude/dickens/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = [open(f'/home/claude/dickens/script/ch{n:02d}.txt').readline().split(':',1)[1].strip() for n in range(1,13)]
def ts(s):
    s = int(s); h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
lines = []; t = tl['lead']
for n in range(1, 13):
    lines.append(f"{'0:00' if n == 1 else ts(t)} {n}. {names[n-1]}"); t += durs[n]
mins = round(tl['total'] / 60); dur = ts(tl['total'])
title = "Charles Dickens and the Story of A Christmas Carol | Biography for Sleep"
desc = f"""Fall asleep to the true story of Charles Dickens, the boy from the blacking warehouse who grew up to write Oliver Twist, David Copperfield, Great Expectations and, in one cold autumn, A Christmas Carol. In this calm, slow biography we follow him from a winter birth in Portsmouth in 1812, through golden childhood years by the Medway, a hard year tying up pots of boot blacking while his father sat in the Marshalsea debtors' prison, shorthand and the reporters' gallery, the first sketch dropped into a dark letter-box, the sudden fame of Mr. Pickwick, a stormy crossing to America, and the six weeks of night walks in which he wrote A Christmas Carol. Then the busy middle years, the real shadows of his marriage, the public readings, Gad's Hill, and a summer evening in 1870. About {mins} minutes of gentle narration over a quiet fireside sound.

🌙 CHAPTERS
""" + "\n".join(lines) + """

📚 SOURCES
- John Forster, The Life of Charles Dickens (1872-74; includes Dickens's own autobiographical fragment)
- The Letters of Charles Dickens (ed. by his sister-in-law and eldest daughter, 1880; public domain), incl. letters to Cornelius Felton, Southwood Smith and Angela Burdett-Coutts
- Charles Dickens, A Christmas Carol (1843), Preface to The Pickwick Papers (1847), The Uncommercial Traveller (1860)
- Library of Congress blog: A Tale of Two Publishings (A Christmas Carol, 2015); Penguin: The story of A Christmas Carol; Encyclopaedia Britannica: The Origins of A Christmas Carol
- The National Archives: Charles Dickens, Warren's Blacking and the Chancery Court (Michael Allen); Victorian Web: Dickens and debtors' prisons
- Charles Dickens Museum (48 Doughty Street) and Charles Dickens' Birthplace Museum (Portsmouth) visitor information
Short lines are quoted only from Dickens's own public-domain writing (A Christmas Carol, his prefaces, essays and letters) and from Thackeray's 1844 review. Stories that come from later memory or later accounts (the walks to Gad's Hill with his father, the New York crowds asking about Little Nell, the girl who asked whether Father Christmas would die too) are marked as such in the narration. Dates of the blacking-warehouse year are uncertain, and the narration says so.

🎙 Narration: AI-generated voice (Kokoro, open source). Research, script writing, fact-checking and production: The Sleepy Biographer. This video is labelled as altered/synthetic content.
🖼 Images: public-domain and CC0 portraits, photographs, paintings, prints and book illustrations from Wikimedia Commons (including Daniel Maclise's and W. P. Frith's portraits, John Leech's original 1843 Christmas Carol plates, Phiz, Seymour, Cruikshank and Fred Barnard illustrations, Gustave Doré's London, and views of Rochester, Boston and Niagara). Fireside sound: synthesized by us.

This is a calm history story for rest and sleep. It is not medical, legal or financial advice.

New biography every Tuesday and Friday. Subscribe for more calm history for sleep.

#HistoryForSleep #BiographyForSleep #CharlesDickens"""
tags = "charles dickens, charles dickens biography, a christmas carol, life of charles dickens, victorian era, victorian london, english literature, oliver twist, history for sleep, biography for sleep, fall asleep to history, sleep story for adults, bedtime history, calm biography, history documentary, relaxing history, christmas history for sleep, writers for sleep"
comment = "Welcome, and goodnight. 🌙 Dickens wrote A Christmas Carol in about six weeks, walking the dark streets of London at night with the story in his head. Do you read or watch A Christmas Carol every December? And who should The Sleepy Biographer tell next?"
meta = f"""TITLE
{title}

DESCRIPTION
{desc}

TAGS (comma separated)
{tags}

FIRST COMMENT (post from the channel 60 minutes after it goes public; pin it by hand in Studio)
{comment}

PLAYLIST
Artists & Writers for Sleep

UPLOAD CHECKLIST
- Visibility: Schedule, Sat 5 Dec 2026 05:30 IST (= Fri 4 Dec 2026 7:00 PM New York = 2026-12-05T00:00:00Z)
- Altered or synthetic content: Yes
- Made for kids: No
- Category: Education; Language: English
- Thumbnail: thumbnail.jpg
- Playlist: Artists & Writers for Sleep
- Chapters: on (first at 0:00)
- End screen: Subscribe + best video
- First comment: queued in ytq/comments.json (posts 60 min after public); pin it by hand

SLOT
sleepy 2026-12-05 05:30 IST (2026-12-05T00:00:00Z)

FILES
Video backup: branch backup-sleepy-dickens (90 MB parts; join with: cat sleepy_v07_dickens.mp4.part* > video.mp4)
Duration: {dur}
"""
open('/home/claude/dickens/metadata.txt', 'w').write(meta)
json.dump({'title': title, 'comment': comment, 'duration': dur}, open('/home/claude/dickens/meta_out.json', 'w'))
print(len(desc), 'chars desc;', dur)
