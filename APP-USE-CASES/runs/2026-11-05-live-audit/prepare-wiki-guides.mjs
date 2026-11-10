// Prepare published example assets and explicit, reviewable exercise edits.
// This does not operate any browser or count as acceptance execution.
import {createServer} from 'vite';
import fs from 'node:fs/promises';
import path from 'node:path';
const root=process.cwd(),out=path.join(root,'test-results/audit-2026-11-05');
const edits=[
 ['r=4, $fn=48','r=6, $fn=48'],['post(12);','post(20);'],['h=8.1','h=12.1'],['center=true','center=false'],['[1.5,1,0.7]','[1.5,1,1]'],['r2=8','r2=12'],['[10,10,18]','[10,10,28]'],['height=4','height=8'],['$fn=6)','$fn=8)'],['linear_extrude(5)','linear_extrude(10)'],
 ['"BOX"','"LID"'],['[0,0,-6]','[0,0,0]'],['twist=90','twist=0'],['angle=360','angle=270'],['[16,0]','[22,0]'],['r=6, $fn=40','r=8, $fn=40'],['[12,8,10]','[8,8,10]'],['sphere(12,','sphere(14,'],['intersection_for(a=','for(a='],[['[-12,0]','[12,0]'],['[-18,0]','[18,0]']],
 ['sphere(2,','sphere(1,'],['[-12,12]','[-18,18]'],['rotate([0,90,0])','rotate([90,0,0])'],['[1.6,1,1]','[1,1,1]'],['[30,0,0]','[40,0,0]'],['translate([3,0,0])','translate([5,0,0])'],['[1,0,0.4,0]','[1,0,0.2,0]'],['color("red")','color("blue")'],['fill()         //','/* fill omitted */ //'],['linear_extrude(5)','linear_extrude(8)'],
 ['[6,16,48]','[6,8,48]'],['width=32;','width=40;'],['wide=true;','wide=false;'],['heights=[8,12,18]','heights=[8,12,18,24]'],['r=2.5,','r=3,'],['hole=true;','hole=false;'],['h=6+i*4','h=6+i*2'],['post(h=18);','post(h=18,wall=1);'],['radial() cylinder','radial(n=8) cylinder'],['? 14 : 7','? 14 : 10'],
 ['if(a!=90 && a!=270) ',''],['requested=10;','requested=2;'],['angle=25;','angle=40;'],['v=[20,12];','v=[20,-12];'],['span=45;','span=60;'],['b=12;','b=20;'],['rotate(a=30,','rotate(a=60,'],['rands(6,18,5,123)','rands(6,18,5,456)'],['right=[[12,0]','right=[[18,0]'],['[10,12]','[10,16]'],
 ['search(10,sizes)','search(14,sizes)'],['str("M",6)','str("M",8)'],['block();','block(30);'],['label="Flange"','label="Component 1"'],['wall=3;','wall=13;'],['radius=8;','radius=10;'],['use <parts/foot.scad>','include <parts/foot.scad>'],['linear_extrude(4)','linear_extrude(8)'],['scale([6,6,2])','scale([6,6,4])'],['cube([16,12,4])','cube([16,12,8])'],
 ['pose=25;','pose=90;'],['[0,10]','[0,16]'],['holes=6;','holes=8;'],['wall=2;','wall=3;'],['translate([4,4,3])','translate([4,4,4])'],['for(x=[-12,12])','for(x=[-10,10])'],[['[15,24]','[15,3]'],['[14,24]','[14,3]']],['[0,0,0.8]','[0,0,1.4]'],['sidesonly=true','sidesonly=false'],['nutHole(6)','nutHole(8)'],
];
const server=await createServer({root,server:{middlewareMode:true,watch:{ignored:['**/test-results/**','**/APP-USE-CASES/**']}}});
try{
 const {WIKI_TOPICS}=await server.ssrLoadModule('/src/cad-wiki-content.ts');
 const examples=WIKI_TOPICS.flatMap(t=>t.examples.filter(e=>e.preview!==false).map(e=>({...e,topic:t.id})));
 if(examples.length!==70||edits.length!==70)throw Error('Exercise inventory changed');
 const fixture=path.join(out,'fixtures/wiki-guided');await fs.mkdir(fixture,{recursive:true});
 for(let i=0;i<examples.length;i++){
  const e=examples[i];e.index=i+1;let [from,to]=edits[i];e.variant=e.code;
  for(const [a,b] of typeof from==='string'?[[from,to]]:from.map((a,j)=>[a,to[j]])){
   if(e.variant.split(a).length!==2)throw Error(`Edit must match once: ${e.title}: ${a}`);
   e.variant=e.variant.replace(a,b);
  }
  for(const [name,text]of Object.entries(e.files??{})){const target=path.join(fixture,name);await fs.mkdir(path.dirname(target),{recursive:true});await fs.writeFile(target,text);}
 }
 await fs.writeFile(path.join(fixture,'main.scad'),'// Asset carrier for the live wiki exercise audit.\ncube([2,3,4]);\n');
 await fs.writeFile(path.join(out,'mouse/wiki-guided-plans.json'),JSON.stringify(examples,null,2)+'\n');console.log('Prepared70explicit exercises and4supplied dependencies');
}finally{await server.close();}
