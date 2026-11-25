import json, collections
B = '/home/claude/lamp6'
tl = json.load(open(f'{B}/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = ['Welcome, and a Famine in Bethlehem', 'The Road Back, and Where You Go, I Will Go', 'Gleaning in the Barley Field', 'An Evening Conversation, and a Long Harvest', 'A Night on the Threshing Floor', 'At the Town Gate, and a Child Named Obed', 'A Long Road East, and the Palace at Susa', 'A Young Woman Named Hadassah', 'Haman, and the Casting of the Lot', 'For Such a Time as This', 'The Golden Scepter, and a Night Without Sleep', 'The Queen Speaks, a Day of Rest, and Goodnight']
def ts(s):
    s = int(s); h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
lines = []; t = tl['lead']
for n in range(1, 13):
    lines.append(f"{'0:00' if n == 1 else ts(t)} {names[n-1]}"); t += durs[n]
src = json.load(open(f'{B}/img/sources.json')); used = set(f for v in json.load(open(f'{B}/ch_imgs.json')).values() for f in v)
BAD=('Rijksmuseum','Internet Archive','Matson','Marie-Lan','Unknown','Coyau','Descouens','NYPL','anonymous','Anonymous')
arts = collections.Counter(i['artist'].strip().split(chr(10))[0] for i in src if i['file'] in used and i['artist'].strip() and not any(b in i['artist'] for b in BAD))
artists = ', '.join(a for a, _ in arts.most_common(10))
length = ts(tl['total'])
title = "Ruth and Esther: Two Women of Quiet Courage | Bible Stories for Sleep"
desc = f"""Settle in, dim the lights, and listen to two of the Bible's shortest and gentlest books. First, the story of Ruth: a famine in Bethlehem, a family in Moab, a grieving widow named Naomi, and a young Moabite woman who said, where you go, I will go. Barley fields at harvest time, a kind landowner named Boaz, a quiet night on the threshing floor, and a child named Obed, the grandfather of King David. Then, the story of Esther: the great palace at Susa, an orphan girl who became queen of Persia, her cousin Mordecai, the proud Haman and the casting of the lot, the words for such a time as this, the golden scepter, and a night when the king could not sleep. A calm, slow-paced retelling for sleep, with the whole book of Ruth and much of Esther read from scripture itself.

🌙 Best with a low volume and the screen dimmed. You can let it play through the night.

CHAPTERS
""" + "\n".join(lines) + f"""

ABOUT THIS VIDEO
The narration is AI-generated (an open-source text-to-speech voice) and is disclosed as altered or synthetic content. The retelling was written for this channel and checked against the text of Ruth and Esther. Background notes (gleaning in the law of Leviticus 19 and Deuteronomy 24, the kinsman-redeemer, the town gate, Susa and the Persian Empire, Ahasuerus often identified with Xerxes I, the feast of Purim) follow standard reference sources, and open questions are mentioned honestly. Nothing is invented and no sermon is added. The hard passage in Esther 9 is summarized briefly rather than read.

SCRIPTURE
Scripture quotations are from the World English Bible (public domain), lightly adapted for reading aloud: the divine name is rendered as "the Lord". Passages read: Ruth 1 to 4 (the whole book); Esther 1:1-22; 2:5-23; 3:1-15; 4:4-17; 5:1-14; 6:1-14; 7:1-10; 8:3-8, 15-17; 9:20-22; 10:1-3.

IMAGES
Public-domain artworks and engravings from Wikimedia Commons and museum collections, including works by {artists}. Full list of file pages on request in the comments.

This video is for rest and reflection. It is not medical advice. If you have trouble sleeping regularly, please talk to a doctor.

Subscribe to Lamplight Scripture for calm Bible stories for sleep.

#BibleStoriesForSleep #Ruth #Esther #SleepStory #ScriptureForSleep"""
desc = desc.replace('<', '').replace('>', '')
tags = "bible stories for sleep, book of ruth, book of esther, ruth and naomi, ruth and boaz, queen esther, for such a time as this, where you go i will go, mordecai and haman, women of the bible, fall asleep to the bible, bible sleep stories, christian sleep stories, scripture for sleep, bedtime bible stories for adults, bible audio for sleep, calm bible reading, relaxing bible stories, lamplight scripture, old testament stories"
comment = "Welcome, and goodnight. 🌙 Ruth said, where you go, I will go. Esther said, if I perish, I perish. Where in the world are you listening from tonight? And which Bible story should Lamplight Scripture tell next?"
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

UPLOAD CHECKLIST (YouTube Studio)
1. Upload video.mp4 (join the parts on branch backup-lamplight-ruth-esther), set the thumbnail to thumbnail.jpg.
2. Visibility: schedule for Wed 2 Dec 2026 05:30 IST (= Tue 1 Dec 2026 7:00 pm New York = 2026-12-02T00:00:00Z).
3. Audience: No, it's not made for kids.
4. Altered content: Yes (AI-generated voice).
5. Category: Education. Language: English.
6. Playlist: Bible Stories for Sleep.
7. First comment posts automatically; pin it.

SLOT
lamplight 2026-12-02 05:30 IST (2026-12-02T00:00:00Z)

Length: {length}
"""
assert len(title) <= 100 and len(desc) < 5000, len(desc)
open(f'{B}/metadata.txt', 'w').write(txt)
print(len(title), len(desc)); print("\n".join(lines))
