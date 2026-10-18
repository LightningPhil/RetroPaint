export interface DraftInfo {id:string;name:string;width:number;height:number;savedAt:number;thumbnail:string;bytes:number}
export interface Draft extends DraftInfo {data:string}

/** Recovery copies live in this browser. Content and its preview are written atomically. */
export class RecoveryStore {
  private database:Promise<IDBDatabase>|null=null;
  constructor(private readonly name='RetroPaintDrafts'){}
  private open():Promise<IDBDatabase> {
    return this.database??=new Promise((resolve,reject)=>{
      const request=indexedDB.open(this.name,1);
      request.onupgradeneeded=()=>{const db=request.result;db.createObjectStore('info',{keyPath:'id'});db.createObjectStore('pictures',{keyPath:'id'});};
      request.onsuccess=()=>{const db=request.result;db.onversionchange=()=>{db.close();this.database=null;};resolve(db);};
      request.onerror=()=>{this.database=null;reject(request.error??new Error('Draft storage is unavailable.'));};
      request.onblocked=()=>reject(new Error('Close older RetroPaint tabs to update draft storage.'));
    });
  }
  async list():Promise<DraftInfo[]> {
    const db=await this.open();return new Promise((resolve,reject)=>{
      const request=db.transaction('info','readonly').objectStore('info').getAll();
      request.onsuccess=()=>resolve((request.result as DraftInfo[]).sort((a,b)=>b.savedAt-a.savedAt));request.onerror=()=>reject(request.error);
    });
  }
  async read(id:string):Promise<Draft|null> {
    const db=await this.open();return new Promise((resolve,reject)=>{
      const transaction=db.transaction(['info','pictures'],'readonly'),info=transaction.objectStore('info').get(id),picture=transaction.objectStore('pictures').get(id);
      transaction.oncomplete=()=>resolve(info.result&&picture.result?{...info.result as DraftInfo,data:(picture.result as {data:string}).data}:null);
      transaction.onerror=()=>reject(transaction.error);transaction.onabort=()=>reject(transaction.error??new Error('Could not read the draft.'));
    });
  }
  async save(draft:Draft):Promise<void> {
    const db=await this.open(),{data,...info}=draft;
    await new Promise<void>((resolve,reject)=>{
      const transaction=db.transaction(['info','pictures'],'readwrite');transaction.objectStore('info').put(info);transaction.objectStore('pictures').put({id:draft.id,data});
      // Keep up to eight recent pictures, within a modest storage budget.
      const request=transaction.objectStore('info').getAll();request.onsuccess=()=>{
        const entries=(request.result as DraftInfo[]).sort((a,b)=>Number(b.id===draft.id)-Number(a.id===draft.id)||b.savedAt-a.savedAt);let bytes=0,count=0;
        for(const entry of entries){
          if(entry.id!==draft.id&&(count>=8||bytes+entry.bytes>128_000_000)){transaction.objectStore('info').delete(entry.id);transaction.objectStore('pictures').delete(entry.id);}else{count++;bytes+=entry.bytes;}
        }
      };
      transaction.oncomplete=()=>resolve();transaction.onerror=()=>reject(transaction.error);transaction.onabort=()=>reject(transaction.error??new Error('Could not save this draft.'));
    });
  }
  async close():Promise<void> {const pending=this.database;this.database=null;if(pending)(await pending).close();}
}
