// Actual browser UI downloads. The event watcher misses child-frame downloads,
// so correlate unique requested names with newly created files on disk.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {makeHarness,root} from './browser-harness.mjs';
const downloads='C:/Users/pglei/Downloads';
export function makeFrameHarness(tab,selector='iframe'){
  const frame=tab.playwright.frameLocator(selector);
  const io={id:tab.id+'-frame',playwright:{locator:s=>frame.locator(s),getByRole:(r,o)=>frame.getByRole(r,o),waitForEvent:(e,o)=>tab.playwright.waitForEvent(e,o)},getAXState:o=>tab.getAXState(o),getScreenshot:o=>tab.getScreenshot(o)};
  const audit=makeHarness(io);
  audit.frame=frame;
  audit.export=async function(label,format='png'){
    await this.drawer();await frame.getByRole('textbox',{name:'Name',exact:true}).fill(label);
    if(format!=='project')await frame.locator('#fileFormat').selectOption(format);
    const extension=format==='project'?'retropaint':format==='jpeg'?'jpg':format==='tiff'?'tif':format;
    const before=new Set(await fs.readdir(downloads)),started=new Date().toISOString();
    await frame.getByRole('button',{name:format==='project'?'Save project':'Save as',exact:true}).click();await tab.getAXState({emit:false});
    let candidates=[],attempts=0;
    while(attempts++<40){
      candidates=(await fs.readdir(downloads)).filter(name=>!before.has(name)&&name.toLowerCase().startsWith(label.toLowerCase())&&name.toLowerCase().endsWith('.'+extension));
      if(candidates.length)break;
      await new Promise(resolve=>setTimeout(resolve,250));
    }
    if(candidates.length!==1)throw new Error('Expected one newly written '+label+' file; found '+candidates.length);
    const actual=downloads+'/'+candidates[0],bytes=await fs.readFile(actual);
    if(format==='project'&&JSON.parse(bytes.toString('utf8')).format!=='RetroPaint')throw new Error('Saved file is not a RetroPaint project');
    if(format==='png'&&!bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))throw new Error('Saved file is not PNG');
    await fs.copyFile(actual,root+'/evidence/'+label+'.'+extension);
    const event={started,finished:new Date().toISOString(),tab:tab.id,label,format,actual_download:actual,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')};
    await fs.appendFile(root+'/frame-download-events.jsonl',JSON.stringify(event)+'\n');await this.close();return event;
  };
  audit.project=function(label){return this.export(label,'project');};
  audit.png=function(label){return this.export(label,'png');};
  audit.stroke=async function(x1,y1,x2,y2){
    const outer=await tab.playwright.locator(selector).evaluate(e=>{const r=e.getBoundingClientRect();return {left:r.left,top:r.top};});
    const r=await frame.locator('#view').evaluate(e=>{const r=e.getBoundingClientRect();return {left:r.left,top:r.top,width:r.width,height:r.height,sourceWidth:e.width,sourceHeight:e.height};});
    if([x1,x2].some(x=>x<0||x>=r.sourceWidth)||[y1,y2].some(y=>y<0||y>=r.sourceHeight))throw new Error('Stroke outside source canvas');
    const point=(x,y)=>[outer.left+r.left+x*r.width/r.sourceWidth,outer.top+r.top+y*r.height/r.sourceHeight];
    await tab.drag(point(x1,y1),point(x2,y2));await tab.getAXState({emit:false});
  };
  return audit;
}
