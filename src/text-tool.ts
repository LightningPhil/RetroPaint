import { bus, emit } from './bus';
import { H, W } from './canvas';
import { previewColor } from './materials';
import { pasteImage } from './selection';
import { state, vectorDrawingEnabled } from './state';
import { addPaintObject, objectId, selectedObjects, replaceSelectedText } from './objects';
import { drawObject, type TextObject } from './object-scene';
import { fitCallout } from './callout';
import { activeLayer, addLayer, canAddLayer, layers, switchLayer } from './layers';
import { pushHistory } from './history';
import { message } from './editor';

export interface TextOptions {
  text: string; font: string; size: number; width: number;
  bold: boolean; italic: boolean; underline: boolean; strike: boolean;
  align: CanvasTextAlign; opaque: boolean;
}
export const textOptions: TextOptions = { text: '', font: 'Trebuchet MS', size: 36, width: 360, bold: false, italic: false, underline: false, strike: false, align: 'left', opaque: false };
let anchor: { x: number; y: number } | null = null;
let cached: HTMLCanvasElement | null = null, signature = '';
let editing:TextObject|null=null;
let calloutPreview:TextObject|null=null,calloutSignature='';
export const calloutOptions={enabled:false,color:'#000000',paper:'#ffffff',border:true,rounded:true};
export function calloutEnabled():boolean{return state.workspaceMode==='advanced'&&calloutOptions.enabled;}
function calloutObject():TextObject {
  const layout:Partial<TextObject>={id:editing?.id??objectId(),name:'Label',opacity:editing?.opacity??state.opacity};
  makeTextBitmap(textOptions,calloutOptions.color,calloutOptions.paper,layout);layout.paper=calloutOptions.paper;
  const object=fitCallout(layout as TextObject,calloutOptions.border,calloutOptions.rounded,editing?.callout?.tip);
  object.callout!.text=textOptions.text.slice(0,20000);object.callout!.wrapWidth=Math.max(20,Math.min(4096,textOptions.width));
  const p=anchor?{...anchor}:{x:Math.max(0,(W-object.width)/2),y:Math.max(0,(H-object.height)/2)};
  p.x=Math.max(0,Math.min(W-object.width,p.x));p.y=Math.max(0,Math.min(H-object.height,p.y));
  const mx=Math.min(10,W/2),my=Math.min(10,H/2);
  if(!editing)object.callout!.tip={x:Math.max(mx,Math.min(W-mx,p.x+object.width+70<W-mx?p.x+object.width+70:p.x-70))-p.x,y:Math.max(my,Math.min(H-my,p.y+object.height+70))-p.y};
  object.matrix=editing?.matrix??[1,0,0,1,p.x,p.y];object.name=textOptions.text.trim().slice(0,60);return object;
}

export function makeTextBitmap(options: TextOptions, ink = previewColor(state.ink), paper = state.secondaryInk, layout?:Partial<TextObject>): HTMLCanvasElement {
  const canvas = document.createElement('canvas'), ctx = canvas.getContext('2d')!;
  const size = Math.max(6, Math.min(300, options.size)), width = Math.max(20, Math.min(4096, options.width));
  const font = `${options.italic ? 'italic ' : ''}${options.bold ? 'bold ' : ''}${size}px "${options.font.replace(/["\\]/g, '')}"`;
  ctx.font = font;
  const lines: string[] = [];
  for (const paragraph of options.text.slice(0, 20000).split('\n')) {
    let line = '';
    for (const word of paragraph.split(/(\s+)/)) {
      if (ctx.measureText(line + word).width <= width - 8) { line += word; continue; }
      if (line.trim()) { lines.push(line.trimEnd()); line = ''; }
      for (const character of word) {
        if (ctx.measureText(line + character).width > width - 8 && line) { lines.push(line); line = ''; }
        line += character;
      }
    }
    lines.push(line.trimEnd());
  }
  canvas.width = width; canvas.height = Math.min(4096, Math.max(size * 1.35 + 8, lines.length * size * 1.35 + 8));
  if (options.opaque) { ctx.fillStyle = paper; ctx.fillRect(0, 0, canvas.width, canvas.height); }
  ctx.font = font; ctx.textBaseline = 'top'; ctx.textAlign = options.align; ctx.fillStyle = ink;
  const x = options.align === 'center' ? width / 2 : options.align === 'right' ? width - 4 : 4;
  if(layout)Object.assign(layout,{kind:'text',width:canvas.width,height:canvas.height,font,size,align:options.align,color:ink,paper:options.opaque?paper:null,underline:options.underline,strike:options.strike,lines:lines.map((text,i)=>({text,x,y:4+i*size*1.35,width:ctx.measureText(text).width}))});
  lines.forEach((line, i) => {
    const y = 4 + i * size * 1.35;
    ctx.fillText(line, x, y);
    const measured = ctx.measureText(line).width, left = x - (options.align === 'center' ? measured / 2 : options.align === 'right' ? measured : 0);
    if (options.underline) ctx.fillRect(left, y + size * 1.04, measured, Math.max(1, size / 18));
    if (options.strike) ctx.fillRect(left, y + size * 0.55, measured, Math.max(1, size / 18));
  });
  return canvas;
}
function bitmap(): HTMLCanvasElement {
  const key = JSON.stringify([textOptions, state.ink, state.secondaryInk]);
  if (!cached || signature !== key) { cached = makeTextBitmap(textOptions); signature = key; }
  return cached;
}
export function beginText(x: number, y: number): void { anchor = { x, y }; emit('text-anchor'); }
export function hasText(): boolean { return Boolean(textOptions.text.trim()); }
export function cancelText(): void { editing=null;anchor = null; textOptions.text = ''; cached = null; emit('text'); }
export function placeText(): void {
  if (!hasText()) return;
  if(calloutEnabled()){
    const support=[...layers].reverse().find(layer=>layer.cad&&layers.indexOf(layer)>=layers.indexOf(activeLayer()));
    if(!editing&&support&&!canAddLayer()){message('Make room for a paint layer before adding a label.');return;}
    const object=calloutObject();
    if(editing){if(activeLayer().objects?.some(o=>o.id===editing!.id))replaceSelectedText(object);else{cancelText();return;}}
    else if(support){pushHistory();switchLayer(support.id);addLayer();activeLayer().name='Annotations';addPaintObject(object,false);}
    else addPaintObject(object);
    cancelText();state.tool='scissors';emit('tool-request');message('Label added. Blue handles move the arrow tip or the box; Select → Edit label changes its words and style.');return;
  }
  if(vectorDrawingEnabled()){
    const object:Partial<TextObject>={id:objectId(),name:'Text',opacity:state.opacity};makeTextBitmap(textOptions,previewColor(state.ink),state.secondaryInk,object);
    const p=anchor??{x:Math.max(0,(W-object.width!)/2),y:Math.max(0,(H-object.height!)/2)};object.matrix=[1,0,0,1,p.x,p.y];addPaintObject(object as TextObject);
    anchor=null;textOptions.text='';cached=null;emit('text');state.tool='scissors';emit('tool-request');return;
  }
  let image = bitmap();
  if (state.opacity < 1) {
    const faded = document.createElement('canvas'); faded.width = image.width; faded.height = image.height;
    const ctx = faded.getContext('2d')!; ctx.globalAlpha = state.opacity; ctx.drawImage(image, 0, 0); image = faded;
  }
  pasteImage(image, anchor ?? { x: Math.max(0, (W - image.width) / 2), y: Math.max(0, (H - image.height) / 2) });
  anchor = null; textOptions.text = ''; cached = null; emit('text');
  state.tool = 'scissors'; emit('tool-request');
}
export function renderTextPreview(ctx: CanvasRenderingContext2D): void {
  if (state.tool !== 'text' || !hasText()) return;
  if(calloutEnabled()){
    if(!editing){const key=JSON.stringify([textOptions,calloutOptions,anchor,state.opacity,W,H]);if(!calloutPreview||key!==calloutSignature){calloutPreview=calloutObject();calloutSignature=key;}drawObject(ctx,calloutPreview,performance.now());}return;
  }
  const image = bitmap(), p = anchor ?? { x: Math.max(0, (W - image.width) / 2), y: Math.max(0, (H - image.height) / 2) };
  ctx.save(); ctx.globalAlpha = state.opacity; ctx.drawImage(image, p.x, p.y); ctx.restore();
}
export function bindText(): void {
  const field=<T extends HTMLElement=HTMLInputElement>(id:string)=>document.getElementById(id) as T;
  const refreshCallout=()=>{field('calloutSettings').hidden=!calloutEnabled();field('textOpaque').parentElement!.hidden=calloutEnabled();};
  field<HTMLSelectElement>('textType').addEventListener('change',()=>{calloutOptions.enabled=field<HTMLSelectElement>('textType').value==='callout';editing=null;refreshCallout();});
  for(const [id,key] of [['calloutInk','color'],['calloutPaper','paper']] as const)field<HTMLInputElement>(id).addEventListener('input',()=>{calloutOptions[key]=field<HTMLInputElement>(id).value;});
  field<HTMLInputElement>('calloutBorder').addEventListener('change',()=>{calloutOptions.border=field<HTMLInputElement>('calloutBorder').checked;});
  field<HTMLSelectElement>('calloutCorners').addEventListener('change',()=>{calloutOptions.rounded=field<HTMLSelectElement>('calloutCorners').value==='rounded';});
  const edit=document.createElement('button');edit.type='button';edit.className='choice';edit.textContent='Edit label';edit.id='editCallout';edit.hidden=true;field('selectionDrawer').append(edit);
  bus.addEventListener('objects',()=>{const picked=selectedObjects();edit.hidden=state.workspaceMode!=='advanced'||picked.length!==1||picked[0].kind!=='text'||!picked[0].callout;});
  bus.addEventListener('advanced-mode',refreshCallout);
  edit.addEventListener('click',()=>{
    const object=selectedObjects()[0];if(object?.kind!=='text'||!object.callout)return;
    document.querySelector<HTMLButtonElement>('[data-tool="text"]')!.click();editing=object;calloutOptions.enabled=true;
    Object.assign(calloutOptions,{color:object.color,paper:object.paper??'#ffffff',border:object.callout.border,rounded:object.callout.rounded});
    Object.assign(textOptions,{text:object.callout.text??object.lines.map(l=>l.text).join('\n'),size:object.size,font:object.font.match(/"([^"]+)"/)?.[1]??'Arial',width:object.callout.wrapWidth??Math.max(360,object.width),bold:object.font.includes('bold'),italic:object.font.includes('italic'),underline:object.underline,strike:object.strike,align:object.align});
    for(const [id,value] of [['textType','callout'],['textContent',textOptions.text],['textSize',textOptions.size],['textFont',textOptions.font],['textWidth',textOptions.width],['textAlign',textOptions.align],['calloutInk',calloutOptions.color],['calloutPaper',calloutOptions.paper],['calloutCorners',calloutOptions.rounded?'rounded':'square']] as const)field<HTMLInputElement>(id).value=String(value);
    field<HTMLInputElement>('calloutBorder').checked=calloutOptions.border;
    document.querySelectorAll<HTMLButtonElement>('[data-text-style]').forEach(button=>{const on=textOptions[button.dataset.textStyle as 'bold'];button.classList.toggle('active',on);button.setAttribute('aria-pressed',String(on));});refreshCallout();
  });
  const content = document.getElementById('textContent') as HTMLTextAreaElement;
  content.addEventListener('input', () => { textOptions.text = content.value; });
  for (const [id, key] of [['textFont', 'font'], ['textSize', 'size'], ['textWidth', 'width'], ['textAlign', 'align']] as const) {
    const field = document.getElementById(id) as HTMLInputElement | HTMLSelectElement;
    field.addEventListener('input', () => {
      if (key === 'size' || key === 'width') textOptions[key] = Number(field.value) || (key === 'size' ? 36 : 360);
      else if (key === 'align') textOptions.align = field.value as CanvasTextAlign;
      else textOptions.font = field.value;
    });
  }
  document.querySelectorAll<HTMLButtonElement>('[data-text-style]').forEach(button => button.addEventListener('click', () => {
    const key = button.dataset.textStyle as 'bold' | 'italic' | 'underline' | 'strike';
    textOptions[key] = !textOptions[key]; button.classList.toggle('active', textOptions[key]); button.setAttribute('aria-pressed', String(textOptions[key]));
  }));
  const opaque = document.getElementById('textOpaque') as HTMLInputElement;
  opaque.addEventListener('change', () => { textOptions.opaque = opaque.checked; });
  document.getElementById('placeText')!.addEventListener('click', placeText);
  document.getElementById('cancelText')!.addEventListener('click', cancelText);
  document.addEventListener('keydown', event => {
    if(state.cad.open)return;
    if (event.ctrlKey && event.key === 'Enter' && state.tool === 'text') { event.preventDefault(); placeText(); }
  });
  bus.addEventListener('text', () => { content.value = textOptions.text; });
}
