// CUA orchestration only. This module never imports or mutates browser application state.
import fs from 'node:fs/promises';
export const root='F:/WebDev/RetroPaint/APP-USE-CASES/runs/2026-10-19-full-audit';
export function makeHarness(tab){
  return {tab,
    async observe(label){
      const state=await tab.getAXState({emit:false,disableDiffing:true});
      await fs.writeFile(root+'/evidence/'+label+'.txt',state);
      await fs.writeFile(root+'/evidence/'+label+'-ui.jpg',await tab.getScreenshot({emit:false}));
      await fs.appendFile(root+'/ui-events-current.jsonl',JSON.stringify({at:new Date().toISOString(),tab:tab.id,label})+'\n');
      return state;
    },
    async drawer(){
      if(await tab.playwright.locator('#studioBtn').getAttribute('aria-expanded')!=='true')await tab.playwright.locator('#studioBtn').click();
      await tab.playwright.getByRole('tab',{name:'📁 File',exact:true}).click();
      await tab.getAXState({emit:false});
    },
    async close(){if(await tab.playwright.locator('#studioBtn').getAttribute('aria-expanded')==='true'){await tab.playwright.getByRole('button',{name:'Close options',exact:true}).click();await tab.getAXState({emit:false});}},
    async open(path,kind='image'){
      await this.drawer();
      const pending=tab.playwright.waitForEvent('filechooser',{timeoutMs:10000}).catch(error=>({error}));
      await tab.playwright.getByRole('button',{name:kind==='project'?'Open project':'Open image',exact:true}).click();
      const chooser=await pending;if(chooser.error)throw chooser.error;
      await chooser.setFiles([path]);await tab.getAXState({emit:false});
    },
    async project(label){
      await this.drawer();await tab.playwright.getByRole('textbox',{name:'Name',exact:true}).fill(label);
      const pending=tab.playwright.waitForEvent('download',{timeoutMs:15000}).catch(error=>({error}));
      await tab.playwright.getByRole('button',{name:'Save project',exact:true}).click();
      const downloaded=await pending;if(downloaded.error)throw downloaded.error;
      const path=await downloaded.path();if(!path)throw new Error('Download produced no path');
      await fs.copyFile(path,root+'/evidence/'+label+'.retropaint');await this.close();
    },
    async png(label){
      await this.close();const pending=tab.playwright.waitForEvent('download',{timeoutMs:15000}).catch(error=>({error}));
      await tab.playwright.getByRole('button',{name:'SAVE',exact:true}).click();
      const downloaded=await pending;if(downloaded.error)throw downloaded.error;
      const path=await downloaded.path();if(!path)throw new Error('Download produced no path');
      await fs.copyFile(path,root+'/evidence/'+label+'.png');await tab.getAXState({emit:false});
    },
    async pngAs(label){
      await this.drawer();
      await tab.playwright.getByRole('textbox',{name:'Name',exact:true}).fill(label);
      await tab.playwright.locator('#fileFormat').selectOption({label:'PNG'});
      const pending=tab.playwright.waitForEvent('download',{timeoutMs:45000}).catch(error=>({error}));
      await tab.playwright.getByRole('button',{name:'Save as',exact:true}).click();
      const downloaded=await pending;if(downloaded.error)throw downloaded.error;
      const path=await downloaded.path({timeoutMs:45000});if(!path)throw new Error('Download produced no path');
      await fs.copyFile(path,root+'/evidence/'+label+'.png');
      await fs.appendFile(root+'/ui-events-current.jsonl',JSON.stringify({at:new Date().toISOString(),tab:tab.id,label,downloadPath:path,method:'Named Save as PNG'})+'\n');
      await this.close();
    },
    async rejectProject(name,expected){
      await this.open(root+'/fixtures/'+name+'.retropaint','project');
      await tab.playwright.locator('#editorStatus').getByText(expected).waitFor({state:'visible',timeoutMs:10000});
      await this.observe('FILE-016-fixed-'+name);await this.project('FILE-016-fixed-'+name);
      await this.open(root+'/evidence/FILE-016-unsaved-before.retropaint','project');
      await tab.playwright.getByText('Project opened with editable pieces, layers, photo adjustments and live ink.',{exact:true}).waitFor({state:'visible',timeoutMs:10000});
      await tab.getAXState({emit:false});return name+' rejected; valid file reopened';
    },
    async stroke(x1,y1,x2,y2){
      const r=await tab.playwright.locator('#view').evaluate(e=>{const r=e.getBoundingClientRect();return {left:r.left,top:r.top,width:r.width,height:r.height,sourceWidth:e.width,sourceHeight:e.height};});
      if([x1,x2].some(x=>x<0||x>=r.sourceWidth)||[y1,y2].some(y=>y<0||y>=r.sourceHeight))throw new Error('Stroke is outside source canvas');
      await tab.drag([r.left+x1*r.width/r.sourceWidth,r.top+y1*r.height/r.sourceHeight],[r.left+x2*r.width/r.sourceWidth,r.top+y2*r.height/r.sourceHeight]);await tab.getAXState({emit:false});
    }
  };
}
