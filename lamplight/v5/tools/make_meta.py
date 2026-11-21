import json, collections
B = '/home/claude/lamp5'
tl = json.load(open(f'{B}/timeline.json'))
durs = {int(k): v for k, v in tl['durs'].items()}
names = ['Welcome, and a City by the River', "Four Young Men and the King's Table", 'A Dream in the Night', 'The Statue and the Stone', 'The Golden Image on the Plain', 'The Fourth Man in the Fire', 'The Great Tree and the Humbled King', 'The Hand by the Lamp', 'An Open Window Toward Jerusalem', "The Night in the Lions' Den", 'Seventy Years, and a Prayer at Evening', 'By the Great River, and Goodnight']
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
title = "Daniel in Babylon: The Furnace, the Wall and the Lions | Bible Stories for Sleep"
desc = f"""Settle in, dim the lights, and listen to the story of Daniel: a young man carried from Jerusalem to Babylon, four friends at a foreign king's table, Nebuchadnezzar's dream of a great statue and a small stone, three friends who would not bow before the golden image, a fourth figure walking in the fiery furnace, a great tree cut down and a proud king humbled, the hand that wrote on the wall beside the lamp, an open window toward Jerusalem, a long night in the lions' den, and an old man's last vision beside a great river. A calm, slow-paced retelling of the book of Daniel for sleep, with the key passages read from scripture itself.

🌙 Best with a low volume and the screen dimmed. You can let it play through the night.

CHAPTERS
""" + "\n".join(lines) + f"""

ABOUT THIS VIDEO
The narration is AI-generated (an open-source text-to-speech voice) and is disclosed as altered or synthetic content. The retelling was written for this channel and checked against the text of Daniel, with background from Jeremiah, 2 Kings, Psalm 137 and Ezra 1. Historical notes (Nebuchadnezzar II, the Ishtar Gate, Belshazzar and Nabonidus, the fall of Babylon in 539 BC, the Cyrus Cylinder) follow standard museum and reference sources, and open questions (the date of the book, Darius the Mede) are mentioned honestly. Nothing is invented and no sermon is added.

SCRIPTURE
Scripture quotations are from the World English Bible (public domain), lightly adapted for reading aloud: the divine name is rendered as "the Lord". Passages read: Daniel 1 to 7, 9, 10 and 12; Psalm 137:1-4; Jeremiah 29:4-11; Ezra 1:1-3; Numbers 6:24-26.

IMAGES
Public-domain artworks, engravings and photographs from Wikimedia Commons and museum collections, including works by {artists}. Full list of file pages on request in the comments.

This video is for rest and reflection. It is not medical advice. If you have trouble sleeping regularly, please talk to a doctor.

Subscribe to Lamplight Scripture for calm Bible stories for sleep.

#BibleStoriesForSleep #Daniel #LionsDen #SleepStory #ScriptureForSleep"""
desc = desc.replace('<', '').replace('>', '')
tags = "bible stories for sleep, book of daniel, daniel in the lions den, daniel bible story, fiery furnace, shadrach meshach and abednego, writing on the wall, nebuchadnezzar dream, belshazzar feast, babylon bible story, fall asleep to the bible, bible sleep stories, christian sleep stories, scripture for sleep, bedtime bible stories for adults, bible audio for sleep, calm bible reading, relaxing bible stories, lamplight scripture, old testament stories"
comment = "Welcome, and goodnight. 🌙 Daniel kept his window open toward home and prayed three times a day, as he did before. Where in the world are you listening from tonight? And which Bible story should Lamplight Scripture tell next?"
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
1. Upload video.mp4 (join the parts on branch backup-lamplight-daniel), set the thumbnail to thumbnail.jpg.
2. Visibility: schedule for Sat 28 Nov 2026 05:30 IST (= Fri 27 Nov 2026 7:00 pm New York = 2026-11-28T00:00:00Z).
3. Audience: No, it's not made for kids.
4. Altered content: Yes (AI-generated voice).
5. Category: Education. Language: English.
6. Playlist: Bible Stories for Sleep.
7. First comment posts automatically; pin it.

SLOT
lamplight 2026-11-28 05:30 IST (2026-11-28T00:00:00Z)

Length: {length}
"""
assert len(title) <= 100 and len(desc) < 5000, len(desc)
open(f'{B}/metadata.txt', 'w').write(txt)
print(len(title), len(desc)); print("\n".join(lines))
