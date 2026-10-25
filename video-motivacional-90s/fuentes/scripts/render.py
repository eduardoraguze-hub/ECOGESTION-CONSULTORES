# Renders the 1080x1920 vertical master as raw RGB frames to stdout.
import json, math, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user-ECOGESTION-CONSULTORES/08e15db7-c263-572c-b3e1-fe55c441bc60/scratchpad/'
W,H,FPS,DUR=1080,1920,30,90.0
OFF=0.5  # voice offset in the final timeline
GOLD=(255,200,61)
_FC={}
def F(n,s):
    k=(n,int(s))
    if k not in _FC: _FC[k]=ImageFont.truetype(S+'fonts/'+n,int(s))
    return _FC[k]
def soft_shadow(lay,xy,txt,font,stroke,blur,alpha=200):
    d=ImageDraw.Draw(lay); bb=d.textbbox(xy,txt,font=font,stroke_width=stroke)
    pad=blur*3; x0,y0=int(bb[0]-pad),int(bb[1]-pad)
    sm=Image.new('RGBA',(int(bb[2]-bb[0]+2*pad),int(bb[3]-bb[1]+2*pad)),(0,0,0,0))
    ImageDraw.Draw(sm).text((xy[0]-x0,xy[1]-y0),txt,font=font,fill=(0,0,0,alpha),stroke_width=stroke,stroke_fill=(0,0,0,alpha))
    sm=sm.filter(ImageFilter.GaussianBlur(blur))
    lay.alpha_composite(sm,(max(x0,0),max(y0,0)),(max(-x0,0),max(-y0,0)))
ANTON='Anton.ttf'; MB='Montserrat_wght_800.ttf'; MM='Montserrat_wght_500.ttf'
IMG={k:Image.open(S+'video/img/'+k+'.png').convert('RGB') for k in ['v01','v02','s01']}
rng=np.random.default_rng(3)

def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)
def lerp(a,b,x): return a+(b-a)*x
def kb(src,a,b,p,bw=False):
    im=IMG[src]; iw,ih=im.size; x=ease(p)
    cx,cy,h=(lerp(a[i],b[i],x) for i in range(3)); w=h*9/16
    cx=min(max(cx,w/2),iw-w/2); cy=min(max(cy,h/2),ih-h/2)
    out=im.transform((W,H),Image.EXTENT,(cx-w/2,cy-h/2,cx+w/2,cy+h/2),Image.BICUBIC)
    if bw: out=out.convert('L').convert('RGB')
    return out

# ---------- procedural scenes (rendered at half res, upscaled) ----------
hw,hh=540,960
def glow(img,r): return img.filter(ImageFilter.GaussianBlur(r))
def bulb(t,on_at):
    im=Image.new('RGB',(hw,hh),(8,6,5)); d=ImageDraw.Draw(im)
    if t<on_at:  # failed attempts: flicker
        k=t*7; lvl=0.15+0.5*max(0,math.sin(k*3.1)*math.sin(k*1.7))*(rng.random()>0.4)
    else: lvl=min(1,0.4+(t-on_at)*1.5)
    lvl*=1+0.03*math.sin(t*40)
    cx,cy=hw/2,hh*0.47
    d.ellipse([cx-120,cy-150,cx+120,cy+110],outline=(40+int(60*lvl),30+int(40*lvl),20),width=3)
    d.rectangle([cx-50,cy+105,cx+50,cy+175],outline=(60,50,40),width=3)
    for i in range(4): d.line([cx-50,cy+120+i*15,cx+50,cy+128+i*15],fill=(70,60,45),width=3)
    d.line([cx-30,cy+105,cx-20,cy-10],fill=(90,80,70),width=2); d.line([cx+30,cy+105,cx+20,cy-10],fill=(90,80,70),width=2)
    pts=[(cx-20+40*i/30, cy-10-12*math.sin(i*1.3)) for i in range(31)]
    fil=Image.new('RGB',(hw,hh),(0,0,0)); fd=ImageDraw.Draw(fil)
    fd.line(pts,fill=(int(255*lvl),int(190*lvl),int(90*lvl)),width=4)
    g=Image.blend(glow(fil,40),glow(fil,10),0.5)
    a=np.asarray(im,dtype=np.float32)+np.asarray(fil,dtype=np.float32)+np.asarray(g,dtype=np.float32)*3.5*lvl
    yy,xx=np.mgrid[0:hh,0:hw]; rr=np.sqrt((xx-cx)**2+(yy-cy)**2)
    a+=(np.exp(-rr/180)*lvl*120)[...,None]*np.array([1.0,0.65,0.3])
    return dust(np.clip(a,0,255),t)
P=rng.random((140,3))
def dust(a,t,col=(255,220,170)):
    im=Image.fromarray(a.astype(np.uint8)); d=ImageDraw.Draw(im)
    for x,y,z in P:
        px=(x*hw+math.sin(t*0.3+z*9)*20)%hw; py=(y*hh-t*(8+20*z))%hh; r=0.6+1.6*z
        c=tuple(int(v*(0.3+0.5*z)) for v in col); d.ellipse([px-r,py-r,px+r,py+r],fill=c)
    return np.asarray(im,dtype=np.float32)
def darkbg(t,tint=(30,22,14)):
    yy,xx=np.mgrid[0:hh,0:hw]; rr=np.sqrt((xx-hw/2)**2+(yy-hh*0.45)**2)
    a=np.exp(-rr/420)[...,None]*np.array(tint,dtype=np.float32)*1.6+4
    return dust(a,t)
NODES=rng.standard_normal((80,3)); NODES/=np.linalg.norm(NODES,axis=1,keepdims=True); NODES*=rng.random((80,1))**0.3
def network(t):
    th=t*0.25; R=np.array([[math.cos(th),0,math.sin(th)],[0,1,0],[-math.sin(th),0,math.cos(th)]])
    p=NODES@R.T; z=p[:,2]+2.5; sx=hw/2+p[:,0]/z*900; sy=hh*0.45+p[:,1]/z*900
    im=Image.new('RGB',(hw,hh),(4,8,14)); d=ImageDraw.Draw(im)
    pulse=0.5+0.5*math.sin(t*2)
    for i in range(len(p)):
        for j in range(i+1,len(p)):
            dd=np.linalg.norm(p[i]-p[j])
            if dd<0.45:
                k=1-dd/0.45; d.line([sx[i],sy[i],sx[j],sy[j]],fill=(int(40*k),int(140*k),int(190*k)),width=1)
    for i in range(len(p)):
        r=2+3/z[i]; gold=(i*7)%11==int(t*3)%11
        d.ellipse([sx[i]-r,sy[i]-r,sx[i]+r,sy[i]+r],fill=GOLD if gold else (150,220,255))
    a=np.asarray(im,dtype=np.float32)+np.asarray(glow(im,8),dtype=np.float32)*1.8*(0.8+0.2*pulse)
    return np.clip(a,0,255)
HOR=np.cumsum(rng.standard_normal(hw))*1.2
HOR=HOR-np.convolve(HOR,np.ones(80)/80,'same')
def sunrise(t,rise):
    yy,xx=np.mgrid[0:hh,0:hw].astype(np.float32)
    top=np.array([10,14,32],np.float32); mid=np.array([120,60,40],np.float32); low=np.array([255,170,80],np.float32)
    k=yy/hh; a=np.where(k[...,None]<0.6, top+(mid-top)*(k[...,None]/0.6), mid+(low-mid)*((k[...,None]-0.6)/0.4))
    sy=hh*0.72-rise*120; rr=np.sqrt((xx-hw/2)**2+(yy-sy)**2)
    a+=(np.exp(-rr/90)*255+np.exp(-rr/300)*90)[...,None]*np.array([1,0.8,0.5])
    ang=np.arctan2(yy-sy,xx-hw/2); rays=(0.5+0.5*np.sin(ang*14+t*0.2))**8*np.exp(-rr/500)*60
    a+=rays[...,None]*np.array([1,0.85,0.6])
    hz=hh*0.74+40*np.sin(np.arange(hw)/90)+HOR*2
    a[yy>hz[None,:].repeat(hh,0)]=np.array([8,7,10])
    return dust(np.clip(a,0,255),t,(255,230,190))
def proc(fn,*args):
    a=fn(*args); return Image.fromarray(np.clip(a,0,255).astype(np.uint8)).resize((W,H),Image.BICUBIC)

# ---------- shot list (video time) ----------
v=lambda x:x+OFF
SH=[  # (start,end, renderer(t_local,p), transition-in)
 (0.0,7.3,  lambda t,p: kb('v01',(576,1024,2048),(540,1120,1650),p),'cut'),
 (7.3,11.6, lambda t,p: kb('v02',(576,1024,2048),(576,880,1450),p),'xf'),
 (11.6,14.5,lambda t,p: kb('v02',(780,430,1150),(760,450,980),p),'xf'),
 (14.5,17.6,lambda t,p: kb('s01',(500,576,1152),(820,576,1152),p),'xf'),
 (17.6,22.6,lambda t,p: kb('s01',(1032,640,1152),(1032,720,820),p),'xf'),
 (22.6,31.2,lambda t,p: proc(bulb,t,v(24.3)-22.6),'xf'),
 (31.2,35.3,lambda t,p: kb('v01',(560,520,1100),(600,600,900),p),'xf'),
 (35.3,37.6,lambda t,p: kb('v02',(560,820,900),(570,800,760),p,bw=True),'xf'),
 (37.6,44.9,lambda t,p: kb('s01',(380,600,1152),(1700,600,1152),p),'xf'),
 (44.9,50.8,lambda t,p: proc(darkbg,t),'flash'),
 (50.8,59.3,lambda t,p: proc(network,t),'xf'),
 (59.3,64.2,lambda t,p: kb('v01',(480,1330,950),(510,1260,700),p),'xf'),
 (64.2,69.45,lambda t,p: proc(sunrise,t,p),'xf'),
 (69.45,70.35,lambda t,p: kb('v02',(570,800,800),(570,800,700),p,bw=True),'flash'),
 (70.35,71.25,lambda t,p: proc(bulb,t+10,0),'flash'),
 (71.25,72.3,lambda t,p: kb('s01',(1032,700,1000),(1032,720,800),p),'flash'),
 (72.3,73.8,lambda t,p: kb('v01',(560,1150,1500),(560,1100,1800),p),'flash'),
 (73.8,80.7,lambda t,p: kb('v01',(560,900,1500),(576,1024,2048),p),'xf'),
 (80.7,90.0,lambda t,p: proc(sunrise,t+3,0.6+0.4*p),'xf'),
]
XF=0.35
def shot_frame(i,T):
    s,e,fn,_=SH[i]; return fn(T-s,(T-s)/(e-s))

# ---------- text ----------
def text_layer(): return Image.new('RGBA',(W,H),(0,0,0,0))
def draw_c(lay,txt,font,y,fill,alpha=1.0,scale=1.0,stroke=0,shadow=True,dx=0):
    if alpha<=0: return
    f=font if scale==1.0 else F(font.path.split('/')[-1],font.size*scale)
    tmp=text_layer(); d=ImageDraw.Draw(tmp)
    bb=d.textbbox((0,0),txt,font=f,stroke_width=stroke); tw=bb[2]-bb[0]; th=bb[3]-bb[1]
    x=(W-tw)/2-bb[0]+dx; yy=y-th/2-bb[1]
    if shadow:
        soft_shadow(tmp,(x+4,yy+6),txt,f,stroke+4,10)
    ImageDraw.Draw(tmp).text((x,yy),txt,font=f,fill=fill+(255,),stroke_width=stroke,stroke_fill=(0,0,0,255))
    if alpha<1:
        a=np.asarray(tmp).copy(); a[...,3]=(a[...,3]*alpha).astype(np.uint8); tmp=Image.fromarray(a)
    lay.alpha_composite(tmp)
def pop(T,t0,t1=None,fi=0.18,fo=0.25):
    if T<t0: return 0,1
    if t1 is not None and T>t1: a=max(0,1-(T-t1)/fo)
    else: a=min(1,(T-t0)/fi)
    sc=1+0.18*(1-ease((T-t0)/0.3))
    return a,sc

words=json.load(open(S+'video/audio/words_clean.json'))
groups=[]; cur=[]
for w in words:
    cur.append(w)
    if len(cur)==3 or w['text'][-1] in '.,…?!' : groups.append(cur); cur=[]
if cur: groups.append(cur)
CAP=F(MB,72)
HIDE=[(69.3,73.5)]
def captions(lay,T):
    if any(a<=T<=b for a,b in HIDE): return
    for gi,g in enumerate(groups):
        gs=v(g[0]['start'])-0.05; ge=v(groups[gi+1][0]['start'])-0.05 if gi+1<len(groups) else v(g[-1]['end'])+0.6
        ge=min(ge,v(g[-1]['end'])+0.9)
        if gs<=T<ge:
            toks=[w['text'].upper() for w in g]
            d=ImageDraw.Draw(lay); sp=22
            widths=[d.textbbox((0,0),tk,font=CAP,stroke_width=6)[2] for tk in toks]
            total=sum(widths)+sp*(len(toks)-1)
            lines=[list(range(len(toks)))]
            if total>W-120:
                lines=[list(range(len(toks)-1)),[len(toks)-1]] if len(toks)>1 else lines
            y0=1400-(len(lines)-1)*45
            for li,ln in enumerate(lines):
                lw=sum(widths[k] for k in ln)+sp*(len(ln)-1); x=(W-lw)/2
                for k in ln:
                    w=g[k]; active=v(w['start'])<=T<v(w['end'])+0.12
                    col=GOLD if active else (255,255,255)
                    soft_shadow(lay,(x+3,y0+li*90+6),toks[k],CAP,10,6,170)
                    ImageDraw.Draw(lay).text((x,y0+li*90),toks[k],font=CAP,fill=col+(255,),stroke_width=6,stroke_fill=(0,0,0,255))
                    x+=widths[k]+sp
            return

def kinetic(lay,T):
    # hook
    a=min(1,T/0.2) if T<6.8 else max(0,1-(T-6.8)/0.4)
    if T<7.3:
        draw_c(lay,'LO QUE NADIE TE DICE',F(MB,50),300,(255,255,255),a)
        draw_c(lay,'SOBRE EL ÉXITO',F(ANTON,128),400,GOLD,a,1+0.06*(1-ease(T/0.5)))
    if 22.6<=T<31.2:
        al,sc=pop(T,23.0,29.4); draw_c(lay,'MILES DE FALLOS',F(ANTON,120),470,(255,255,255),al,sc)
        al,sc=pop(T,v(29.28),30.9); draw_c(lay,'APRENDIZAJE',F(ANTON,140),470,GOLD,al,sc)
    if 44.9<=T<50.8:
        g_a,g_s=pop(T,v(46.16)); dim=0.45 if T>v(48.96) else 1
        draw_c(lay,'GRAMOS',F(ANTON,150),620,(255,255,255),g_a*dim,g_s)
        draw_c(lay,'vs',F(MM,56),760,(200,200,200),pop(T,v(47.04))[0]*dim)
        t_a,t_s=pop(T,v(48.96)); shake=int(14*math.sin(T*90)*max(0,1-(T-v(48.96))/0.35)) if T>v(48.96) else 0
        draw_c(lay,'TONELADAS',F(ANTON,230),930,GOLD,t_a,t_s,dx=shake)
    if 64.2<=T<69.45:
        al,sc=pop(T,v(64.24)); col=GOLD if T>v(66.04) else (255,255,255)
        draw_c(lay,'HOY',F(ANTON,400),720,col,al,sc if T<v(66.04) else 1+0.12*(1-ease((T-v(66.04))/0.3)))
        al2,_=pop(T,v(65.0),v(66.0)); draw_c(lay,'NO MAÑANA',F(MB,64),980,(255,255,255),al2)
    for t0,t1,txt,col in [(69.45,70.35,'LEVÁNTATE',(255,255,255)),(70.35,71.25,'APRENDE',(255,255,255)),(71.25,72.3,'PERSISTE',(255,255,255)),(72.3,73.8,'CONQUISTA',GOLD)]:
        if t0<=T<t1:
            al,sc=pop(T,t0); draw_c(lay,txt,F(ANTON,210),900,col,al,sc)
    if T>=80.7:
        al,sc=pop(T,80.9); draw_c(lay,'AQUÍ NO VENIMOS A SOÑAR.',F(MB,58),560,(255,255,255),al)
        al,sc=pop(T,81.6); draw_c(lay,'VENIMOS A',F(ANTON,150),700,(255,255,255),al,sc)
        al,sc=pop(T,82.2); draw_c(lay,'CONSTRUIR.',F(ANTON,190),880,GOLD,al,sc)
        al,sc=pop(T,83.6)
        if al>0:
            d=ImageDraw.Draw(lay); bw,bh=560,120; x0=(W-bw)/2; y0=1180
            pill=text_layer(); ImageDraw.Draw(pill).rounded_rectangle([x0,y0,x0+bw,y0+bh],60,fill=GOLD+(int(255*al),))
            lay.alpha_composite(pill)
            draw_c(lay,'+  SÍGUEME',F(MB,62),y0+bh/2,(15,15,15),al,shadow=False)
        al,_=pop(T,85.0); draw_c(lay,'Comenta "HOY" si empiezas ahora',F(MM,46),1400,(255,255,255),al)
    # end fade
    return

out=sys.stdout.buffer
NF=int(DUR*FPS)
start=int(sys.argv[1]) if len(sys.argv)>1 else 0
end=int(sys.argv[2]) if len(sys.argv)>2 else NF
for fi in range(start,end):
    T=fi/FPS
    i=next(k for k,s in enumerate(SH) if s[0]<=T<s[1]) if T<DUR else len(SH)-1
    fr=shot_frame(i,T)
    s,e,_,tr=SH[i]
    if tr=='xf' and T-s<XF and i>0:
        prev=shot_frame(i-1,T); fr=Image.blend(prev,fr,ease((T-s)/XF))
    a=np.asarray(fr,dtype=np.float32)
    if tr=='flash' and T-s<0.2: a=a+(255-a)*(1-(T-s)/0.2)*0.85
    if T>DUR-1.2: a*=max(0,(DUR-T)/1.2)
    fr=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA')
    lay=text_layer(); kinetic(lay,T); captions(lay,T)
    fr.alpha_composite(lay)
    if T>DUR-1.2:
        k=max(0,(DUR-T)/1.2); fr=Image.blend(Image.new('RGBA',(W,H),(0,0,0,255)),fr,k)
    out.write(fr.convert('RGB').tobytes())
