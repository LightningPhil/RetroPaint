import { defineConfig } from 'vite';
import { readFileSync, readdirSync, createReadStream } from 'node:fs';
import { fileURLToPath } from 'node:url';

// Ship only the two models we use, on the same origin as the app. Images never
// leave the browser, and deployment does not depend on a third-party model CDN.
const modelAssets=new Map<string,string>();
for(const scale of [2,4]){
  const directory=fileURLToPath(new URL(`./node_modules/@upscalerjs/esrgan-thick/models/x${scale}/`,import.meta.url));
  for(const file of readdirSync(directory))modelAssets.set(`models/super-resolution/${scale}/${file}`,`${directory}/${file}`);
}
modelAssets.set('models/super-resolution/LICENSE.txt',fileURLToPath(new URL('./node_modules/@upscalerjs/esrgan-thick/LICENSE',import.meta.url)));
modelAssets.set('licenses/three.txt',fileURLToPath(new URL('./node_modules/three/LICENSE',import.meta.url)));
modelAssets.set('licenses/manifold-3d.txt',fileURLToPath(new URL('./node_modules/manifold-3d/LICENSE',import.meta.url)));
modelAssets.set('licenses/replicad.txt',fileURLToPath(new URL('./node_modules/replicad/LICENSE',import.meta.url)));
modelAssets.set('licenses/opencascade.txt',fileURLToPath(new URL('./node_modules/replicad-opencascadejs/LICENSE',import.meta.url)));

// Relative asset URLs so the same build works on GitHub project pages
// (https://<user>.github.io/RetroPaint/) and under `vite preview`.
export default defineConfig({
  base: './',
  worker:{format:'es'},
  plugins:[{
    name:'local-models-and-licenses',
    configureServer(server){server.middlewares.use((request,response,next)=>{
      const path=(request.url||'').split('?')[0].replace(/^\//,''),source=modelAssets.get(path);
      if(!source){next();return;}
      response.setHeader('Content-Type',path.endsWith('.json')?'application/json':path.endsWith('.txt')?'text/plain; charset=utf-8':'application/octet-stream');
      response.setHeader('Cache-Control','public, max-age=86400');createReadStream(source).pipe(response);
    });},
    generateBundle(){for(const [fileName,path] of modelAssets)this.emitFile({type:'asset',fileName,source:readFileSync(path)});},
  }],
  server: {
    port: 8080,
    strictPort: true,
  },
  preview: {
    port: 8080,
    strictPort: true,
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
  },
});
