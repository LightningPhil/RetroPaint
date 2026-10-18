const crcTable=Uint32Array.from({length:256},(_,index)=>{
  let value=index;for(let bit=0;bit<8;bit++)value=value&1?0xedb88320^(value>>>1):value>>>1;return value>>>0;
});
function chunk(type:string,data:Uint8Array):Uint8Array<ArrayBuffer> {
  const bytes=new Uint8Array(data.length+12),view=new DataView(bytes.buffer);view.setUint32(0,data.length);
  for(let i=0;i<4;i++)bytes[4+i]=type.charCodeAt(i);bytes.set(data,8);
  let crc=0xffffffff;for(let i=4;i<bytes.length-4;i++)crc=crcTable[(crc^bytes[i])&255]^(crc>>>8);view.setUint32(bytes.length-4,(crc^0xffffffff)>>>0);
  return bytes;
}
/** Encodes successive RGBA row bands without allocating a full-size canvas. */
export class PngStream {
  private parts:BlobPart[]=[];
  private writer:WritableStreamDefaultWriter<BufferSource>;
  private drain:Promise<void>;
  private rows=0;
  constructor(private width:number,private height:number){
    const header=new Uint8Array(13),view=new DataView(header.buffer);view.setUint32(0,width);view.setUint32(4,height);header[8]=8;header[9]=6;
    this.parts.push(new Uint8Array([137,80,78,71,13,10,26,10]),chunk('IHDR',header));
    const compressor=new CompressionStream('deflate');this.writer=compressor.writable.getWriter();
    const reader=compressor.readable.getReader();
    this.drain=(async()=>{try{for(;;){const {done,value}=await reader.read();if(done)break;this.parts.push(chunk('IDAT',value));}}finally{reader.releaseLock();}})();
    // A failed compressor must not leave an unhandled background rejection.
    void this.drain.catch(()=>{});
  }
  async write(rgba:Uint8ClampedArray,rowCount:number):Promise<void>{
    if(rgba.length!==this.width*rowCount*4||this.rows+rowCount>this.height)throw new Error('Invalid PNG row band.');
    const stride=this.width*4,filtered=new Uint8Array((stride+1)*rowCount);
    for(let y=0;y<rowCount;y++){
      const source=y*stride,target=y*(stride+1);filtered[target]=1;
      for(let x=0;x<stride;x++)filtered[target+1+x]=(rgba[source+x]-(x>=4?rgba[source+x-4]:0))&255;
    }
    await this.writer.write(filtered);this.rows+=rowCount;
  }
  async finish():Promise<Blob>{
    if(this.rows!==this.height)throw new Error('The enhanced image is incomplete.');
    await this.writer.close();await this.drain;this.parts.push(chunk('IEND',new Uint8Array()));return new Blob(this.parts,{type:'image/png'});
  }
  async abort():Promise<void>{await this.writer.abort().catch(()=>{});await this.drain.catch(()=>{});this.parts=[];}
}
