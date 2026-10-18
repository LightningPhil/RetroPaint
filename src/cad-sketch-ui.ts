import { cadId, type CadProfile, type CadSketchConstraint, type V2 } from './cad-model';
import { constraintLabel, solveSketch } from './cad-sketch-constraints';

export interface SketchAdapter {
  points:()=>V2[]; shape:()=>CadProfile['shape']; constraints:()=>CadSketchConstraint[]|undefined;
  update:(points:V2[],constraints:CadSketchConstraint[])=>void;
}
interface Callbacks { changed:()=>void; notice:(text:string)=>void; guide:()=>void }
const esc=(s:string)=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
const round=(v:number)=>Math.round(v*10000)/10000;
/** Shared by new sketches and the original sketches in feature history. Edits stay in the caller's draft. */
export class CadSketchEditor {
  private edge=0;
  private other=1;
  private page='add';
  private kind:CadSketchConstraint['kind']='length';
  private selected='';
  constructor(private host:HTMLElement,private prefix:string,private sketch:SketchAdapter,private callbacks:Callbacks){if(sketch.shape()==='circle')this.kind='diameter';this.render();}
  private el<T extends HTMLElement=HTMLElement>(id:string):T{return this.host.querySelector<T>('#'+this.prefix+id)!;}
  private button(id:string,label:string):string{return `<button type="button" class="choice" id="${this.prefix+id}">${label}</button>`;}
  private valueDefault():number{
    const p=this.sketch.points(),a=p[this.edge],b=p[(this.edge+1)%p.length],angle=(edge:number)=>{const a=p[edge],b=p[(edge+1)%p.length];return Math.atan2(b[1]-a[1],b[0]-a[0]);};
    if(this.kind==='diameter')return Math.max(...p.map(p=>p[0]))-Math.min(...p.map(p=>p[0]));
    if(this.kind==='angle')return angle(this.edge)*180/Math.PI;
    if(this.kind==='angle-between')return Math.acos(Math.max(-1,Math.min(1,Math.cos(angle(this.edge)-angle(this.other)))))*180/Math.PI;
    return Math.hypot(b[0]-a[0],b[1]-a[1]);
  }
  private change(rules:CadSketchConstraint[]):void{
    try{const points=solveSketch(this.sketch.points(),rules,this.sketch.shape());this.sketch.update(points,rules);this.callbacks.guide();this.render();this.callbacks.changed();}
    catch(error){const message=error instanceof Error?error.message:String(error);this.el('Error').textContent=message;this.el('Error').hidden=false;this.callbacks.notice(message);this.callbacks.changed();}
  }
  private readValue():number{const input=this.el<HTMLInputElement>('Value');if(!input.value.trim()||!Number.isFinite(Number(input.value)))throw new Error('Enter a finite dimension in mm or degrees.');return Number(input.value);}
  private render():void{
    const p=this.sketch.points(),rules=this.sketch.constraints()??[],circle=this.sketch.shape()==='circle';this.edge=Math.min(this.edge,p.length-1);this.other=Math.min(this.other,p.length-1);
    if(!rules.some(c=>c.id===this.selected))this.selected=rules[0]?.id??'';
    const current=rules.find(c=>c.id===this.selected),kind=this.page==='saved'?current?.kind:this.kind,paired=kind==='parallel'||kind==='perpendicular'||kind==='angle-between',driving=['length','angle','angle-between','diameter'].includes(kind??'');
    const options=(selected:number)=>p.map((_,i)=>`<option value="${i}" ${selected===i?'selected':''}>Line ${i+1}</option>`).join('');
    const kinds: [CadSketchConstraint['kind'],string][]=circle?[['diameter','Diameter · mm']]:[['length','Length · mm'],['angle','Angle to X · °'],['angle-between','Angle between · °'],['horizontal','Horizontal'],['vertical','Vertical'],['parallel','Parallel'],['perpendicular','Perpendicular']];
    this.host.innerHTML=`<div class="cad-actions"><button type="button" class="choice ${this.page==='add'?'active':''}" id="${this.prefix}AddPage" aria-pressed="${this.page==='add'}">＋ Dimension / relation</button><button type="button" class="choice ${this.page==='saved'?'active':''}" id="${this.prefix}SavedPage" aria-pressed="${this.page==='saved'}">Edit ${rules.length?`(${rules.length})`:''}</button></div><svg id="${this.prefix}Plot" class="cad-constraint-plot" role="group" aria-label="Sketch lines and dimensions"></svg>${this.page==='add'?`<div class="cad-fields"><label>Constraint<select id="${this.prefix}Kind">${kinds.map(([value,label])=>`<option value="${value}" ${kind===value?'selected':''}>${label}</option>`).join('')}</select></label>${!circle?`<label>First line<select id="${this.prefix}Edge">${options(this.edge)}</select></label>`:''}${paired?`<label>Second line<select id="${this.prefix}Other">${options(this.other)}</select></label>`:''}${driving?`<label>${kind==='angle'||kind==='angle-between'?'Angle · °':'Size · mm'}<input id="${this.prefix}Value" type="number" step="0.1" value="${round(this.valueDefault())}"></label>`:''}</div>${this.button('Add','＋ Add constraint')}`:`${rules.length?`<label class="cad-full-field">Saved dimensions & relations<select id="${this.prefix}Saved">${rules.map(c=>`<option value="${esc(c.id)}" ${c.id===this.selected?'selected':''}>${esc(constraintLabel(c))}</option>`).join('')}</select></label>${driving&&current&&'value' in current?`<label class="cad-full-field">${kind==='angle'||kind==='angle-between'?'Angle · °':'Size · mm'}<input id="${this.prefix}Value" type="number" step="0.1" value="${current.value}"></label>`:''}<div class="cad-actions">${driving?this.button('Update','✓ Update size'):''}${this.button('Remove','− Remove')}</div>`:'<p class="cad-hint">No constraints yet. Add a dimension or relation to start.</p>'}`}<p id="${this.prefix}Error" class="cad-feature-error" role="alert" hidden></p><small class="cad-hint">${rules.length?`${rules.length} constraints · solved`:'Free sketch'} · ${circle?'A diameter makes an ellipse round.':this.sketch.shape()==='rectangle'?'Rectangle keeps square corners.':'Tap a line; Shift-tap selects the second.'}</small>`;
    this.el('AddPage').onclick=()=>{this.page='add';this.render();this.callbacks.changed();};this.el('SavedPage').onclick=()=>{this.page='saved';this.render();this.callbacks.changed();};
    if(this.page==='add'){
      this.el<HTMLSelectElement>('Kind').onchange=()=>{this.kind=this.el<HTMLSelectElement>('Kind').value as CadSketchConstraint['kind'];this.render();this.callbacks.changed();};
      for(const id of ['Edge','Other']){const input=this.host.querySelector<HTMLSelectElement>('#'+this.prefix+id);if(input)input.onchange=()=>{if(id==='Edge')this.edge=Number(input.value);else this.other=Number(input.value);this.render();this.callbacks.changed();};}
      this.el('Add').onclick=()=>{try{const id=cadId(),kind=this.kind,edge=this.edge,other=this.other;let next:CadSketchConstraint;if(kind==='diameter')next={id,kind,value:this.readValue()};else if(kind==='length'||kind==='angle')next={id,kind,edge,value:this.readValue()};else if(kind==='angle-between')next={id,kind,edge,other,value:this.readValue()};else if(kind==='horizontal'||kind==='vertical')next={id,kind,edge};else next={id,kind,edge,other};this.selected=id;this.change([...structuredClone(rules),next]);}catch(error){this.el('Error').textContent=error instanceof Error?error.message:String(error);this.el('Error').hidden=false;}};
    }else if(current){
      this.el<HTMLSelectElement>('Saved').onchange=()=>{this.selected=this.el<HTMLSelectElement>('Saved').value;this.render();this.callbacks.changed();};
      if(driving)this.el('Update').onclick=()=>{try{const value=this.readValue();this.change(rules.map(c=>c.id===current.id&&'value' in c?{...c,value}:structuredClone(c)));}catch(error){this.el('Error').textContent=error instanceof Error?error.message:String(error);this.el('Error').hidden=false;}};
      this.el('Remove').onclick=()=>this.change(rules.filter(c=>c.id!==current.id));
    }
    this.draw();
  }
  private draw():void{
    const p=this.sketch.points(),rules=this.sketch.constraints()??[],xs=p.map(p=>p[0]),ys=p.map(p=>p[1]),x=Math.min(...xs),y=Math.min(...ys),w=Math.max(...xs)-x,h=Math.max(...ys)-y,span=Math.max(10,w,h),margin=span*.25,svg=this.el('Plot') as unknown as SVGSVGElement;
    svg.setAttribute('viewBox',`${x-margin} ${-y-h-margin} ${Math.max(w,1)+2*margin} ${Math.max(h,1)+2*margin}`);
    const selected=this.page==='saved'?rules.find(c=>c.id===this.selected):undefined,edge=selected&&'edge' in selected?selected.edge:this.edge,other=selected&&'other' in selected?selected.other:this.other,circle=this.sketch.shape()==='circle';
    svg.innerHTML=`<polygon points="${p.map(v=>v[0]+','+-v[1]).join(' ')}" fill="#f8bf4533" stroke="${circle?'#247c88':'none'}" stroke-width="${span/100}"/>${circle?'':p.map((a,i)=>{const b=p[(i+1)%p.length];return `<g data-line="${i}" role="button" tabindex="0" aria-label="Select line ${i+1}"><path d="M${a[0]},${-a[1]}L${b[0]},${-b[1]}" stroke="transparent" stroke-width="${span/12}"/><path d="M${a[0]},${-a[1]}L${b[0]},${-b[1]}" stroke="${i===edge?'#147786':i===other?'#b34d78':'#647782'}" stroke-width="${span/100}" pointer-events="none"/><text x="${(a[0]+b[0])/2}" y="${-(a[1]+b[1])/2-span/25}" text-anchor="middle" font-size="${span/13}" fill="#34434d" pointer-events="none">${i+1}</text></g>`;}).join('')}${rules.filter(c=>'value' in c).slice(0,6).map(c=>{const a='edge' in c?p[c.edge]:[x+w/2,y+h/2],b='edge' in c?p[(c.edge+1)%p.length]:a;return `<text data-constraint="${esc(c.id)}" role="button" tabindex="0" aria-label="Edit ${esc(constraintLabel(c))}" x="${(a[0]+b[0])/2}" y="${-(a[1]+b[1])/2+span/10}" text-anchor="middle" font-size="${span/12}" fill="${c.id===this.selected&&this.page==='saved'?'#b34d78':'#147786'}" stroke="#fff9e8" stroke-width="${span/120}" paint-order="stroke">${c.kind==='diameter'?'Ø ':''}${'value' in c?round(c.value):''}${c.kind==='angle'||c.kind==='angle-between'?'°':' mm'}</text>`;}).join('')}`;
    const activate=(target:Element,second=false)=>{const label=target.closest('[data-constraint]'),line=target.closest('[data-line]');if(label){this.selected=label.getAttribute('data-constraint')!;this.page='saved';}else if(line){if(second)this.other=Number(line.getAttribute('data-line'));else this.edge=Number(line.getAttribute('data-line'));this.page='add';}else return;this.render();this.callbacks.changed();};
    svg.onclick=event=>{if(event.target instanceof Element)activate(event.target,event.shiftKey);};svg.onkeydown=event=>{if((event.key==='Enter'||event.key===' ')&&event.target instanceof Element){event.preventDefault();activate(event.target,event.shiftKey);}};
  }
}
