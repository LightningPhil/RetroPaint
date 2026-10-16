export interface CurvePoint { x: number; y: number }
export type CurveChannel = 'rgb' | 'red' | 'green' | 'blue';
export interface ColourMix { hue: number; saturation: number; luminance: number }
export interface CropBox { x: number; y: number; width: number; height: number }
export interface PhotoSettings {
  exposure: number; brightness: number; contrast: number; highlights: number; shadows: number; whites: number; blacks: number;
  temperature: number; tint: number; balance: [number, number, number]; saturation: number; vibrance: number; hue: number;
  mixer: ColourMix[]; curves: Record<CurveChannel, CurvePoint[]>;
  sharpness: number; radius: number; threshold: number; texture: number; clarity: number; pop: number; dehaze: number; noise: number; colourNoise: number;
  vignette: number; midpoint: number; feather: number; roundness: number; grain: number;
  distortion: number; aberration: number; vertical: number; horizontal: number; angle: number; zoom: number; flipX: boolean; flipY: boolean;
  crop: CropBox;
}
export function defaultPhotoSettings(): PhotoSettings {
  const line = () => [{ x:0, y:0 }, { x:1, y:1 }];
  return { exposure:0, brightness:0, contrast:0, highlights:0, shadows:0, whites:0, blacks:0, temperature:0, tint:0, balance:[1,1,1], saturation:0, vibrance:0, hue:0,
    mixer:Array.from({ length:8 }, () => ({ hue:0, saturation:0, luminance:0 })), curves:{ rgb:line(), red:line(), green:line(), blue:line() },
    sharpness:0, radius:1, threshold:0, texture:0, clarity:0, pop:0, dehaze:0, noise:0, colourNoise:0,
    vignette:0, midpoint:50, feather:75, roundness:0, grain:0, distortion:0, aberration:0, vertical:0, horizontal:0, angle:0, zoom:100, flipX:false, flipY:false,
    crop:{ x:0, y:0, width:1, height:1 } };
}
const clamp = (v: number, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, v));
const luminance = (r: number, g: number, b: number) => 0.2126*r + 0.7152*g + 0.0722*b;
const smooth = (a: number, b: number, x: number) => { const t = clamp((x-a) / Math.max(0.0001,b-a)); return t*t*(3-2*t); };
const linear = (n: number) => n <= 0.04045 ? n/12.92 : ((n+0.055)/1.055)**2.4;
const srgb = (n: number) => n <= 0.0031308 ? n*12.92 : 1.055*Math.max(0,n)**(1/2.4)-0.055;
const decode = Array.from({ length:256 }, (_,i) => linear(i/255));

// Shape-preserving cubic interpolation avoids rings and overshoot around curve points.
export function curveTable(points: CurvePoint[]): Float32Array {
  const p = points.slice().sort((a,b) => a.x-b.x), n = p.length, d: number[] = [], m: number[] = [];
  for (let i=0;i<n-1;i++) d[i] = (p[i+1].y-p[i].y)/Math.max(1/255,p[i+1].x-p[i].x);
  m[0]=d[0]; m[n-1]=d[n-2];
  for(let i=1;i<n-1;i++) {
    const a=p[i].x-p[i-1].x,b=p[i+1].x-p[i].x;
    m[i]=d[i-1]*d[i]<=0?0:3*(a+b)/((a+2*b)/d[i-1]+(2*a+b)/d[i]);
  }
  const out=new Float32Array(256); let j=0;
  for(let i=0;i<256;i++) {
    const x=i/255; while(j<n-2 && x>p[j+1].x)j++;
    const a=p[j],b=p[j+1],h=b.x-a.x,t=clamp((x-a.x)/Math.max(1/255,h)),t2=t*t,t3=t2*t;
    out[i]=clamp((2*t3-3*t2+1)*a.y+(t3-2*t2+t)*h*m[j]+(-2*t3+3*t2)*b.y+(t3-t2)*h*m[j+1]);
  }
  return out;
}
export function histogram(image: ImageData): { rgb: number[][]; clipped: [number,number]; count: number } {
  const rgb=Array.from({ length:3 },()=>Array<number>(256).fill(0)); let count=0,black=0,white=0;
  for(let i=0;i<image.data.length;i+=4)if(image.data[i+3]>0) {
    count++; for(let c=0;c<3;c++)rgb[c][image.data[i+c]]++;
    if(Math.min(image.data[i],image.data[i+1],image.data[i+2])<=1)black++;
    if(Math.max(image.data[i],image.data[i+1],image.data[i+2])>=254)white++;
  }
  return { rgb,clipped:[black/Math.max(1,count),white/Math.max(1,count)],count };
}
export function neutralBalance(rgb: number[]): [number,number,number] {
  const values=rgb.map(v=>linear(clamp(v/255,0.02,0.98))), target=(values[0]*values[1]*values[2])**(1/3);
  return values.map(v=>clamp(target/v,0.25,4)) as [number,number,number];
}
export function autoWhiteBalance(image: ImageData): [number,number,number] {
  const sum=[0,0,0]; let weight=0;
  for(let i=0;i<image.data.length;i+=4) {
    const r=image.data[i],g=image.data[i+1],b=image.data[i+2],l=luminance(r,g,b),sat=(Math.max(r,g,b)-Math.min(r,g,b))/Math.max(1,r,g,b);
    if(image.data[i+3]<128||l<20||l>235)continue;
    const w=(1-sat)**2; weight+=w; sum[0]+=r*w; sum[1]+=g*w; sum[2]+=b*w;
  }
  return weight>0?neutralBalance(sum.map(v=>v/weight)):[1,1,1];
}
export function autoPhoto(image: ImageData): Partial<PhotoSettings> {
  const bins=Array<number>(256).fill(0); let count=0,total=0;
  for(let i=0;i<image.data.length;i+=4)if(image.data[i+3]>127){const l=Math.round(luminance(image.data[i],image.data[i+1],image.data[i+2])); bins[l]++;count++;total+=l;}
  if(!count)return {};
  const percentile=(fraction:number)=>{let sum=0; for(let i=0;i<256;i++){sum+=bins[i];if(sum>=count*fraction)return i;}return 255;};
  const low=percentile(0.02),high=percentile(0.98),mean=total/count;
  if(high-low<8)return {};
  return { exposure:clamp(Math.log2(0.35/Math.max(0.01,linear(mean/255)))*0.45,-1.5,1.5), contrast:Math.round(clamp((210-(high-low))*0.2,-10,25)), shadows:low<30?18:0, highlights:high>245?-20:0, vibrance:12 };
}

function geometry(source: ImageData, s: PhotoSettings): ImageData {
  if(!s.distortion&&!s.aberration&&!s.vertical&&!s.horizontal&&!s.angle&&s.zoom===100&&!s.flipX&&!s.flipY)return new ImageData(new Uint8ClampedArray(source.data),source.width,source.height);
  const {width:w,height:h,data:src}=source, dst=new Uint8ClampedArray(src.length), unit=Math.min(w,h)/2,angle=-s.angle*Math.PI/180,c=Math.cos(angle),sin=Math.sin(angle),zoom=s.zoom/100;
  // Bilinear sampling in premultiplied alpha prevents dark fringes at clear edges.
  const sample=(x:number,y:number,channel:number)=>{
    if(x<-.5||y<-.5||x>w-.5||y>h-.5)return 0;
    x=clamp(x,0,w-1);y=clamp(y,0,h-1);const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy;
    let alpha=0,value=0;
    for(let yy=0;yy<2;yy++)for(let xx=0;xx<2;xx++){
      const k=(Math.min(h-1,iy+yy)*w+Math.min(w-1,ix+xx))*4,weight=(xx?fx:1-fx)*(yy?fy:1-fy),a=src[k+3]*weight;
      alpha+=a;value+=src[k+channel]*a;
    }
    return channel===3?alpha:alpha?value/alpha:0;
  };
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
    let nx=(x+0.5-w/2)/unit/zoom,ny=(y+0.5-h/2)/unit/zoom;
    const den=1-s.horizontal/250*nx-s.vertical/250*ny;
    if(den<0.1)continue;
    nx/=den;ny/=den;
    const rx=c*nx-sin*ny,ry=sin*nx+c*ny;nx=rx*(s.flipX?-1:1);ny=ry*(s.flipY?-1:1);
    const radial=1+s.distortion/350*(nx*nx+ny*ny),sx=nx*radial*unit+w/2-0.5,sy=ny*radial*unit+h/2-0.5,i=(y*w+x)*4;
    dst[i+3]=sample(sx,sy,3);if(!dst[i+3])continue;
    const fringe=s.aberration/20000;
    dst[i]=sample(sx+nx*unit*fringe,sy+ny*unit*fringe,0);dst[i+1]=sample(sx,sy,1);dst[i+2]=sample(sx-nx*unit*fringe,sy-ny*unit*fringe,2);
  }
  return new ImageData(dst,w,h);
}
function toHsl(r:number,g:number,b:number):[number,number,number]{
  const max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min,l=(max+min)/2;
  if(d<1e-6)return [0,0,l];
  const hue=max===r?((g-b)/d+(g<b?6:0)):max===g?(b-r)/d+2:(r-g)/d+4;
  return [hue/6,d/(1-Math.abs(2*l-1)),l];
}
function fromHsl(h:number,s:number,l:number):[number,number,number]{
  h=((h%1)+1)%1;const a=s*Math.min(l,1-l),f=(n:number)=>{const k=(n+h*12)%12;return l-a*Math.max(-1,Math.min(k-3,9-k,1));};return [f(0),f(8),f(4)];
}
// O(pixels) separable box blur, alpha weighted so clear margins are not treated as black.
function blurLuma(data:Uint8ClampedArray,w:number,h:number,radius:number):Float32Array{
  const r=Math.max(1,Math.round(radius)),tmp=new Float32Array(w*h),weight=new Float32Array(w*h),out=new Float32Array(w*h);
  for(let y=0;y<h;y++){
    let sum=0,a=0;
    for(let x=-r;x<=r;x++){const i=(y*w+clamp(x,0,w-1))*4,k=data[i+3]/255;sum+=luminance(data[i],data[i+1],data[i+2])*k;a+=k;}
    for(let x=0;x<w;x++){
      tmp[y*w+x]=sum;weight[y*w+x]=a;
      const left=(y*w+clamp(x-r,0,w-1))*4,right=(y*w+clamp(x+r+1,0,w-1))*4,al=data[left+3]/255,ar=data[right+3]/255;
      sum+=luminance(data[right],data[right+1],data[right+2])*ar-luminance(data[left],data[left+1],data[left+2])*al;a+=ar-al;
    }
  }
  for(let x=0;x<w;x++){
    let sum=0,a=0;for(let y=-r;y<=r;y++){const i=clamp(y,0,h-1)*w+x;sum+=tmp[i];a+=weight[i];}
    for(let y=0;y<h;y++){
      out[y*w+x]=a>0?sum/a:0;
      const left=clamp(y-r,0,h-1)*w+x,right=clamp(y+r+1,0,h-1)*w+x;sum+=tmp[right]-tmp[left];a+=weight[right]-weight[left];
    }
  }
  return out;
}
function detail(data:Uint8ClampedArray,w:number,h:number,radius:number,amount:number,threshold=0,midtone=false):void{
  if(!amount)return;const blurred=blurLuma(data,w,h,radius);
  for(let i=0,p=0;i<data.length;i+=4,p++)if(data[i+3]){
    const l=luminance(data[i],data[i+1],data[i+2]),d=l-blurred[p],mask=smooth(threshold,threshold+4,Math.abs(d)),mid=midtone?4*(l/255)*(1-l/255):1;
    const delta=d*amount*mask*mid;for(let c=0;c<3;c++)data[i+c]+=delta;
  }
}
function denoise(data:Uint8ClampedArray,w:number,h:number,amount:number,chroma:number):void{
  if(!amount&&!chroma)return;const source=data.slice(),strength=amount/100,colour=chroma/100,tolerance=8+strength*38;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
    const i=(y*w+x)*4;if(!source[i+3])continue;
    const l=luminance(source[i],source[i+1],source[i+2]),sum=[0,0,0];let total=0;
    for(let yy=Math.max(0,y-1);yy<=Math.min(h-1,y+1);yy++)for(let xx=Math.max(0,x-1);xx<=Math.min(w-1,x+1);xx++){
      const j=(yy*w+xx)*4,other=luminance(source[j],source[j+1],source[j+2]),weight=Math.exp(-(((other-l)/tolerance)**2))*source[j+3]/255;
      total+=weight;for(let c=0;c<3;c++)sum[c]+=source[j+c]*weight;
    }
    if(!total)continue;const avg=sum.map(n=>n/total),ll=luminance(...avg as [number,number,number]);
    for(let c=0;c<3;c++)data[i+c]=source[i+c]*(1-strength)+avg[c]*strength+((avg[c]-ll)-(source[i+c]-l))*colour*(1-strength);
  }
}
export function processPhoto(source: ImageData, s: PhotoSettings): ImageData {
  const result=geometry(source,s),{data,width:w,height:h}=result,exposure=2**s.exposure;
  const gains=s.balance.map((v,c)=>v*Math.exp((c===0?s.temperature:c===2?-s.temperature:0)/220+(c===1?-s.tint:s.tint*0.5)/280));
  const contrast=Math.exp(s.contrast/100*1.2),master=curveTable(s.curves.rgb),tables=[s.curves.red,s.curves.green,s.curves.blue].map(curveTable);
  const mixerOn=s.mixer.some(m=>m.hue||m.saturation||m.luminance),centres=[0,1/12,1/6,1/3,0.5,2/3,0.75,5/6],vibrance=(s.vibrance+s.pop*0.2)/100,dehaze=(s.dehaze+s.pop*0.15)/100;
  for(let i=0;i<data.length;i+=4)if(data[i+3]){
    let r=srgb(decode[data[i]]*exposure*gains[0]),g=srgb(decode[data[i+1]]*exposure*gains[1]),b=srgb(decode[data[i+2]]*exposure*gains[2]);
    const l=clamp(luminance(r,g,b)),tone=s.brightness/300+s.shadows/100*0.35*(1-l)**3+s.highlights/100*0.35*l**3+s.whites/100*0.25*l**6+s.blacks/100*0.25*(1-l)**6;
    const adjust=(v:number)=>clamp(((v+tone-0.5)*contrast+0.5-dehaze*0.09)/(1-dehaze*0.18));
    r=adjust(r);g=adjust(g);b=adjust(b);
    if(s.hue||mixerOn){
      let [hue,sat,light]=toHsl(r,g,b);const originalHue=hue;
      hue+=s.hue/360;
      if(mixerOn)for(let c=0;c<8;c++){
        const distance=Math.min(Math.abs(originalHue-centres[c]),1-Math.abs(originalHue-centres[c])),weight=Math.max(0,1-distance/(1/9))*Math.min(1,sat*4),mix=s.mixer[c];
        hue+=mix.hue/360*weight;sat=clamp(sat*(1+mix.saturation/100*weight));light=clamp(light+mix.luminance/100*0.35*weight);
      }
      [r,g,b]=fromHsl(hue,sat,light);
    }
    const y=luminance(r,g,b),max=Math.max(r,g,b),sat=max?1-Math.min(r,g,b)/max:0,skin=r>g&&g>b&&r-b>0.06?0.55:1,factor=Math.max(0,1+s.saturation/100+vibrance*(1-sat)*skin);
    const channels=[r,g,b];for(let c=0;c<3;c++){const value=clamp(y+(channels[c]-y)*factor);data[i+c]=tables[c][Math.round(master[Math.round(value*255)]*255)]*255;}
  }
  denoise(data,w,h,s.noise,s.colourNoise);
  const scale=Math.max(0.25,w/960);
  detail(data,w,h,12*scale,(s.clarity+s.pop*0.6)/100*1.4,0,true);
  detail(data,w,h,2*scale,s.texture/100*0.9);
  detail(data,w,h,s.radius*scale,s.sharpness/100*1.8,s.threshold);
  if(s.vignette||s.grain){
    const crop=s.crop,cx=(crop.x+crop.width/2)*w,cy=(crop.y+crop.height/2)*h,rx=Math.max(1,crop.width*w/2),ry=Math.max(1,crop.height*h/2),round=s.roundness/100;
    for(let y=0;y<h;y++)for(let x=0;x<w;x++){
      const i=(y*w+x)*4;if(!data[i+3])continue;
      const dx=(x+0.5-cx)/(rx*(1-round)+Math.min(rx,ry)*round),dy=(y+0.5-cy)/(ry*(1-round)+Math.min(rx,ry)*round),distance=Math.sqrt(dx*dx+dy*dy)/Math.SQRT2;
      const start=s.midpoint/100*0.8,end=start+0.08+s.feather/100*(1-start),v=smooth(start,end,distance)*s.vignette/100;
      const seed=Math.imul(x+1,374761393)^Math.imul(y+1,668265263),noise=(((Math.imul(seed^(seed>>>13),1274126177)>>>0)/4294967295)-0.5)*s.grain*0.65;
      for(let c=0;c<3;c++)data[i+c]=(v<0?data[i+c]*(1+v*0.85):data[i+c]+(255-data[i+c])*v*0.85)+noise;
    }
  }
  return result;
}
export function cropPixels(crop: CropBox, width: number, height: number): { x:number; y:number; width:number; height:number } {
  const x=Math.min(width-1,Math.max(0,Math.round(crop.x*width))),y=Math.min(height-1,Math.max(0,Math.round(crop.y*height)));
  return { x,y,width:Math.max(1,Math.min(width-x,Math.round(crop.width*width))),height:Math.max(1,Math.min(height-y,Math.round(crop.height*height))) };
}
