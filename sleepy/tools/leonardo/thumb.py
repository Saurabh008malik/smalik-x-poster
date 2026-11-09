import glob, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1280,720
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
d=np.sqrt(((xx-560)/700)**2+((yy-330)/520)**2)
bg=np.clip(1-d,0,1)[...,None]*np.array([70,42,18],np.float32)+np.array([14,9,6],np.float32)
base=Image.fromarray(np.clip(bg,0,255).astype(np.uint8))
im=Image.open(glob.glob('img/ld_001_*')[0]).convert('RGB')
TW=470
cw=int(im.width*0.97); ch=int(cw*H/TW)
y0=int(im.height*0.04); ch=min(ch,im.height-y0); cw=int(ch*TW/H)
x1=int((im.width-cw)/2)
im=im.crop((x1,y0,x1+cw,y0+ch)).resize((TW,H),Image.LANCZOS)
a=np.asarray(im).astype(np.float32)*np.array([0.95,0.82,0.62],np.float32)
im=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
x0=W-TW-20
m=np.ones((H,TW),np.float32)*255
m*=np.clip(np.linspace(0,1,TW)/0.35,0,1)[None,:]
m*=np.clip(np.linspace(1,0,TW)/0.10,0,1)[None,:]
base.paste(im,(x0,0),Image.fromarray(m.astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)))
dr=ImageDraw.Draw(base)
fb='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'; fr='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
def t(xy,s,f,sz,col):
    ft=ImageFont.truetype(f,sz); x,y=xy
    dr.text((x+4,y+4),s,font=ft,fill=(0,0,0)); dr.text((x,y),s,font=ft,fill=col)
t((64,125),'LEONARDO',fb,122,(245,228,190))
t((64,250),'DA VINCI',fb,122,(245,228,190))
t((64,410),'BIOGRAPHY FOR SLEEP',fr,50,(214,168,100))
t((64,490),'Calm story  ·  2 hours  ·  Fireplace',fr,34,(190,160,115))
base.save('thumb_leonardo.jpg',quality=92); base.save('thumb_leonardo.png')
