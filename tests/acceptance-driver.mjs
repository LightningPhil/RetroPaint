import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';

// Only public user controls and actual browser download payloads. Expected
// image/geometry results belong in independent verifier scripts.
export class AcceptanceDriver{
 constructor(page,out){this.page=page;this.out=out;this.events=[];page.setDefaultTimeout(180000);}
 async record(event){this.events.push({at:new Date().toISOString(),...event});await fs.writeFile(path.join(this.out,'events.json'),JSON.stringify(this.events,null,2)+'\n');}
 async drawer(){if(await this.page.locator('#studioBtn').getAttribute('aria-expanded')!=='true')await this.page.locator('#studioBtn').click();await this.page.getByRole('tab',{name:'📁 File',exact:true}).click();}
 async close(){if(await this.page.locator('#studioBtn').getAttribute('aria-expanded')==='true')await this.page.getByRole('button',{name:'Close options',exact:true}).click();}
 async advanced(){await this.drawer();await this.page.getByRole('switch',{name:'Advanced mode',exact:true}).check();await this.close();}
 async open(file,kind='image'){
  await this.drawer();const pending=this.page.waitForEvent('filechooser');pending.catch(()=>{});await this.page.getByRole('button',{name:kind==='project'?'Open project':'Open image',exact:true}).click();await(await pending).setFiles(file);
  await this.page.locator('#editorStatus').getByText(kind==='project'?'Project opened with editable pieces, layers, photo adjustments and live ink.':'Image opened. Undo brings back the previous picture.',{exact:true}).waitFor();await this.page.locator('#studioBtn[aria-expanded="false"]').waitFor();await this.record({action:'open',kind,file});
 }
 async download(label,kind='project'){
  const target=path.join(this.out,label+'.'+(kind==='project'?'retropaint':kind));
  await assert.rejects(fs.access(target),{code:'ENOENT'},'Refusing to overwrite retained evidence: '+target);
  await this.drawer();await this.page.locator('#studioDrawer').getByRole('textbox',{name:'Name',exact:true}).fill(label);if(kind!=='project')await this.page.locator('#fileFormat').selectOption(kind);
  const pending=this.page.waitForEvent('download'),started=Date.now();pending.catch(()=>{});await this.page.getByRole('button',{name:kind==='project'?'Save project':'Save as',exact:true}).click();const download=await pending;await download.saveAs(target);assert.equal(await download.failure(),null);
  const bytes=await fs.readFile(target);if(kind==='project')assert.equal(JSON.parse(bytes).format,'RetroPaint');else if(kind==='png')assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
  await this.record({action:'download',kind,label,path:target,filename:download.suggestedFilename(),bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex'),elapsed_ms:Date.now()-started});await this.close();return target;
 }
 async photo(){assert.equal(await this.page.locator('#photoPanel').isVisible(),false,'Photo lab is already open');await this.page.locator('#photoToggle').click();await this.ready();}
 async ready(){await this.page.locator('#photoStatus[aria-busy="false"]').waitFor();}
 async group(category,group){
  const tab=this.page.locator(`[data-photo-category="${category}"]`),buttons=await tab.isVisible();
  if(buttons)await tab.click();
  else if(!group){group=await this.page.locator('#photoGroup option').evaluateAll((items,category)=>items.find(option=>option.closest('optgroup')?.label.toLowerCase()===category)?.value,category);assert(group,'No visible combined-selector route for '+category);}
  if(group){await this.page.locator('#photoGroup').selectOption(group);assert.equal(await this.page.locator('#photoGroup').inputValue(),group);}
  await this.record({action:'photo-group-navigation',category,group:group??null,route:buttons?'category-buttons':'combined-group-selector'});
 }
 async slider(label,value){
  const control=this.page.getByRole('slider',{name:label,exact:true}),range=await control.evaluate(e=>({min:Number(e.min),max:Number(e.max),step:Number(e.step),value:Number(e.value)}));
  assert(value>=range.min&&value<=range.max);const fromMin=Math.round((value-range.min)/range.step),fromMax=Math.round((range.max-value)/range.step),minimum=fromMin<=fromMax;
  await control.press(minimum?'Home':'End');for(let i=0;i<(minimum?fromMin:fromMax);i++)await control.press(minimum?'ArrowRight':'ArrowLeft');
  assert.equal(Number(await control.inputValue()),value);await this.record({action:'slider',label,value,range});
 }
 async snapshot(label){await this.page.screenshot({path:path.join(this.out,label+'-ui.png')});await fs.writeFile(path.join(this.out,label+'.txt'),await this.page.locator('body').innerText());await this.record({action:'snapshot',label});}
 async canvas(selector,label){const data=await this.page.locator(selector).evaluate(e=>e.toDataURL('image/png'));assert(data.startsWith('data:image/png;base64,'));await fs.writeFile(path.join(this.out,label+'.png'),Buffer.from(data.split(',')[1],'base64'));await this.record({action:'public-canvas-output',selector,label});}
}
