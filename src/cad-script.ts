import { body, readCadLayer, XY, type CadBody, type V2, type V3 } from './cad-model';
import {ADVANCED_SCRIPT_EXAMPLES} from './cad-script-examples';

type Value = number | boolean | string | Value[];
interface Token { text:string; line:number; column:number }
type Expr = { token:Token; op:string; args:Expr[]; value?:Value };
interface Arg { name?:string; value:Expr }
interface Statement { token:Token; kind:'assign'|'call'|'block'|'for'|'if'|'module'; name?:string; args:Arg[]; children:Statement[]; otherwise?:Statement[] }
type Sketch = {points:V2[]} | {operation:'union'|'subtract'|'intersect'|'hull';children:Sketch[]};
type Geometry = { flat:Sketch } | { solid:CadBody };
interface Scope { values:Map<string,Value>; modules:Map<string,{node:Statement;scope:Scope}>; parent?:Scope }

export class ScriptError extends Error {
  constructor(message:string,public line:number,public column:number){super(`Line ${line}, column ${column}: ${message}`);}
}
const fail=(token:Token,message:string):never=>{throw new ScriptError(message,token.line,token.column);};
function tokenize(source:string):Token[] {
  if(source.length>50000)throw new Error('Keep scripts below 50,000 characters.');
  const tokens:Token[]=[];let offset=0,line=1,column=1;
  while(offset<source.length){
    const rest=source.slice(offset),match=/^(?:\s+|\/\/[^\n]*|\/\*[\s\S]*?\*\/|"(?:\\.|[^"\\])*"|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?|[a-zA-Z_$][\w$]*|==|!=|<=|>=|&&|\|\||[{}()[\],;:?+*\/%^=!<>-])/.exec(rest);
    if(!match)fail({text:rest[0],line,column},rest.startsWith('/*')?'Unclosed comment.':`Unexpected character ${rest[0]}.`);
    const text=match![0];if(!/^\s|^\/\//.test(text)&&!text.startsWith('/*'))tokens.push({text,line,column});
    for(const c of text){if(c==='\n'){line++;column=1;}else column++;}offset+=text.length;
  }
  tokens.push({text:'<end>',line,column});return tokens;
}
class Parser {
  i=0;depth=0;
  constructor(public tokens:Token[]){}
  get token(){return this.tokens[this.i];}
  take(text?:string):Token {const t=this.token;if(text&&t.text!==text)fail(t,`Expected '${text}', found '${t.text}'.`);this.i++;return t;}
  accept(text:string):boolean{if(this.token.text!==text)return false;this.i++;return true;}
  guard<T>(fn:()=>T):T{if(++this.depth>80)fail(this.token,'Nesting limit exceeded.');try{return fn();}finally{this.depth--;}}
  list(end:string):Statement[]{const out:Statement[]=[];while(this.token.text!==end){if(this.token.text==='<end>')fail(this.token,`Expected '${end}'.`);out.push(this.statement());}return out;}
  args():Arg[]{this.take('(');const out:Arg[]=[];if(!this.accept(')')){do{let name:string|undefined;if(this.tokens[this.i+1]?.text==='='){name=this.take().text;this.take('=');}out.push({name,value:this.expr()});}while(this.accept(','));this.take(')');}return out;}
  statement():Statement{return this.guard(()=>{
    const token=this.token;
    if(this.accept(';'))return {token,kind:'block',args:[],children:[]};
    if(this.accept('{')){const children=this.list('}');this.take('}');return {token,kind:'block',args:[],children};}
    if(this.accept('module')){const name=this.take().text;this.take('(');const args:Arg[]=[];if(!this.accept(')')){do{const parameter=this.take();if(!/^[a-zA-Z_$][\w$]*$/.test(parameter.text))fail(parameter,'Expected a parameter name.');args.push({name:parameter.text,value:this.accept('=')?this.expr():{token:parameter,op:'required',args:[]}});}while(this.accept(','));this.take(')');}return {token,kind:'module',name,args,children:[this.statement()]};}
    if(this.accept('for'))return {token,kind:'for',args:this.args(),children:[this.statement()]};
    if(this.accept('if')){const args=this.args();if(args.length!==1)fail(token,'if needs one condition.');const children=[this.statement()],otherwise=this.accept('else')?[this.statement()]:undefined;return {token,kind:'if',args,children,otherwise};}
    const name=this.take().text;if(!/^[a-zA-Z_$][\w$]*$/.test(name))fail(token,'Expected a shape, transform, module or variable.');
    if(this.accept('=')){const value=this.expr();this.take(';');return {token,kind:'assign',name,args:[{value}],children:[]};}
    const args=this.args(),children=this.accept(';')?[]:[this.statement()];return {token,kind:'call',name,args,children};
  });}
  expr(min=0):Expr{return this.guard(()=>{
    const token=this.take();let left:Expr;
    if(['-','+','!'].includes(token.text))left={token,op:'unary'+token.text,args:[this.expr(8)]};
    else if(token.text==='('){left=this.expr();this.take(')');}
    else if(token.text==='['){const args:Expr[]=[];let range=false;if(!this.accept(']')){args.push(this.expr());if(this.accept(':')){range=true;args.push(this.expr());if(this.accept(':'))args.push(this.expr());}else while(this.accept(','))args.push(this.expr());this.take(']');}left={token,op:range?'range':'array',args};}
    else if(/^\d|^\./.test(token.text))left={token,op:'literal',value:Number(token.text),args:[]};
    else if(token.text.startsWith('"')){try{left={token,op:'literal',value:JSON.parse(token.text),args:[]};}catch{fail(token,'Invalid string escape.');}}
    else if(['true','false'].includes(token.text))left={token,op:'literal',value:token.text==='true',args:[]};
    else if(/^[a-zA-Z_$][\w$]*$/.test(token.text)){if(this.token.text==='('){const args=this.args();if(args.some(a=>a.name))fail(token,'Math functions use positional arguments.');left={token,op:'function',value:token.text,args:args.map(a=>a.value)};}else left={token,op:'variable',value:token.text,args:[]};}
    else return fail(token,'Expected a number, variable or expression.');
    while(true){const op=this.token.text,precedence:Record<string,number>={'||':1,'&&':2,'==':3,'!=':3,'<':4,'>':4,'<=':4,'>=':4,'+':5,'-':5,'*':6,'/':6,'%':6,'^':7};
      if(op==='['){this.take();const index=this.expr();this.take(']');left={token,op:'index',args:[left!,index]};continue;}
      if(op==='?'&&min===0){this.take();const yes=this.expr();this.take(':');left={token,op:'?',args:[left!,yes,this.expr()]};continue;}
      const p=precedence[op];if(!p||p<min)break;this.take();left={token,op,args:[left!,this.expr(p+(op==='^'?0:1))]};
    }return left!;
  });}
}
const scope=(parent?:Scope):Scope=>({parent,values:new Map(),modules:new Map()});
function lookup(env:Scope,name:string,token:Token):Value {if(env.values.has(name))return env.values.get(name)!;if(env.parent)return lookup(env.parent,name,token);return fail(token,`Unknown variable '${name}'.`);}
function numeric(value:Value,token:Token):number{if(typeof value!=='number'||!Number.isFinite(value))return fail(token,'Expected a finite number.');return value;}
function vector(value:Value,n:number,token:Token):number[]{if(!Array.isArray(value)||value.length!==n)fail(token,`Expected a vector with ${n} numbers.`);return (value as Value[]).map(v=>numeric(v,token));}
function mapSketch(sketch:Sketch,fn:(p:V2)=>V2):Sketch{return 'points' in sketch?{points:sketch.points.map(fn)}:{...sketch,children:sketch.children.map(s=>mapSketch(s,fn))};}
const operations={union:'union',difference:'subtract',intersection:'intersect',hull:'hull'} as const;

/** A bounded interpreter; scripts never execute as JavaScript or access the host. */
export function compileCadScript(source:string):CadBody {
  const parser=new Parser(tokenize(source)),program=parser.list('<end>');let work=0,nodes=0,depth=0;
  const tick=(token:Token)=>{if(++work>60000)fail(token,'Script work limit exceeded. Use fewer repetitions.');};
  const make=(solid:CadBody['solid'],token:Token):CadBody=>{if(++nodes>1500)fail(token,'Too many solid operations (maximum 1500).');return body(solid,'Script');};
  function expression(e:Expr,env:Scope):Value {
    tick(e.token);const number=(v:Value)=>numeric(v,e.token),a=()=>expression(e.args[0],env),b=()=>expression(e.args[1],env);
    if(e.op==='literal')return e.value!;if(e.op==='variable')return lookup(env,String(e.value),e.token);
    if(e.op==='required')return fail(e.token,'Missing required module argument.');
    if(e.op==='array')return e.args.map(v=>expression(v,env));
    if(e.op==='range'){const values=e.args.map(v=>number(expression(v,env))),[start,step,end]=values.length===2?[values[0],1,values[1]]:values;if(!step)fail(e.token,'Range step cannot be zero.');const count=Math.max(0,Math.floor((end-start)/step+1e-9)+1);if(count>256)fail(e.token,'A range may contain at most 256 values.');return Array.from({length:count},(_,i)=>start+i*step);}
    if(e.op==='index'){const value=a(),index=number(b());if(!Array.isArray(value)||!Number.isInteger(index)||index<0||index>=value.length)fail(e.token,'Array index is out of range.');return (value as Value[])[index];}
    if(e.op==='?')return expression(e.args[a()?1:2],env);if(e.op==='&&')return Boolean(a())&&Boolean(b());if(e.op==='||')return Boolean(a())||Boolean(b());
    if(e.op==='unary!')return !a();if(e.op==='unary-')return -number(a());if(e.op==='unary+')return number(a());
    if(e.op==='function'){
      const values=e.args.map(v=>expression(v,env));if(e.value==='len'){if(values.length!==1||!(Array.isArray(values[0])||typeof values[0]==='string'))fail(e.token,'len needs one array or string.');return (values[0] as Value[]).length;}
      const args=values.map(number),rad=Math.PI/180,functions:Record<string,{min:number;max:number;fn:(...v:number[])=>number}>={sin:{min:1,max:1,fn:x=>Math.sin(x*rad)},cos:{min:1,max:1,fn:x=>Math.cos(x*rad)},tan:{min:1,max:1,fn:x=>Math.tan(x*rad)},asin:{min:1,max:1,fn:x=>Math.asin(x)/rad},acos:{min:1,max:1,fn:x=>Math.acos(x)/rad},atan:{min:1,max:1,fn:x=>Math.atan(x)/rad},atan2:{min:2,max:2,fn:(y,x)=>Math.atan2(y,x)/rad},sqrt:{min:1,max:1,fn:Math.sqrt},abs:{min:1,max:1,fn:Math.abs},floor:{min:1,max:1,fn:Math.floor},ceil:{min:1,max:1,fn:Math.ceil},round:{min:1,max:1,fn:Math.round},min:{min:1,max:256,fn:Math.min},max:{min:1,max:256,fn:Math.max},pow:{min:2,max:2,fn:Math.pow}};
      const fn=functions[String(e.value)];if(!fn)fail(e.token,`Unsupported function '${e.value}'.`);if(args.length<fn.min||args.length>fn.max)fail(e.token,`Wrong number of arguments for ${e.value}.`);return number(fn.fn(...args));
    }
    const left=a(),right=b();if(e.op==='==')return JSON.stringify(left)===JSON.stringify(right);if(e.op==='!=')return JSON.stringify(left)!==JSON.stringify(right);
    if(e.op==='+'&&typeof left==='string'&&typeof right==='string'){if(left.length+right.length>10000)fail(e.token,'String limit exceeded.');return left+right;}
    const x=number(left),y=number(right);if(e.op==='<')return x<y;if(e.op==='>')return x>y;if(e.op==='<=')return x<=y;if(e.op==='>=')return x>=y;
    return number(e.op==='+'?x+y:e.op==='-'?x-y:e.op==='*'?x*y:e.op==='/'?x/y:e.op==='%'?x%y:x**y);
  }
  function combine(items:Geometry[],operation:'union'|'subtract'|'intersect'|'hull',token:Token):Geometry[] {
    if(!items.length)return [];if(items.length>128)fail(token,'A group can contain at most 128 shapes.');
    if(items.every(g=>'flat' in g))return [{flat:{operation,children:items.map(g=>(g as {flat:Sketch}).flat)}}];
    if(!items.every(g=>'solid' in g))fail(token,'Do not mix 2D profiles and 3D solids in one operation.');
    return [{solid:make({kind:'boolean',operation,children:items.map(g=>(g as {solid:CadBody}).solid)},token)}];
  }
  function extrude(sketch:Sketch,token:Token,height:number,taper:number,twist:number,revolve:number|undefined):CadBody {
    if('points' in sketch)return make(revolve===undefined?{kind:'extrude',points:sketch.points,plane:structuredClone(XY),height,taper,twist}:{kind:'revolve',points:sketch.points,degrees:revolve,plane:structuredClone(XY)},token);
    return make({kind:'boolean',operation:sketch.operation,children:sketch.children.map(s=>extrude(s,token,height,taper,twist,revolve))},token);
  }
  function run(statements:Statement[],env:Scope):Geometry[]{
    if(++depth>48)fail(statements[0]?.token??parser.token,'Module or geometry nesting limit exceeded.');
    try{
      for(const node of statements)if(node.kind==='module')env.modules.set(node.name!,{node,scope:env});
      const result:Geometry[]=[];
      for(const node of statements){tick(node.token);const t=node.token;
        if(node.kind==='module')continue;
        if(node.kind==='assign'){env.values.set(node.name!,expression(node.args[0].value,env));continue;}
        if(node.kind==='block'){result.push(...combine(run(node.children,scope(env)),'union',t));continue;}
        if(node.kind==='if'){result.push(...run(expression(node.args[0].value,env)?node.children:node.otherwise??[],scope(env)));continue;}
        if(node.kind==='for'){
          const iterate=(index:number,current:Scope):void=>{tick(t);if(index===node.args.length){result.push(...run(node.children,current));return;}const arg=node.args[index];if(!arg.name)fail(t,'for needs a named iterator, for example for(i=[0:3]).');const values=expression(arg.value,current);if(!Array.isArray(values)||values.length>256)fail(t,'for needs a bounded array or range.');for(const value of values as Value[]){const child=scope(current);child.values.set(arg.name!,value);iterate(index+1,child);}};
          if(!node.args.length||node.args.length>4)fail(t,'Use one to four loop iterators.');iterate(0,env);continue;
        }
        let definition:Scope|undefined=env;while(definition&&!definition.modules.has(node.name!))definition=definition.parent;
        if(definition){const module=definition.modules.get(node.name!)!,local=scope(module.scope),provided=new Map<string,Value>();node.args.forEach((arg,i)=>{const name=arg.name??module.node.args[i]?.name;if(!name||!module.node.args.some(p=>p.name===name)||provided.has(name))fail(t,'Unknown or duplicate module argument.');provided.set(name!,expression(arg.value,env));});for(const parameter of module.node.args)local.values.set(parameter.name!,provided.has(parameter.name!)?provided.get(parameter.name!)!:expression(parameter.value,local));if(node.children.length)fail(t,'Child modules are not supported. Pass parameters instead.');result.push(...run(module.node.children,local));continue;}
        const name=node.name!,positional:Value[]=[],named=new Map<string,Value>();let sawNamed=false;
        for(const arg of node.args){const value=expression(arg.value,env);if(arg.name){sawNamed=true;if(named.has(arg.name))fail(t,'Duplicate named argument.');named.set(arg.name,value);}else {if(sawNamed)fail(t,'Put positional arguments before named arguments.');positional.push(value);}}
        const arg=(key:string,index:number,fallback:Value):Value=>{if(named.has(key)){if(index>=0&&positional[index]!==undefined)fail(t,`Argument '${key}' was supplied twice.`);return named.get(key)!;}return index>=0?positional[index]??fallback:fallback;};
        const number=(key:string,index:number,fallback:number)=>numeric(arg(key,index,fallback),t);
        const check=(keys:string[],max:number)=>{for(const key of named.keys())if(!keys.includes(key))fail(t,`Unsupported argument '${key}' for ${name}.`);if(positional.length>max)fail(t,`Too many arguments for ${name}.`);};
        const children=()=>run(node.children.length===1&&node.children[0].kind==='block'?node.children[0].children:node.children,scope(env));
        const segments=()=>{const value=number('$fn',-1,Number(lookup(env,'$fn',t))),count=value===0?96:value;if(!Number.isInteger(count)||count<3||count>128)fail(t,'$fn must be zero or an integer from 3 to 128.');return count;};
        const circle=(r:number):V2[]=>Array.from({length:segments()},(_,i)=>[r*Math.cos(i*2*Math.PI/segments()),r*Math.sin(i*2*Math.PI/segments())]);
        if(name in operations){check([],0);result.push(...combine(children(),operations[name as keyof typeof operations],t));continue;}
        if(['translate','rotate','scale','mirror'].includes(name)){
          check(name==='rotate'?['a']:['v'],1);const value=arg(name==='rotate'?'a':'v',0,name==='scale'?[1,1,1]:[0,0,0]);
          for(const geometry of combine(children(),'union',t)){
            if('flat' in geometry){let v:number[];if(name==='rotate'){const angle=typeof value==='number'?value:vector(value,3,t)[2];if(Array.isArray(value)&&(value[0]!==0||value[1]!==0))fail(t,'Rotate 2D profiles only around Z.');const a=numeric(angle,t)*Math.PI/180;result.push({flat:mapSketch(geometry.flat,([x,y])=>[x*Math.cos(a)-y*Math.sin(a),x*Math.sin(a)+y*Math.cos(a)])});continue;}
              v=typeof value==='number'?[value,value]:vector(value,Array.isArray(value)&&value.length===3?3:2,t);if(v.length===3&&v[2]!==0&&!(name==='scale'&&v[2]===1))fail(t,'Keep profile transforms in the XY plane.');
              if(name==='mirror'){const length=Math.hypot(v[0],v[1]);if(!length)fail(t,'Mirror needs a nonzero normal.');const nx=v[0]/length,ny=v[1]/length;result.push({flat:mapSketch(geometry.flat,([x,y])=>[x-2*(x*nx+y*ny)*nx,y-2*(x*nx+y*ny)*ny])});}
              else result.push({flat:mapSketch(geometry.flat,([x,y])=>name==='translate'?[x+v[0],y+v[1]]:[x*v[0],y*v[1]])});
            }else{const wrapper=make({kind:'boolean',operation:'union',children:[geometry.solid]},t),v=(typeof value==='number'?(name==='rotate'?[0,0,value]:[value,value,value]):vector(value,3,t)) as V3;
              if(name==='translate')wrapper.position=v;else if(name==='rotate')wrapper.rotation=v;else if(name==='scale'){if(v.some(n=>n<=0))fail(t,'3D scale factors must be positive.');wrapper.scale=v;}else fail(t,'3D mirror is not supported yet; use 2D mirror before extrusion.');result.push({solid:wrapper});}
          }continue;
        }
        if(name==='linear_extrude'||name==='rotate_extrude'){
          check(name==='linear_extrude'?['height','center','twist','scale']:['angle'],1);const h=number('height',0,10),angle=name==='rotate_extrude'?number('angle',0,360):undefined;
          if(name==='linear_extrude'&&h<=0)fail(t,'Extrusion height must be positive.');
          for(const geometry of combine(children(),'union',t)){if(!('flat' in geometry))fail(t,'Extrusion requires a 2D square, circle or polygon.');const made=extrude((geometry as {flat:Sketch}).flat,t,h,number('scale',-1,1),number('twist',-1,0),angle);if(name==='linear_extrude'&&arg('center',-1,false))made.position[2]=-h/2;result.push({solid:made});}continue;
        }
        if(node.children.length)fail(t,`${name} does not accept child shapes.`);
        if(name==='cube'||name==='square'){
          check(['size','center'],2);const dimension=name==='cube'?3:2,value=arg('size',0,1),size=typeof value==='number'?Array(dimension).fill(value):vector(value,dimension,t);if(size.some(n=>n<=0))fail(t,'Sizes must be positive.');const centred=Boolean(arg('center',1,false));
          if(name==='square'){const x=centred?-size[0]/2:0,y=centred?-size[1]/2:0;result.push({flat:{points:[[x,y],[x+size[0],y],[x+size[0],y+size[1]],[x,y+size[1]]]}});}else{const made=make({kind:'primitive',shape:'box',size:size as V3,wall:2},t);if(!centred)made.position=size.map(n=>n/2) as V3;result.push({solid:made});}continue;
        }
        if(name==='sphere'||name==='circle'){
          check(name==='circle'?['r','d','$fn']:['r','d'],1);if(named.has('r')&&named.has('d'))fail(t,'Choose radius or diameter, not both.');const r=named.has('d')?number('d',-1,2)/2:number('r',0,1);if(r<=0)fail(t,'Radius must be positive.');result.push(name==='circle'?{flat:{points:circle(r)}}:{solid:make({kind:'primitive',shape:'sphere',size:[r*2,r*2,r*2],wall:2},t)});continue;
        }
        if(name==='cylinder'){
          check(['h','r','d','r1','r2','d1','d2','center','$fn'],4);const h=number('h',0,1),r=named.has('d')?number('d',-1,2)/2:number('r',-1,1),r1=named.has('d1')?number('d1',-1,2)/2:number('r1',1,r),r2=named.has('d2')?number('d2',-1,2)/2:number('r2',2,r1);if(h<=0||r1<0||r2<0||Math.max(r1,r2)<=0)fail(t,'Cylinder height and at least one radius must be positive.');
          const inverted=r2>r1,base=inverted?r2:r1,top=inverted?r1:r2;let made:CadBody;
          if(top===0){const ring=circle(base),positions=ring.flatMap(([x,y])=>[x,y,0]),indices:number[]=[],n=ring.length;positions.push(0,0,0,0,0,h);for(let i=0;i<n;i++){const next=(i+1)%n;indices.push(n,next,i,i,next,n+1);}made=make({kind:'mesh',positions,indices,sourceName:'Script cone'},t);}
          else made=extrude({points:circle(base)},t,h,top/base,0,undefined);
          if(inverted){made.rotation=[180,0,0];made.position[2]=h;}if(arg('center',3,false))made.position[2]-=h/2;result.push({solid:made});continue;
        }
        if(name==='polygon'){check(['points'],1);const points=arg('points',0,[]);if(!Array.isArray(points)||points.length<3||points.length>128)fail(t,'Polygon needs 3–128 [x,y] points.');result.push({flat:{points:(points as Value[]).map(p=>vector(p,2,t) as V2)}});continue;}
        fail(t,`Unsupported command '${name}'. Open Language help for supported features.`);
      }return result;
    }finally{depth--;}
  }
  const env=scope();env.values.set('$fn',96);env.values.set('PI',Math.PI);
  const output=combine(run(program,env),'union',parser.tokens[0]);if(!output.length||!('solid' in output[0]))throw new Error('The script must produce a 3D solid. Extrude or revolve 2D profiles.');
  const result=output[0].solid;result.name='Script model';result.script={language:'retrocad-1',source};
  return readCadLayer({units:'mm',bodies:[result]})!.bodies[0];
}

export const LEGACY_SCRIPT_EXAMPLES:Record<string,string>={
  'Drilled flange':`// A round mounting plate. Edit dimensions, then Preview (F5).
$fn = 64; // Segments used to approximate circles.
radius = 28; // Outside radius, in millimetres.
height = 7; // Plate thickness.
bolt_circle = 20; // Distance from centre to each small hole.
holes = 6; // Number of evenly spaced bolt holes.
difference() { // Keep the first shape; subtract the remaining shapes.
  cylinder(h=height, r=radius); // Starting disk.
  // Cutters extend 1 mm past each face for reliable through-holes.
  translate([0,0,-1]) cylinder(h=height+2, r=8);
  for (i=[0:holes-1]) // Stop before duplicating the first hole at 360 degrees.
    rotate([0,0,i*360/holes]) // Swing the displaced cutter around the centre.
      translate([bolt_circle,0,-1])
        cylinder(h=height+2, r=2.5); // Radius 2.5 makes a 5 mm hole.
}`,
  'Parametric box':`// Outside dimensions in millimetres.
width=50;
depth=35;
height=24;
wall=3; // Side walls and floor share this thickness.
difference() {
  cube([width,depth,height]); // Start with a solid block at Z=0.
  // Lift and inset the cavity to preserve the floor and side walls.
  translate([wall,wall,wall])
    cube([width-2*wall,depth-2*wall,height]); // Extend through the open top.
}`,
  'Reusable towers':`// Define one tower recipe; calls can override its dimensions.
module tower(height=20, radius=5) {
  cylinder(h=height, r=radius); // Upright stem.
  translate([0,0,height]) sphere(r=radius*1.2); // Ball overlaps the stem's top.
}
union() { // Combine the base and all towers.
  cube([65,20,3]); // Shared supporting plate.
  for(i=[0:3]) // Four copies with increasing heights.
    translate([10+i*15,10,3]) tower(height=12+i*6); // Place each on the base.
}`,
  'Twisted star':`$fn=64; // Curve detail for any circular geometry added later.
// Pull a flat outline upward, turning and shrinking it towards the top.
linear_extrude(height=35, twist=90, scale=0.6)
  // Ordered [x,y] corners; the last edge closes automatically.
  polygon([[15,0],[5,4],[4,15],[-4,5],[-15,4],[-5,-4],[-4,-15],[4,-5]]);`,
  'Revolved bowl':`// Spin the filled wall-and-floor cross-section through a full turn.
rotate_extrude(angle=360)
  polygon([
    [0,0],   // Bottom centre: each point is [radius,height].
    [12,0],  // Outside base edge.
    [25,24], // Outside rim.
    [22,24], // Inside rim.
    [10,3],  // Inside wall meets the floor.
    [0,3]    // Floor centre; closing the outline completes the base.
  ]);`
};

// Preserve the original subset fixtures while offering native-engine starters.
export const SCRIPT_EXAMPLES:Record<string,string>={...LEGACY_SCRIPT_EXAMPLES,...ADVANCED_SCRIPT_EXAMPLES};
