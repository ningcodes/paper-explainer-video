/* chrome.js — 全片统一的固定元素（风格卡 ④）：报纸栏目导航进度条 / 字幕条 / 麦色字幕底带 / 头像 / 章节翻页进场
   用法（scene.html 里）：
     <div id="stage"> <div id="content"> ...你的画面... </div> </div>
     <script src="../kit/timeline.js"></script> <script src="../kit/chrome.js"></script>
     CHROME.init({chapter:'04', steps:[...可选], band:t=>0..1, avDim:t=>0..1});
     function seek(t){ ...你的画面...; CHROME.seek(t); }
     window.READY = (async()=>{ await CHROME.ready(); ...你的加载...; seek(0); return true; })();
     window.CUES = CHROME.cues().concat(你的cues);   window.DURATION = CHROME.duration;
   所有时间都是本章局部时间 t（0 = 本章开始）。
   ?nochrome=1 时不画任何固定元素、不做翻页（用来导出本章最后一帧给下一章当翻页底图）。 */
(function(){
'use strict';
const TL = window.TIMELINE;
const Q = new URLSearchParams(location.search);
const NOCHROME = Q.has('nochrome');
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const p=(t,a,d)=>clamp((t-a)/d);
const eQ=x=>1-Math.pow(1-x,4);
const eIO=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const eBack=x=>{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);};
const fmt=s=>{s=Math.max(0,Math.floor(s));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');};
let cfg, CH, IDX, stage, content, bar, cap, capt, capBand, av, prevImg, shade, edge, avImgs=[], slots=[], stepEls=[], glob, tc, under;

const CSS=`
#stage{position:relative;width:1920px;height:1080px;overflow:hidden;background:#FFF1E5;color:#33302E;font-family:'Noto Sans CJK SC',sans-serif;-webkit-font-smoothing:antialiased;}
#content{position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:hidden;background:#FFF1E5;}
.chr{position:absolute;white-space:nowrap;}
#chr-bar{left:0;top:0;width:1920px;height:64px;background:#FFF1E5;z-index:50;}
#chr-bar .slot{position:absolute;top:0;height:62px;}
#chr-bar .n{position:absolute;top:20px;font-family:'Inter';font-weight:600;font-size:22px;font-feature-settings:'tnum' 1;letter-spacing:.04em;color:#66605C;}
#chr-bar .nm{position:absolute;top:16px;font-size:25px;color:#66605C;font-family:'Noto Sans CJK SC';}
#chr-bar .slot.on .n{color:#990F3D;font-weight:700;}
#chr-bar .slot.on .nm{font-family:'Noto Serif CJK SC',serif;font-weight:700;font-size:28px;top:13px;color:#990F3D;}
#chr-bar .slot.past .n,#chr-bar .slot.past .nm{color:#33302E;opacity:.82;}
#chr-bar .stp{position:absolute;top:18px;font-size:24px;color:#66605C;font-family:'Noto Sans CJK SC';}
#chr-bar .stp.on{color:#990F3D;font-weight:700;font-family:'Noto Serif CJK SC',serif;}
#chr-cap{left:0;top:958px;width:1660px;height:92px;z-index:40;}
#chr-capt{position:absolute;left:0;width:1660px;top:18px;text-align:center;font-family:'Noto Serif CJK SC',serif;font-weight:700;font-size:44px;line-height:56px;color:#33302E;white-space:nowrap;}
#chr-band{left:0;top:958px;width:1920px;height:122px;background:#F8E7D8;z-index:39;}
#chr-av{left:1670px;top:860px;height:220px;width:242px;z-index:60;}
#chr-prev{left:0;top:0;width:1920px;height:1080px;z-index:0;}
#chr-shade{left:0;top:0;width:1920px;height:1080px;background:#33302E;opacity:0;z-index:1;pointer-events:none;}
#chr-edge{top:0;width:60px;height:1080px;z-index:2;background:linear-gradient(90deg,rgba(51,48,46,0),rgba(51,48,46,.28));opacity:0;}
`;
function el(parent,tag,id,cls,css,html){const e=document.createElement(tag);if(id)e.id=id;if(cls)e.className=cls;if(css)e.style.cssText=css;if(html!=null)e.innerHTML=html;parent.appendChild(e);return e;}

function init(c){
  cfg=Object.assign({steps:null,band:null,avDim:null,prev:'prev.png',offset:0,length:null},c||{});
  IDX=TL.chapters.findIndex(x=>x.id===cfg.chapter); CH=TL.chapters[IDX];
  const st=document.createElement('style');st.textContent=CSS;document.head.appendChild(st);
  stage=document.getElementById('stage'); content=document.getElementById('content');
  content.style.zIndex=5;
  if(NOCHROME) return;
  if(IDX>0 && !cfg.offset){ prevImg=el(stage,'img','chr-prev','chr'); prevImg.src=cfg.prev; stage.insertBefore(prevImg,stage.firstChild);
             shade=el(stage,'div','chr-shade','chr'); stage.insertBefore(shade,content); edge=el(stage,'div','chr-edge','chr'); }
  capBand=el(stage,'div','chr-band','chr');
  cap=el(stage,'div','chr-cap','chr',null,
    '<div style="position:absolute;left:0;top:0;width:1660px;height:1px;background:#33302E"></div>'+
    '<div style="position:absolute;left:0;top:1px;width:1660px;height:91px;background:#FFF1E5"></div>'+
    '<div style="position:absolute;left:0;top:1px;width:1660px;height:91px;background:#F2DFCE;opacity:.55"></div>');
  capt=el(cap,'div','chr-capt');
  // ---- bar
  bar=el(stage,'div','chr-bar','chr');
  el(bar,'div',null,'chr','left:40px;top:12px;font-family:"Noto Serif CJK SC",serif;font-size:28px;font-weight:900;color:#33302E;letter-spacing:.02em','论文速读');
  el(bar,'div',null,'chr','left:176px;top:16px;width:1px;height:32px;background:#CCC1B7');
  let sx=206;
  TL.chapters.forEach((s,i)=>{const d=el(bar,'div',null,'slot'+(i===IDX?' on':i<IDX?' past':''),`left:${sx}px;width:130px`,
      `<span class="n" style="left:0">${s.id}</span><span class="nm" style="left:34px">${s.name}</span>`);slots.push({d,x:sx});sx+=124;});
  // under-line for current section: length = progress within the section
  under=el(bar,'div',null,'chr',`left:${slots[IDX].x+34}px;top:52px;height:4px;width:0;background:#990F3D`);
  if(cfg.steps){ let x=sx+18; el(bar,'div',null,'chr',`left:${x-14}px;top:18px;width:1px;height:28px;background:#CCC1B7`);
    cfg.steps.forEach((s,k)=>{const e=el(bar,'div',null,'stp','left:'+x+'px',s.label);stepEls.push(e);});
  }
  el(bar,'div',null,'chr','left:0;top:63px;width:1920px;height:1px;background:#33302E');
  glob=el(bar,'div',null,'chr','left:0;top:61px;height:3px;background:#990F3D');
  tc=el(bar,'div',null,'chr','left:1636px;top:18px;font-family:Inter;font-feature-settings:"tnum" 1;font-size:24px;font-weight:500;color:#66605C;width:244px;text-align:right');
  av=el(stage,'img','chr-av','chr');
}
function layoutSteps(t){
  if(!cfg.steps) return;
  // current step = last whose start<=t ; current shows "② 提两份改法", others show only numeral
  let cur=0; cfg.steps.forEach((s,k)=>{if(t>=s.start)cur=k;});
  let x=slots[slots.length-1].x+124+18;
  stepEls.forEach((e,k)=>{const s=cfg.steps[k];const on=k===cur;
    const txt=on?s.label:s.label.slice(0,1); if(e.dataset.t!==txt){e.textContent=txt;e.dataset.t=txt;}
    e.className='stp'+(on?' on':''); e.style.left=x+'px'; e.style.opacity=k<cur?0.9:on?1:0.6;
    x+=on?(txt.length*25+14):34;});
}
function seek(tl){
  if(NOCHROME){content.style.transform='';return;}
  const t0=tl; const t=tl+cfg.offset; const g=CH.start+t;
  // page flip in (first 0.6s)
  if(prevImg){const e=eIO(p(t0,0,0.6));
    content.style.transform=e<1?`translateX(${(1-e)*1920}px)`:'';
    content.style.boxShadow=e<1?'-30px 0 60px rgba(51,48,46,.22)':'';
    prevImg.style.transform=`translateX(${-e*480}px)`; prevImg.style.opacity=e<1?1:0;
    shade.style.opacity=e<1?0.18*e:0; shade.style.transform=`translateX(${-e*480}px)`;
  }
  // bar
  const local=clamp(t/CH.duration);
  under.style.width=(56*local)+'px';
  glob.style.width=(1920*g/TL.total)+'px';
  // section change pop (0.42s ease-out-back on current slot)
  const pe=eBack(p(t,0.15,0.42)); slots[IDX].d.style.transform=`translateY(${(1-pe)*-10}px)`; slots[IDX].d.style.opacity=clamp(pe*1.2);
  // teaser pulse on next slot in last 2s
  if(IDX<slots.length-1){const tp=p(t,CH.duration-2,2);const nd=slots[IDX+1].d;
    nd.style.transform=tp>0?`scale(${1+0.06*Math.sin(Math.PI*4*tp)*(tp<1?1:0)})`:'';}
  tc.innerHTML=`<span style="color:#33302E;font-weight:700">${fmt(g)}</span> / ${fmt(TL.total)}`;
  layoutSteps(t);
  // captions
  const S=CH.subs; let ci=-1; for(let i=0;i<S.length;i++){ if(t>=S[i].start-0.06) ci=i; }
  let show=ci>=0; if(show){const s=S[ci];const nxt=S[ci+1];const hold=nxt?Math.min(nxt.start-0.06, s.end+0.6):s.end+0.25; if(t>hold) show=false;}
  if(!show){capt.textContent='';capt.dataset.i='';capt.style.opacity=0;}
  else{const s=S[ci]; if(capt.dataset.i!==String(ci)){capt.textContent=s.text;capt.dataset.i=ci;}
    const e=eQ(p(t,s.start-0.06,0.22)); capt.style.opacity=e; capt.style.transform=`translateY(${(1-e)*8}px)`; capt.style.clipPath=`inset(0 0 ${(1-e)*30}% 0)`;}
  const bandV=cfg.band?clamp(cfg.band(t0)):0; capBand.style.opacity=bandV;
  // avatar
  const f=Math.round(g*30); av.src=avImgs[Math.floor(f*24/30)%242].src;
  {const v=cfg.avDim?clamp(cfg.avDim(t0)):0; const e=eIO(v); av.style.transform=`translateY(${e*250}px)`; av.style.opacity=v>=0.999?0:1;} // 作者 10-21：推近论文时头像整个下滑出画面，不做半透明
}
async function ready(){
  const ps=[];
  if(!NOCHROME){for(let i=0;i<242;i++){const im=new Image();im.src=`../kit/av/${String(i).padStart(3,'0')}.png`;avImgs.push(im);ps.push(im.decode().catch(()=>{}));}
    if(prevImg) ps.push(prevImg.decode().catch(()=>{}));}
  await Promise.all(ps);
  await Promise.all(["700 44px 'Noto Serif CJK SC'","900 28px 'Noto Serif CJK SC'","600 22px Inter","25px 'Noto Sans CJK SC'","500 24px Inter"].map(f=>document.fonts.load(f,'论文速读导读背景思路拆解进化结果存疑启示0123456789①②③④')));
  await document.fonts.ready;
}
function cues(){ if(IDX>0 && !cfg.offset && !NOCHROME) return [{t:0.04,type:'whoosh',d:0.55,soft:1},{t:0.1,type:'paper'}]; return []; }
window.CHROME={init,seek,ready,cues,get duration(){return cfg.length!=null?cfg.length:CH.duration;},get chapter(){return CH;},NOCHROME};
})();
