import * as tf from '@tensorflow/tfjs-core';
import { layers, loadLayersModel, type LayersModel, type Shape } from '@tensorflow/tfjs-layers';
import '@tensorflow/tfjs-backend-webgl';
import '@tensorflow/tfjs-backend-cpu';
import { enhancementSize, type EnhancementProgress, type EnhancementScale, type EnhancementRegion } from './enhancement-size';
import { PngStream } from './png-stream';

// ESRGAN RRDN custom layers, following the MIT-licensed UpscalerJS model
// definitions. The model's residual scaling and pixel shuffle are essential;
// plain interpolation is never substituted for neural inference.
class ResidualScale extends layers.Layer {
  static className='MultiplyBeta';
  call(input:tf.Tensor|tf.Tensor[]):tf.Tensor {return tf.mul(Array.isArray(input)?input[0]:input,.2);}
}
tf.serialization.registerClass(ResidualScale);
for(const factor of [2,4]){
  class PixelShuffle extends layers.Layer {
    static className=`PixelShuffle${factor}x`;
    computeOutputShape(input:Shape|Shape[]):Shape {const s=input as Shape;return [s[0],s[1]===null?null:s[1]*factor,s[2]===null?null:s[2]*factor,3];}
    call(input:tf.Tensor|tf.Tensor[]):tf.Tensor {return tf.depthToSpace((Array.isArray(input)?input[0]:input) as tf.Tensor4D,factor,'NHWC');}
  }
  tf.serialization.registerClass(PixelShuffle);
}
let model:LayersModel|null=null,modelScale=0;
async function getModel(scale:EnhancementScale,progress:(value:EnhancementProgress)=>void):Promise<LayersModel>{
  if(model&&modelScale===scale)return model;
  model?.dispose();model=null;modelScale=0;
  if(!tf.getBackend()){
    try{if(!await tf.setBackend('webgl'))await tf.setBackend('cpu');}catch{await tf.setBackend('cpu');}
    await tf.ready();
  }
  const root=new URL(/* @vite-ignore */ '../models/super-resolution/',import.meta.url);
  model=await loadLayersModel(new URL(`${scale}/model.json`,root).href,{onProgress:fraction=>progress({fraction:fraction*.08,message:`Loading ${scale}× AI model… ${Math.round(fraction*100)}%`})});
  modelScale=scale;return model;
}
const mirror=(position:number,size:number):number=>{if(size===1)return 0;const period=2*size-2,p=((position%period)+period)%period;return p<size?p:period-p;};
function tilePixels(image:ImageData,x:number,y:number,width:number,height:number):Float32Array {
  const data=new Float32Array(width*height*3),known=new Uint8Array(width*height),queue=new Int32Array(width*height);let end=0;
  for(let j=0;j<height;j++)for(let i=0;i<width;i++){
    const p=j*width+i,s=(mirror(y+j,image.height)*image.width+mirror(x+i,image.width))*4;
    for(let c=0;c<3;c++)data[p*3+c]=image.data[s+c]/255;
    if(image.data[s+3]){known[p]=1;queue[end++]=p;}
  }
  // Extend real colour into fully clear pixels, preventing a dark matte at the
  // edge when a three-channel neural model processes a transparent image.
  for(let head=0;head<end;head++){
    const p=queue[head],px=p%width;
    for(const n of [px?p-1:-1,px<width-1?p+1:-1,p-width,p+width])if(n>=0&&n<known.length&&!known[n]){
      known[n]=1;queue[end++]=n;for(let c=0;c<3;c++)data[n*3+c]=data[p*3+c];
    }
  }
  return data;
}
function alphaAt(image:ImageData,x:number,y:number):number {
  const x0=Math.floor(x),y0=Math.floor(y),fx=x-x0,fy=y-y0;
  const a=(xx:number,yy:number)=>image.data[(Math.max(0,Math.min(image.height-1,yy))*image.width+Math.max(0,Math.min(image.width-1,xx)))*4+3];
  return (a(x0,y0)*(1-fx)+a(x0+1,y0)*fx)*(1-fy)+(a(x0,y0+1)*(1-fx)+a(x0+1,y0+1)*fx)*fy;
}
async function renderBands(image:ImageData,scale:EnhancementScale,progress:(value:EnhancementProgress)=>void,write:(pixels:Uint8ClampedArray,y:number,height:number)=>Promise<void>):Promise<void>{
  const size=enhancementSize(image.width,image.height,scale),clear=!image.data.some((value,index)=>index%4===3&&value>0);
  const network=clear?null:await getModel(scale,progress);
  progress({fraction:.08,message:clear?'Preparing transparent copy…':'Model ready · preparing the first image tile…'});
  const gpu=tf.getBackend()==='webgl',core=clear?128:gpu?64:24,padding=32,cols=clear?1:Math.ceil(image.width/core),rows=Math.ceil(image.height/core);
  for(let row=0;row<rows;row++){
    const bandHeight=Math.min(core,image.height-row*core)*scale,band=new Uint8ClampedArray(size.width*bandHeight*4);
    for(let col=0;col<cols;col++){
    const x=col*core,y=row*core,w=Math.min(core,image.width-x),h=Math.min(core,image.height-y),tw=w+2*padding,th=h+2*padding;
    if(network){
    progress({fraction:.08+.9*(row*cols+col)/(rows*cols),message:`Enhancing ${scale}× · processing tile ${row*cols+col+1} of ${rows*cols}${gpu?'':' · CPU'}`});
    const predicted=tf.tidy(()=>{
      const input=tf.tensor4d(tilePixels(image,x-padding,y-padding,tw,th),[1,th,tw,3]);
      return tf.clipByValue(network.predict(input) as tf.Tensor,0,1);
    });
    try{
      const rgb=await predicted.data(),stride=tw*scale;
      for(let j=0;j<h*scale;j++)for(let i=0;i<w*scale;i++){
        const dx=x*scale+i,dy=y*scale+j,d=(j*size.width+dx)*4,s=((j+padding*scale)*stride+i+padding*scale)*3,a=alphaAt(image,(dx+.5)/scale-.5,(dy+.5)/scale-.5);
        band[d+3]=a;
        if(a>0)for(let c=0;c<3;c++){if(!Number.isFinite(rgb[s+c]))throw new Error('The graphics processor could not render this image.');band[d+c]=rgb[s+c]*255;}
      }
    }finally{predicted.dispose();}
    }
    const fraction=(row*cols+col+1)/(rows*cols);
    progress({fraction:.08+.90*fraction,message:`Enhancing ${scale}× · tile ${row*cols+col+1} of ${rows*cols} · ${Math.round(fraction*100)}%${gpu?'':' · CPU'}`});
    }
    await write(band,row*core*scale,bandHeight);
  }
}
export async function superResolvePixels(image:ImageData,scale:EnhancementScale,progress:(value:EnhancementProgress)=>void):Promise<ImageData>{
  const size=enhancementSize(image.width,image.height,scale);
  if(size.width*size.height>32_000_000)throw new Error('Use the tiled PNG path for a large enhanced copy.');
  const result=new ImageData(size.width,size.height);
  await renderBands(image,scale,progress,async(band,y)=>{result.data.set(band,y*size.width*4);});
  progress({fraction:1,message:'Enhanced detail ready.'});
  return result;
}
export async function superResolvePng(image:ImageData,scale:EnhancementScale,region:EnhancementRegion,progress:(value:EnhancementProgress)=>void):Promise<{png:Blob;preview:ImageData}>{
  if(!Object.values(region).every(Number.isInteger)||region.x<0||region.y<0||region.width<1||region.height<1||region.width>256||region.height>256||region.x+region.width>image.width||region.y+region.height>image.height)throw new Error('Choose a preview area inside the picture.');
  const size=enhancementSize(image.width,image.height,scale),encoder=new PngStream(size.width,size.height),preview=new ImageData(region.width*scale,region.height*scale);
  try{
    await renderBands(image,scale,progress,async(band,y,height)=>{
      const top=Math.max(y,region.y*scale),bottom=Math.min(y+height,(region.y+region.height)*scale),stride=preview.width*4;
      for(let row=top;row<bottom;row++)preview.data.set(band.subarray(((row-y)*size.width+region.x*scale)*4,((row-y)*size.width+region.x*scale)*4+stride),(row-region.y*scale)*stride);
      await encoder.write(band,height);
    });
    progress({fraction:.99,message:'Finishing enhanced PNG…'});const png=await encoder.finish();progress({fraction:1,message:'Enhanced copy ready.'});return {png,preview};
  }catch(error){await encoder.abort();throw error;}
}
