import fs from 'node:fs/promises';
import path from 'node:path';

// Normal application startup in an isolated browser profile. The layout test
// preview intentionally disables automatic recovery, so it cannot cover this.
export async function testRecoveryResume(browser,{origin,out}){
 const context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});
 const page=await context.newPage();page.setDefaultTimeout(15000);const errors=[];
 page.on('pageerror',error=>errors.push(String(error)));
 const result={status:'Fail',cycles:0,errors};
 const save=async(name)=>{
  await page.locator('#studioBtn').click();await page.locator('[data-studio="file"]').click();
  await page.locator('#fileName').fill('Recovery reload regression');
  const pending=page.waitForEvent('download');await page.locator('#saveProject').click();
  const download=await pending;const file=path.join(out,name+'.retropaint');await download.saveAs(file);
  await page.locator('#studioBtn').click();return JSON.parse(await fs.readFile(file,'utf8'));
 };
 try{
  await page.goto(origin,{waitUntil:'domcontentloaded'});
  await page.getByRole('button',{name:'Blue',exact:true}).click();
  const r=await page.locator('#view').boundingBox();if(!r)throw Error('Missing ready paper');
  await page.mouse.move(r.x+r.width*.25,r.y+r.height*.4);await page.mouse.down();
  await page.mouse.move(r.x+r.width*.55,r.y+r.height*.4,{steps:8});await page.mouse.up();
  const baseline=await save('recovery-resume-baseline');
  await page.waitForFunction(()=>document.querySelector('#draftStatus')?.textContent==='Draft saved');
  for(let cycle=1;cycle<=3;cycle++){
   await page.reload({waitUntil:'domcontentloaded'});
   await page.getByRole('button',{name:'Resume',exact:true}).click();
   await page.waitForFunction(()=>document.querySelector('#draftStatus')?.textContent==='Draft restored');
   const actual=await save('recovery-resume-cycle-'+cycle);
   if(JSON.stringify(actual)!==JSON.stringify(baseline))throw Error('Recovered document changed at cycle '+cycle);
   result.cycles=cycle;
  }
  if(errors.length)throw Error(errors.join('\n'));
  result.status='Pass';result.wholeDocumentExact=true;
 }catch(error){result.error=String(error.stack??error);}
 finally{await page.screenshot({path:path.join(out,'recovery-resume.png')});await context.close();}
 return result;
}
