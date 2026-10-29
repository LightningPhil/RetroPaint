// Real app controls, file inputs and actual download payloads in an isolated
// headless context. Independent Python verification evaluates the saved bytes.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export async function testReset(browser,{out,origin,fixture,progress}){
  const report={started:new Date().toISOString(),status:'In progress',execution:'Headless automated UI, desktop mouse/keyboard; native chooser and physical device behavior are not certified',fixture,downloads:[],observations:[]};
  const raw=await fs.readFile(fixture);report.fixture_sha256=createHash('sha256').update(raw).digest('hex');
  const baseline=JSON.parse(raw);
  let context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});
  let page=await context.newPage();page.setDefaultTimeout(180000);
  const errors=[];page.on('pageerror',error=>errors.push(String(error)));
  const saveReport=async()=>fs.writeFile(path.join(out,'PHOTO-008-headless-ui.json'),JSON.stringify({...report,errors},null,2)+'\n');
  async function drawer(){if(await page.locator('#studioBtn').getAttribute('aria-expanded')!=='true')await page.locator('#studioBtn').click();await page.getByRole('tab',{name:'📁 File',exact:true}).click();}
  async function closeDrawer(){if(await page.locator('#studioBtn').getAttribute('aria-expanded')==='true')await page.getByRole('button',{name:'Close options',exact:true}).click();}
  async function openProject(file){
    await drawer();const pending=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Open project',exact:true}).click();await(await pending).setFiles(file);
    await page.locator('#editorStatus').getByText('Project opened with editable pieces, layers, photo adjustments and live ink.',{exact:true}).waitFor();await closeDrawer();
  }
  async function download(label,kind){
    progress(label+' '+kind);await drawer();await page.getByRole('textbox',{name:'Name',exact:true}).fill(label);if(kind==='png')await page.locator('#fileFormat').selectOption('png');
    const start=Date.now(),pending=page.waitForEvent('download',{timeout:180000});await page.getByRole('button',{name:kind==='png'?'Save as':'Save project',exact:true}).click();const payload=await pending;
    const target=path.join(out,label+'.'+(kind==='png'?'png':'retropaint'));await payload.saveAs(target);assert.equal(await payload.failure(),null);
    const bytes=await fs.readFile(target);if(kind==='png')assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a');else assert.equal(JSON.parse(bytes).format,'RetroPaint');
    report.downloads.push({label,kind,bytes:bytes.length,filename:payload.suggestedFilename(),sha256:createHash('sha256').update(bytes).digest('hex'),elapsed_ms:Date.now()-start});await closeDrawer();await saveReport();return target;
  }
  async function snapshot(label){await page.screenshot({path:path.join(out,label+'-ui.png')});await fs.writeFile(path.join(out,label+'.txt'),await page.locator('body').innerText());report.observations.push({label,at:new Date().toISOString()});await saveReport();}
  try{
    progress('open preserved fixture');await page.goto(origin,{waitUntil:'domcontentloaded'});await openProject(fixture);
    await drawer();await page.getByRole('switch',{name:'Advanced mode',exact:true}).check();await closeDrawer();
    const start=await download('PHOTO-008-headless-before','project');assert.deepEqual(JSON.parse(await fs.readFile(start,'utf8')),baseline);
    await download('PHOTO-008-headless-before','png');
    progress('Reset then Cancel');await page.locator('#photoToggle').click();await page.locator('#photoReset').click();await page.locator('#photoStatus[aria-busy="false"]').waitFor();await snapshot('PHOTO-008-headless-reset-before-cancel');await page.locator('#photoCancel').click();
    const cancelled=await download('PHOTO-008-all-settings-reset-cancelled','project');assert.deepEqual(JSON.parse(await fs.readFile(cancelled,'utf8')),baseline);await download('PHOTO-008-all-settings-reset-cancelled','png');
    progress('Reset then Done');await page.locator('#photoToggle').click();await page.locator('#photoReset').click();await page.locator('#photoStatus[aria-busy="false"]').waitFor();await snapshot('PHOTO-008-headless-reset-before-done');await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});
    await snapshot('PHOTO-008-headless-reset-completed');const committed=await download('PHOTO-008-all-settings-reset-done','project');await download('PHOTO-008-all-settings-reset-done','png');
    progress('Undo');await page.locator('#undoBtn').click();const undone=await download('PHOTO-008-all-settings-reset-undone','project');assert.deepEqual(JSON.parse(await fs.readFile(undone,'utf8')),baseline);await download('PHOTO-008-all-settings-reset-undone','png');
    progress('Redo');await page.locator('#view').press('Control+Shift+z');await download('PHOTO-008-all-settings-reset-redone','project');await download('PHOTO-008-all-settings-reset-redone','png');
    await context.close();context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});page=await context.newPage();page.setDefaultTimeout(180000);page.on('pageerror',error=>errors.push(String(error)));
    progress('fresh project reopen');await page.goto(origin,{waitUntil:'domcontentloaded'});await openProject(committed);await download('PHOTO-008-all-settings-reset-reopened','project');await download('PHOTO-008-all-settings-reset-reopened','png');await snapshot('PHOTO-008-headless-reopened');
    assert.deepEqual(errors,[]);report.status='Pass';
  }catch(error){report.status='Fail';report.error=String(error.stack??error);await snapshot('PHOTO-008-headless-failure').catch(()=>{});}
  finally{report.finished=new Date().toISOString();await saveReport();await context.close();}
  return report;
}
