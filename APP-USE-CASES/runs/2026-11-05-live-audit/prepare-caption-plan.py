"""Record a native pairwise caption plan and Windows font provenance."""
from pathlib import Path
from itertools import combinations,product
from PIL import ImageFont
import hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';fonts=['Trebuchet MS','Arial','Georgia','Courier New','Comic Sans MS','Impact'];patterns=[3,5,6,9,10,12];rows=[]
for gi,font in enumerate(fonts):
 for a,align in enumerate(['left','center','right']):
  mask=[0,15,patterns[gi]][(a+gi)%3];rows.append({'label':f'font-{gi+1}-align-{a+1}','font':font,'align':align,'mode':'vector' if (gi+a)%2 else 'raster','size':[18,24,36.5][(gi+2*a)%3],'width':[180,260,360][(gi+a+gi//3)%3],'opaque':bool((gi+a//2)%2),'bold':bool(mask&1),'italic':bool(mask&2),'underline':bool(mask&4),'strike':bool(mask&8),'text':'One\nTwo lines','anchor':[200,100],'move_delta':[200,150]})
factors=['font','align','mode','bold','italic','underline','strike'];coverage={}
for x,y in combinations(factors,2):
 required=set(product({r[x] for r in rows},{r[y] for r in rows}));actual={(r[x],r[y]) for r in rows};assert required==actual,(x,y,required-actual);coverage[x+' / '+y]=len(actual)
files=['trebuc.ttf','trebucbd.ttf','trebucit.ttf','trebucbi.ttf','arial.ttf','arialbd.ttf','ariali.ttf','arialbi.ttf','georgia.ttf','georgiab.ttf','georgiai.ttf','georgiaz.ttf','cour.ttf','courbd.ttf','couri.ttf','courbi.ttf','comic.ttf','comicbd.ttf','comici.ttf','comicz.ttf','impact.ttf'];installed=[]
for filename in files:
 p=Path('C:/Windows/Fonts')/filename;family,style=ImageFont.truetype(str(p),24).getname();installed.append({'file':str(p),'family':family,'style':style,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'rows':rows,'pairwise_factors':factors,'pairwise_coverage':coverage,'other_properties':'Size18/24/36.5, width180/260/360 and opaque/clear backgrounds vary, with boundary controls checked separately under LIVE-040. No full Cartesian claim.','requested_font_families_installed':True,'font_files':installed,'style_note':'Impact regular is installed; Windows/Canvas may synthesize requested bold/italic styles. No unavailable-family fallback has been identified.','preview_evidence':'Supported browser screenshots are JPEG, not raw canvas pixels. Retain paired frames and actual clipboard source PNGs; use saved PNG/project bytes for exact persistence.'};(out/'caption-font-plan40.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'rows':len(rows),'covered_factor_pairs':len(coverage),'fonts':fonts},indent=2))
