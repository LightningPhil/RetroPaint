// Each render gets a fresh, disposable OpenSCAD process and virtual filesystem.
import OpenSCAD from './openscad.js';
self.onmessage = async ({data}) => {
  const logs=[],diagnostics=[];let logSize=0,diagnosticSize=0,fatal=false,truncated=false;
  const report=value=>{
    const line=String(value),diagnostic=/^(ERROR:|WARNING:)/i.test(line);
    // ECHO strings may contain "ERROR:". Only actual diagnostics can fail a render.
    if(/^ERROR:|^WARNING:.*(Can't open|Can't find|cannot open|Unable to open)/i.test(line))fatal=true;
    if(diagnostic&&diagnosticSize<16000){diagnostics.push(line.slice(0,4000));diagnosticSize+=line.length;}
    if(logSize<48000){logs.push(line.slice(0,4000));logSize+=line.length;}
    else if(!truncated){logs.push('Output truncated: further echo messages omitted.');truncated=true;}
  };
  try {
    const font=await fetch(new URL('./NotoSans-Regular.ttf',import.meta.url));
    if(!font.ok)throw new Error('The bundled font could not be loaded.');
    const fontBytes=new Uint8Array(await font.arrayBuffer());
    const engine=await OpenSCAD({noInitialRun:true,preRun:[module=>{module.ENV.FONTCONFIG_PATH='/etc/fonts';module.ENV.FONTCONFIG_FILE='/etc/fonts/fonts.conf';module.ENV.OPENSCADPATH='/project:/project/libraries:/libraries';}],locateFile:name=>new URL(name,import.meta.url).href,print:report,printErr:report});
    const fs=engine.FS;
    const library=await fetch(new URL('./mcad.json',import.meta.url));if(!library.ok)throw new Error('The bundled MCAD library could not be loaded.');
    for(const file of await library.json()){const path='/libraries/MCAD/'+file.path;fs.mkdirTree(path.slice(0,path.lastIndexOf('/')));fs.writeFile(path,Uint8Array.from(atob(file.data),c=>c.charCodeAt(0)));}
    fs.mkdirTree('/project');fs.mkdirTree('/fonts');fs.mkdirTree('/etc/fonts');
    fs.writeFile('/fonts/NotoSans-Regular.ttf',fontBytes);
    fs.writeFile('/etc/fonts/fonts.conf','<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>/fonts</dir><dir>/project</dir><cachedir>/tmp/font-cache</cachedir></fontconfig>');
    engine.ENV.FONTCONFIG_PATH='/etc/fonts';engine.ENV.OPENSCADPATH='/project:/project/libraries:/libraries';
    for(const file of data.files){const path='/project/'+file.path;fs.mkdirTree(path.slice(0,path.lastIndexOf('/')));fs.writeFile(path,Uint8Array.from(atob(file.data),c=>c.charCodeAt(0)));}
    fs.mkdirTree(('/project/'+data.entry).slice(0,('/project/'+data.entry).lastIndexOf('/')));fs.writeFile('/project/'+data.entry,data.source);fs.chdir('/project');
    const code=engine.callMain(['/project/'+data.entry,'--backend=Manifold','--export-format=binstl','-o','/output.stl']);
    // OpenSCAD permits missing includes/imports as warnings. Do not commit partial models.
    if(code||fatal){const details=diagnostics.length?diagnostics.join('\n'):logs.join('\n');const hint=/not a 3D object|top level object is empty/i.test(details)?'No 3D solid was produced. Extrude 2D profiles, and check for an empty intersection or difference.\n':'';throw new Error(hint+(details||'OpenSCAD could not render this file.'));}
    let bytes;try{bytes=fs.readFile('/output.stl');}catch{throw new Error('No 3D solid was produced. Extrude 2D profiles, and check for an empty intersection or difference.');}
    if(!bytes.length)throw new Error('No 3D solid was produced. Extrude 2D profiles, and check for an empty intersection or difference.');
    for(const line of diagnostics)if(!logs.includes(line))logs.push(line);
    self.postMessage({bytes,logs},[bytes.buffer]);
  } catch(error) {self.postMessage({error:String(error?.message||error).slice(0,16000)});}
};
