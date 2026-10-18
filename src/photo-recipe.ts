import { defaultPhotoSettings, type PhotoSettings } from './photo-engine';

export const PHOTO_LOOKS:Record<string,{label:string;settings:Partial<PhotoSettings>}>= {
  natural:{label:'Natural',settings:{contrast:8,vibrance:15,clarity:8}},
  punch:{label:'Punchy',settings:{contrast:15,pop:35,vibrance:20}},
  mono:{label:'Black & white',settings:{saturation:-100,contrast:12}},
  warm:{label:'Warm film',settings:{temperature:24,tint:5,grain:12}},
  cool:{label:'Cool',settings:{temperature:-25,tint:0}},
};
export interface PhotoRecipe { settings:PhotoSettings; normal:PhotoSettings; look:string; lookActive:boolean }
export function newPhotoRecipe(settings=defaultPhotoSettings()):PhotoRecipe {
  return {settings:structuredClone(settings),normal:structuredClone(settings),look:'normal',lookActive:false};
}
export function photoManualChange(recipe:PhotoRecipe):void {
  recipe.look='custom';
  if(!recipe.lookActive)recipe.normal=structuredClone(recipe.settings);
}
export function choosePhotoLook(recipe:PhotoRecipe,value:string):void {
  if(value==='normal') {recipe.settings=structuredClone(recipe.normal);recipe.look='normal';recipe.lookActive=false;return;}
  const look=PHOTO_LOOKS[value];if(!look)return;
  if(!recipe.lookActive)recipe.normal=structuredClone(recipe.settings);
  recipe.settings=Object.assign(structuredClone(recipe.normal),look.settings);recipe.look=value;recipe.lookActive=true;
}
export function hasPhotoAdjustments(settings:PhotoSettings):boolean {
  return JSON.stringify({...settings,crop:defaultPhotoSettings().crop})!==JSON.stringify(defaultPhotoSettings());
}
function object(value:unknown):Record<string,unknown> {if(!value||typeof value!=='object'||Array.isArray(value))throw new Error('Invalid photo adjustment data.');return value as Record<string,unknown>;}
function finite(value:unknown,min:number,max:number):number {if(typeof value!=='number'||!Number.isFinite(value)||value<min||value>max)throw new Error('Invalid photo adjustment value.');return value;}
export function readPhotoCrop(value:unknown):PhotoSettings['crop'] {
  const c=object(value),x=finite(c.x,0,1),y=finite(c.y,0,1),width=finite(c.width,.000001,1),height=finite(c.height,.000001,1);
  if(x+width>1.000001||y+height>1.000001)throw new Error('Photo crop lies outside the original image.');return {x,y,width,height};
}
function readSettings(value:unknown):PhotoSettings {
  const input=object(value),settings=defaultPhotoSettings();
  const ranges:Record<string,[number,number]>={exposure:[-4,4],hue:[-180,180],sharpness:[0,150],radius:[.5,3],threshold:[0,32],noise:[0,100],colourNoise:[0,100],pop:[0,100],midpoint:[0,100],feather:[0,100],roundness:[0,100],grain:[0,100],vertical:[-75,75],horizontal:[-75,75],angle:[-45,45],zoom:[50,200]};
  for(const [key,initial] of Object.entries(settings)){
    if(typeof initial==='number'){
      if(input[key]===undefined&&['grainSize','grainRoughness'].includes(key))continue;
      const [min,max]=key==='grainSize'?[.5,3]:key==='grainRoughness'?[0,100]:ranges[key]||[-100,100];Object.assign(settings,{[key]:finite(input[key],min,max)});
    }
    else if(typeof initial==='boolean'){if(typeof input[key]!=='boolean')throw new Error('Invalid photo flip value.');Object.assign(settings,{[key]:input[key]});}
  }
  if(!Array.isArray(input.balance)||input.balance.length!==3)throw new Error('Invalid white balance.');settings.balance=input.balance.map(n=>finite(n,.25,4)) as [number,number,number];
  if(!Array.isArray(input.mixer)||input.mixer.length!==8)throw new Error('Invalid colour mixer.');settings.mixer=input.mixer.map(value=>{const m=object(value);return {hue:finite(m.hue,-60,60),saturation:finite(m.saturation,-100,100),luminance:finite(m.luminance,-100,100)};});
  const curves=object(input.curves);
  for(const channel of ['rgb','red','green','blue'] as const){
    const points=curves[channel];if(!Array.isArray(points)||points.length<2||points.length>12)throw new Error('Invalid photo curve.');
    settings.curves[channel]=points.map(value=>{const p=object(value);return {x:finite(p.x,0,1),y:finite(p.y,0,1)};});
    const p=settings.curves[channel];if(p[0].x!==0||p.at(-1)!.x!==1||p.some((v,i)=>i>0&&v.x<=p[i-1].x))throw new Error('Photo curve points must be ordered.');
  }
  settings.crop=readPhotoCrop(input.crop);return settings;
}
export function readPhotoRecipe(value:unknown):PhotoRecipe|undefined {
  if(value===undefined)return undefined;const recipe=object(value);
  if(typeof recipe.look!=='string'||!['normal','custom',...Object.keys(PHOTO_LOOKS)].includes(recipe.look)||typeof recipe.lookActive!=='boolean')throw new Error('Invalid photo look.');
  return {settings:readSettings(recipe.settings),normal:readSettings(recipe.normal),look:recipe.look,lookActive:recipe.lookActive};
}
