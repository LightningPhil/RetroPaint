import { binaryStl, printMesh, solidMesh, solidEdges, solidFaces } from './cad-kernel';
import type { CadBody } from './cad-model';

interface Request { id: number; action: 'mesh' | 'print' | 'edges' | 'faces'; bodies: CadBody[]; bed?: boolean }
let queue = Promise.resolve();
self.addEventListener('message', (event: MessageEvent<Request>) => {
  const request = event.data;
  queue = queue.then(async () => {
    self.postMessage({id:request.id,started:true});
    try {
      if (request.action === 'print') {
        const mesh = await printMesh(request.bodies, request.bed), stl = binaryStl(mesh);
        self.postMessage({ id: request.id, mesh, stl }, { transfer: [mesh.positions.buffer, mesh.indices.buffer, stl] });
      } else if(request.action==='faces'){
        const faces=await solidFaces(request.bodies[0]);self.postMessage({id:request.id,faces});
      } else if(request.action==='edges'){
        const edges=await solidEdges(request.bodies[0]);self.postMessage({id:request.id,edges});
      } else {
        const mesh = await solidMesh(request.bodies[0]);
        self.postMessage({ id: request.id, mesh }, { transfer: [mesh.positions.buffer, mesh.indices.buffer] });
      }
    } catch (error) { self.postMessage({ id: request.id, error: error instanceof Error ? error.message : String(error) }); }
  });
});
