import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/layer-limits')),origin=option('--origin','http://127.0.0.1:8097/'),only=option('--variant','all');
await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0,'Choose a fresh evidence directory');
const manifest=JSON.parse(await fs.readFile(path.join(root,'fixtures/layer-limits/manifest.json'),'utf8')),browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Real image inputs, layer buttons, disabled native attempts, history and fresh project chooser in isolated headless contexts; no desktop access.',fixtures:manifest,rows:[],errors:[]};
try{
 for(const fixture of manifest.fixtures.filter(f=>only==='all'||f.label===only)){
  console.log('LIMIT '+fixture.label);const folder=path.join(out,fixture.label);await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,folder);page.setDefaultTimeout(60000);page.on('pageerror',e=>report.errors.push(String(e)));
  const list=async()=>{if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();if(await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();};
  const options=async()=>{await list();await page.locator('#layerOptions summary').click();};
  try{
   await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.open(path.resolve(fixture.file),'image');if(await page.locator('#photoPanel').isVisible())await page.locator('#photoCancel').click();await driver.advanced();await driver.download('before');
   await list();for(let count=1;count<fixture.max_layers;count++){assert.equal(await page.locator('#addLayer').isDisabled(),false);await page.locator('#addLayer').click();assert.equal(Number(await page.locator('#layerCount').innerText()),count+1);await driver.record({action:'actual-add-layer',count:count+1,stored_pixels:(count+1)*fixture.width*fixture.height});}
   assert(await page.locator('#addLayer').isDisabled());assert(await page.locator('#duplicateLayer').isDisabled());const full=await driver.download('at-limit');await driver.snapshot('at-limit');await list();const rect=await page.locator('#addLayer').boundingBox();await page.mouse.click(rect.x+rect.width/2,rect.y+rect.height/2);await driver.download('rejected-add');
   const hint=await page.locator('#layersHint').innerText(),title=await page.locator('#addLayer').getAttribute('title'),explanation=hint+' '+(title??'');await driver.record({action:'limit-explanation',hint,title});
   assert(fixture.label==='count'?/16\s+(?:sheets|layers)|stack is full|layer limit/i.test(explanation):/64.?million|64[,. ]000[,. ]000|pixel.*(budget|limit)/i.test(explanation),'Layer limit does not explain the actual limiting condition: '+explanation);
   await options();await page.locator('#deleteLayer').click();await driver.download('space-released');await list();assert.equal(await page.locator('#addLayer').isDisabled(),false);await page.locator('#addLayer').click();assert.equal(Number(await page.locator('#layerCount').innerText()),fixture.max_layers);const saved=await driver.download('space-reused');
   await page.locator('#undoBtn').click();await driver.download('add-undone');await page.locator('#view').press('Control+Shift+z');await driver.download('add-redone');
   const freshFolder=path.join(folder,'fresh');await fs.mkdir(freshFolder,{recursive:true});const fresh=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),p=await fresh.newPage(),d=new AcceptanceDriver(p,freshFolder);p.on('pageerror',e=>report.errors.push(String(e)));try{await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(saved,'project');await d.download('reopened');await d.download('reopened','png');await d.snapshot('reopened');}finally{await fresh.close();}
   report.rows.push({label:fixture.label,width:fixture.width,height:fixture.height,count:fixture.max_layers,stored_pixels:fixture.width*fixture.height*fixture.max_layers,rejected_next_pixels:fixture.width*fixture.height*(fixture.max_layers+1),hint,title,original_full_stack:full,actual_rejection_release_reuse_history_and_fresh_reopen:true});
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'LAYER-012-ui.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log('LIMIT '+report.status);if(report.status!=='Pass')process.exitCode=1;}
