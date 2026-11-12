"""python3 tools/render_all.py <project_dir> <voice> <speed> ch ch ..."""
import sys, time, pathlib
sys.path.insert(0,'/home/claude/lamplight/tools')
from narrate import render
from kokoro_onnx import Kokoro
proj, voice, speed = pathlib.Path(sys.argv[1]), sys.argv[2], float(sys.argv[3])
(proj/'audio').mkdir(exist_ok=True)
k=Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
for n in sys.argv[4:]:
    t=time.time()
    txt=(proj/'script'/f'ch{int(n):02d}.txt').read_text(encoding='utf-8')
    d,w=render(txt,voice,speed,str(proj/'audio'/f'ch{int(n):02d}.wav'),pause_s=1.0,pause_p=1.6,k=k)
    print(f"ch{n}: {d/60:.1f} min audio, {w/(d/60):.0f} wpm, took {time.time()-t:.0f}s",flush=True)
