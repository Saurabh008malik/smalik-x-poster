import sys, time, re
sys.path.insert(0,'/home/claude/leonardo')
from narrate import render
from kokoro_onnx import Kokoro
FIX=[("Verrocchio","Verrokyo"),("Salaì","Salai"),("Cloux","Kloo"),("Clos Lucé","Clo Lussay"),("Anchiano","Ankyano"),("Gherardini","Gerardeeni"),("Giocondo","Jokondo"),("Gioconda","Jokonda"),("Joconde","Zhokond"),("Melzi","Meltsi"),("Caprotti","Caprotty"),("Pacioli","Pachyoli"),("Isonzo","Eezontso"),("Cesena","Chezayna"),("Cesenatico","Chezaynatico"),("Imola","Eemola"),("Romagna","Romanya"),("Romorantin","Romorontan"),("Marignano","Marinyano"),("Sfumato","sfoomahto"),("sfumato","sfoomahto"),("Giampietrino","Jampietreeno"),("Maturina","Maturina"),("Scopeto","Skopayto"),("Annunziata","Annuntsiata")]
k=Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
for n in sys.argv[1:]:
    t=time.time()
    txt=open(f'/home/claude/leonardo/script/ch{int(n):02d}.txt',encoding='utf-8').read()
    for a,b in FIX: txt=txt.replace(a,b)
    d,w=render(txt,"bm_george",0.74,f"/home/claude/leonardo/audio/ch{int(n):02d}.wav",pause_s=1.0,pause_p=1.6,k=k)
    print(f"ch{n}: {d/60:.1f} min audio, {w/(d/60):.0f} wpm, took {time.time()-t:.0f}s",flush=True)
