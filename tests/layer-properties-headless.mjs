import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
import {controlledRenderClock} from './controlled-render-time.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/layer-properties')),origin=option('--origin','http://127.0.0.1:8094/'),kind=option('--case','rename');assert(['rename','opacity'].includes(kind));await fs.mkdir(out,{recursive:true});const file=path.join(out,'LAYER-properties-ui.json');if(await fs.access(file).then(()=>true,()=>false))throw new Error('Choose a fresh output folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,kind,execution:'Actual public layer controls in isolated headless contexts; render phase10000ms only for animated-art pixel comparisons',rows:[],errors:[]};
try{
 for(const [width,height] of [[1280,720],[320,568],[390,844],[844,390]]){
  console.log('LAYER '+kind+' '+width+'x'+height);const location=path.join(out,width+'x'+height);await fs.mkdir(location,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true});await context.addInitScript(controlledRenderClock);await context.addInitScript(()=>{window.__acceptanceRenderTime=10000;});const page=await context.newPage(),driver=new AcceptanceDriver(page,location);page.on('pageerror',e=>report.errors.push(String(e)));
  page.setDefaultTimeout(20000);
  const layers=async()=>{if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();};
  const options=async()=>{await layers();if(!await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();};
  const list=async()=>{await layers();if(await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();};
  const pair=async label=>{if(width===844&&label==='before')await driver.snapshot('before-download-diagnostic');const saved=await driver.download(label);await driver.download(label,'png');return saved;};
  const name=async(value,label)=>{await options();await page.locator('#layerName').fill('');await page.locator('#layerName').pressSequentially(value,{delay:3});await page.locator('#layerName').press('Enter');await driver.record({action:'typed-layer-name',value,label});};
  const verifyName=async expected=>{await options();assert.equal(await page.locator('#layerName').inputValue(),expected);await page.locator('#closeLayers').click();await list();const pick=page.locator('#layerList .layer-row.active .layer-pick');await pick.waitFor({state:'visible'});assert.equal(await pick.getAttribute('aria-label'),'Paint on '+expected+', selected');assert.equal(await page.locator('#layerList .layer-row.active .layer-name').innerText(),expected);const r=await pick.boundingBox();assert(r&&r.width>44&&r.height>=44&&r.x>=0&&r.x+r.width<=width+1);await driver.record({action:'consistent-visible-layer-name',expected,rect:r});};
  try{
   await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();await driver.open(path.join(root,'headless/MIX-final/MIX-enriched.retropaint'),'project');let saved;const row={width,height,kind,render_time_ms:10000};
   if(kind==='rename'){
    await name('Sketch sheet','setup');await verifyName('Sketch sheet');await pair('before');
    for(const [label,entered,expected] of [['character','Character','Character'],['blank','   ','Layer'],['long','Character bEfSTrM 0123456789 '.repeat(3).slice(0,60),'Character bEfSTrM 0123456789 '.repeat(3).slice(0,60).trim()]]){
     await name(entered,label);await verifyName(expected);await driver.snapshot(label);saved=await pair(label);await page.locator('#undoBtn').click();await pair(label+'-undone');await page.locator('#view').press('Control+Shift+z');await verifyName(expected);await pair(label+'-redone');
    }
    row.long_name='Character bEfSTrM 0123456789 '.repeat(3).slice(0,60).trim();row.blank_fallback='Layer';
   }else{
    await options();await page.locator('#layerOpacity').press('End');await page.locator('#layerName').focus();assert.equal(Number(await page.locator('#layerOpacity').inputValue()),1);await pair('before');await options();
    await page.locator('#layerOpacity').evaluate(e=>{window.__layerOpacityInputs=[];e.addEventListener('input',event=>window.__layerOpacityInputs.push({value:Number(e.value),trusted:event.isTrusted}));});const r=await page.locator('#layerOpacity').boundingBox();await page.mouse.move(r.x+r.width-10,r.y+r.height/2);await page.mouse.down();await page.mouse.move(r.x+r.width/2,r.y+r.height/2,{steps:20});await page.mouse.up();assert.equal(Number(await page.locator('#layerOpacity').inputValue()),.5);assert.equal(await page.locator('#layerOpacityValue').innerText(),'50%');row.pointer_inputs=await page.evaluate(()=>window.__layerOpacityInputs);assert(row.pointer_inputs.length>5&&row.pointer_inputs.every(item=>item.trusted));await driver.snapshot('half');await pair('half');await page.locator('#undoBtn').click();await pair('half-undone');await page.locator('#view').press('Control+Shift+z');await pair('half-redone');
    for(const [label,key,value] of [['zero','Home',0],['full','End',1]]){await options();await page.locator('#layerOpacity').press(key);await page.locator('#layerName').focus();assert.equal(Number(await page.locator('#layerOpacity').inputValue()),value);assert.equal(await page.locator('#layerOpacityValue').innerText(),value*100+'%');await driver.snapshot(label);saved=await pair(label);await page.locator('#undoBtn').click();await pair(label+'-undone');await page.locator('#view').press('Control+Shift+z');await pair(label+'-redone');}
   }
   const freshOut=path.join(location,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width,height},acceptDownloads:true});await fresh.addInitScript(controlledRenderClock);await fresh.addInitScript(()=>{window.__acceptanceRenderTime=10000;});const p=await fresh.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(saved,'project');await d.download('reopened');await d.download('reopened','png');await d.snapshot('reopened');await fresh.close();row.fresh_reopen_complete=true;report.rows.push(row);
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await browser.close();console.log('LAYER '+kind+' '+report.status);if(report.status!=='Pass')process.exitCode=1;}
