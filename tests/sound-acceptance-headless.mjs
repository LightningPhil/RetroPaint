import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const out=path.resolve(option('--out','test-results/sound')),origin=option('--origin','http://127.0.0.1:8094/');await fs.mkdir(out,{recursive:true});const file=path.join(out,'ACCESS-009-headless-ui.json');if(await fs.access(file).then(()=>true,()=>false))throw new Error('Choose a new folder; previous evidence retained.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});
// Observe the actual Web Audio signal at the node connected to the browser's
// output. Preserve its original connection; the observer's own output is zero.
// No application audio functions/settings are replaced or invoked directly.
await context.addInitScript(()=>{
 const original=AudioNode.prototype.connect,contexts=new WeakSet();window.__audioProbe={active:false,chunks:[],sampleRate:0,connections:0};
 AudioNode.prototype.connect=function(destination,...args){const result=original.call(this,destination,...args),ctx=this.context;
  if(destination===ctx.destination&&!contexts.has(ctx)){
   contexts.add(ctx);const probe=ctx.createScriptProcessor(4096,1,1);window.__audioProbe.sampleRate=ctx.sampleRate;window.__audioProbe.connections++;
   probe.onaudioprocess=event=>{if(window.__audioProbe.active)window.__audioProbe.chunks.push(event.inputBuffer.getChannelData(0).slice());event.outputBuffer.getChannelData(0).fill(0);};
   original.call(this,probe);original.call(probe,ctx.destination);window.__audioProbe.node=probe;
  }return result;
 };
});
const page=await context.newPage(),driver=new AcceptanceDriver(page,out),report={started:new Date().toISOString(),origin,execution:'Actual headless UI and real destination-input Web Audio PCM observer; no desktop or hardware mixer access',rows:[],errors:[],controls:[]};page.on('pageerror',e=>report.errors.push(String(e)));
const open=async()=>{await driver.drawer();await page.locator('[data-studio="view"]').click();await page.locator('#openPreferences').click();await page.locator('[data-preference-tab="sound"]').click();};
const close=async()=>{await page.locator('#preferencesDone').click();await driver.close();};
const controls=async label=>{const state={label,enabled:await page.locator('#soundEnabled').isChecked(),volume:Number(await page.locator('#soundVolume').inputValue()),drawing:await page.locator('#drawingSounds').isChecked(),quick:await page.locator('#soundToggle').getAttribute('aria-pressed'),preview_disabled:await page.locator('#soundPreview').isDisabled()};assert.equal(state.quick,String(state.enabled&&state.volume>0));assert.equal(state.preview_disabled,!(state.enabled&&state.volume>0));report.controls.push(state);await driver.snapshot(label);return state;};
const volume=async value=>{await page.locator('#soundVolume').press('Home');for(let i=0;i<value/5;i++)await page.locator('#soundVolume').press('ArrowRight');assert.equal(Number(await page.locator('#soundVolume').inputValue()),value);};
const capture=async(label,expected,action)=>{
 await page.waitForTimeout(400);await page.evaluate(()=>{window.__audioProbe.active=true;window.__audioProbe.chunks=[];});await action();await page.waitForTimeout(850);
 const data=await page.evaluate(()=>{const probe=window.__audioProbe;probe.active=false;return {sample_rate:probe.sampleRate,connections:probe.connections,frame_sizes:probe.chunks.map(a=>a.length),samples:probe.chunks.flatMap(a=>Array.from(a))};});
 const samples=new Float32Array(data.samples);await fs.writeFile(path.join(out,label+'.f32'),Buffer.from(samples.buffer));let peak=0,squares=0;for(const value of samples){peak=Math.max(peak,Math.abs(value));squares+=value*value;}
 const row={label,expected,sample_rate:data.sample_rate,frames:samples.length,frame_sizes:data.frame_sizes,connections:data.connections,peak,rms:Math.sqrt(squares/Math.max(1,samples.length)),pcm_file:label+'.f32',encoding:'little-endian float32 mono; sequential actual ScriptProcessor input blocks'};report.rows.push(row);await driver.record({action:'actual-output-pcm',...row});
 assert(samples.length>10000,'No actual audio frames captured');assert(Number.isFinite(peak));assert(expected==='audible'?peak>1e-4:peak<1e-5,label+' signal contradicts settings: '+peak);console.log('AUDIO '+label+' peak='+peak);
};
const stroke=async()=>{const r=await page.locator('#view').boundingBox();await page.mouse.move(r.x+r.width*.2,r.y+r.height*.55);await page.mouse.down();for(let i=1;i<=20;i++){await page.mouse.move(r.x+r.width*(.2+.025*i),r.y+r.height*.55);await page.waitForTimeout(25);}await page.mouse.up();};
const undoStroke=async label=>{await page.locator('#undoBtn').click();await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await driver.canvas('#view',label+'-undone-visible');};
const pair=async label=>{const saved=await driver.download(label);await driver.download(label,'png');return saved;};
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await pair('before');await open();await controls('initial');await capture('preview-volume45','audible',()=>page.locator('#soundPreview').click());
 await volume(100);await controls('volume100');await capture('preview-volume100','audible',()=>page.locator('#soundPreview').click());
 await volume(0);await controls('zero-volume');assert(await page.locator('#soundPreview').isDisabled());await close();
 await capture('zero-feedback-and-paint','silent',async()=>{await page.getByRole('button',{name:'Blue',exact:true}).click();await stroke();});await undoStroke('zero');
 await open();await volume(45);await close();await page.locator('#soundToggle').click();assert.equal(await page.locator('#soundToggle').getAttribute('aria-pressed'),'false');await open();assert.equal((await controls('speaker-muted')).enabled,false);await close();
 await capture('muted-feedback-and-paint','silent',async()=>{await page.getByRole('button',{name:'Blue',exact:true}).click();await stroke();});await undoStroke('muted');
 await page.locator('#view').press('m');assert.equal(await page.locator('#soundToggle').getAttribute('aria-pressed'),'true');await open();let state=await controls('keyboard-unmuted');assert(state.enabled&&state.volume===45&&state.drawing);await close();
 await capture('painting-enabled','audible',stroke);await undoStroke('drawing-enabled');
 await open();await page.locator('#drawingSounds').uncheck();await controls('painting-off');await capture('feedback-with-painting-off','audible',()=>page.locator('#soundPreview').click());await close();await capture('painting-disabled','silent',stroke);await undoStroke('drawing-disabled');
 await open();await volume(65);await page.locator('#soundEnabled').uncheck();state=await controls('checkbox-muted-persisted');assert(!state.enabled&&state.volume===65&&!state.drawing);await close();const saved=await pair('after-settings');
 const freshOut=path.join(out,'fresh');await fs.mkdir(freshOut,{recursive:true});const p=await context.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});await d.drawer();await p.locator('[data-studio="view"]').click();await p.locator('#openPreferences').click();const restored={enabled:await p.locator('#soundEnabled').isChecked(),volume:Number(await p.locator('#soundVolume').inputValue()),drawing:await p.locator('#drawingSounds').isChecked(),quick:await p.locator('#soundToggle').getAttribute('aria-pressed'),preview_disabled:await p.locator('#soundPreview').isDisabled()};assert.deepEqual(restored,{enabled:false,volume:65,drawing:false,quick:'false',preview_disabled:true});await d.snapshot('restored-settings');await p.locator('#preferencesDone').click();await d.close();await d.open(saved,'project');await d.download('reopened');await d.download('reopened','png');await p.close();report.restored=restored;report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('AUDIO '+report.status);if(report.status!=='Pass')process.exitCode=1;}
