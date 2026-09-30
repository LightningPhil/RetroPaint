export interface SmudgeDab { x: number; y: number; dx: number; dy: number; }

export function advect(source: Uint8ClampedArray, width: number, height: number,
  cx: number, cy: number, dx: number, dy: number, radius: number, strength: number): Uint8ClampedArray {
  return advectMany(source,width,height,[{x:cx,y:cy,dx,dy}],radius,strength);
}

/** Blend the displacement fields before sampling one immutable source. Overlapping
 * mirror footprints cannot overwrite or amplify each other at the centre/seams. */
export function advectMany(source: Uint8ClampedArray, width: number, height: number,
  dabs: SmudgeDab[], radius: number, strength: number, sampleLimit?: (x:number,y:number,sx:number,sy:number)=>{x:number;y:number}): Uint8ClampedArray {
  const out=new Uint8ClampedArray(source), size=width*height;
  const vx=new Float32Array(size),vy=new Float32Array(size),weight=new Float32Array(size),peak=new Float32Array(size);
  const touched:number[]=[];
  for(const dab of dabs) {
    for(let y=Math.max(0,Math.floor(dab.y-radius));y<Math.min(height,Math.ceil(dab.y+radius));y++) {
      for(let x=Math.max(0,Math.floor(dab.x-radius));x<Math.min(width,Math.ceil(dab.x+radius));x++) {
        const distance=Math.hypot(x+0.5-dab.x,y+0.5-dab.y)/radius;
        if(distance>=1)continue;
        const t=1-distance*distance,falloff=t*t*(3-2*t),i=y*width+x;
        if(weight[i]===0)touched.push(i);
        vx[i]+=dab.dx*falloff;vy[i]+=dab.dy*falloff;weight[i]+=falloff;peak[i]=Math.max(peak[i],falloff);
      }
    }
  }
  for(const i of touched) {
    const factor=peak[i]*strength/weight[i],x=i%width,y=Math.floor(i/width);
    let sx=Math.max(0,Math.min(width-1,x-vx[i]*factor)),sy=Math.max(0,Math.min(height-1,y-vy[i]*factor));
    if (sampleLimit) { const p=sampleLimit(x,y,sx,sy); sx=Math.max(0,Math.min(width-1,p.x)); sy=Math.max(0,Math.min(height-1,p.y)); }
    const x0=Math.floor(sx),y0=Math.floor(sy),x1=Math.min(width-1,x0+1),y1=Math.min(height-1,y0+1),fx=sx-x0,fy=sy-y0;
    for(let c=0;c<4;c++) {
      const top=source[(y0*width+x0)*4+c]*(1-fx)+source[(y0*width+x1)*4+c]*fx;
      const bottom=source[(y1*width+x0)*4+c]*(1-fx)+source[(y1*width+x1)*4+c]*fx;
      out[i*4+c]=top*(1-fy)+bottom*fy;
    }
  }
  return out;
}

/** Distance-based elastic follower: sub-pixel mouse noise never gets stamped. */
export class SmudgePath {
  private fx: number;
  private fy: number;
  private px: number;
  private py: number;
  constructor(x: number, y: number, private radius: number,
    private dab: (x: number, y: number, dx: number, dy: number) => void) {
    this.fx = this.px = x;
    this.fy = this.py = y;
  }
  move(x: number, y: number, finish = false): void {
    const distance = Math.hypot(x - this.fx, y - this.fy);
    const follow = finish ? 1 : 1 - Math.exp(-distance / Math.max(3, this.radius * 0.18));
    this.fx += (x - this.fx) * follow;
    this.fy += (y - this.fy) * follow;
    const dx = this.fx - this.px, dy = this.fy - this.py;
    const length = Math.hypot(dx, dy);
    const spacing = Math.max(1.5, this.radius * 0.1);
    if (length < (finish ? 0.25 : spacing)) return;
    const steps = finish ? Math.ceil(length / spacing) : Math.floor(length / spacing);
    const step = finish ? length / steps : spacing;
    for (let i = 0; i < steps; i++) {
      const vx = dx / length * step, vy = dy / length * step;
      this.px += vx; this.py += vy;
      this.dab(this.px, this.py, vx, vy);
    }
  }
}
