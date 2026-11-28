import re, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
def render(text, voice, speed, out, pause_s=1.0, pause_p=1.6, k=None, lang="en-us"):
    k = k or Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
    sr=24000; seg=[]
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if para.startswith("## "):
            seg.append(np.zeros(int(sr*2.5),np.float32)); para=para[3:]
        if para.startswith("[NARRATOR"): continue
        for s in re.split(r'(?<=[.!?:;])\s+(?=[A-Z"\'])', para):
            s=s.strip()
            if not s: continue
            a,sr=k.create(s, voice=voice, speed=speed, lang=lang); seg+=[a, np.zeros(int(sr*pause_s),np.float32)]
        seg.append(np.zeros(int(sr*pause_p),np.float32))
    x=np.concatenate(seg); sf.write(out,x,sr)
    words=len(re.sub(r'\[.*?\]|##','',text).split())
    return len(x)/sr, words
