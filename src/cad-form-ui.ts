import { basePlane, sketchPoints, type CadForm, type CadProfile, type V2, type V3 } from './cad-model';
import { newProfile, pathBeziers } from './cad-profiles';
import { CadSketchEditor } from './cad-sketch-ui';
import { solveSketch } from './cad-sketch-constraints';

export interface ProfileSource { name:string; profile:CadProfile }
interface Callbacks { changed:()=>void; notice:(message:string)=>void; sources:()=>ProfileSource[]; drawing:()=>CadProfile|undefined; guide:(form:CadForm)=>void }
const esc=(s:string)=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
const bounds=(points:V2[])=>{const x=Math.min(...points.map(p=>p[0])),y=Math.min(...points.map(p=>p[1]));return{x,y,width:Math.max(...points.map(p=>p[0]))-x,height:Math.max(...points.map(p=>p[1]))-y};};

/** Shared builder/history editor. It owns only a draft recipe, never saved document data. */
export class CadFormEditor {
  private profileIndex=0;
  private pane='outline';
  private point=0;
  private projection:'xy'|'xz'|'yz'='xz';
  private dragging=false;
  constructor(private host:HTMLElement,readonly form:CadForm,private prefix:string,private callbacks:Callbacks,initial:{profile?:number;path?:boolean;settings?:boolean}={}){
    this.profileIndex=initial.profile??0;this.pane=initial.path?'path':initial.settings?'settings':'outline';this.render();
  }
  private el<T extends HTMLElement=HTMLElement>(id:string):T{return this.host.querySelector<T>('#'+this.prefix+id)!;}
  private field(id:string,label:string,value:number,min=-10000,max=10000):string{return `<label>${label}<input id="${this.prefix+id}" type="number" step="0.1" min="${min}" max="${max}" value="${Math.round(value*10000)/10000}"></label>`;}
  private button(id:string,label:string):string{return `<button type="button" class="choice" id="${this.prefix+id}">${label}</button>`;}
  private profile():CadProfile{return this.form.kind==='loft'?this.form.profiles[this.profileIndex]:this.form.profile;}
  private number(id:string,min=-10000,max=10000):number{const input=this.el<HTMLInputElement>(id),value=Number(input.value);if(!input.value.trim()||!Number.isFinite(value)||value<min||value>max)throw new Error(`${input.closest('label')?.firstChild?.textContent?.trim()??'Value'} must be between ${min} and ${max}.`);return value;}
  read():CadForm{this.collect();return structuredClone(this.form);}
  showGuide():void{this.callbacks.guide(this.form);}
  private attempt(action:()=>void):void{try{action();this.showGuide();this.callbacks.changed();}catch(error){this.callbacks.notice(error instanceof Error?error.message:String(error));}}
  private change(action:()=>void):void{this.attempt(()=>{this.collect();action();this.render();});}
  private collect():void{
    const p=this.profile();
    if(p.constraints?.length&&(this.pane==='outline'||this.pane==='draw'||(this.form.kind==='loft'&&(this.pane==='point'||this.pane==='coordinates'))))return;
    if(this.pane==='outline'){
      const name=this.el<HTMLInputElement>('ProfileName').value.trim();p.name=name||'Profile';
      const b=bounds(p.points),width=this.number('Width',.1,2000),height=this.number('Height',.1,2000),x=this.number('CenterX'),y=this.number('CenterY'),shape=this.el<HTMLSelectElement>('Shape').value as CadProfile['shape'];
      if(shape==='polygon'&&p.shape==='polygon')p.points=p.points.map(v=>[x+(v[0]-b.x-b.width/2)*width/(b.width||1),y+(v[1]-b.y-b.height/2)*height/(b.height||1)]);
      else if(shape==='polygon')p.points=sketchPoints('rectangle',x-width/2,y-height/2,width,height);
      else p.points=sketchPoints(shape,shape==='circle'?x:x-width/2,shape==='circle'?y:y-height/2,width,height);
      p.shape=shape;
    }else if(this.pane==='placement'){
      const axis=this.el<HTMLSelectElement>('Plane').value;if(axis!=='keep')p.plane=basePlane(axis);
      p.plane.origin=[0,1,2].map(i=>this.number('Origin'+i)) as V3;p.rotation=this.number('Rotation',-36000,36000);
    }else if(this.pane==='coordinates'){
      const isPath=this.form.kind==='sweep',dimensions=isPath?3:2,pairs=this.el<HTMLTextAreaElement>('Coordinates').value.split(';').filter(v=>v.trim()).map(v=>v.split(',').map(n=>n.trim()?Number(n):NaN));
      if(pairs.length<(isPath?2:3)||pairs.length>(isPath?64:256)||pairs.some(p=>p.length!==dimensions||p.some(n=>!Number.isFinite(n)||Math.abs(n)>10000)))throw new Error(`Enter ${isPath?'2–64 x,y,z':'3–256 x,y'} points separated by semicolons.`);
      if(this.form.kind==='sweep'){this.form.path.points=pairs as V3[];this.form.path.name=this.el<HTMLInputElement>('PathName').value.trim()||'Sweep path';}else{p.points=pairs as V2[];p.shape='polygon';}
    }else if(this.pane==='point'){
      if(this.form.kind==='sweep')this.form.path.points[this.point]=[0,1,2].map(i=>this.number('Point'+i)) as V3;
      else{p.points[this.point]=[this.number('Point0'),this.number('Point1')];p.shape='polygon';}
    }else if(this.pane==='settings'){
      if(this.form.kind==='loft')this.form.ruled=this.el<HTMLSelectElement>('Sides').value==='ruled';
      else{this.form.path.smooth=this.el<HTMLSelectElement>('PathMode').value==='smooth';this.form.transition=this.el<HTMLSelectElement>('Corners').value as 'right';this.form.roll=this.number('Roll',-36000,36000);}
    }
  }
  private render():void{
    const p=this.profile();p.points=solveSketch(p.points,p.constraints,p.shape);const b=bounds(p.points),loft=this.form.kind==='loft',choices=loft?[['outline','Profile · shape & size'],['constraints','Profile · dimensions & constraints'],['placement','Profile · position & turn'],['draw','Profile · draw points'],['point','Profile · exact point'],['coordinates','Profile · coordinates'],['copy','Copy a sketch outline'],['settings','Loft settings']]:[['outline','Profile · shape & size'],['constraints','Profile · dimensions & constraints'],['draw','Profile · draw points'],['copy','Copy a sketch outline'],['path','Path · draw & drag'],['point','Path · exact point'],['coordinates','Path · coordinates'],['settings','Sweep settings']];
    let content='';
    if(this.pane==='outline')content=`<label class="cad-full-field">Sketch name<input id="${this.prefix}ProfileName" maxlength="60" value="${esc(p.name)}"></label><div class="cad-fields"><label>Outline<select id="${this.prefix}Shape">${[['circle','Circle / ellipse'],['rectangle','Rectangle'],['polygon','Custom polygon']].map(([value,label])=>`<option value="${value}" ${p.shape===value?'selected':''}>${label}</option>`).join('')}</select></label>${this.field('Width','Width / diameter · mm',b.width,.1,2000)}${this.field('Height','Height / diameter · mm',b.height,.1,2000)}${this.field('CenterX','Centre X · mm',b.x+b.width/2)}${this.field('CenterY','Centre Y · mm',b.y+b.height/2)}</div>`;
    if(this.pane==='placement')content=`<label class="cad-full-field">Sketch plane<select id="${this.prefix}Plane"><option value="keep">Keep current axes</option><option value="xy">XY · horizontal</option><option value="xz">XZ · front</option><option value="yz">YZ · side</option></select></label><div class="cad-fields three">${p.plane.origin.map((v,i)=>this.field('Origin'+i,['Origin X · mm','Origin Y · mm','Origin Z · mm'][i],v)).join('')}</div>${this.field('Rotation','Turn on plane · °',p.rotation,-36000,36000)}`;
    if(this.pane==='settings')content=loft?`<label class="cad-full-field">Between profiles<select id="${this.prefix}Sides"><option value="smooth" ${!this.form.ruled?'selected':''}>Smooth · flow through sketches</option><option value="ruled" ${this.form.ruled?'selected':''}>Ruled · straight between sketches</option></select></label><p class="cad-hint">Profiles connect in the listed order. Use ↑ / ↓ to reorder them. Each sketch keeps its own position, outline and turn.</p>`:this.form.kind==='sweep'?`<div class="cad-fields"><label>Path<select id="${this.prefix}PathMode"><option value="smooth" ${this.form.path.smooth?'selected':''}>Smooth curve through points</option><option value="polyline" ${!this.form.path.smooth?'selected':''}>Straight segments</option></select></label><label>At sharp corners<select id="${this.prefix}Corners"><option value="right" ${this.form.transition==='right'?'selected':''}>Miter · meet neatly</option><option value="round" ${this.form.transition==='round'?'selected':''}>Round transition</option></select></label>${this.field('Roll','Profile turn · °',this.form.roll,-36000,36000)}</div><p class="cad-hint">The profile follows the path from its first point, perpendicular to the tangent. Tight bends may need a smaller profile.</p>`:'';
    if(this.pane==='copy'){const sources=this.callbacks.sources();content=`<label class="cad-full-field">Saved sketch outline<select id="${this.prefix}Source">${sources.length?sources.map((s,i)=>`<option value="${i}">${esc(s.name)}</option>`).join(''):'<option value="">No saved sketches yet</option>'}</select></label>${this.button('Copy','Copy selected outline')}${this.button('Drawing','Copy current sketch drawing')}<p class="cad-hint">Copies stay editable inside this feature. The source sketch stays as it was. This profile keeps its placement.</p>`;}
    if(this.pane==='draw'||this.pane==='path')content=`${this.pane==='path'?`<label class="cad-full-field">Draw in view<select id="${this.prefix}Projection"><option value="xz" ${this.projection==='xz'?'selected':''}>Front · X / Z</option><option value="xy" ${this.projection==='xy'?'selected':''}>Top · X / Y</option><option value="yz" ${this.projection==='yz'?'selected':''}>Side · Y / Z</option></select></label>`:''}<svg id="${this.prefix}Plot" class="cad-form-plot" role="img" aria-label="${this.pane==='path'?'Sweep path':'Profile outline'}: tap to add, drag points to edit"></svg><div class="cad-actions">${this.button('AddPoint','＋ Point')}${this.button('RemovePoint','− Point')}</div><p class="cad-hint">Tap empty space to add a point. Drag dots to shape it. Exact point edits include ${this.pane==='path'?'all three coordinates':'x and y'}.</p>`;
    if(this.pane==='point'){const points=this.form.kind==='sweep'?this.form.path.points:p.points;this.point=Math.min(this.point,points.length-1);content=`<label class="cad-full-field">Point<select id="${this.prefix}Point">${points.map((_,i)=>`<option value="${i}" ${i===this.point?'selected':''}>Point ${i+1}</option>`).join('')}</select></label><div class="cad-fields ${this.form.kind==='sweep'?'three':''}">${points[this.point].map((v,i)=>this.field('Point'+i,['X · mm','Y · mm','Z · mm'][i],v)).join('')}</div><div class="cad-actions">${this.button('AddPoint','＋ Point')}${this.button('RemovePoint','− Point')}</div>`;}
    if(this.pane==='coordinates'){const path=this.form.kind==='sweep'?this.form.path:undefined;content=`${path?`<label class="cad-full-field">Path name<input id="${this.prefix}PathName" maxlength="60" value="${esc(path.name)}"></label>`:''}<label class="cad-full-field">${path?'x,y,z':'x,y'} points · mm<textarea id="${this.prefix}Coordinates" rows="3" spellcheck="false">${(path?.points??p.points).map(p=>p.map(n=>Math.round(n*10000)/10000).join(',')).join('; ')}</textarea></label><p class="cad-hint">Separate points with semicolons. ${path?'The path stays open.':'The profile closes automatically.'}</p>`;}
    const driven=!!p.constraints?.length&&(this.pane==='outline'||this.pane==='draw'||(loft&&(this.pane==='point'||this.pane==='coordinates')));
    if(driven)content='<p class="cad-hint">This profile is driven by saved dimensions and constraints. Choose “Profile · dimensions & constraints” to edit them. Remove its constraints to draw freely again.</p>';
    if(this.pane==='constraints')content=`<div id="${this.prefix}Constraints" class="cad-constraint-editor"></div>`;
    this.host.innerHTML=`${loft&&this.form.kind==='loft'?`<label class="cad-full-field">Loft profiles · in order<select id="${this.prefix}Profile">${this.form.profiles.map((p,i)=>`<option value="${i}" ${i===this.profileIndex?'selected':''}>${i+1}. ${esc(p.name)}</option>`).join('')}</select></label><div class="cad-actions cad-profile-order">${this.button('AddProfile','＋ Sketch')}${this.button('RemoveProfile','−')}${this.button('Up','↑')}${this.button('Down','↓')}</div>`:''}<label class="cad-full-field">Edit<select id="${this.prefix}Pane">${choices.map(([id,label])=>`<option value="${id}" ${id===this.pane?'selected':''}>${label}</option>`).join('')}</select></label><div class="cad-form-section">${content}</div>`;
    this.el<HTMLSelectElement>('Pane').onchange=()=>{const next=this.el<HTMLSelectElement>('Pane').value;this.change(()=>{this.pane=next;});this.el<HTMLSelectElement>('Pane').value=this.pane;};
    if(this.form.kind==='loft'){
      const form=this.form;this.el<HTMLSelectElement>('Profile').onchange=()=>{const next=Number(this.el<HTMLSelectElement>('Profile').value);this.change(()=>{this.profileIndex=next;this.point=0;});this.el<HTMLSelectElement>('Profile').value=String(this.profileIndex);};
      this.el<HTMLButtonElement>('AddProfile').disabled=form.profiles.length>=16;this.el('AddProfile').onclick=()=>this.change(()=>{const previous=this.profile(),next=structuredClone(previous??newProfile());next.name='Profile '+(form.profiles.length+1);next.plane.origin=next.plane.origin.map((v,i)=>v+next.plane.normal[i]*15) as V3;form.profiles.splice(this.profileIndex+1,0,next);this.profileIndex++;});
      this.el<HTMLButtonElement>('RemoveProfile').disabled=form.profiles.length<=2;this.el('RemoveProfile').onclick=()=>this.change(()=>{if(form.profiles.length>2){form.profiles.splice(this.profileIndex,1);this.profileIndex=Math.min(this.profileIndex,form.profiles.length-1);}});
      for(const[id,delta]of [['Up',-1],['Down',1]] as const){this.el<HTMLButtonElement>(id).disabled=this.profileIndex+delta<0||this.profileIndex+delta>=form.profiles.length;this.el(id).onclick=()=>this.change(()=>{const next=this.profileIndex+delta;[form.profiles[next],form.profiles[this.profileIndex]]=[form.profiles[this.profileIndex],form.profiles[next]];this.profileIndex=next;});}
    }
    for(const input of this.host.querySelectorAll<HTMLInputElement|HTMLTextAreaElement|HTMLSelectElement>('.cad-form-section input,.cad-form-section textarea,.cad-form-section select'))input.onchange=()=>this.attempt(()=>{this.collect();});
    if(this.pane==='copy'){
      this.el<HTMLButtonElement>('Copy').disabled=!this.callbacks.sources().length;this.el<HTMLButtonElement>('Drawing').disabled=!this.callbacks.drawing();
      const copy=(source:CadProfile|undefined)=>{if(!source)throw new Error('Draw a sketch or create a sketch-based solid first.');const placement=this.profile().plane;Object.assign(this.profile(),structuredClone(source),{constraints:structuredClone(source.constraints),plane:placement,rotation:this.profile().rotation});this.pane='outline';this.render();};
      this.el('Copy').onclick=()=>this.change(()=>copy(this.callbacks.sources()[Number(this.el<HTMLSelectElement>('Source').value)]?.profile));this.el('Drawing').onclick=()=>this.change(()=>copy(this.callbacks.drawing()));
    }
    if(this.pane==='point'&&!driven)this.el<HTMLSelectElement>('Point').onchange=()=>{const next=Number(this.el<HTMLSelectElement>('Point').value);this.change(()=>{this.point=next;});this.el<HTMLSelectElement>('Point').value=String(this.point);};
    for(const id of ['AddPoint','RemovePoint']){const button=this.host.querySelector<HTMLButtonElement>('#'+this.prefix+id);if(button)button.onclick=()=>this.change(()=>{const points=this.form.kind==='sweep'&&this.pane!=='draw'?this.form.path.points:p.points;if(id==='RemovePoint'){if(points.length>(points===p.points?3:2))points.splice(this.point,1);this.point=Math.min(this.point,points.length-1);}else if(points===p.points&&p.points.length<256){const a=p.points.at(-1)!;p.points.push([a[0]+5,a[1]+5]);this.point=p.points.length-1;p.shape='polygon';}else if(points!==p.points&&this.form.kind==='sweep'&&this.form.path.points.length<64){const last=this.form.path.points.at(-1)!;this.form.path.points.push([last[0]+10,last[1],last[2]+10]);this.point=this.form.path.points.length-1;}});}
    if(this.pane==='path')this.el<HTMLSelectElement>('Projection').onchange=()=>this.change(()=>{this.projection=this.el<HTMLSelectElement>('Projection').value as 'xz';});
    if((this.pane==='draw'&&!driven)||this.pane==='path')this.bindPlot();
    if(this.pane==='constraints')new CadSketchEditor(this.el('Constraints'),this.prefix+'Constraint',{points:()=>p.points,shape:()=>p.shape,constraints:()=>p.constraints,update:(points,constraints)=>{p.points=points;p.constraints=constraints;}},{changed:this.callbacks.changed,notice:this.callbacks.notice,guide:()=>this.showGuide()});
    this.callbacks.changed();
  }
  private bindPlot():void{
    const path=this.pane==='path'&&this.form.kind==='sweep'?this.form.path:undefined,p=this.profile(),svg=this.el('Plot') as unknown as SVGSVGElement,axes=path?(this.projection==='xy'?[0,1]:this.projection==='yz'?[1,2]:[0,2]):[0,1],points=path?.points??p.points;
    const draw=(fit=true)=>{const view=points.map(point=>[point[axes[0]],point[axes[1]]] as V2),b=bounds(view),span=Math.max(10,b.width,b.height),margin=span*.13;if(fit)svg.setAttribute('viewBox',`${b.x-margin} ${-b.y-b.height-margin} ${Math.max(1,b.width)+margin*2} ${Math.max(1,b.height)+margin*2}`);const command=path?.smooth?pathBeziers(path.points).map((controls,i)=>`${i?'':'M'+controls[0][axes[0]]+','+-controls[0][axes[1]]} C${controls.slice(1).map(c=>c[axes[0]]+','+-c[axes[1]]).join(' ')}`).join(' '):'M'+view.map(v=>v[0]+','+-v[1]).join(' L')+(path?'':' Z');svg.innerHTML=`<path d="${command}" fill="${path?'none':'#efb9cb55'}" stroke="#a74975" stroke-width="${span/160}"/>${view.map((v,i)=>`<circle data-form-point="${i}" cx="${v[0]}" cy="${-v[1]}" r="${span/55}" fill="${i===this.point?'#f5bd52':'#fff9e8'}" stroke="#874265" stroke-width="${span/180}"/>`).join('')}`;};
    draw();svg.onpointerdown=event=>{event.preventDefault();const dot=(event.target as Element).closest('[data-form-point]');if(dot)this.point=Number(dot.getAttribute('data-form-point'));else{if(points.length>=(path?64:256))return;const pos=new DOMPoint(event.clientX,event.clientY).matrixTransform(svg.getScreenCTM()!.inverse()),last=points.at(-1)!,next=[...last];next[axes[0]]=Math.round(Math.max(-10000,Math.min(10000,pos.x))*10)/10;next[axes[1]]=Math.round(Math.max(-10000,Math.min(10000,-pos.y))*10)/10;if(path)path.points.push(next as V3);else p.points.push(next as V2);this.point=points.length-1;}if(!path)p.shape='polygon';this.dragging=true;svg.setPointerCapture(event.pointerId);draw(false);};
    svg.onpointermove=event=>{if(!this.dragging)return;const pos=new DOMPoint(event.clientX,event.clientY).matrixTransform(svg.getScreenCTM()!.inverse());points[this.point][axes[0]]=Math.round(Math.max(-10000,Math.min(10000,pos.x))*10)/10;points[this.point][axes[1]]=Math.round(Math.max(-10000,Math.min(10000,-pos.y))*10)/10;draw(false);this.showGuide();};
    svg.onpointerup=svg.onpointercancel=()=>{this.dragging=false;draw();this.showGuide();};
  }
}
