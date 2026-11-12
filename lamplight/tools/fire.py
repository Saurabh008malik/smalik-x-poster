import numpy as np, soundfile as sf
def fire(seconds, sr=24000, seed=1):
    rng=np.random.default_rng(seed); n=int(seconds*sr)
    # warm low rumble: brown-ish noise, low-passed
    w=rng.standard_normal(n).astype(np.float32)
    b=np.cumsum(w); b-=np.linspace(b[0],b[-1],n); b/=np.abs(b).max()+1e-9
    k=int(sr*0.02); lp=np.convolve(b,np.ones(k)/k,mode='same')
    bed=lp*0.5
    # crackles: sparse short decaying pops
    cr=np.zeros(n,np.float32); count=int(seconds*3.2)
    for pos in rng.integers(0,n-2000,count):
        L=rng.integers(120,900); env=np.exp(-np.linspace(0,7,L)); cr[pos:pos+L]+= (rng.standard_normal(L)*env*rng.uniform(.05,.35)).astype(np.float32)
    x=bed+cr*0.6
    # slow swell
    x*=0.85+0.15*np.sin(np.linspace(0,seconds/9,n))
    return (x/np.abs(x).max()*0.9).astype(np.float32)
