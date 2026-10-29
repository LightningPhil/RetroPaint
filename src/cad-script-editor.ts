/** Find only unambiguous top-level numeric constants, preserving source offsets. */
export function numericScriptParameters(source:string):Array<{name:string;value:string;start:number;end:number}>{
  const mask=source.replace(/\/\*[\s\S]*?(?:\*\/|$)|\/\/[^\n]*|"(?:\\[\s\S]|[^"\\])*"/g,text=>text.replace(/[^\n]/g,' '));
  const depths=new Int32Array(mask.length);let depth=0;
  for(let i=0;i<mask.length;i++){depths[i]=depth;if('{[('.includes(mask[i]))depth++;else if('}])'.includes(mask[i]))depth=Math.max(0,depth-1);}
  const assignments=new Map<string,Array<{name:string;value:string;start:number;end:number}>>();
  for(const match of mask.matchAll(/^[ \t]*([A-Za-z_]\w*)[ \t]*=[ \t]*([^;\n]*);/gm)){
    if(depths[match.index!])continue;
    const name=match[1],value=match[2].trim(),start=match.index!+match[0].indexOf('=')+1+match[0].slice(match[0].indexOf('=')+1).search(/\S/);
    const list=assignments.get(name)??[];list.push({name,value,start,end:start+value.length});assignments.set(name,list);
  }
  const occurrences=new Map<string,number>();for(const match of mask.matchAll(/\b([A-Za-z_]\w*)\s*=(?!=)/g))if(!depths[match.index!])occurrences.set(match[1],(occurrences.get(match[1])??0)+1);
  return [...assignments.values()].filter(list=>list.length===1&&occurrences.get(list[0].name)===1&&/^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i.test(list[0].value)).map(list=>list[0]).slice(0,12);
}

export function openSCADLocation(message:string):{file:string;line:number}|undefined{
  const match=message.match(/(?:in file|file)\s+(.+?),\s*line\s*:?\s*(\d+)/i);
  if(!match)return;
  return{file:match[1].replace(/^\/project\//,''),line:Number(match[2])};
}
