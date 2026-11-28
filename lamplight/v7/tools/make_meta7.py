import json, collections
B = '/home/claude/lamp7'
tl = json.load(open(f'{B}/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = [open(f'{B}/script/ch{n:02d}.txt').readline().split(':', 1)[1].strip() for n in range(1, 13)]
def ts(s):
    s = int(s); h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
lines = []; t = tl['lead']
for n in range(1, 13):
    lines.append(f"{'0:00' if n == 1 else ts(t)} {names[n-1]}"); t += durs[n]
src = json.load(open(f'{B}/img/sources.json')); used = set(f for v in json.load(open(f'{B}/ch_imgs.json')).values() for f in v)
BAD=('Rijksmuseum','Internet Archive','Matson','Marie-Lan','Unknown','unknown','Coyau','Descouens','NYPL','anonymous','Anonymous','Google','Museum','Library','Byzantine Institute','After ')
arts = collections.Counter(i['artist'].strip().split(chr(10))[0].strip() for i in src if i['file'] in used and i['artist'].strip() and not any(b in i['artist'] for b in BAD) and len(i['artist'])<60)
artists = ', '.join(a for a, _ in arts.most_common(14))
length = ts(tl['total'])
title = "The First Christmas: The Nativity Story from Luke and Matthew | Bible Stories for Sleep"
desc = f"""Settle in, dim the lights, and listen to the oldest Christmas story there is, the first telling of it in the gospels of Luke and Matthew. An old priest named Zacharias and an angel in the temple. A young woman in Nazareth who said, let it be done. Mary and Elizabeth in the hill country, and the songs they sang. Joseph and his dream. The long road to Bethlehem, a baby wrapped in strips of cloth and laid in a feeding trough, shepherds keeping watch by night, and a sky full of singing. Simeon and Anna in the temple courts, wise men from the east, the flight into Egypt, and the boy Jesus in his Father's house. A calm, slow-paced retelling for sleep, with Luke 1 and 2 and Matthew 1 and 2 read almost in full from scripture itself.

🌙 Best with a low volume and the screen dimmed. You can let it play through the night.

CHAPTERS
""" + "\n".join(lines) + f"""

ABOUT THIS VIDEO
The narration is AI-generated (an open-source text-to-speech voice) and is disclosed as altered or synthetic content. The retelling was written for this channel and checked against the text of Luke and Matthew. Background notes (the priestly divisions, the census under Augustus and the old question of how Luke's Quirinius fits with Josephus, Bethlehem and Nazareth, the manger and the Greek word kataluma, the purification offering in Leviticus 12, the magi and the star, Herod and Archelaus) follow standard reference sources, and open questions are mentioned honestly. Things the gospels do not say (the donkey, the innkeeper, the number of wise men, the date of the birth) are named as later tradition. Nothing is invented and no sermon is added. The journey maps show one likely route; the gospels do not record the roads taken. The hard passage in Matthew 2:16-18 is summarized gently rather than read.

SCRIPTURE
Scripture quotations are from the World English Bible (public domain), lightly adapted for reading aloud: the divine name is rendered as "the Lord". Passages read: Luke 1:1-80; Luke 2:1-52; Matthew 1:1, 18-25; Matthew 2:1-14, 19-23; Micah 5:2.

IMAGES
Public-domain artworks, engravings and early photographs from Wikimedia Commons and museum collections, including works by {artists}. Full list of file pages on request in the comments.

This video is for rest and reflection. It is not medical advice. If you have trouble sleeping regularly, please talk to a doctor.

Subscribe to Lamplight Scripture for calm Bible stories for sleep.

#BibleStoriesForSleep #Christmas #Nativity #SleepStory #ScriptureForSleep"""
desc = desc.replace('<', '').replace('>', '')
tags = "bible stories for sleep, christmas story, nativity story, the first christmas, christmas bible story, gospel of luke, luke 2, birth of jesus, mary and joseph, shepherds and angels, wise men, christmas sleep story, fall asleep to the bible, bible sleep stories, christian sleep stories, scripture for sleep, bedtime bible stories for adults, calm bible reading, lamplight scripture, advent"
comment = "Welcome, and goodnight. 🌙 Don't be afraid: the angel says it to Zacharias, to Mary, to Joseph and to the shepherds. Where in the world are you listening from tonight? And which Bible story should Lamplight Scripture tell next?"
txt = f"""TITLE
{title}

DESCRIPTION
{desc}

TAGS (comma separated)
{tags}

FIRST COMMENT (posted automatically 60 minutes after it goes public via ytq/comments.json; pin it by hand)
{comment}

PLAYLIST
Bible Stories for Sleep

THUMBNAILS
thumbnail.jpg (A: The First Christmas) and thumbnail_b.jpg (B: Silent Night) for Test & compare

UPLOAD CHECKLIST (YouTube Studio)
1. Upload video.mp4 (join the parts on branch backup-lamplight-nativity), set the thumbnail to thumbnail.jpg (add thumbnail_b.jpg in Test & compare if available).
2. Visibility: schedule for Wed 9 Dec 2026 05:30 IST (= Tue 8 Dec 2026 7:00 pm New York = 2026-12-09T00:00:00Z).
3. Audience: No, it's not made for kids.
4. Altered content: Yes (AI-generated voice).
5. Category: Education. Language: English.
6. Playlist: Bible Stories for Sleep.
7. First comment posts automatically; pin it.

SLOT
lamplight 2026-12-09 05:30 IST (2026-12-09T00:00:00Z)

Length: {length}
"""
assert len(title) <= 100 and len(desc) < 5000, (len(title), len(desc))
open(f'{B}/metadata.txt', 'w').write(txt)
json.dump(dict(title=title, comment=comment, length=length), open(f'{B}/meta_out.json','w'))
print(len(title), len(desc), artists); print("\n".join(lines))
