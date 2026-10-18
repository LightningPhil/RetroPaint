import { enhancementRegion, type EnhancementRegion } from './enhancement-size';

export class EnhancementArea {
  readonly element=document.createElement('div');
  private canvas:HTMLCanvasElement;
  private size:HTMLSelectElement;
  private source:HTMLCanvasElement|null=null;
  private cx=.5;private cy=.5;private pointer:number|null=null;
  private offset={x:0,y:0};
  constructor(private changed:()=>void){
    this.element.className='enhance-overview';
    this.element.innerHTML='<canvas id="enhanceArea" width="400" height="280" tabindex="0" role="application" aria-label="Choose preview area. Click or drag the yellow box; arrow keys move it."></canvas><label>Area <select id="enhanceAreaSize" aria-label="Preview area size"><option value="64">64 px</option><option value="128" selected>128 px</option><option value="256">256 px</option></select></label><span>Move the yellow box onto detail.</span>';
    this.canvas=this.element.querySelector('canvas')!;this.size=this.element.querySelector('select')!;
    this.size.addEventListener('change',()=>{this.paint();this.changed();});
    const point=(event:PointerEvent)=>{
      const rect=this.canvas.getBoundingClientRect(),map=this.map(),fit=Math.min(rect.width/this.canvas.width,rect.height/this.canvas.height),x=(event.clientX-rect.left-(rect.width-this.canvas.width*fit)/2)/fit,y=(event.clientY-rect.top-(rect.height-this.canvas.height*fit)/2)/fit;
      return {x:(x-map.x)/map.scale,y:(y-map.y)/map.scale};
    };
    const move=(event:PointerEvent)=>{if(!this.source)return;const p=point(event);this.cx=(p.x-this.offset.x)/this.source.width;this.cy=(p.y-this.offset.y)/this.source.height;this.paint();this.changed();};
    this.canvas.addEventListener('pointerdown',event=>{
      if(event.button!==0||!this.source||this.element.inert)return;event.preventDefault();const p=point(event),r=this.region;
      this.offset=p.x>=r.x&&p.x<=r.x+r.width&&p.y>=r.y&&p.y<=r.y+r.height?{x:p.x-r.x-r.width/2,y:p.y-r.y-r.height/2}:{x:0,y:0};
      this.pointer=event.pointerId;this.canvas.setPointerCapture(event.pointerId);this.canvas.focus();move(event);
    });
    this.canvas.addEventListener('pointermove',event=>{if(this.pointer===event.pointerId)move(event);});
    for(const type of ['pointerup','pointercancel','lostpointercapture'])this.canvas.addEventListener(type,()=>{this.pointer=null;});
    this.canvas.addEventListener('keydown',event=>{
      if(!this.source||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;event.preventDefault();
      const r=this.region,step=event.shiftKey?32:8;this.cx=(r.x+r.width/2+(event.key==='ArrowLeft'?-step:event.key==='ArrowRight'?step:0))/this.source.width;this.cy=(r.y+r.height/2+(event.key==='ArrowUp'?-step:event.key==='ArrowDown'?step:0))/this.source.height;this.paint();this.changed();
    });
  }
  get region():EnhancementRegion {return this.source?enhancementRegion(this.source.width,this.source.height,this.cx,this.cy,Number(this.size.value)):{x:0,y:0,width:1,height:1};}
  setSource(source:HTMLCanvasElement|null):void {this.source=source;this.cx=this.cy=.5;this.pointer=null;this.paint();}
  private map():{x:number;y:number;scale:number}{
    const s=this.source!,scale=Math.min((this.canvas.width-12)/s.width,(this.canvas.height-12)/s.height);return {x:(this.canvas.width-s.width*scale)/2,y:(this.canvas.height-s.height*scale)/2,scale};
  }
  private paint():void {
    const ctx=this.canvas.getContext('2d')!;ctx.clearRect(0,0,this.canvas.width,this.canvas.height);if(!this.source)return;
    const m=this.map(),r=this.region,x=m.x+r.x*m.scale,y=m.y+r.y*m.scale,w=r.width*m.scale,h=r.height*m.scale;
    this.cx=(r.x+r.width/2)/this.source.width;this.cy=(r.y+r.height/2)/this.source.height;
    ctx.drawImage(this.source,m.x,m.y,this.source.width*m.scale,this.source.height*m.scale);
    ctx.fillStyle='#18223766';ctx.beginPath();ctx.rect(m.x,m.y,this.source.width*m.scale,this.source.height*m.scale);ctx.rect(x,y,w,h);ctx.fill('evenodd');
    ctx.strokeStyle='#263047';ctx.lineWidth=5;ctx.strokeRect(x,y,w,h);ctx.strokeStyle='#ffd16f';ctx.lineWidth=2;ctx.strokeRect(x,y,w,h);
    this.canvas.dataset.region=`${r.x},${r.y},${r.width},${r.height}`;
  }
}
