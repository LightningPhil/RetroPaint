import { WIKI_TOPICS,WIKI_SOURCE_URL,type WikiTopic,type WikiExample } from './cad-wiki-content';
import { WikiPreview } from './cad-wiki-preview';
import './cad-wiki.css';

export function searchWiki(topics:WikiTopic[],query:string,category=''):WikiTopic[]{const words=query.toLowerCase().trim().split(/\s+/).filter(Boolean);return topics.filter(topic=>(!category||topic.category===category)&&words.every(word=>[topic.title,topic.summary,topic.syntax,...topic.symbols,...topic.lesson.beginner,topic.lesson.deeper,...topic.body,...topic.parameters.flat(),...topic.examples.flatMap(example=>[example.title,example.result,example.experiment,example.code])].join(' ').toLowerCase().includes(word)));}
export function mcadTopics(files:Array<{path:string;data:string}>):WikiTopic[]{
  return files.filter(file=>file.path.endsWith('.scad')).map(file=>{
    const source=new TextDecoder().decode(Uint8Array.from(atob(file.data),c=>c.charCodeAt(0))),masked=source.replace(/\/\*[\s\S]*?\*\/|\/\/[^\n]*/g,text=>text.replace(/[^\n]/g,' '));
    const declarations:Array<[string,string]>=[];for(const match of masked.matchAll(/\b(module|function)\s+([\w]+)\s*\(/g)){let end=match.index!+match[0].length,depth=1,quote=false;for(;end<masked.length&&depth;end++){const ch=masked[end];if(ch==='"'&&masked[end-1]!=='\\')quote=!quote;if(!quote){if(ch==='(')depth++;if(ch===')')depth--;}}declarations.push([match[2],source.slice(match.index!,end)]);}
    const description=MCAD_DESCRIPTIONS[file.path]??'Supplementary MCAD source; inspect its declarations and original comments before use.';
    const constants=['constants.scad','units.scad','materials.scad'].includes(file.path);
    const load=constants?'include':'use';
    return{id:'mcad-'+file.path.replace(/\W/g,'-'),title:'MCAD / '+file.path,category:'MCAD source catalogue',symbols:declarations.map(([name])=>name),summary:description,syntax:`${load} <MCAD/${file.path}>`,parameters:declarations,
      lesson:{beginner:[`This is a ready-made toolbox file supplied with Code studio. ${description}`,constants?'This file supplies named values. include makes those values available to your recipe, including any top-level demonstration geometry in that file. Read the source before including it so you know what will be added.':`Start by loading this exact file with the use line shown below. That makes its recipes available without automatically making a part. Then call the module you need. ${declarations.length?'The declaration list names the available recipes and shows their settings.':'This file may contain demonstrations or data rather than directly callable recipes; inspect its source first.'}`],
        deeper:`Read a signature such as module name(a,b=6) as a geometry recipe with required input a and optional input b, whose default is 6. A function signature returns a value instead of making geometry. Parameters without defaults must be supplied in declaration order or by name. ${constants?'These files mainly supply constants; a short or empty declaration list does not mean the file is empty.':'A child-geometry wrapper needs a shape after its call; a flat-profile module needs extrusion before it can become a workshop solid.'} Use the original comments below to check this file’s units, origin, required children and valid input ranges. A listed helper nested inside another declaration is not automatically callable from your script.`},
      body:['The declarations below are read from the exact library shipped with RetroPaint. Parameter defaults are shown verbatim. Several files have overlapping names, and nested or test helpers may not be intended as public APIs.','Expand Original commented source for the library author’s explanations, parameter notes, examples and implementation. The original third-party source is retained unchanged, including attribution. Some legacy routines may require adaptation for the current engine.'],tips:['Try one module at a time and inspect its dimensions before combining it with your model. Follow the MCAD guide under Related topics for complete commented examples.'],examples:[],related:['mcad','include-use'],source};
  });
}
const MCAD_DESCRIPTIONS:Record<string,string>={
 'boxes.scad':'Rounded boxes and cubes, with corner radius and dimensions controlled by parameters.',
 'nuts_and_bolts.scad':'Nut and bolt clearance cutters for mechanical joints; inspect tolerances and diameter conventions.',
 'involute_gears.scad':'Spur, bevel, helical and rack gear construction, with tooth geometry and meshing demonstrations.',
 'gears.scad':'Earlier gear helpers and involute tooth calculations; do not mix its gear signature with involute_gears.',
 'bearing.scad':'Bearing dimension lookup functions and visual bearing envelopes.',
 'linear_bearing.scad':'Linear-bearing dimension tables and cylindrical bearing envelopes.',
 '2Dshapes.scad':'Parametric 2D outlines, rounded rectangles, polygonal shapes, ellipses and circular slices. Extrude them for solids.',
 '3d_triangle.scad':'Triangle geometry helpers, centres, radii and triangular solid constructions.',
 'regular_shapes.scad':'Regular polygons, prisms, tubes, toruses, pyramids and other reusable shapes.',
 'shapes.scad':'Older shape helpers. This file is deprecated upstream; prefer regular_shapes or core modules when possible.',
 'array.scad':'Cubic and radial repetition wrappers for supplied children.',
 'multiply.scad':'Spin, duplicate and linear repetition helpers.',
 'layouts.scad':'List and grid arrangement wrappers for child geometry.',
 'transformations.scad':'Local scaling transformation helper.',
 'utilities.scad':'Vector distances, normalisation, angle calculations and geometry placement helpers.',
 'math.scad':'A degree conversion helper for formulas expressed in radians.',
 'constants.scad':'Shared mathematical constants. Use include when you need top-level constants.',
 'units.scad':'Unit conversion constants. Use include when you need their values in the calling scope.',
 'materials.scad':'Material colour constants and colour demonstrations; STL transfer does not preserve these colours.',
 'profiles.scad':'Extrusion cross-sections such as angle, tube, channel and T-slot profiles.',
 'gridbeam.scad':'Gridbeam members, fastening envelopes and shelf/board helpers.',
 'hardware.scad':'Simplified rods, screws, nuts, washers and bearing geometry.',
 'metric_fastners.scad':'Metric fastener shapes and chamfer helpers. The filename retains the upstream spelling.',
 'motors.scad':'Stepper motor mounting geometry and mounting-pattern helpers.',
 'stepper.scad':'Stepper motor envelopes, dimensions and examples.',
 'servos.scad':'Model-specific servo envelopes for layout and clearance checking.',
 'screw.scad':'Helical, auger and ball-screw style constructions and examples; potentially expensive geometry.',
 'teardrop.scad':'Teardrop-shaped profiles and holes, useful when planning unsupported upper surfaces.',
 'polyholes.scad':'Polygonal hole cutters with compensation conventions; verify the resulting physical fit.',
 'triangles.scad':'2D triangular profile helpers; extrude for solid output.',
 'libtriangles.scad':'Triangular prisms and pyramids.',
 'lego_compatibility.scad':'Parametric block, post, reinforcement and axle shapes for compatibility experiments.',
 'trochoids.scad':'Epitrochoid and hypotrochoid profiles, bores and extruded variants.',
 'curves.scad':'Parametric curve helpers including a helix point generator.',
 'fonts.scad':'Outline, bold, polygon-font and braille text constructions, distinct from the core text module.',
 'unregular_shapes.scad':'A helper that connects square sections.',
 'bitmap/alphabet_block.scad':'Lettered block constructions using the bundled bitmap alphabet.',
 'bitmap/bitmap.scad':'Bitmap-to-geometry helpers: rows of on/off cells become small geometric features.',
 'bitmap/height_map.scad':'Helpers for representing bitmap cell values as raised geometry.',
 'bitmap/letter_necklace.scad':'A letter-necklace example assembled from bitmap lettering.',
 'bitmap/name_tag.scad':'A name-tag example using the bundled bitmap character shapes.',
 'bitmap/test_name_tag.scad':'Demonstration calls for bitmap name tags; inspect the source for the imported modules and inputs.',
};

export class CadWiki {
  readonly dialog=document.createElement('dialog');
  private topics=[...WIKI_TOPICS];
  private current='start';
  private history=['start'];
  private cursor=0;
  private loaded=false;
  private loading=false;
  private opener?:HTMLElement;
  private preview:WikiPreview;
  private search:HTMLInputElement;
  private categories:HTMLSelectElement;
  private nav:HTMLElement;
  private article:HTMLElement;
  constructor(root:HTMLElement){
    this.dialog.id='cadWiki';this.dialog.setAttribute('aria-labelledby','cadWikiTitle');
    this.dialog.innerHTML='<header><div><h2 id="cadWikiTitle">Code studio wiki</h2><p>Learn OpenSCAD · reference · worked projects</p></div><button id="cadWikiClose" class="choice" type="button">Back to code</button></header><div class="cad-wiki-search"><label>Search topics and functions<input id="cadWikiSearch" type="search" placeholder="Try holes, rotate_extrude or text…"></label><label>Section<select id="cadWikiCategory"><option value="">All sections</option></select></label></div><div class="cad-wiki-history"><button type="button" class="choice" id="cadWikiBack" aria-label="Previous wiki topic">← Back</button><button type="button" class="choice" id="cadWikiForward" aria-label="Next wiki topic">Forward →</button><button type="button" class="choice" id="cadWikiHome">Start here</button><output id="cadWikiCount" role="status" aria-live="polite"></output></div><div class="cad-wiki-layout"><nav id="cadWikiTopics" aria-label="Wiki topics"></nav><article id="cadWikiArticle" aria-label="Wiki article" tabindex="-1"></article></div>';
    root.append(this.dialog);this.preview=new WikiPreview(root);this.search=this.field('cadWikiSearch');this.categories=this.field('cadWikiCategory');this.nav=this.field('cadWikiTopics');this.article=this.field('cadWikiArticle');
    this.field<HTMLButtonElement>('cadWikiClose').onclick=()=>this.close();this.dialog.addEventListener('cancel',event=>{event.preventDefault();event.stopPropagation();this.close();});this.dialog.addEventListener('keydown',event=>event.stopPropagation());
    this.search.oninput=()=>this.filter();this.categories.onchange=()=>this.filter();this.field<HTMLButtonElement>('cadWikiHome').onclick=()=>{this.search.value='';this.categories.value='';this.navigate('start');};
    this.field<HTMLButtonElement>('cadWikiBack').onclick=()=>this.travel(-1);this.field<HTMLButtonElement>('cadWikiForward').onclick=()=>this.travel(1);this.updateCategories();
  }
  private field<T extends HTMLElement>(id:string):T{return this.dialog.querySelector('#'+id) as T;}
  open(opener?:HTMLElement):void{this.opener=opener;this.dialog.showModal();this.filter();this.search.focus();if(!this.loaded&&!this.loading)void this.loadLibrary();}
  close():void{this.preview.close();this.dialog.close();this.opener?.focus();}
  private async loadLibrary():Promise<void>{this.loading=true;try{const response=await fetch(new URL('openscad/mcad.json',new URL(import.meta.env.BASE_URL,location.href)));if(!response.ok)throw new Error('MCAD source unavailable');this.topics.push(...mcadTopics(await response.json()));this.loaded=true;this.updateCategories();this.filter(true);}catch{this.field('cadWikiCount').textContent='Core reference ready. MCAD catalogue could not load; reopen help to retry.';}finally{this.loading=false;}}
  private updateCategories():void{const value=this.categories.value;this.categories.replaceChildren(new Option('All sections',''));for(const category of new Set(this.topics.map(topic=>topic.category)))this.categories.add(new Option(category,category));this.categories.value=value;}
  private navigate(id:string,record=true):void{if(!this.topics.some(topic=>topic.id===id))return;if(record){this.history=this.history.slice(0,this.cursor+1);if(this.history[this.cursor]!==this.current){this.history.push(this.current);this.cursor++;}if(this.current!==id){this.history.push(id);this.cursor++;}}this.current=id;this.search.value='';this.categories.value='';this.filter();this.article.focus();}
  private travel(direction:number):void{const next=this.cursor+direction;if(next<0||next>=this.history.length)return;this.cursor=next;this.navigate(this.history[next],false);}
  private filter(preserveArticle=false):void{
    const results=searchWiki(this.topics,this.search.value,this.categories.value);this.nav.replaceChildren();this.field('cadWikiCount').textContent=`${results.length} of ${this.topics.length} topics`;if(results.length&&!results.some(topic=>topic.id===this.current))this.current=results[0].id;
    for(const topic of results){const button=document.createElement('button');button.type='button';button.className='cad-wiki-topic';button.dataset.wikiTopic=topic.id;button.textContent=topic.title;button.setAttribute('aria-current',String(topic.id===this.current));button.onclick=()=>this.navigate(topic.id);this.nav.append(button);}
    if(results.length){if(!preserveArticle||this.article.dataset.topic!==this.current)this.renderArticle();}else{delete this.article.dataset.topic;this.article.replaceChildren();const message=document.createElement('p');message.textContent='No topics match. Try a function name, a simpler word, or another section.';this.article.append(message);const clear=document.createElement('button');clear.type='button';clear.className='choice';clear.textContent='Clear search';clear.onclick=()=>{this.search.value='';this.categories.value='';this.filter();this.search.focus();};this.article.append(clear);}
    this.field<HTMLButtonElement>('cadWikiBack').disabled=this.cursor===0;this.field<HTMLButtonElement>('cadWikiForward').disabled=this.cursor===this.history.length-1;
  }
  private renderArticle():void{
    const topic=this.topics.find(topic=>topic.id===this.current)!;this.article.dataset.topic=topic.id;this.article.replaceChildren();
    const add=(tag:string,text:string,parent:HTMLElement=this.article)=>{const element=document.createElement(tag);element.textContent=text;parent.append(element);return element;};
    add('p',topic.category+(topic.status?' · '+topic.status:'')).className='cad-wiki-kicker';add('h3',topic.title);add('p',topic.summary).className='cad-wiki-lead';
    const jumps=add('nav','');jumps.className='cad-wiki-related cad-wiki-jumps';jumps.setAttribute('aria-label','On this page');
    const section=(id:string,title:string)=>{const heading=add('h4',title);heading.id='cadWiki-'+id;heading.tabIndex=-1;const button=document.createElement('button');button.type='button';button.className='choice';button.textContent=title;button.dataset.wikiJump=id;button.onclick=()=>{heading.focus({preventScroll:true});heading.scrollIntoView({block:'start'});};jumps.append(button);return heading;};
    section('beginner','Level 1: the idea');
    for(const text of topic.lesson.beginner)add('p',text);
    section('deeper','Level 2: how it works');add('p',topic.lesson.deeper);
    add('h5','Syntax reference');add('pre',topic.syntax).className='cad-wiki-code';
    if(topic.parameters.length){add('h5',topic.source?'Declarations and signatures':'Parameters and results');const list=document.createElement('dl');for(const [name,description]of topic.parameters){add('dt',name,list);add('dd',description,list);}this.article.append(list);}
    for(const text of topic.body)add('p',text);
    if(topic.tips.length){add('h4','Things to watch');const list=document.createElement('ul');for(const tip of topic.tips)add('li',tip,list);this.article.append(list);}
    if(topic.examples.length){section('examples','Commented examples');add('p','Preview runs the example as printed. To try a suggested change, copy the code into your Code studio draft, edit it there and preview again. Include any supplied helper files or assets. Changes to your draft are kept separate from these reference examples.');for(const example of topic.examples)this.example(example);}
    if(topic.source){const details=document.createElement('details');add('summary','Original commented source · MCAD licence and attribution retained',details);add('pre',topic.source,details).className='cad-wiki-library-source';this.article.append(details);const licence=document.createElement('a');licence.href=new URL('openscad/MCAD-LICENSE',new URL(import.meta.env.BASE_URL,location.href)).href;licence.target='_blank';licence.rel='noopener';licence.textContent='MCAD licence';this.article.append(licence);}
    if(topic.related.length){add('h4','Related topics');const links=add('div','');links.className='cad-wiki-related';for(const id of topic.related){const related=this.topics.find(item=>item.id===id);if(!related)continue;const button=document.createElement('button');button.type='button';button.className='choice';button.textContent=related.title;button.onclick=()=>this.navigate(id);links.append(button);}}
    const sources=add('p','Reference basis: OpenSCAD 2026.10.27, checked against the upstream source. ');sources.className='cad-wiki-sources';for(const [label,url]of [['OpenSCAD source',WIKI_SOURCE_URL],['Official language index','https://openscad.org/cheatsheet/']]){const link=document.createElement('a');link.href=url;link.textContent=label;link.target='_blank';link.rel='noopener';sources.append(link,document.createTextNode(' · '));}this.article.scrollTop=0;
  }
  private example(example:WikiExample):void{
    const section=document.createElement('section');section.className='cad-wiki-example';const heading=document.createElement('h5');heading.textContent=example.title;const pre=document.createElement('pre');pre.className='cad-wiki-code';pre.textContent=example.code;
    const result=document.createElement('p');result.className='cad-wiki-result';const resultLabel=document.createElement('strong');resultLabel.textContent='What you should see: ';result.append(resultLabel,document.createTextNode(example.result));section.append(heading,result,pre);
    if(example.files){const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Included example files';details.append(summary);for(const [path,source]of Object.entries(example.files)){const name=document.createElement('h5'),code=document.createElement('pre');name.textContent=path;code.textContent=source;code.className='cad-wiki-code';details.append(name,code);}section.append(details);}
    const actions=document.createElement('div');actions.className='cad-wiki-related';const copy=document.createElement('button');copy.type='button';copy.className='choice';copy.textContent='Copy code';const status=document.createElement('output');status.setAttribute('role','status');
    copy.onclick=()=>{void navigator.clipboard.writeText(example.code).then(()=>{status.textContent=example.files?'Code copied. Also supply the included files shown above.':'Code copied.';}).catch(()=>{const selection=window.getSelection(),range=document.createRange();range.selectNodeContents(pre);selection?.removeAllRanges();selection?.addRange(range);status.textContent='Code selected. Press Ctrl/Cmd+C to copy.';});};actions.append(copy);
    if(example.preview!==false){const run=document.createElement('button');run.type='button';run.className='choice';run.textContent='Preview example';run.onclick=()=>void this.preview.show(example);actions.append(run);}section.append(actions,status);
    const experiment=document.createElement('p');experiment.className='cad-wiki-experiment';const experimentLabel=document.createElement('strong');experimentLabel.textContent='Try one change: ';experiment.append(experimentLabel,document.createTextNode(example.experiment));section.append(experiment);
    if(example.note){const note=document.createElement('p');note.textContent=example.note;section.append(note);}this.article.append(section);
  }
}
