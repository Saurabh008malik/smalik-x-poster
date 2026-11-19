import json, collections
B = '/home/claude/lamp4'
tl = json.load(open(f'{B}/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = ['Welcome, and a Boy with the Sheep', "A Harp in the King's House", 'The Valley of Elah', 'Jonathan, and a Song That Went Wrong', 'A Fugitive in the Wilderness', 'The Cave at En Gedi, and a Wise Woman', 'A Spear, a Water Jar, and the Mountains of Gilboa', 'A King in Hebron, and a City on a Hill', 'Dancing Before the Ark, and a Promise of a House', "A Rooftop in the Evening, and a Prophet's Story", 'Absalom, and the Road Up the Mount of Olives', 'Last Words, a Song, and Goodnight']
def ts(s):
    s = int(s); h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
lines = []; t = tl['lead']
for n in range(1, 13):
    lines.append(f"{'0:00' if n == 1 else ts(t)} {names[n-1]}"); t += durs[n]
src = json.load(open(f'{B}/img/sources.json')); used = set(f for v in json.load(open(f'{B}/ch_imgs.json')).values() for f in v)
BAD=('Rijksmuseum','Marie-Lan','Unknown','Coyau','Descouens','NYPL','anonymous','Anonymous')
arts = collections.Counter(i['artist'].strip().split(chr(10))[0] for i in src if i['file'] in used and i['artist'].strip() and not any(b in i['artist'] for b in BAD))
artists = ', '.join(a for a, _ in arts.most_common(10))
length = ts(tl['total'])
title = "The Life of David: Shepherd, Poet and King | Bible Stories for Sleep"
desc = f"""Settle in, dim the lights, and listen to the life of David: a shepherd boy anointed in Bethlehem, a harp in King Saul's house, five smooth stones in the valley of Elah, a friendship with Jonathan, years of hiding in the caves of the wilderness, a crown in Hebron and a city on a hill, a great wrong and a prophet's story, the grief of a father for Absalom, and an old king's last song. A calm, slow-paced retelling of 1 and 2 Samuel and the opening of 1 Kings for sleep, with the key passages and Psalms read from scripture itself.

🌙 Best with a low volume and the screen dimmed. You can let it play through the night.

CHAPTERS
""" + "\n".join(lines) + f"""

ABOUT THIS VIDEO
The narration is AI-generated (an open-source text-to-speech voice) and is disclosed as altered or synthetic content. The retelling was written for this channel and checked against the text of 1 and 2 Samuel and 1 Kings. Where the text is hard (the death of Saul, David and Bathsheba, the rebellion of Absalom), the narration stays honest and gentle; nothing is invented and no sermon is added.

SCRIPTURE
Scripture quotations are from the World English Bible (public domain), lightly adapted for reading aloud: the divine name is rendered as "the Lord". Passages read: 1 Samuel 16 to 30, 2 Samuel 1 to 23, 1 Kings 2, and Psalms 3, 23, 51 and 57.

Tapestry and painting details include the "David and Bathsheba" tapestries (Musée national de la Renaissance, Écouen) and engravings from the Rijksmuseum collection.

IMAGES
Public-domain artworks, engravings and illustrations from Wikimedia Commons and museum collections, including works by {artists}. Full list of file pages on request in the comments.

This video is for rest and reflection. It is not medical advice. If you have trouble sleeping regularly, please talk to a doctor.

Subscribe to Lamplight Scripture for calm Bible stories for sleep.

#BibleStoriesForSleep #KingDavid #Psalm23 #SleepStory #ScriptureForSleep"""
desc = desc.replace('<', '').replace('>', '')
tags = "bible stories for sleep, story of david, king david bible story, david and goliath, life of king david, fall asleep to the bible, bible sleep stories, christian sleep stories, scripture for sleep, bedtime bible stories for adults, psalm 23, the lord is my shepherd, david and jonathan, 1 samuel, 2 samuel, bible audio for sleep, calm bible reading, relaxing bible stories, lamplight scripture, old testament stories"
comment = "Welcome, and goodnight. 🌙 If you are listening tonight, tell us where in the world you are, and which Bible story you would like Lamplight Scripture to tell next."
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
1. Upload video.mp4 (join the parts on branch backup-lamplight-david), set the thumbnail to thumbnail.jpg.
2. Visibility: schedule for Wed 25 Nov 2026 05:30 IST (= Tue 24 Nov 2026 7:00 pm New York = 2026-11-25T00:00:00Z).
3. Audience: No, it's not made for kids.
4. Altered content: Yes (AI-generated voice).
5. Category: Education. Language: English.
6. Playlist: Bible Stories for Sleep.
7. First comment posts automatically; pin it.

SLOT
lamplight 2026-11-25 05:30 IST (2026-11-25T00:00:00Z)

Length: {length}
"""
assert len(title) <= 100 and len(desc) < 5000, len(desc)
open(f'{B}/metadata.txt', 'w').write(txt)
print(len(title), len(desc)); print("\n".join(lines))
