import json
tl = json.load(open('/home/claude/victoria/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = ["Welcome, and a Baby at Kensington", "The Kensington Years", "The Morning She Became Queen", "A Crown in the Abbey",
         "Albert", "A Growing Family, and a House by the Sea", "The Highlands and the Crystal Palace", "War, Medals, and the Wider World",
         "The Winter of 1861", "The Widow of Windsor", "Two Jubilees, and the Grandmother of Europe", "A Winter Afternoon at Osborne, and Goodnight"]
def ts(s):
    s = int(s); h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
lines = []
t = tl['lead']
for n in range(1, 13):
    lines.append(f"{ts(t if n > 1 else t)} {n}. {names[n-1]}"); t += durs[n]
lines[0] = '0:00' + lines[0][lines[0].index(' '):]
title = "Queen Victoria: A Long Reign, a Quiet Heart | Biography for Sleep"
desc = f"""Fall asleep to the true story of Queen Victoria, who reigned for more than sixty-three years. In this calm, slow biography we follow her from a quiet nursery at Kensington Palace in 1819, through the morning she became Queen at eighteen, her marriage to Prince Albert, the seaside house at Osborne and the hills of Balmoral, to her long widowhood, her two Jubilees, and a winter evening at Osborne in 1901. About {round(tl['total']/60)} minutes of gentle narration over a quiet fireside sound.

🌙 CHAPTERS
""" + "\n".join(lines) + """

📚 SOURCES
- Queen Victoria's journals and letters (public-domain editions: The Letters of Queen Victoria, ed. Benson and Esher, 1907; The Girlhood of Queen Victoria, ed. Esher, 1912)
- The Royal Family / Royal Collection Trust: Timeline of Queen Victoria and Prince Albert (royal.uk)
- Encyclopaedia Britannica: Victoria, queen of the United Kingdom
- Lytton Strachey, Queen Victoria (1921, public domain)
- English Heritage: Osborne; Royal Collection Trust: Balmoral and the Great Exhibition
Short lines from Victoria's own journal are quoted or closely paraphrased from her public-domain writings. Where a story comes only from a later memory (for example "I will be good"), the narration says so.

🎙 Narration: AI-generated voice (Kokoro, open source). Research, script writing, fact-checking and production: The Sleepy Biographer. This video is labelled as altered/synthetic content.
🖼 Images: public-domain paintings, prints and photographs from Wikimedia Commons (including works from the Royal Collection, The Met Open Access, the British Museum and the Library of Congress). Fireside sound: synthesized by us.

This is a calm history story for rest and sleep. It is not medical advice.

New biography every Tuesday and Friday. Subscribe for more calm history for sleep.

#HistoryForSleep #BiographyForSleep #QueenVictoria"""
tags = "queen victoria, queen victoria biography, history for sleep, biography for sleep, fall asleep to history, sleep story for adults, bedtime history, calm biography, history documentary, relaxing history, victorian era, prince albert, british royal history, kings and queens for sleep, boring history for sleep, sleepy history, osborne house, balmoral"
comment = "Welcome, and goodnight. 🌙 If you are listening tonight, tell us where you are in the world and what time it is there. And who should The Sleepy Biographer put to bed next? Leave a name below."
txt = f"""TITLE
{title}

DESCRIPTION
{desc}

TAGS (comma separated)
{tags}

FIRST COMMENT (post from the channel 60 minutes after it goes public; pin it by hand in Studio)
{comment}

PLAYLIST
Kings & Queens for Sleep

UPLOAD CHECKLIST
- Visibility: Schedule, Wed 21 Nov? NO -> Sat 21 Nov 2026 05:30 IST (= Fri 20 Nov 2026 7:00 PM New York = 2026-11-21T00:00:00Z)
- Altered or synthetic content: Yes
- Made for kids: No
- Category: Education; Language: English
- Thumbnail: thumbnail.jpg
- Playlist: Kings & Queens for Sleep
- Chapters: on (first at 0:00)
- End screen: Subscribe + best video
- First comment: queued in ytq/comments.json (posts 60 min after public); pin it by hand

SLOT
sleepy 2026-11-21 05:30 IST (2026-11-21T00:00:00Z)

FILES
Video backup: branch backup-sleepy-victoria (90 MB parts; join with: cat sleepy_v03_victoria.mp4.part* > video.mp4)
"""
txt = txt.replace("Schedule, Wed 21 Nov? NO -> Sat 21 Nov 2026", "Schedule, Sat 21 Nov 2026")
assert len(title) <= 100 and '<' not in desc and '>' not in desc and len(desc) < 5000, (len(desc))
open('/home/claude/victoria/metadata.txt', 'w').write(txt)
print(len(desc)); print("\n".join(lines))
