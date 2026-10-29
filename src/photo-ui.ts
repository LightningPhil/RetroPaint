import { bus, emit } from './bus';
import { eventPos, H, view, W } from './canvas';
import { activeLayer } from './layers';
import { autoPhoto, autoWhiteBalance, cropPixels, curveTable, defaultPhotoSettings, histogram, neutralBalance, processPhoto, type CropBox, type CurveChannel, type CurvePoint, type PhotoSettings } from './photo-engine';
import { setPhotoGuides } from './photo-guides';
import { applyPhoto, beginPhoto, cancelPhoto, comparePhoto, photoSession, refreshPhoto } from './photo-session';
import { icon } from './icons';
import { expandPhotoFrame } from './document-frame';
import { choosePhotoLook, newPhotoRecipe, photoManualChange, PHOTO_LOOKS, type PhotoRecipe } from './photo-recipe';
import { advancedEnabled } from './advanced-mode';
import { state } from './state';

interface Actions { editable:()=>boolean; settle:()=>void; message:(text:string)=>void; open:()=>void }
type Category='light'|'colour'|'curves'|'detail'|'effects'|'geometry';
type NumberKey={ [K in keyof PhotoSettings]:PhotoSettings[K] extends number?K:never }[keyof PhotoSettings];
interface Slider { key:NumberKey; label:string; min:number; max:number; step?:number; unit?:string }
interface Group { id:string; category:Category; label:string; sliders:Slider[]; hint?:string }
const slider=(key:NumberKey,label:string,min=-100,max=100,step=1,unit=''):Slider=>({key,label,min,max,step,unit});
const groups:Group[]=[
  {id:'light-basic',category:'light',label:'Exposure & contrast',sliders:[slider('exposure','Exposure',-4,4,.05,' EV'),slider('brightness','Brightness'),slider('contrast','Contrast')]},
  {id:'light-tone',category:'light',label:'Highlights & shadows',sliders:[slider('highlights','Highlights'),slider('shadows','Shadows'),slider('whites','Whites'),slider('blacks','Blacks')]},
  {id:'colour-balance',category:'colour',label:'White balance',sliders:[slider('temperature','Temperature · cool / warm'),slider('tint','Tint · green / magenta')]},
  {id:'colour-basic',category:'colour',label:'Colour intensity',sliders:[slider('saturation','Saturation'),slider('vibrance','Vibrance'),slider('hue','Hue',-180,180,1,'°')]},
  {id:'colour-mixer',category:'colour',label:'Colour mixer · HSL',sliders:[]},
  {id:'curves',category:'curves',label:'Tone curves',sliders:[]},
  {id:'detail-presence',category:'detail',label:'Pop & presence',sliders:[slider('pop','Pop',0,100),slider('clarity','Clarity'),slider('texture','Texture'),slider('dehaze','Dehaze')],hint:'Pop blends local contrast, vibrance and dehaze.'},
  {id:'detail-sharp',category:'detail',label:'Sharpening',sliders:[slider('sharpness','Sharpness',0,150),slider('radius','Radius',.5,3,.1,' px'),slider('threshold','Threshold · protect smooth areas',0,32)]},
  {id:'detail-noise',category:'detail',label:'Noise reduction',sliders:[slider('noise','Luminance noise',0,100),slider('colourNoise','Colour noise',0,100)],hint:'Smooth small speckles while protecting stronger edges.'},
  {id:'effects-vignette',category:'effects',label:'Vignette',sliders:[slider('vignette','Vignette · dark / light'),slider('midpoint','Midpoint',0,100),slider('feather','Feather',0,100),slider('roundness','Roundness',0,100)]},
  {id:'effects-grain',category:'effects',label:'Film grain',sliders:[slider('grain','Amount',0,100),slider('grainSize','Size',.5,3,.1),slider('grainRoughness','Roughness',0,100)],hint:'Fine silver-like texture. Size sets the clumps; roughness varies their structure.'},
  {id:'geometry-crop',category:'geometry',label:'Crop & alignment grid',sliders:[],hint:'Drag a box on the paper or small preview. Move it from inside; resize with yellow corners. Crop trims every layer.'},
  {id:'geometry-align',category:'geometry',label:'Straighten & flip',sliders:[slider('angle','Straighten',-45,45,.1,'°'),slider('zoom','Scale · fill clear edges',50,200,1,'%')],hint:'Alignment moves this layer inside the existing frame.'},
  {id:'geometry-perspective',category:'geometry',label:'Perspective',sliders:[slider('vertical','Vertical perspective',-75,75),slider('horizontal','Horizontal perspective',-75,75)],hint:'Use the grid to make buildings and horizons look straight.'},
  {id:'geometry-lens',category:'geometry',label:'Lens correction',sliders:[slider('distortion','Barrel / pincushion'),slider('aberration','Red / blue fringe alignment')],hint:'Manual corrections for this layer; no camera or lens profile is required.'},
];
const colours=['Red','Orange','Yellow','Green','Aqua','Blue','Purple','Magenta'];
const shortPhoto=matchMedia('(max-height:550px)');
const categoryNames:Record<Category,string>={light:'Light',colour:'Colour',curves:'Curves',detail:'Detail',effects:'Effects',geometry:'Geometry'};
const field=<T extends HTMLElement=HTMLElement>(id:string)=>document.getElementById(id) as T;
let actions:Actions,category:Category='light',group='light-basic',channel:CurveChannel='rgb',point=0,mixColour=0,cropRatio=0,picking=false,horizon=false,curvePointer:number|null=null;
let cropDrag:{id:number;kind:string;start:{x:number;y:number};box:CropBox}|null=null;
let restoreLayers=false,pendingImport=false,importDraft:PhotoRecipe|null=null;
const clamp=(v:number,min=0,max=1)=>Math.max(min,Math.min(max,v));
function changed(manual=true):void{ if(manual&&photoSession)photoManualChange(photoSession);picking=false;horizon=false;syncGuides();syncValues();void refreshPhoto(); }
function sliderMarkup(s:Slider,key:string=s.key,value?:number):string{
  return `<label class="photo-slider"><span>${s.label}<output data-photo-output="${key}">${value??0}${s.unit||''}</output></span><input type="range" data-photo-value="${key}" aria-label="${s.label}" min="${s.min}" max="${s.max}" step="${s.step??1}" value="${value??0}"></label>`;
}
function syncValues():void{
  const session=photoSession;if(!session)return;
  field<HTMLSelectElement>('photoLook').value=session.look;
  for(const input of field('photoControls').querySelectorAll<HTMLInputElement>('[data-photo-value]')){
    const key=input.dataset.photoValue!,mix=key.startsWith('mix-'),value=mix?session.settings.mixer[mixColour][key.slice(4) as 'hue'|'saturation'|'luminance']:session.settings[key as NumberKey];
    input.value=String(value);const spec=groups.flatMap(g=>g.sliders).find(s=>s.key===key);
    field('photoControls').querySelector<HTMLOutputElement>(`[data-photo-output="${key}"]`)!.value=`${Number(value.toFixed(2))}${spec?.unit||''}`;
  }
  for(const key of ['flipX','flipY'] as const)field('photoControls').querySelector(`[data-photo-flip="${key}"]`)?.setAttribute('aria-pressed',String(session.settings[key]));
  const crop=cropPixels(session.settings.crop,W,H);
  for(const key of ['x','y','width','height'] as const){const input=field<HTMLInputElement>(`photoCrop-${key}`);if(input&&document.activeElement!==input)input.value=String(crop[key]);}
  const p=session.settings.curves[channel][point];if(p){for(const key of ['x','y'] as const){const input=field<HTMLInputElement>(`curve-${key}`);if(input)input.value=String(Math.round(p[key]*255));}}
  drawCurve();
}
function syncGuides():void{
  const session=photoSession;if(!session){setPhotoGuides(null);return;}
  expandPhotoFrame(category==='geometry');
  const c=session.settings.crop,show=category==='geometry'||c.x>0||c.y>0||c.width<1||c.height<1;
  setPhotoGuides(show?c:null);view.classList.toggle('photo-picking',picking||horizon);
}
function updateStatus():void{
  const s=photoSession;if(!s)return;
  field('photoTarget').textContent=`Editing ${s.name}`;
  field('photoStatus').textContent=s.applying?'Saving editable adjustments…':picking?'Tap a neutral patch on the paper or preview.':horizon?'Drag along a line that should be level.':s.compare?'Before · original pixels':s.rendered!==s.revision?'Updating preview…':'Original kept · reopen to change any adjustment';
  field('photoStatus').setAttribute('aria-busy',String(s.applying||s.rendered!==s.revision));
  field('photoCompare').setAttribute('aria-pressed',String(s.compare));field('photoCompare').textContent=s.compare?'After':'Before';
  for(const id of ['photoApply','photoReset','photoCompare','photoOpen'])field<HTMLButtonElement>(id).disabled=s.applying;
  field<HTMLSelectElement>('photoLook').disabled=s.applying;
  field('photoControls').inert=s.applying;field('photoTabs').inert=s.applying;field('photoGroupRow').inert=s.applying;
  const src=s.compare?s.source:s.preview,mini=field<HTMLCanvasElement>('photoMiniCanvas'),ctx=mini.getContext('2d')!;
  ctx.clearRect(0,0,mini.width,mini.height);const scale=Math.min(mini.width/src.width,mini.height/src.height),w=src.width*scale,h=src.height*scale,x=(mini.width-w)/2,y=(mini.height-h)/2;
  ctx.drawImage(src,x,y,w,h);const crop=s.settings.crop;
  if(category==='geometry'||crop.width<1||crop.height<1){
    const xx=x+crop.x*w,yy=y+crop.y*h,ww=crop.width*w,hh=crop.height*h;
    ctx.fillStyle='#18223766';ctx.beginPath();ctx.rect(x,y,w,h);ctx.rect(xx,yy,ww,hh);ctx.fill('evenodd');
    ctx.strokeStyle='#ffd16f';ctx.lineWidth=2;ctx.strokeRect(xx,yy,ww,hh);
    ctx.fillStyle='#ffd16f';for(const [px,py] of [[xx,yy],[xx+ww,yy],[xx,yy+hh],[xx+ww,yy+hh]])ctx.fillRect(px-4,py-4,8,8);
  }
  const data=(s.compare?s.small:s.preview.getContext('2d')!.getImageData(0,0,s.preview.width,s.preview.height)),hist=histogram(data),canvas=field<HTMLCanvasElement>('photoHistogram'),hc=canvas.getContext('2d')!;
  hc.clearRect(0,0,canvas.width,canvas.height);const max=Math.max(1,...hist.rgb.flat().map(Math.sqrt));
  for(let c=0;c<3;c++){hc.fillStyle=['#df557b80','#399c7a80','#6b81d980'][c];hc.beginPath();hc.moveTo(0,canvas.height);for(let x=0;x<256;x++)hc.lineTo(x/255*canvas.width,canvas.height-Math.sqrt(hist.rgb[c][x])/max*canvas.height);hc.lineTo(canvas.width,canvas.height);hc.closePath();hc.fill();}
  canvas.setAttribute('aria-label',`RGB histogram. ${Math.round(hist.clipped[0]*100)}% shadow clipping; ${Math.round(hist.clipped[1]*100)}% highlight clipping.`);canvas.title=canvas.getAttribute('aria-label')!;
}
function buildControls():void{
  const session=photoSession;if(!session)return;const selected=groups.find(g=>g.id===group)!,container=field('photoControls');
  container.classList.toggle('photo-curves-controls',group==='curves');
  container.innerHTML=selected.sliders.map(s=>sliderMarkup(s,s.key,session.settings[s.key])).join('');
  if(group==='light-basic')container.insertAdjacentHTML('beforeend','<div class="photo-action-row"><button class="choice" id="photoAuto">✨ Auto light</button></div>');
  if(group==='colour-balance')container.insertAdjacentHTML('beforeend','<div class="photo-action-row"><button class="choice" id="photoAutoBalance">Auto WB</button><button class="choice" id="photoNeutral">💉 Pick neutral</button></div><p class="photo-hint">Temperature and tint are relative to your image. Pick a grey patch for a neutral starting point.</p>');
  if(group==='colour-mixer')container.innerHTML=`<select id="photoMixColour" aria-label="Colour range">${colours.map((c,i)=>`<option value="${i}" ${i===mixColour?'selected':''}>${c}</option>`).join('')}</select>`+['hue','saturation','luminance'].map((k,i)=>sliderMarkup(slider('hue',['Hue','Saturation','Luminance'][i],i? -100:-60,i?100:60),`mix-${k}`,session.settings.mixer[mixColour][k as 'hue'])).join('');
  if(group==='curves'){
    const options=['rgb','red','green','blue'].map(c=>`<option value="${c}" ${c===channel?'selected':''}>${c==='rgb'?'RGB · all channels':c[0].toUpperCase()+c.slice(1)}</option>`).join('');
    container.innerHTML=`<div class="photo-action-row"><select id="photoCurveChannel" aria-label="Curve channel">${options}</select><select id="photoCurvePreset" aria-label="Curve preset"><option value="">Curve preset…</option value="linear">Linear</option><option value="contrast">Gentle S</option><option value="fade">Faded blacks</option><option value="shadows">Lift shadows</option></select></div><canvas id="photoCurve" width="512" height="240" tabindex="0" role="application" aria-label="Tone curve. Tap to add points; drag to adjust. Arrow keys adjust the selected point; Delete removes it."></canvas><div class="photo-curve-fields"><label>Input<input id="curve-x" type="number" min="0" max="255" aria-label="Curve input"></label><label>Output<input id="curve-y" type="number" min="0" max="255" aria-label="Curve output"></label><button class="choice" id="photoCurveRemove">Remove point</button></div>`;
  }
  if(group==='geometry-crop'){
    container.innerHTML=`<select id="photoCropRatio" aria-label="Crop aspect ratio">${[['0','Free crop'],[String(W/H),'Original ratio'],['1','Square · 1:1'],['1.333333','4:3'],['1.5','3:2'],['1.777778','16:9'],['0.5625','9:16'],['0.8','4:5']].map(([value,label])=>`<option value="${value}" ${Number(value)===cropRatio?'selected':''}>${label}</option>`).join('')}</select><div class="photo-crop-fields">${(['x','y','width','height'] as const).map(k=>`<label>${({x:'Left',y:'Top',width:'Width',height:'Height'})[k]}<input type="number" id="photoCrop-${k}" aria-label="Crop ${k}" min="${k==='width'||k==='height'?1:0}"></label>`).join('')}</div><button class="choice" id="photoCropReset">Use whole picture</button>`;
  }
  if(group==='geometry-align')container.insertAdjacentHTML('beforeend','<div class="photo-action-row"><button class="choice" data-photo-flip="flipX" aria-pressed="false">Flip ↔</button><button class="choice" data-photo-flip="flipY" aria-pressed="false">Flip ↕</button><button class="choice" id="photoHorizon">Draw horizon</button></div>');
  if(selected.hint)container.insertAdjacentHTML('beforeend',`<p class="photo-hint">${selected.hint}</p>`);
  for(const input of container.querySelectorAll<HTMLInputElement>('[data-photo-value]')){
    input.addEventListener('input',()=>{const key=input.dataset.photoValue!,value=Number(input.value);if(key.startsWith('mix-'))Object.assign(session.settings.mixer[mixColour],{[key.slice(4)]:value});else Object.assign(session.settings,{[key]:value});changed();});
    input.addEventListener('dblclick',()=>{const key=input.dataset.photoValue!;if(key.startsWith('mix-'))Object.assign(session.settings.mixer[mixColour],{[key.slice(4)]:0});else Object.assign(session.settings,{[key]:defaultPhotoSettings()[key as NumberKey]});changed();});
  }
  field('photoAuto')?.addEventListener('click',()=>{Object.assign(session.settings,autoPhoto(session.small));changed();});
  field('photoAutoBalance')?.addEventListener('click',()=>{session.settings.balance=autoWhiteBalance(session.small);session.settings.temperature=session.settings.tint=0;changed();});
  field('photoNeutral')?.addEventListener('click',()=>{picking=!picking;horizon=false;syncGuides();updateStatus();});
  field('photoHorizon')?.addEventListener('click',()=>{horizon=!horizon;picking=false;syncGuides();updateStatus();});
  container.querySelectorAll<HTMLButtonElement>('[data-photo-flip]').forEach(button=>button.addEventListener('click',()=>{const key=button.dataset.photoFlip as 'flipX'|'flipY';session.settings[key]=!session.settings[key];changed();}));
  field<HTMLSelectElement>('photoMixColour')?.addEventListener('change',event=>{mixColour=Number((event.target as HTMLSelectElement).value);syncValues();});
  bindCurves();bindCrop();syncValues();syncGuides();updateStatus();
}
function selectCategory(value:Category):void{
  category=value;group=groups.find(g=>g.category===category)!.id;picking=horizon=false;
  const select=field<HTMLSelectElement>('photoGroup');
  select.innerHTML=shortPhoto.matches?Object.entries(categoryNames).map(([id,label])=>`<optgroup label="${label}">${groups.filter(g=>g.category===id).map(g=>`<option value="${g.id}">${g.label}</option>`).join('')}</optgroup>`).join(''):groups.filter(g=>g.category===category).map(g=>`<option value="${g.id}">${g.label}</option>`).join('');
  select.value=group;
  for(const button of field('photoTabs').querySelectorAll<HTMLElement>('[data-photo-category]'))button.setAttribute('aria-pressed',String(button.dataset.photoCategory===category));
  buildControls();
}
function resetGroup():void{
  if(!photoSession)return;const defaults=defaultPhotoSettings(),settings=photoSession.settings;
  for(const s of groups.find(g=>g.id===group)!.sliders)Object.assign(settings,{[s.key]:defaults[s.key]});
  if(group==='colour-balance')settings.balance=[1,1,1];
  if(group==='colour-mixer')settings.mixer[mixColour]={hue:0,saturation:0,luminance:0};
  if(group==='curves'){settings.curves[channel]=defaults.curves[channel];point=0;}
  if(group==='geometry-crop'){settings.crop=defaults.crop;cropRatio=0;}
  if(group==='geometry-align')settings.flipX=settings.flipY=false;
  buildControls();changed();
}
function drawCurve():void{
  const canvas=field<HTMLCanvasElement>('photoCurve'),session=photoSession;if(!canvas||!session)return;
  const ctx=canvas.getContext('2d')!,w=canvas.width,h=canvas.height,points=session.settings.curves[channel],table=curveTable(points),hist=histogram(session.small),c=channel==='red'?0:channel==='green'?1:2,bins=channel==='rgb'?hist.rgb[0].map((v,i)=>v+hist.rgb[1][i]+hist.rgb[2][i]):hist.rgb[c],max=Math.max(1,...bins);
  ctx.fillStyle='#f2f0f7';ctx.fillRect(0,0,w,h);ctx.fillStyle='#cfc9dd';ctx.beginPath();ctx.moveTo(0,h);bins.forEach((n,i)=>ctx.lineTo(i/255*w,h-Math.sqrt(n/max)*h*.8));ctx.lineTo(w,h);ctx.fill();
  ctx.strokeStyle='#d5cfe0';ctx.lineWidth=1;for(let i=1;i<4;i++){ctx.beginPath();ctx.moveTo(w*i/4,0);ctx.lineTo(w*i/4,h);ctx.moveTo(0,h*i/4);ctx.lineTo(w,h*i/4);ctx.stroke();}
  ctx.strokeStyle='#aaa3b7';ctx.setLineDash([5,5]);ctx.beginPath();ctx.moveTo(0,h);ctx.lineTo(w,0);ctx.stroke();ctx.setLineDash([]);
  ctx.strokeStyle=({rgb:'#7952b8',red:'#d34463',green:'#258469',blue:'#4268c1'})[channel];ctx.lineWidth=4;ctx.beginPath();table.forEach((v,i)=>i?ctx.lineTo(i/255*w,(1-v)*h):ctx.moveTo(0,(1-v)*h));ctx.stroke();
  points.forEach((p,i)=>{ctx.beginPath();ctx.arc(clamp(p.x*w,7,w-7),clamp((1-p.y)*h,7,h-7),i===point?8:6,0,Math.PI*2);ctx.fillStyle=i===point?'#ffd16f':'#fff';ctx.fill();ctx.stroke();});
  const remove=field<HTMLButtonElement>('photoCurveRemove');if(remove)remove.disabled=point===0||point===points.length-1;
  const input=field<HTMLInputElement>('curve-x');if(input)input.disabled=point===0||point===points.length-1;
}
function moveCurve(x:number,y:number):void{
  const points=photoSession!.settings.curves[channel],p=points[point];p.x=point===0?0:point===points.length-1?1:clamp(x,points[point-1].x+1/255,points[point+1].x-1/255);p.y=clamp(y);changed();
}
function bindCurves():void{
  const canvas=field<HTMLCanvasElement>('photoCurve');if(!canvas)return;
  field<HTMLSelectElement>('photoCurveChannel').addEventListener('change',event=>{channel=(event.target as HTMLSelectElement).value as CurveChannel;point=0;syncValues();});
  field<HTMLSelectElement>('photoCurvePreset').addEventListener('change',event=>{
    const value=(event.target as HTMLSelectElement).value,presets:Record<string,CurvePoint[]>={linear:[{x:0,y:0},{x:1,y:1}],contrast:[{x:0,y:0},{x:.25,y:.18},{x:.75,y:.82},{x:1,y:1}],fade:[{x:0,y:.12},{x:.5,y:.5},{x:1,y:.95}],shadows:[{x:0,y:0},{x:.25,y:.38},{x:1,y:1}]};
    if(presets[value]){photoSession!.settings.curves[channel]=presets[value];point=0;changed();}
  });
  const remove=()=>{const points=photoSession!.settings.curves[channel];if(point>0&&point<points.length-1){points.splice(point,1);point--;changed();}};
  field('photoCurveRemove').addEventListener('click',remove);
  for(const key of ['x','y'] as const)field<HTMLInputElement>(`curve-${key}`).addEventListener('change',event=>{const p=photoSession!.settings.curves[channel][point],value=Number((event.target as HTMLInputElement).value)/255;moveCurve(key==='x'?value:p.x,key==='y'?value:p.y);});
  const position=(e:PointerEvent)=>{const r=canvas.getBoundingClientRect();return {x:clamp((e.clientX-r.left)/r.width),y:1-clamp((e.clientY-r.top)/r.height)};};
  canvas.addEventListener('pointerdown',event=>{
    if(event.button!==0)return;event.preventDefault();canvas.focus();const p=position(event),points=photoSession!.settings.curves[channel];
    let nearest=0,distance=Infinity;points.forEach((v,i)=>{const d=Math.hypot((v.x-p.x)*canvas.clientWidth,(v.y-p.y)*canvas.clientHeight);if(d<distance){distance=d;nearest=i;}});
    if(distance>14&&points.length<12&&p.x>1/255&&p.x<254/255&&!points.some(v=>Math.abs(v.x-p.x)<2/255)){points.push(p);points.sort((a,b)=>a.x-b.x);point=points.indexOf(p);changed();}else{point=nearest;syncValues();}
    curvePointer=event.pointerId;canvas.setPointerCapture(event.pointerId);
  });
  canvas.addEventListener('pointermove',event=>{if(event.pointerId===curvePointer){const p=position(event);moveCurve(p.x,p.y);}});
  const stop=()=>{curvePointer=null;};for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,stop);
  canvas.addEventListener('keydown',event=>{const p=photoSession!.settings.curves[channel][point],step=(event.shiftKey?10:1)/255;if(['Delete','Backspace'].includes(event.key)){event.preventDefault();remove();}else if(event.key.startsWith('Arrow')){event.preventDefault();event.stopPropagation();moveCurve(p.x+(event.key==='ArrowRight'?step:event.key==='ArrowLeft'?-step:0),p.y+(event.key==='ArrowUp'?step:event.key==='ArrowDown'?-step:0));}});
}
function ratioCrop(box:CropBox):CropBox{
  if(!cropRatio)return box;const ratio=cropRatio*H/W;let width=box.width,height=width/ratio;
  if(height>box.height){height=box.height;width=height*ratio;}
  return {x:box.x+(box.width-width)/2,y:box.y+(box.height-height)/2,width,height};
}
function bindCrop():void{
  field<HTMLSelectElement>('photoCropRatio')?.addEventListener('change',event=>{cropRatio=Number((event.target as HTMLSelectElement).value);photoSession!.settings.crop=ratioCrop(photoSession!.settings.crop);changed();});
  field('photoCropReset')?.addEventListener('click',()=>{photoSession!.settings.crop=ratioCrop({x:0,y:0,width:1,height:1});changed();});
  for(const key of ['x','y','width','height'] as const)field<HTMLInputElement>(`photoCrop-${key}`)?.addEventListener('change',event=>{
    const c=photoSession!.settings.crop,value=Number((event.target as HTMLInputElement).value)/(key==='x'||key==='width'?W:H);
    if(!Number.isFinite(value)){syncValues();return;}
    if(key==='x')c.x=clamp(value,0,1-c.width);else if(key==='y')c.y=clamp(value,0,1-c.height);
    else if(key==='width'){c.width=clamp(value,1/W,1-c.x);if(cropRatio){c.height=Math.min(c.width/(cropRatio*H/W),1-c.y);c.width=c.height*cropRatio*H/W;}}
    else{c.height=clamp(value,1/H,1-c.y);if(cropRatio){c.width=Math.min(c.height*cropRatio*H/W,1-c.x);c.height=c.width/(cropRatio*H/W);}}
    changed();
  });
}
function bindPaper():void{
  for(const target of [view,field<HTMLCanvasElement>('photoMiniCanvas')]){
  const pos=(event:PointerEvent)=>{
    if(target===view){const p=eventPos(event);return {x:clamp(p.x/W),y:clamp(p.y/H)};}
    const r=target.getBoundingClientRect(),scale=Math.min(r.width/W,r.height/H);
    return {x:clamp((event.clientX-r.left-(r.width-W*scale)/2)/(W*scale)),y:clamp((event.clientY-r.top-(r.height-H*scale)/2)/(H*scale))};
  };
  target.addEventListener('pointerdown',event=>{
    const session=photoSession;if(!session||field('canvasSlot').classList.contains('moving-paper'))return;
    event.stopImmediatePropagation();event.preventDefault();if(session.applying||event.button!==0)return;
    const p=pos(event);
    if(picking){
      const neutral=defaultPhotoSettings();for(const k of ['distortion','aberration','vertical','horizontal','angle','zoom','flipX','flipY'] as const)Object.assign(neutral,{[k]:session.settings[k]});
      const image=processPhoto(session.small,neutral),x=Math.min(image.width-1,Math.floor(p.x*image.width)),y=Math.min(image.height-1,Math.floor(p.y*image.height)),sum=[0,0,0];let count=0;
      for(let yy=Math.max(0,y-2);yy<=Math.min(image.height-1,y+2);yy++)for(let xx=Math.max(0,x-2);xx<=Math.min(image.width-1,x+2);xx++){const i=(yy*image.width+xx)*4;if(image.data[i+3]<128)continue;count++;for(let c=0;c<3;c++)sum[c]+=image.data[i+c];}
      if(!count){actions.message('Choose a painted grey or white area.');return;}
      session.settings.balance=neutralBalance(sum.map(n=>n/count));session.settings.temperature=session.settings.tint=0;changed();return;
    }
    if(!horizon&&group!=='geometry-crop')return;
    const box={...session.settings.crop},r=target.getBoundingClientRect(),scale=Math.min(r.width/W,r.height/H);let kind=horizon?'horizon':'new';
    if(!horizon){for(const [key,x,y] of [['nw',box.x,box.y],['ne',box.x+box.width,box.y],['sw',box.x,box.y+box.height],['se',box.x+box.width,box.y+box.height]] as const)if(Math.hypot((p.x-x)*W*scale,(p.y-y)*H*scale)<16)kind=key;
      if(kind==='new'&&p.x>box.x&&p.x<box.x+box.width&&p.y>box.y&&p.y<box.y+box.height&&(box.width<.999||box.height<.999))kind='move';}
    cropDrag={id:event.pointerId,kind,start:p,box};target.setPointerCapture(event.pointerId);
  },true);
  target.addEventListener('pointermove',event=>{
    if(!photoSession||field('canvasSlot').classList.contains('moving-paper'))return;event.stopImmediatePropagation();if(!cropDrag||event.pointerId!==cropDrag.id)return;
    const p=pos(event),d=cropDrag,b=d.box;
    if(d.kind==='horizon'){
      setPhotoGuides(photoSession.settings.crop,{x:d.start.x*W,y:d.start.y*H,xx:p.x*W,yy:p.y*H});updateStatus();
      const mini=field<HTMLCanvasElement>('photoMiniCanvas'),ctx=mini.getContext('2d')!,scale=Math.min(mini.width/W,mini.height/H),x=(mini.width-W*scale)/2,y=(mini.height-H*scale)/2;
      ctx.strokeStyle='#ffd16f';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(x+d.start.x*W*scale,y+d.start.y*H*scale);ctx.lineTo(x+p.x*W*scale,y+p.y*H*scale);ctx.stroke();return;
    }
    if(d.kind==='move')photoSession.settings.crop={...b,x:clamp(b.x+p.x-d.start.x,0,1-b.width),y:clamp(b.y+p.y-d.start.y,0,1-b.height)};
    else{
      const anchor=d.kind==='new'?d.start:{x:d.kind.includes('w')?b.x+b.width:b.x,y:d.kind.includes('n')?b.y+b.height:b.y};
      let dx=p.x-anchor.x,dy=p.y-anchor.y;
      if(cropRatio){const ratio=cropRatio*H/W;if(Math.abs(dx/dy)>ratio)dy=Math.sign(dy||1)*Math.abs(dx)/ratio;else dx=Math.sign(dx||1)*Math.abs(dy)*ratio;const scale=Math.min(1,dx>0?(1-anchor.x)/dx:-anchor.x/dx,dy>0?(1-anchor.y)/dy:-anchor.y/dy);dx*=scale;dy*=scale;}
      if(Math.abs(dx)>1/W&&Math.abs(dy)>1/H)photoSession.settings.crop={x:Math.min(anchor.x,anchor.x+dx),y:Math.min(anchor.y,anchor.y+dy),width:Math.abs(dx),height:Math.abs(dy)};
    }
    syncValues();syncGuides();updateStatus();
  },true);
  const stop=(event:PointerEvent)=>{
    if(!photoSession||!cropDrag||event.pointerId!==cropDrag.id)return;event.stopImmediatePropagation();
    const d=cropDrag;cropDrag=null;
    if(event.type==='pointercancel')photoSession.settings.crop=d.box;
    else if(d.kind==='horizon'){const p=pos(event),dx=(p.x-d.start.x)*W,dy=(p.y-d.start.y)*H;if(Math.hypot(dx,dy)>8){let angle=Math.atan2(dy,dx)*180/Math.PI;if(angle>90)angle-=180;if(angle< -90)angle+=180;photoSession.settings.angle=Math.round(clamp(-angle,-45,45)*10)/10;}}
    changed();
  };
  target.addEventListener('pointerup',stop,true);target.addEventListener('pointercancel',stop,true);target.addEventListener('lostpointercapture',stop,true);
  }
}
function lockDrawing(locked:boolean):void{for(const id of ['bottomTray','layersPanel'])field(id).inert=locked;for(const button of field('toolBin').querySelectorAll<HTMLButtonElement>('button:not(.advanced-tool)'))button.disabled=locked;field('canvasSlot').classList.toggle('editing-photo',locked);}
export function initPhotoUi(callbacks:Actions):void{
  actions=callbacks;
  const panel=document.createElement('aside');panel.id='photoPanel';panel.hidden=true;panel.setAttribute('aria-labelledby','photoTitle');
  panel.innerHTML=`<header class="photo-heading"><strong id="photoTitle">📸 Photo lab</strong><button type="button" id="photoOpen" title="Open a photo" aria-label="Open a photo">Open photo</button><button type="button" id="photoClose" aria-label="Cancel photo edits">✕</button></header><div class="photo-content"><div class="photo-choices"><div class="photo-info"><span id="photoTarget"></span><select id="photoLook" aria-label="Photo look" title="Try a look"><option value="normal">Normal</option><option value="custom" disabled>Custom</option>${Object.entries(PHOTO_LOOKS).map(([value,look])=>`<option value="${value}">${look.label}</option>`).join('')}</select><canvas id="photoHistogram" width="256" height="48" role="img" aria-label="RGB histogram"></canvas></div><div id="photoMini"><canvas id="photoMiniCanvas" width="400" height="180" aria-label="Photo preview"></canvas></div><nav id="photoTabs" aria-label="Photo adjustments">${([['light','☀️','Light'],['colour','🎨','Colour'],['curves','〰','Curves'],['detail','✨','Detail'],['effects','◉','Effects'],['geometry','▧','Geometry']] as const).map(([id,glyph,label])=>`<button type="button" data-photo-category="${id}" aria-pressed="false">${glyph} ${label}</button>`).join('')}</nav></div><div class="photo-adjustments"><div id="photoGroupRow"><select id="photoGroup" aria-label="Adjustment group"></select><button type="button" id="photoGroupReset" aria-label="Reset this adjustment group" title="Reset this group">↺</button></div><div id="photoControls"></div></div></div><output id="photoStatus" aria-live="polite"></output><footer class="photo-footer"><button type="button" class="choice" id="photoCompare" aria-pressed="false">Before</button><button type="button" class="choice" id="photoReset">Reset</button><button type="button" class="choice" id="photoCancel">Cancel</button><button type="button" class="choice" id="photoApply">Done</button></footer>`;
  field('canvasSlot').append(panel);
  const toggle=document.createElement('button');toggle.type='button';toggle.id='photoToggle';toggle.className='tool-btn advanced-tool';toggle.hidden=true;toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls','photoPanel');toggle.title='Photo lab (P)';toggle.innerHTML=icon('photo')+'<span>Photo lab</span>';field('toolBin').append(toggle);
  const open=()=>{
    if(photoSession){cancelPhoto();return;}if(!advancedEnabled()||!actions.editable())return;
    if(activeLayer().cad){actions.message('Choose a paint layer for Photo lab. Open the 3D workshop to edit solids.');return;}
    if(!activeLayer().visible||activeLayer().opacity===0){actions.message('Show this layer and raise its opacity before opening Photo lab.');return;}
    actions.settle();restoreLayers=!field('layersPanel').hidden;beginPhoto();picking=horizon=false;cropRatio=0;point=0;panel.hidden=false;toggle.setAttribute('aria-expanded','true');toggle.classList.add('active');lockDrawing(true);emit('close-options');emit('photo-panel',true);
    const previousGroup=group;selectCategory(category);if(groups.some(g=>g.id===previousGroup&&g.category===category)){group=previousGroup;field<HTMLSelectElement>('photoGroup').value=group;buildControls();}
    field<HTMLSelectElement>('photoLook').focus({preventScroll:true});
  };
  toggle.addEventListener('click',open);
  const moreButton=document.createElement('button');moreButton.type='button';moreButton.className='choice';moreButton.id='openPhotoLab';moreButton.textContent='📸 Photo lab';moreButton.addEventListener('click',open);document.querySelector('[data-studio-panel="layers"]')!.insertBefore(moreButton,field('openSuperResolution'));
  for(const id of ['photoClose','photoCancel'])field(id).addEventListener('click',()=>cancelPhoto());
  field('photoApply').addEventListener('click',()=>{void applyPhoto().then(applied=>{if(applied)actions.message('Photo adjustments saved. Your original is kept; reopen Photo lab to change them.');}).catch(error=>actions.message(error instanceof Error?error.message:String(error)));});
  field('photoCompare').addEventListener('click',()=>{if(photoSession)comparePhoto(!photoSession.compare);});
  field('photoOpen').addEventListener('click',()=>{if(photoSession)importDraft=structuredClone({settings:photoSession.settings,normal:photoSession.normal,look:photoSession.look,lookActive:photoSession.lookActive});pendingImport=true;cancelPhoto();actions.open();});
  field('photoReset').addEventListener('click',()=>{if(photoSession){Object.assign(photoSession,newPhotoRecipe());point=0;cropRatio=0;buildControls();changed(false);}});
  field<HTMLSelectElement>('photoLook').addEventListener('change',event=>{if(photoSession){choosePhotoLook(photoSession,(event.target as HTMLSelectElement).value);changed(false);}});
  field('photoGroupReset').addEventListener('click',resetGroup);
  for(const button of panel.querySelectorAll<HTMLButtonElement>('[data-photo-category]'))button.addEventListener('click',()=>selectCategory(button.dataset.photoCategory as Category));
  field<HTMLSelectElement>('photoGroup').addEventListener('change',event=>{group=(event.target as HTMLSelectElement).value;category=groups.find(g=>g.id===group)!.category;for(const button of field('photoTabs').querySelectorAll<HTMLElement>('[data-photo-category]'))button.setAttribute('aria-pressed',String(button.dataset.photoCategory===category));picking=horizon=false;buildControls();});
  shortPhoto.addEventListener('change',()=>{if(photoSession){const previous=group;selectCategory(category);group=previous;field<HTMLSelectElement>('photoGroup').value=group;buildControls();}});
  bus.addEventListener('photo-update',updateStatus);bus.addEventListener('photo-error',event=>{actions.message((event as CustomEvent<string>).detail);field('photoStatus').textContent='Preview failed. Cancel and try again.';});
  bus.addEventListener('photo-end',()=>{panel.hidden=true;field('photoControls').replaceChildren();toggle.setAttribute('aria-expanded','false');toggle.classList.remove('active');picking=horizon=false;cropDrag=null;curvePointer=null;setPhotoGuides(null);view.classList.remove('photo-picking');lockDrawing(false);emit('restore-layers',restoreLayers);emit('photo-panel',false);if(!toggle.hidden)toggle.focus({preventScroll:true});});
  bus.addEventListener('advanced-mode',()=>{if(!advancedEnabled())cancelPhoto();});
  bus.addEventListener('close-photo',()=>cancelPhoto());
  bus.addEventListener('image-opened',()=>{if(pendingImport){pendingImport=false;importDraft=null;open();}});
  bus.addEventListener('image-open-cancelled',()=>{if(pendingImport){pendingImport=false;const draft=importDraft;importDraft=null;open();if(photoSession&&draft){Object.assign(photoSession,draft);buildControls();changed(false);}}});
  bus.addEventListener('photo-undo',event=>{if(photoSession){event.preventDefault();cancelPhoto();}});
  document.addEventListener('keydown',event=>{
    if(state.cad.open)return;
    const target=event.target,typing=target instanceof HTMLInputElement&&target.type!=='range'||target instanceof HTMLTextAreaElement||target instanceof HTMLSelectElement;
    if(photoSession){
      if(event.key==='Escape'){event.preventDefault();event.stopImmediatePropagation();cancelPhoto();toggle.focus();return;}
      if((event.ctrlKey||event.metaKey)&&!typing){event.preventDefault();event.stopImmediatePropagation();if(event.key.toLowerCase()==='z')cancelPhoto();else actions.message('Choose Done or Cancel in Photo lab first.');}
      if(!typing&&!event.ctrlKey&&!event.metaKey&&['b','e','f','i','t','r','l','p'].includes(event.key.toLowerCase()))event.stopImmediatePropagation();
    }else if(!typing&&!document.querySelector('dialog[open]')&&event.key.toLowerCase()==='p'&&!event.ctrlKey&&!event.metaKey&&!event.altKey){event.preventDefault();open();}
  },true);
  bindPaper();
}
