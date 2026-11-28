import json
R='/home/claude/smalik-x-poster'
S=json.load(open(R+'/ytq/shorts.json'))
desc="Watch the full story, told slowly and calmly for sleep: {LONG_URL}\n\nSubscribe and turn on the notification bell for new Bible stories.\n\nLamplight Scripture tells calm Bible stories for sleep and rest. Scripture text: World English Bible (public domain). Narration is AI-generated.\n\n#BibleStories #Christmas #Shorts"
base_tags=["bible stories","bible stories for sleep","bible story","sleep story","calm bible reading","world english bible","lamplight scripture"]
dates=['2026-12-24T01:35:00Z','2026-12-25T01:35:00Z','2026-12-26T01:35:00Z','2026-12-27T01:35:00Z']
have={x['id'] for x in S}
for i in range(4):
    sp=json.load(open(f'/home/claude/lamp7/shorts/s{i+1}.json')); n=41+i; sid=f'lamplight-{n}'
    if sid in have: continue
    S.append(dict(id=sid,channel='lamplight',branch='feed-shorts-lamplight-9',file=f'shorts/lamplight_{n}_nativity_s{i+1}.mp4',
        publish_after=dates[i],link_title_contains='The First Christmas',title=sp['title'],description=desc,
        tags=base_tags+sp['tags'],hook=sp['hook'],source=sp['source'],done=False))
json.dump(S,open(R+'/ytq/shorts.json','w'),indent=2,ensure_ascii=False)
C=json.load(open(R+'/ytq/comments.json'))
m=json.load(open('/home/claude/lamp7/meta_out.json'))
if not any(c.get('title_contains')=='The First Christmas' for c in C):
    C.append(dict(channel='lamplight',title_contains='The First Christmas',go_live='2026-12-09T00:00:00Z',text=m['comment'],done=False))
json.dump(C,open(R+'/ytq/comments.json','w'),indent=2,ensure_ascii=False)
print('ok',len(S),len(C))
