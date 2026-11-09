import sys, time
sys.path.insert(0,'/home/claude/franklin')
from narrate import render
from kokoro_onnx import Kokoro
k=Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
for n in sys.argv[1:]:
    t=time.time()
    txt=open(f'/home/claude/franklin/script/ch{int(n):02d}.txt',encoding='utf-8').read()
    d,w=render(txt,"bm_george",0.74,f"/home/claude/franklin/audio/ch{int(n):02d}.wav",pause_s=1.0,pause_p=1.6,k=k)
    print(f"ch{n}: {d/60:.1f} min audio, {w/(d/60):.0f} wpm, took {time.time()-t:.0f}s",flush=True)
