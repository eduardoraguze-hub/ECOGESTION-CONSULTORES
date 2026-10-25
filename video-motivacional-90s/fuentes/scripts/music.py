# Original cinematic score, synthesized from scratch (100% royalty-free).
import numpy as np, scipy.signal as sg, scipy.io.wavfile as wf, sys
SR=44100; DUR=90.0; N=int(SR*DUR); t=np.arange(N)/SR
BPM=70; BEAT=60/BPM; BAR=4*BEAT
rng=np.random.default_rng(7)
def midi(m): return 440*2**((m-69)/12)
def env_adsr(n,a,d,s,r,sus_len):
    A=int(a*SR);D=int(d*SR);S=max(int(sus_len*SR),0);R=int(r*SR)
    e=np.concatenate([np.linspace(0,1,A,endpoint=False),np.linspace(1,s,D,endpoint=False),np.full(S,s),np.linspace(s,0,R)])
    return e[:n] if len(e)>=n else np.pad(e,(0,n-len(e)))
def place(buf,sig,start):
    i=int(start*SR); 
    if i>=len(buf): return
    j=min(len(buf),i+len(sig)); buf[i:j]+=sig[:j-i]
def lp(x,fc,order=2): b,a=sg.butter(order,min(fc/(SR/2),0.99),'low'); return sg.lfilter(b,a,x)
def hp(x,fc,order=2): b,a=sg.butter(order,fc/(SR/2),'high'); return sg.lfilter(b,a,x)
def saw(f,tt,det=0.0):
    out=np.zeros_like(tt)
    for d in (-det,0,det):
        ph=(f*(1+d)*tt + rng.random())%1.0; out+=2*ph-1
    return out/3
# progression Dm Bb F C  (2 bars each), voicings (midi)
prog=[[50,57,62,65,69],[46,58,62,65,70],[53,57,60,65,69],[48,55,60,64,67]]
roots=[38,34,41,36]
CH=2*BAR
def chord_at(time): return int(time//CH)%4
L=np.zeros(N); R=np.zeros(N)
def add(sig,start,pan=0.0,g=1.0):
    place(L,sig*g*np.sqrt(0.5*(1-pan)),start); place(R,sig*g*np.sqrt(0.5*(1+pan)),start)
# intensity curve: 0-15 soft, 15-45 build, 45-69 bigger, 69.4-80 climax, 80-90 resolve
def inten(x): return np.interp(x,[0,15,45,64,69.4,80,84,90],[0.25,0.4,0.6,0.75,1.0,1.0,0.5,0.3])
# 1) pads
nch=int(np.ceil(DUR/CH))
for k in range(nch):
    st=k*CH; c=prog[k%4]; ln=CH+1.5; n=int(ln*SR); tt=np.arange(n)/SR
    sig=np.zeros(n)
    for m in c: sig+=saw(midi(m),tt,0.004)
    sig=lp(sig,900+1800*inten(st)); sig*=env_adsr(n,1.2,0.5,0.85,1.5,ln-3.2)
    add(sig,st,0,0.02+0.10*inten(st)**2)
# 2) low drone / cello root
for k in range(nch):
    st=k*CH; f=midi(roots[k%4]); ln=CH+1.0; n=int(ln*SR); tt=np.arange(n)/SR
    sig=lp(saw(f,tt,0.002),500)+0.5*np.sin(2*np.pi*f/2*tt)
    sig*=env_adsr(n,0.8,0.3,0.9,1.0,ln-2.1); add(sig,st,0,0.04+0.14*inten(st)**2)
# 3) piano arpeggio (throughout, sparser in climax)
def piano(f,ln=2.5):
    n=int(ln*SR); tt=np.arange(n)/SR
    s=sum((0.6**h)*np.sin(2*np.pi*f*(h+1)*tt*(1+0.0005*h))*np.exp(-tt*(1.6+h*0.9)) for h in range(5))
    s*=np.minimum(1,tt/0.004); return s
pat=[0,2,3,4,3,2,1,2]
x=0.0
while x<DUR-2:
    k=chord_at(x); c=prog[k%4]; 
    for i,p in enumerate(pat):
        tm=x+i*BEAT/2
        if tm>=DUR-1: break
        g=0.20 if not(69.4<tm<80) else 0.10
        add(piano(midi(c[p]+12)),tm,0.3*np.sin(i),g)
    x+=2*BEAT
# 4) string ostinato from 15s (16ths-ish 8ths)
x=15.0
while x<84:
    k=chord_at(x); c=prog[k%4]
    for i in range(8):
        tm=x+i*BEAT/2; n=int(BEAT/2*SR*0.95); tt=np.arange(n)/SR
        f=midi(c[0]+12 if i%2==0 else c[2]+12)
        s=lp(saw(f,tt,0.003),1500+2500*inten(tm))*env_adsr(n,0.02,0.1,0.6,0.08,BEAT/2*0.6)
        add(s,tm,-0.4 if i%2 else 0.4,0.10*min(1,(tm-15)/10)*inten(tm)/0.6)
    x+=BAR
# 5) drums: taiko/boom
def boom(g=1.0,ln=1.2):
    n=int(ln*SR); tt=np.arange(n)/SR
    f=55*np.exp(-tt*3)+38; ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-tt*4.5)+0.25*lp(rng.standard_normal(n),800)*np.exp(-tt*25)
    return s*g
x=30.0; 
while x<80:
    b=int(round((x-30)/BEAT))
    if x<45: hits=[0] if b%4==0 else []
    elif x<64: hits=[0,0.5] if b%2==0 else ([0] if b%4==3 else [])
    elif x<69.4: hits=[0,0.5]
    else: hits=[0] if b%2==0 else [0,0.5]
    for h in hits: add(boom(),x+h*BEAT,0,0.9*inten(x))
    x+=BEAT
# 6) riser 64 -> 69.4 then impact
n=int(5.4*SR); tt=np.arange(n)/SR; noise=rng.standard_normal(n)
fc=200*np.exp(np.log(40)*tt/5.4)
rs=np.zeros(n); seg=2048
for i in range(0,n,seg):
    b,a=sg.butter(2,[min(fc[i],8000)/(SR/2)*0.7,min(fc[i]*1.3,9000)/(SR/2)],'band'); rs[i:i+seg]=sg.lfilter(b,a,noise[i:i+seg])
rs*= (tt/5.4)**2; add(rs,64.0,0,0.35)
imp=boom(1.6,3.0)+0.5*lp(rng.standard_normal(int(3*SR)),3000)*np.exp(-np.arange(int(3*SR))/SR*6)
add(imp,69.45,0,0.9)
# 7) brass-like swells in climax 69.4-82
x=69.45
while x<82:
    k=chord_at(x); c=prog[k%4]; ln=2*BAR if x<79 else 4.0; n=int(ln*SR); tt=np.arange(n)/SR
    s=sum(saw(midi(m-12 if i<2 else m),tt,0.006) for i,m in enumerate(c[:4]))
    s=lp(s,2600)*env_adsr(n,0.25,0.4,0.8,1.0,ln-1.65)
    add(s,x,0,0.13)
    x=(int(x//CH)+1)*CH
# 8) choir-ish pad (sine stack w/ vibrato) climax
seg_s,seg_e=69.45,84.0; n=int((seg_e-seg_s)*SR); tt=np.arange(n)/SR; ch=np.zeros(n)
for m in [62,65,69,74]:
    f=midi(m); vib=1+0.004*np.sin(2*np.pi*5.2*tt)
    ch+=np.sin(2*np.pi*np.cumsum(f*vib)/SR)+0.3*np.sin(2*np.pi*np.cumsum(2*f*vib)/SR)
ch*=env_adsr(n,1.5,0.5,0.8,3.0,n/SR-5); add(lp(ch,3000),seg_s,0,0.05)
# final resolve: Dmaj-ish -> D (picardy) piano + pad 84-90
for i,m in enumerate([62,66,69,74]):
    add(piano(midi(m),5.0),84.0+i*0.25,0.2*(i-1.5),0.25)
# reverb (convolution with decaying noise IR)
irn=int(2.8*SR); irt=np.arange(irn)/SR
irL=rng.standard_normal(irn)*np.exp(-irt*2.2); irR=rng.standard_normal(irn)*np.exp(-irt*2.2)
irL=lp(irL,5000); irR=lp(irR,5000); irL/=np.abs(irL).sum()**0.5*30; irR/=np.abs(irR).sum()**0.5*30
wetL=sg.fftconvolve(L,irL)[:N]; wetR=sg.fftconvolve(R,irR)[:N]
L2=L+0.9*wetL; R2=R+0.9*wetR
fade=np.ones(N); fn=int(3*SR); fade[-fn:]=np.linspace(1,0,fn)**1.5; fade[:int(0.3*SR)]=np.linspace(0,1,int(0.3*SR))
out=np.stack([L2*fade,R2*fade],1); out=hp(out.T,30).T
out/=np.abs(out).max()*1.12
wf.write(sys.argv[1],SR,(out*32767).astype(np.int16))
print('ok')
