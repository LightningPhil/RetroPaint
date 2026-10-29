import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const out=path.resolve(option('--out','test-results/shortcuts')),origin=option('--origin','http://127.0.0.1:8094/');await fs.mkdir(out,{recursive:true});const reportFile=path.join(out,'START-009-headless-ui.json');if(await fs.access(reportFile).then(()=>true,()=>false))throw new Error('Retained evidence exists; choose a fresh folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Separate isolated headless browser contexts; real public controls and downloads',rows:[],errors:[]};
try{
 for(const [width,height] of [[1280,720],[320,568],[390,844],[844,390]]){
  console.log('HELP '+width+'x'+height);const location=path.join(out,width+'x'+height);await fs.mkdir(location,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,location);page.on('pageerror',e=>report.errors.push(String(e)));
  try{
   await page.goto(origin,{waitUntil:'domcontentloaded'});await page.locator('[data-tool="stamp"]').click();await page.getByRole('button',{name:'Stamp 🐱',exact:true}).click();
   await page.locator('#brushSize').press('Home');for(let i=0;i<13;i++)await page.locator('#brushSize').press('ArrowRight');assert.equal(Number(await page.locator('#stampScale').inputValue()),1.7);
   const bounds=await page.locator('#view').boundingBox();await page.locator('#view').click({position:{x:bounds.width*.25,y:bounds.height*.35}});await driver.download('before');await driver.download('before','png');await driver.snapshot('before');
   const row={width,height,categories:[],dismissals:[],blocked_keys:[],unexpected_downloads:0,unexpected_choosers:0};let watch=false;page.on('download',()=>{if(watch)row.unexpected_downloads++;});page.on('filechooser',()=>{if(watch)row.unexpected_choosers++;});
   for(const dismissal of ['done','escape']){
    await driver.drawer();await page.locator('[data-studio="view"]').click();await page.locator('#openShortcuts').click();await page.locator('#shortcutsDialog[open]').waitFor();
    for(const category of ['tools','edit','view']){
     await page.locator(`[data-shortcut-tab="${category}"]`).click();
     const measured=await page.locator('#shortcutsDialog').evaluate(dialog=>{const rect=e=>{const r=e.getBoundingClientRect();return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height};};return {viewport:[innerWidth,innerHeight],dialog:rect(dialog),scroll:dialog.scrollHeight,client:dialog.clientHeight,rows:[...dialog.querySelectorAll('.shortcut-grid>div')].filter(e=>e.getClientRects().length).map(e=>({rect:rect(e),scroll:e.scrollWidth,client:e.clientWidth,text:e.innerText}))};});
     const fits=r=>r.left>=-1&&r.top>=-1&&r.right<=width+1&&r.bottom<=height+1;assert(fits(measured.dialog),'Help dialog exceeds viewport');assert(measured.scroll<=measured.client+1,'Help dialog clips content');for(const item of measured.rows){assert(fits(item.rect),'Shortcut row exceeds viewport: '+item.text);assert(item.scroll<=item.client+1,'Shortcut row clips text: '+item.text);}
     await driver.snapshot(dismissal+'-'+category);row.categories.push({dismissal,category,measured});
    }
    watch=true;await page.locator('#shortcutsDone').focus();for(const key of ['b','e','t','r','Delete','Control+z','Control+Shift+z','Control+a','Control+s','Control+o']){await page.keyboard.press(key);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));assert.equal(await page.locator('#shortcutsDialog').getAttribute('open'),'');assert(await page.locator('[data-tool="stamp"]').evaluate(e=>e.classList.contains('active')));row.blocked_keys.push({dismissal,key});}watch=false;
    if(dismissal==='done')await page.locator('#shortcutsDone').click();else await page.keyboard.press('Escape');await page.locator('#shortcutsDialog').waitFor({state:'hidden'});
    const focus=await page.evaluate(()=>{const e=document.activeElement;return {id:e?.id,tag:e?.tagName,visible:!!e?.getClientRects().length};});assert.equal(focus.id,'openShortcuts');assert(focus.visible);row.dismissals.push({dismissal,focus});await driver.close();
    assert.equal(Number(await page.locator('#stampScale').inputValue()),1.7);assert(await page.locator('[data-tool="stamp"]').evaluate(e=>e.classList.contains('active')));
    await driver.download('after-'+dismissal);await driver.download('after-'+dismissal,'png');
   }
   assert.equal(row.unexpected_downloads,0);assert.equal(row.unexpected_choosers,0);
   // Resume stamping and prove that one Undo removes just the next gesture.
   const r=await page.locator('#view').boundingBox();await page.locator('#view').click({position:{x:r.width*.65,y:r.height*.65}});await driver.download('resumed');await driver.download('resumed','png');await page.locator('#undoBtn').click();await driver.download('resumed-undone');await driver.download('resumed-undone','png');await page.locator('#view').press('Control+Shift+z');await driver.download('resumed-redone');await driver.download('resumed-redone','png');report.rows.push(row);
  }finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(reportFile,JSON.stringify(report,null,2)+'\n');await browser.close();console.log('HELP '+report.status);if(report.status!=='Pass')process.exitCode=1;}
