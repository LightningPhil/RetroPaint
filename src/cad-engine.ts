import type { CadBody, CadMesh, CadEdge, CadFace } from './cad-model';
export interface CadResult { mesh: CadMesh; stl?: ArrayBuffer }
export interface CadEdgesResult { edges:CadEdge[] }
export interface CadFacesResult { faces:CadFace[] }
type Result=CadResult|CadEdgesResult|CadFacesResult;
let worker: Worker | undefined, next = 0;
const pending = new Map<number, { resolve: (value: Result) => void; reject: (error: Error) => void; timer?: ReturnType<typeof setTimeout> }>();
function stopWorker(message:string):void {for(const job of pending.values()){clearTimeout(job.timer);job.reject(new Error(message));}pending.clear();worker?.terminate();worker=undefined;}
export function cadCompute(bodies:CadBody[],action:'edges',bed?:boolean):Promise<CadEdgesResult>;
export function cadCompute(bodies:CadBody[],action:'faces',bed?:boolean):Promise<CadFacesResult>;
export function cadCompute(bodies:CadBody[],action?:'mesh'|'print',bed?:boolean):Promise<CadResult>;
export function cadCompute(bodies: CadBody[], action: 'mesh' | 'print' | 'edges' | 'faces' = 'mesh', bed = true): Promise<Result> {
  if (!worker) {
    worker = new Worker(new URL('./cad-worker.ts', import.meta.url), { type: 'module' });
    const activeWorker=worker;
    worker.addEventListener('message', (event: MessageEvent<Result & { id: number; error?: string; started?: boolean }>) => {
      if(worker!==activeWorker)return;
      const job = pending.get(event.data.id); if (!job) return;
      if(event.data.started){job.timer=setTimeout(()=>stopWorker('This precision operation took too long. Try fewer profiles, a simpler path or a smaller profile. Your original model is unchanged; the engine is ready to try again.'),45000);return;}
      clearTimeout(job.timer);pending.delete(event.data.id);
      if (event.data.error) job.reject(new Error(event.data.error)); else job.resolve(event.data);
    });
    worker.addEventListener('error', () => {if(worker===activeWorker)stopWorker('The 3D engine could not start. Try the operation again. Your original model is unchanged.');});
  }
  return new Promise((resolve, reject) => { const id = ++next; pending.set(id, { resolve, reject }); worker!.postMessage({ id, action, bodies, bed }); });
}
