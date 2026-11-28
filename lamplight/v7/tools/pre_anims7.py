import json, sys
sys.path.insert(0,'/home/claude/lamp7/tools')
import anim, maps7 as maps
B='/home/claude/lamp7'
ch={int(k):v for k,v in json.load(open(B+'/ch_imgs.json')).items()}
titles={n:open(f'{B}/script/ch{n:02d}.txt').readline().split(':',1)[1].strip() for n in range(1,13)}
I=lambda n,k: B+'/img/'+ch[n][k]
import os; os.makedirs(B+'/anim',exist_ok=True)
anim.title_card(B+'/anim/title.mp4','LAMPLIGHT SCRIPTURE','The First Christmas','The Nativity story from Luke and Matthew','Bible stories for sleep  ·  AI-generated narration',I(1,0)); print('title',flush=True)
for n in range(2,13): anim.chapter_card(f'{B}/anim/ch{n:02d}.mp4',n,titles[n],I(n,0)); print('card',n,flush=True)
anim.quote_card(B+'/anim/q1.mp4',['“Don’t be afraid, Zacharias,','because your request has been heard.”'],'Luke 1:13 (World English Bible)',I(1,2))
anim.quote_card(B+'/anim/q9.mp4',['“Glory to God in the highest,','on earth peace, good will toward men.”'],'Luke 2:14 (World English Bible)',I(9,3))
anim.quote_card(B+'/anim/q9b.mp4',['“But Mary kept all these sayings,','pondering them in her heart.”'],'Luke 2:19 (World English Bible)',I(9,5))
anim.quote_card(B+'/anim/q10.mp4',['“Now you are releasing your servant, Master,','according to your word, in peace.”'],'Luke 2:29 (World English Bible)',I(10,3))
maps.m1(B+'/anim/map1.mp4',secs=22.0); maps.m2(B+'/anim/map2.mp4',secs=20.0); print('all done',flush=True)
