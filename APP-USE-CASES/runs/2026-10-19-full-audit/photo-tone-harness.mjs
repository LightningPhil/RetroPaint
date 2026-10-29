// Real CUA actions only; this helper does not access application internals.
import fs from 'node:fs/promises';
export const root='F:/WebDev/RetroPaint/APP-USE-CASES/runs/2026-10-19-full-audit';
export async function setSlider(tab,label,value){
  const state=await tab.getAXState({emit:false,disableDiffing:true});
  const lines=state.split('\n').filter(line=>line.includes(' slider ')&&line.includes('Description: '+label+', Value:'));
  if(lines.length!==1)throw new Error('Expected one accessible slider '+label+': '+lines.length);
  const index=Number(lines[0].trim().match(/^([0-9]+) /)[1]);
  await tab.setValue(index,String(value));
  await tab.getAXState({emit:false});
  const actual=await tab.playwright.getByRole('slider',{name:label,exact:true}).evaluate(e=>({label:e.getAttribute('aria-label'),value:Number(e.value),min:Number(e.min),max:Number(e.max),step:Number(e.step)}));
  if(actual.value!==value)throw new Error('Slider '+label+' expected '+value+' got '+actual.value);
  await fs.appendFile(root+'/photo-tone-events.jsonl',JSON.stringify({at:new Date().toISOString(),tab:tab.id,...actual})+'\n');
  return actual;
}
export async function measureTone(tab,harness,{key,label,value,name}){
  await tab.playwright.locator('#photoToggle').click();
  await tab.playwright.getByRole('button',{name:'☀️ Light',exact:true}).click();
  await tab.playwright.locator('#photoReset').click();
  const slider=await setSlider(tab,label,value);
  await tab.playwright.locator('#photoStatus[aria-busy="false"]').waitFor({state:'visible',timeoutMs:20000});
  const visible=await tab.playwright.locator('#photoControls').evaluate(e=>Array.from(e.querySelectorAll('input')).map(n=>({label:n.getAttribute('aria-label'),value:n.value})));
  await harness.observe(name+'-draft');
  await tab.playwright.locator('#photoApply').click();
  await tab.playwright.locator('#photoPanel').waitFor({state:'hidden',timeoutMs:20000});
  await harness.project(name);await harness.png(name);
  await fs.writeFile(root+'/evidence/'+name+'.json',JSON.stringify({at:new Date().toISOString(),key,label,value,slider,visible,status:await tab.playwright.locator('#editorStatus').textContent()},null,2));
  return name;
}
