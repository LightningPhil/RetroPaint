const clamp=(value:number,min:number,max:number)=>Math.max(min,Math.min(max,value));
function gaussian(x:number,y:number,seed:number):number {
  let a=Math.imul(x+1,374761393)^Math.imul(y+1,668265263)^seed;a=Math.imul(a^(a>>>13),1274126177);a^=a>>>16;
  let b=Math.imul(a^0x68bc21eb,1597334677);b^=b>>>15;
  return ((a&65535)+(a>>>16)+(b&65535)+(b>>>16)-131070)/65535*1.7320508;
}
function field(width:number,height:number,pitch:number,seed:number):(x:number,y:number)=>number {
  const cols=Math.ceil(width/pitch)+2,rows=Math.ceil(height/pitch)+2,values=new Float32Array(cols*rows);
  for(let y=0;y<rows;y++)for(let x=0;x<cols;x++)values[y*cols+x]=gaussian(x,y,seed);
  return (x,y)=>{
    const xx=(x+.5)/pitch,yy=(y+.5)/pitch,ix=Math.floor(xx),iy=Math.floor(yy),fx=xx-ix,fy=yy-iy,p=iy*cols+ix;
    return (values[p]*(1-fx)+values[p+1]*fx)*(1-fy)+(values[p+cols]*(1-fx)+values[p+cols+1]*fx)*fy;
  };
}
/** Fixed, achromatic grain with correlated clumps and a photographic tonal response. */
export function applyFilmGrain(data:Uint8ClampedArray,width:number,height:number,amount:number,size=1.2,roughness=50):void {
  if(!amount)return;
  const pitch=clamp(size,.5,3)*Math.max(width,height)/960,fine=field(width,height,pitch*.65,0x517cc1b7),coarse=field(width,height,pitch*1.8,0x3c6ef372);
  const mix=clamp(roughness,0,100)/100*.75,norm=1.5/Math.hypot(1-mix,mix),strength=clamp(amount,0,100)/100*.095;
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){
    const i=(y*width+x)*4;if(!data[i+3])continue;
    const r=data[i]/255,g=data[i+1]/255,b=data[i+2]/255,l=.2126*r+.7152*g+.0722*b;
    if(l<.00001||l>.99999)continue;
    const noise=clamp((fine(x,y)*(1-mix)+coarse(x,y)*mix)*norm,-2.8,2.8),target=clamp(l+noise*strength*Math.sqrt(l*(1-l)),0,1);
    // One luminance gain preserves hue and avoids coloured speckles or clipped channels.
    const gain=Math.min(target/l,1/Math.max(r,g,b));
    data[i]=r*gain*255;data[i+1]=g*gain*255;data[i+2]=b*gain*255;
  }
}
