import json,re,subprocess,numpy as np,wave
SR=48000
vt={};[vt.__setitem__(*l.rstrip('\n').split('\t',1)) for l in open('script.txt',encoding='utf-8') if '\t' in l]
cuts=json.load(open('cuts.json'))
cuts['H01']=['h01',0.12,11.85]; cuts['H25']=['h25',0.13,10.26]
INS={'H01':[(10.58,0.35)],'H05':[(12.55,0.6)]}   # (time in src, extra silence)
CH=[('01','导读',['H01','H02']),('02','背景',['H03','H04','H05']),('03','思路',['H06','H07']),
    ('04','拆解',['H08','H09','H10','H11','H12','H13','H14','H15','H16','H17']),('05','进化',['H18']),
    ('06','结果',['H19','H20']),('07','存疑',['H21','H22']),('08','启示',['H23','H24','H25'])]
def load(n):
    with wave.open(f'src/{n}.wav') as w: return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
src={};asr={}
for n in set(c[0] for c in cuts.values()):
    src[n]=load(n); asr[n]=json.load(open(f'src/{n}.json'))['segs']
FILL=set('嗯啊呵是哎我不是。')
def isfill(s):
    t=re.sub(r'[。，？！\s]','',s['text']); return (len(t)<=2 and (s['e']-s['s'])<0.35) or t in ('','嗯','啊','呵','是','哎','我','不是')
def nchar(s):
    s=re.sub(r'[A-Za-z0-9.\-²]+','W',s); return len(re.sub(r'[\s，。？！：；、“”「」,.?!:;]','',s))
def para(h):
    n,a,b=cuts[h]; x=src[n]; a0=max(0,a-0.05); b0=min(len(x)/SR,b+0.08)
    seg=[dict(s=s['s']-a0,e=s['e']-a0,text=s['text']) for s in asr[n] if s['s']>=a-0.02 and s['e']<=b+0.02 and not isfill(s)]
    clip=x[int(a0*SR):int(b0*SR)].copy()
    for t,d in sorted(INS.get(h,[]),reverse=True):
        k=int((t-a0)*SR); clip=np.concatenate([clip[:k],np.zeros(int(d*SR),np.float32),clip[k:]])
        for s in seg:
            if s['s']>=t-a0: s['s']+=d; s['e']+=d
    # fade edges
    f=int(0.01*SR); clip[:f]*=np.linspace(0,1,f); clip[-f:]*=np.linspace(1,0,f)
    return clip,seg
def wid(s):
    w=0
    for ch in s:
        if ch.isspace(): w+=0.3
        elif ord(ch)<128: w+=0.55
        else: w+=1
    return w
def splitlong(u):
    if wid(u)<=21: return [u]
    # split near middle at a space or CJK boundary
    best=None
    for i in range(1,len(u)):
        a,b=u[:i],u[i:]
        if u[i-1].isascii() and u[i].isascii() and u[i]!=' ' and u[i-1]!=' ': continue
        sc=abs(wid(a)-wid(b))
        if best is None or sc<best[0]: best=(sc,i)
    i=best[1]; return splitlong(u[:i].strip())+splitlong(u[i:].strip())
def units(text):
    parts=[p.strip() for p in re.findall(r'[^，。？！；：]+[，。？！；：]?',text)]
    out=[];cur=''
    for p in parts:
        if cur and (wid(cur+p)>15 or cur[-1] in '。？！'): out.append(cur);cur=p
        else: cur+=p
    if cur: out.append(cur)
    res=[]
    for u in out: res+=splitlong(u)
    return res
def align(text,seg):
    us=units(text); tot=sum(nchar(u) for u in us)
    sl=[nchar(s['text']) or 1 for s in seg]; st=sum(sl)
    # map fraction->time across speech segs
    def tm(f):
        acc=0
        for s,l in zip(seg,sl):
            if acc+l/st>=f-1e-9: return s['s']+(f-acc)/(l/st)*(s['e']-s['s'])
            acc+=l/st
        return seg[-1]['e']
    bnd=sorted([s['s'] for s in seg]+[s['e'] for s in seg])
    def snap(t,which):
        c=[s['s'] for s in seg] if which=='s' else [s['e'] for s in seg]
        b=min(c,key=lambda v:abs(v-t)); return b if abs(b-t)<0.5 else t
    res=[];acc=0
    for u in us:
        f0=acc/tot; acc+=nchar(u); f1=acc/tot
        res.append(dict(text=re.sub(r'[，。；：]$','',u),s=round(snap(tm(f0),'s'),3),e=round(snap(tm(f1),'e'),3)))
    for i in range(1,len(res)):
        if res[i]['s']<res[i-1]['e']: res[i]['s']=res[i-1]['e']
    return res
out={'fps':30,'chapters':[]}; full=[]; T=0.0
GAP=0.7
for ci,(cid,name,hs) in enumerate(CH):
    lead=0.5 if ci==0 else 0.6; tail=3.0 if ci==len(CH)-1 else 0.6
    buf=[np.zeros(int(lead*SR),np.float32)]; t=lead; paras=[]; subs=[]
    for j,h in enumerate(hs):
        clip,seg=para(h)
        if j>0: buf.append(np.zeros(int(GAP*SR),np.float32)); t+=GAP
        d=len(clip)/SR
        paras.append(dict(id=h,start=round(t,3),end=round(t+d,3),text=vt[h]))
        for u in align(vt[h],seg): subs.append(dict(id=h,text=u['text'],start=round(t+u['s'],3),end=round(t+u['e'],3)))
        buf.append(clip); t+=d
    t+=tail; nf=int(np.ceil(t*30)); dur=nf/30
    a=np.concatenate(buf); a=np.concatenate([a,np.zeros(int(dur*SR)-len(a),np.float32)])
    with wave.open(f'ch{cid}.wav','w') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(a,-1,1)*32767).astype(np.int16).tobytes())
    out['chapters'].append(dict(id=cid,name=name,start=round(T,4),duration=round(dur,4),frames=nf,paras=paras,subs=subs))
    full.append(a); T+=dur
A=np.concatenate(full)
with wave.open('voice_full.wav','w') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(A,-1,1)*32767).astype(np.int16).tobytes())
out['total']=round(T,4)
json.dump(out,open('timeline.json','w'),ensure_ascii=False,indent=1)
for c in out['chapters']: print(c['id'],c['name'],c['start'],c['duration'],c['frames'],len(c['subs']))
print('total',T)
