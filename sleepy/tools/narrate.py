import re, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
def render(text, voice, speed, out, pause_s=0.9, pause_p=1.4, k=None):
    k = k or Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
    sr=24000; seg=[]
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if para.startswith("## "):
            seg.append(np.zeros(int(sr*2.5),np.float32)); para=para[3:]
        if para.startswith("[NARRATOR"): continue
        for s in re.split(r'(?<=[.!?:])\s+', para):
            s=s.strip()
            if not s: continue
            a,sr=k.create(s, voice=voice, speed=speed, lang="en-gb"); seg+=[a, np.zeros(int(sr*pause_s),np.float32)]
        seg.append(np.zeros(int(sr*pause_p),np.float32))
    x=np.concatenate(seg); sf.write(out,x,sr)
    words=len(re.sub(r'\[.*?\]|##','',text).split())
    return len(x)/sr, words
if __name__=="__main__":
    txt=open('/home/claude/franklin/script/ch01.txt',encoding='utf-8').read()
    # first part only
    part="\n\n".join(txt.split("\n\n")[1:9])
    k=Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
    for v in ("bm_george","bm_fable"):
        for sp in (0.8,):
            d,w=render(part,v,sp,f"/home/claude/franklin/sample_{v}.wav",k=k)
            print(v,sp,f"{d:.0f}s",f"{w/(d/60):.0f} wpm")
