import sys, time, os
sys.path.insert(0,'/home/claude/marcus')
from narrate import render
from kokoro_onnx import Kokoro
k=Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
for n in [int(a) for a in sys.argv[1:]]:
    src=f'/home/claude/marcus/script/ch{n:02d}.txt'; ok=src.replace('.txt','.ok'); out=f'/home/claude/marcus/audio/ch{n:02d}.wav'
    if os.path.exists(out): continue
    while not os.path.exists(ok): time.sleep(20)
    t=time.time(); txt=open(src,encoding='utf-8').read()
    d,w=render(txt,"bm_george",0.74,out+'.tmp.wav',pause_s=1.0,pause_p=1.6,k=k); os.rename(out+'.tmp.wav',out)
    print(f"ch{n}: {d/60:.1f} min, {w/(d/60):.0f} wpm, {time.time()-t:.0f}s",flush=True)
