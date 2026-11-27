import json, sys
sys.path.insert(0,'/home/claude/marie')
import anim, maps
B='/home/claude/marie'
ch={int(k):v for k,v in json.load(open(B+'/ch_imgs.json')).items()}
titles={n:open(f'{B}/script/ch{n:02d}.txt').readline().split(':',1)[1].strip() for n in range(1,13)}
anim.title_card(B+'/anim/title.mp4','THE SLEEPY BIOGRAPHER','Marie Antoinette','The Last Queen of Versailles','A calm biography for sleep  ·  AI-generated narration',B+'/img/'+ch[1][0]); print('title',flush=True)
for n in range(2,13): anim.chapter_card(f'{B}/anim/ch{n:02d}.mp4',n,titles[n],B+'/img/'+ch[n][0]); print('card',n,flush=True)
anim.quote_card(B+'/anim/q1.mp4',['“Let them eat cake.”'],'A line with no good evidence that she ever said it',B+'/img/'+ch[1][1])
anim.quote_card(B+'/anim/q4.mp4',['“I put on my rouge and wash my hands','in front of the whole world.”'],'Marie Antoinette to her mother, 1770 (translated)',B+'/img/'+ch[4][1])
anim.quote_card(B+'/anim/q12.mp4',['“I am calm, as one is when','one’s conscience has nothing to reproach.”'],'Her last letter, 16 October 1793 (translated)',B+'/img/'+ch[12][1])
maps.m1(B+'/anim/map1.mp4',secs=22.0); maps.m2(B+'/anim/map2.mp4',secs=20.0); print('all done',flush=True)
