// Actual project controls/downloads in two fresh headless contexts. This never
// attaches to a visible browser or reads its storage/profile.
import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const fixture=path.resolve(option('--fixture','APP-USE-CASES/runs/2026-10-19-full-audit/backups/artwork-before-acceptance-audit.retropaint'));
const out=path.resolve(option('--out','test-results/project-roundtrip'));
const origin=option('--origin','http://127.0.0.1:8093/');
const source=await fs.readFile(fixture),sha=bytes=>createHash('sha256').update(bytes).digest('hex');
await fs.mkdir(out,{recursive:true});
if(await fs.access(path.join(out,'ARTWORK-headless-ui.json')).then(()=>true,()=>false))throw new Error('Choose a new output folder; previous evidence is retained here.');
const report={started:new Date().toISOString(),fixture,original_sha256:sha(source),origin,execution:'Two isolated headless contexts; actual project chooser and download payloads; no desktop interaction',downloads:[]};
const browser=await chromium.launch({headless:true,channel:option('--channel','chrome')});
try{
 let file=fixture;
 for(const label of ['ARTWORK-headless-saved','ARTWORK-headless-reopened']){
  console.log('ARTWORK '+label);const context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage();page.setDefaultTimeout(120000);
  const errors=[];page.on('pageerror',error=>errors.push(String(error)));await page.goto(origin,{waitUntil:'domcontentloaded'});
  const drawer=async()=>{if(await page.locator('#studioBtn').getAttribute('aria-expanded')!=='true')await page.locator('#studioBtn').click();await page.getByRole('tab',{name:'📁 File',exact:true}).click();};
  await drawer();let pending=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Open project',exact:true}).click();await(await pending).setFiles(file);await page.locator('#editorStatus').getByText('Project opened with editable pieces, layers, photo adjustments and live ink.',{exact:true}).waitFor();
  await drawer();await page.getByRole('textbox',{name:'Name',exact:true}).fill(label);
  for(const kind of ['project','png']){
   if(kind==='png')await page.locator('#fileFormat').selectOption('png');pending=page.waitForEvent('download');await page.getByRole('button',{name:kind==='project'?'Save project':'Save as',exact:true}).click();const download=await pending;
   const target=path.join(out,label+'.'+(kind==='project'?'retropaint':'png'));await download.saveAs(target);assert.equal(await download.failure(),null);const bytes=await fs.readFile(target);if(kind==='project'){assert.deepEqual(bytes,source);file=target;}else assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
   report.downloads.push({label,kind,filename:download.suggestedFilename(),bytes:bytes.length,sha256:sha(bytes),path:target});
  }
  await page.getByRole('button',{name:'Close options',exact:true}).click();await page.screenshot({path:path.join(out,label+'-ui.png')});assert.deepEqual(errors,[]);await context.close();
 }
 report.status='Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);process.exitCode=1;}
finally{await browser.close();report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'ARTWORK-headless-ui.json'),JSON.stringify(report,null,2)+'\n');console.log(report.status+' actual artwork project roundtrip');}
