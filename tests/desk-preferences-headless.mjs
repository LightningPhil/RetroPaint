import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const out=path.resolve(option('--out','test-results/desk-preferences')),origin=option('--origin','http://127.0.0.1:8094/');await fs.mkdir(out,{recursive:true});const file=path.join(out,'ACCESS-008-headless-ui.json');if(await fs.access(file).then(()=>true,()=>false))throw new Error('Choose a fresh output folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Isolated headless UI; fresh storage fixtures and explicit Storage failure injection only in disposable contexts',rows:[],errors:[]};
const context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,out);page.on('pageerror',e=>report.errors.push(String(e)));
const choose=async(p,d,value)=>{await d.drawer();await p.locator('[data-studio="view"]').click();await p.locator('#openPreferences').click();await p.locator('[data-preference-tab="desk"]').click();await p.locator(`[data-desk-choice="${value}"]`).click();assert.equal(await p.locator('body').getAttribute('data-desk'),value);for(const other of ['mint','lavender','sand','night'])assert.equal(await p.locator(`[data-desk-choice="${other}"]`).getAttribute('aria-pressed'),String(other===value));await d.snapshot('choice-'+value);await p.locator('#preferencesDone').click();await d.close();};
const mark=async p=>{await p.locator('[data-tool="draw"]').click();await p.getByRole('button',{name:'Blue',exact:true}).click();const r=await p.locator('#view').boundingBox();await p.locator('#view').click({position:{x:r.width*.3,y:r.height*.4}});};
const pair=async(d,label)=>{const saved=await d.download(label);await d.download(label,'png');return saved;};
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await mark(page);await pair(driver,'before');
 for(const value of ['mint','lavender','sand','night']){
  console.log('DESK '+value);await choose(page,driver,value);const style=await page.locator('body').evaluate(e=>getComputedStyle(e).backgroundImage);const saved=await pair(driver,'theme-'+value);
  const location=path.join(out,'reopen-'+value);await fs.mkdir(location,{recursive:true});const p=await context.newPage(),d=new AcceptanceDriver(p,location);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});assert.equal(await p.locator('body').getAttribute('data-desk'),value);assert.equal(await p.locator('body').evaluate(e=>getComputedStyle(e).backgroundImage),style);await d.open(saved,'project');await pair(d,'reopened');await d.snapshot('reopened');await p.close();report.rows.push({value,computed_background_image:style,restored_on_new_app_page:true});
 }
 await page.locator('#undoBtn').click();await pair(driver,'undone');await page.locator('#view').press('Control+Shift+z');await pair(driver,'redone');
 for(const mode of ['unknown','unavailable']){
  console.log('DESK storage '+mode);const location=path.join(out,mode);await fs.mkdir(location,{recursive:true});
  const options={viewport:{width:1280,height:720},acceptDownloads:true};if(mode==='unknown')options.storageState={cookies:[],origins:[{origin:new URL(origin).origin,localStorage:[{name:'retropaint-desk',value:'unknown-external-theme'}]}]};
  const c=await browser.newContext(options);if(mode==='unavailable')await c.addInitScript(()=>{for(const key of ['getItem','setItem'])Object.defineProperty(Storage.prototype,key,{configurable:true,value(){throw new DOMException('Storage deliberately unavailable in isolated acceptance test','SecurityError');}});});
  const p=await c.newPage(),d=new AcceptanceDriver(p,location);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});assert.equal(await p.locator('body').getAttribute('data-desk'),'mint');await mark(p);
  if(mode==='unavailable'){await choose(p,d,'night');await pair(d,'current-visit-night');await p.reload({waitUntil:'domcontentloaded'});assert.equal(await p.locator('body').getAttribute('data-desk'),'mint');await mark(p);}
  await pair(d,'fallback-usable');await d.snapshot('fallback-usable');await c.close();report.rows.push({storage_mode:mode,fallback:'mint',actual_drawing_and_download_complete:true});
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('DESK '+report.status);if(report.status!=='Pass')process.exitCode=1;}
