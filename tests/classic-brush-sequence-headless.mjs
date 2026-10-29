import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];},out=path.resolve(option('--out','test-results/classic-sequence')),origin=option('--origin','http://127.0.0.1:8101/');await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0,'Keep earlier sequence evidence');
const report={started:new Date().toISOString(),origin,scope:'PAINT-007 actual UI execution, one isolated headless browser at a time; all56 boundary rows and four main material flows must finish before independent verification.',steps:[]};let active='starting';const save=()=>fs.writeFile(path.join(out,'sequence.json'),JSON.stringify(report,null,2)+'\n'),progress=setInterval(()=>console.log('CLASSIC-SEQUENCE '+active+' '+new Date().toISOString()),20000);
try{
 for(const kind of ['brush','oil','crayon','natural','main']){
  active=kind;const folder=path.join(out,kind),script=path.resolve(kind==='main'?'tests/classic-brush-main-headless.mjs':'tests/classic-brush-boundary-headless.mjs'),childArgs=[script,'--origin',origin,'--out',folder,...(kind==='main'?[]:['--applicator',kind])],started=new Date().toISOString();console.log('CLASSIC-SEQUENCE START '+kind);
  const code=await new Promise((resolve,reject)=>{const child=spawn(process.execPath,childArgs,{stdio:'inherit',windowsHide:true});child.once('error',reject);child.once('exit',resolve);});const ui=JSON.parse(await fs.readFile(path.join(folder,kind==='main'?'PAINT-007-main-ui.json':`PAINT-007-${kind}-ui.json`),'utf8'));report.steps.push({kind,started,finished:new Date().toISOString(),exit_code:code,status:ui.status,completed_rows:ui.rows.length,folder});await save();assert.equal(code,0,'Child workflow failed; all original evidence retained');assert.equal(ui.status,'Pass');assert.equal(ui.rows.length,kind==='main'?4:14);
 }
 report.status='Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);process.exitCode=1;}
finally{clearInterval(progress);report.finished=new Date().toISOString();await save();console.log('CLASSIC-SEQUENCE '+report.status);}
