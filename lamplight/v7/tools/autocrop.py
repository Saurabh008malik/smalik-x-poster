import sys, numpy as np
from PIL import Image
def run(mask, thr):
    best=(0,0,0); s=None
    for i,v in enumerate(list(mask>thr)+[False]):
        if v and s is None: s=i
        if not v and s is not None:
            if i-s>best[0]: best=(i-s,s,i)
            s=None
    return best[1],best[2]
def crop(src,dst,thr=0.30,pad=6):
    im=Image.open(src).convert('RGB'); g=np.asarray(im.convert('L')).astype(np.float32)
    b=np.concatenate([g[:20].ravel(),g[-20:].ravel(),g[:,:20].ravel(),g[:,-20:].ravel()])
    # paper = brightest common tone
    paper=np.percentile(g,90)
    m=np.abs(g-paper)>45
    r0,r1=run(m.mean(1),thr); c0,c1=run(m[r0:r1].mean(0),thr)
    if (r1-r0)<0.3*g.shape[0] or (c1-c0)<0.3*g.shape[1]: im.save(dst,quality=92); return 'nochange'
    im.crop((max(c0-pad,0),max(r0-pad,0),min(c1+pad,g.shape[1]),min(r1+pad,g.shape[0]))).save(dst,quality=92)
    return (c0,r0,c1,r1,g.shape)
if __name__=='__main__':
    for s in sys.argv[1:]:
        import os; print(s, crop(s,'/tmp/'+os.path.basename(s)))
