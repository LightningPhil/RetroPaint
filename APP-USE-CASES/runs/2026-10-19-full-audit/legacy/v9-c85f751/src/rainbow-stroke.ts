import { paintStroke } from './brush';
import { W, H, cloneCanvas } from './canvas';
import { rainbowCss } from './color';
import type { Applicator, Pt } from './types';

function surface(w: number, h: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas'); canvas.width=w; canvas.height=h; return canvas;
}
const pigmentTiles = new Map<number, HTMLCanvasElement>();
function pigmentTile(hue: number): HTMLCanvasElement {
  const key = ((Math.round(hue / 5) * 5) % 360 + 360) % 360;
  const cached = pigmentTiles.get(key);
  if (cached) return cached;
  const tile = surface(128, 128), ctx = tile.getContext('2d')!;
  const gradient = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  for (const [stop, alpha] of [[0,1],[0.4,0.95],[0.7,0.42],[0.9,0.045],[1,0]]) {
    gradient.addColorStop(stop, rainbowCss(key) + Math.round(alpha*255).toString(16).padStart(2,'0'));
  }
  ctx.fillStyle = gradient; ctx.fillRect(0, 0, 128, 128);
  pigmentTiles.set(key, tile); return tile;
}

interface Bounds { left:number; top:number; right:number; bottom:number; }

/** Fixed-size pigment buffers and one last point. No retained gesture history.
 * Watercolour's unfinished dab is previewed separately, never stamped repeatedly.
 * Opacity is applied when compositing the layer, so long strokes do not darken
 * merely because they were delivered in more pointer events or animation frames. */
export class RainbowStroke {
  private pigment: HTMLCanvasElement;
  private coverage: HTMLCanvasElement | null;
  private output: HTMLCanvasElement;
  private last: Pt | null = null;
  private distance = 0;
  private nextDab: number;
  private dirty: Bounds | null = null;
  private readonly spacing: number;
  private readonly radius: number;
  constructor(private readonly applicator: Applicator, private readonly width: number, w=W, h=H) {
    this.pigment=surface(w,h);this.output=surface(w,h);
    this.coverage=applicator==='watercolor' ? null : surface(w,h);
    this.spacing=Math.max(0.75,width*0.08);this.nextDab=this.spacing;
    this.radius=width*0.8+1;
  }
  private dab(ctx: CanvasRenderingContext2D, x:number, y:number, distance:number, alpha:number):void {
    ctx.globalAlpha=alpha;
    ctx.drawImage(pigmentTile(distance*0.6),x-this.radius,y-this.radius,this.radius*2,this.radius*2);
    ctx.globalAlpha=1;
  }
  append(point:Pt):void {
    const a=this.last ?? point, b=point;
    const pad=this.width*1.5+4;
    const bounds={left:Math.min(a.x,b.x)-pad,top:Math.min(a.y,b.y)-pad,right:Math.max(a.x,b.x)+pad,bottom:Math.max(a.y,b.y)+pad};
    if(this.dirty){
      this.dirty.left=Math.min(this.dirty.left,bounds.left);this.dirty.top=Math.min(this.dirty.top,bounds.top);
      this.dirty.right=Math.max(this.dirty.right,bounds.right);this.dirty.bottom=Math.max(this.dirty.bottom,bounds.bottom);
    }else this.dirty=bounds;
    const ctx=this.pigment.getContext('2d')!;
    const length=Math.hypot(b.x-a.x,b.y-a.y);
    if(this.applicator==='watercolor'){
      if(!this.last)this.dab(ctx,b.x,b.y,0,0.8);
      if(length>=0.001){
        while(this.nextDab<=this.distance+length){
          const t=(this.nextDab-this.distance)/length;
          this.dab(ctx,a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t,this.nextDab,0.25);
          this.nextDab+=this.spacing;
        }
      }
    }else if(!this.last || length>=0.001){
      const nib=this.applicator==='biro'?Math.max(1.2,this.width*0.16):this.width;
      let color:string|CanvasGradient=rainbowCss(this.distance*0.6);
      if(length>=0.001){
        color=ctx.createLinearGradient(a.x,a.y,b.x,b.y);
        const stops=Math.max(2,Math.ceil(length/8));
        for(let j=0;j<=stops;j++)color.addColorStop(j/stops,rainbowCss((this.distance+length*j/stops)*0.6));
      }
      const coverage=this.coverage!.getContext('2d')!;
      if(this.applicator==='callig'){
        paintStroke(ctx,a.x,a.y,b.x,b.y,this.width,color,1,'callig',false);
        paintStroke(coverage,a.x,a.y,b.x,b.y,this.width,'#ffffff',1,'callig',false);
      }else{
        for(const [target,ink] of [[ctx,color],[coverage,'#ffffff']] as const){
          target.lineCap='round';target.lineJoin='round';target.lineWidth=nib;target.strokeStyle=ink;
          target.beginPath();target.moveTo(a.x,a.y);target.lineTo(b.x+(length<0.001?0.01:0),b.y);target.stroke();
        }
      }
      if(this.applicator==='gouache'){
        // Clip the bristles to this segment's nib, including when crossing old paint.
        ctx.save();const angle=Math.atan2(b.y-a.y,b.x-a.x),r=nib/2;
        ctx.beginPath();ctx.arc(a.x,a.y,r,angle+Math.PI/2,angle+Math.PI*1.5);
        ctx.arc(b.x,b.y,r,angle-Math.PI/2,angle+Math.PI/2);ctx.closePath();ctx.clip();
        for(let i=0;i<13;i++){
          const offset=(i/12-0.5)*this.width*0.88;
          ctx.lineWidth=Math.max(0.5,this.width/28);ctx.strokeStyle=i%4===0?'#ffffff':'#20202a';
          ctx.globalAlpha=i%4===0?0.12:0.055;
          ctx.beginPath();ctx.moveTo(a.x+offset*0.8,a.y+offset*0.6);
          ctx.lineTo(b.x+offset*0.8+(length<0.001?0.01:0),b.y+offset*0.6);ctx.stroke();
        }
        ctx.restore();
      }
    }
    if(length>=0.001)this.distance+=length;
    this.last={...point};
  }
  private flush():void {
    if(!this.dirty)return;
    const x=Math.max(0,Math.floor(this.dirty.left)),y=Math.max(0,Math.floor(this.dirty.top));
    const w=Math.min(this.output.width,Math.ceil(this.dirty.right))-x,h=Math.min(this.output.height,Math.ceil(this.dirty.bottom))-y;
    this.dirty=null;if(w<=0||h<=0)return;
    const ctx=this.output.getContext('2d')!;
    ctx.save();ctx.beginPath();ctx.rect(x,y,w,h);ctx.clip();ctx.clearRect(x,y,w,h);
    ctx.drawImage(this.pigment,x,y,w,h,x,y,w,h);
    if(this.coverage){
      ctx.globalCompositeOperation='destination-in';ctx.drawImage(this.coverage,x,y,w,h,x,y,w,h);
    }else if(this.last){
      const fraction=Math.max(0,Math.min(1,(this.distance-(this.nextDab-this.spacing))/this.spacing));
      this.dab(ctx,this.last.x,this.last.y,this.distance,0.25*fraction);
    }
    ctx.restore();
  }
  render(ctx:CanvasRenderingContext2D,opacity:number):void {
    this.flush();ctx.save();ctx.globalAlpha=opacity*(this.applicator==='watercolor'?0.62:1);
    ctx.drawImage(this.output,0,0);ctx.restore();
  }
  clone():RainbowStroke {
    const copy=new RainbowStroke(this.applicator,this.width,this.output.width,this.output.height);
    copy.pigment=cloneCanvas(this.pigment);copy.output=cloneCanvas(this.output);
    copy.coverage=this.coverage?cloneCanvas(this.coverage):null;
    copy.last=this.last?{...this.last}:null;copy.distance=this.distance;copy.nextDab=this.nextDab;
    copy.dirty=this.dirty?{...this.dirty}:null;return copy;
  }
  erase(draw:(ctx:CanvasRenderingContext2D)=>void):void {
    this.flush();
    for(const canvas of [this.pigment,this.coverage,this.output]){
      if(!canvas)continue;const ctx=canvas.getContext('2d')!;
      ctx.save();ctx.globalCompositeOperation='destination-out';draw(ctx);ctx.restore();
    }
  }
}
