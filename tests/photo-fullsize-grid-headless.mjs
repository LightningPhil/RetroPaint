import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/photo-fullsize-grid')),origin=option('--origin','http://127.0.0.1:8094/');
await fs.mkdir(out,{recursive:true});const file=path.join(out,'PHOTO-018-grid-ui.json');if(await fs.access(file).then(()=>true,()=>false))throw new Error('Choose a new folder; evidence retained.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,out),report={started:new Date().toISOString(),origin,execution:'Isolated headless UI; actual full-resolution parity-grid image input, detail controls and downloads',errors:[]};page.on('pageerror',e=>report.errors.push(String(e)));
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();await driver.open(path.join(root,'fixtures/FULLSIZE-grid.png'));await driver.download('grid-before');await driver.download('grid-before','png');await driver.photo();await driver.group('detail','detail-sharp');await driver.slider('Sharpness',80);await driver.slider('Threshold · protect smooth areas',5);await driver.ready();await driver.canvas('#photoMiniCanvas','grid-public-preview');await driver.snapshot('grid-draft');
 await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});const saved=await driver.download('grid-done');await driver.download('grid-done','png');
 const freshOut=path.join(out,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),p=await fresh.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(saved,'project');await d.download('grid-reopened');await d.download('grid-reopened','png');await d.snapshot('grid-reopened');await fresh.close();report.fresh_reopen_complete=true;report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('GRID '+report.status);if(report.status!=='Pass')process.exitCode=1;}
