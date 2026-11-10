"""Record independently verified boundaries, circular finishes and legacy imports."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,re
from pathlib import Path
folder=Path(__file__).resolve().parent;root=folder.parents[2]
path=folder/'execution.json';ledger=json.loads(path.read_text(encoding='utf-8'))
updates={
 'LAYER-012':('Pass','Native Add reached exactly16 sheets at960×640; Add and Duplicate disabled with16-layer explanation. Tried disabled Add; removed top disposable sheet, added replacement and independently verified first15 layers unchanged. Prepared4000²one-sheet fixture with known red corner; added to exactly4 sheets=64,000,000 stored pixels, next Add disabled with pixel-budget explanation. Removed top sheet and successfully added replacement; source and first3 sheets exact. At4096²,3 sheets=50,331,648 accepted and fourth67,108,864 blocked. Saved actual files decoded independently; every added sheet transparent and original marker preserved. Initial size fixture with stale photo dimensions was correctly rejected, then preparation corrected; that is not an application defect.','tiff-limit-verification.json'),
 'FILE-010':('Pass','Native Open image imported independently encoded uncompressed8bit RGB/RGBA/greyscale PATCH TIFF fixtures. Actual PNG and saved-layer pixels exactly match Pillow decoding for all3, including alpha. UnsupportedLZW reported unsupported compression/depth. Native zero-width/oversize-width reported1–4096 limit; outside-directory/outside-strip/short-strip/zero-rows/missing-last-strip/truncated all reported damaged/incomplete. Saved whole project after each of9 rejections is exactly equal to prior greyscale document.','tiff-limit-verification.json'),
 'FILE-015':('Partial','Located genuine historical UI downloads with producer revisions and matching manifest hashes forv1(3916c24),v2(5ae1169),v9(c85f751). Imported each through native chooser, saved currentformat, reopened natively and saved again: whole upgradedJSON exact for all3; original nonraster fields retained. v1/v2 renderedPNG pixel-exact to historical reference, includingv2 photo original and768×192crop. v9 rebuilt20mmCube and exportedSTL byte-identical to historicaloriginal; historical CADpreview has3 pixels with red difference1 and alphaexact after currentCanvas decode. Do not callv9 historicalpreview bitexact. Authenticv3–8 unavailable; prior producer search/user record confirms no additional files.','legacy-import-verification.json'),
 'FEATURE-001':('Partial','Read cut/finish tree and original rectangle/circle branches. Renamed finish with deliberately long label; stored60-character supported name appears in tree and timeline and survives actual native reopen exactly. Tree secondpage selects circle sketch and editor reports4×4mm supportingface. Full primitive+cut+finish node expansion and other name branches remain pending.','circular-finish-verification.json'),
 'FEATURE-007':('Partial','At measuredCSS844×390, paged six-node tree1/2→2/2; selected final circle sketch, opened corresponding original4×4mm editor and reachedCancel. Returned unchanged and resetviewport. Timeline currently4steps; a longer timeline requiring its ownpaging remains pending.','circular-finish-verification.json'),
 'FEATURE-013':('Partial','Native separate specimens: plate20×10×5 with4mmthroughhole, topentrance0.5mmfillet and0.5mmchamfer; cylinderD20H20 topouterrim1mmfillet. ActualSTLs independently decoded closed/oppositelypairededges. Horizontal rays verify intendedtopfinish radius and unchanged bottomrim/bore. Holevolumes agreeanalytic within0.02mm³; outercylinderwithin0.02percent tessellation tolerance (0.01503percentactual), sampledYbounds within0.002mm. Savededge references are wholeclosedCIRCLE,centerZ1,normal+Z. Additional nestedconcentric/similar-radius references pending.','circular-finish-verification.json'),
 'FEATURE-014':('Partial','Edited existing0.5mmholefillet and choseReselectedges: sharp original hole/plate displayed with completecircle selected. Toggledtopcircleoff; picked different original outeredge; previewed0.3mm replacement. Cancel restores exact savedbody/recipe. Applying replacement with dependent laterfeatures remains pending.','circular-finish-verification.json'),
 'FILE-024':('Partial','Observed automaticdraft status pause above24million storedpixels on actual64million-pixel project; nativeSaveproject succeeds and bytes independentlydecoded. Retention count/character cutoff and remaining recovery variants still pending.','tiff-limit-verification.json'),
}
for case in ledger['cases']:
 if case['id'] not in updates:continue
 status,note,evidence=updates[case['id']];case['status']=status
 if note not in case['observations']:case['observations'].append(note)
 evidence='test-results/audit-2026-11-05/mouse/'+evidence
 if evidence not in case['evidence']:case['evidence'].append(evidence)
ledger['updated']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts=Counter(x['status'] for x in ledger['cases']);print(dict(counts))
p=folder/'README.md';text=p.read_text(encoding='utf-8')
text=re.sub(r'Current accounting: \*\*[^\n]+\*\*',f"Current accounting: **{counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Not run']} Not run, {counts['Blocked']} Blocked**",text,count=1)
note='''

## TIFF, layer boundaries, circular finishes and legacy migrations

FILE-010 and LAYER-012 pass with actual native import/save bytes checked by
verify-tiff-and-limits.py. RGB/RGBA/greyscale TIFFs are pixel exact, and nine
rejected variants leave the whole prior document exact. Sixteen sheets and
the exact64-million-pixel boundary disable Add with the correct explanation;
removal releases capacity. Three4096² sheets are accepted; four are blocked.

verify-circular-finishes.py checks actual outer-cylinder and hole entrance
finishes against analytic volumes and horizontal cross sections, including
unchanged bottom rims/bores. Whole circle references and native name persistence
are verified; additional nested references and dependent reselection remain.

verify-legacy-imports.py verifies producer hashes and current native migration
roundtrips for authentic versions1/2/9. Versions1/2 render pixel-exactly;
version9 has three one-level red preview differences after canvas decoding.
Its rebuilt STL is byte-identical to the historical cube. Authentic versions
3–8 remain unavailable; historical status is not reused as a fresh pass.

LIVE016 fixes stale Print validation: geometry/history, relevant selection,
scope and bed-setting changes clear old size/fit output and require a fresh
check. Starting a check also clears old success before a possible failure.
The corrected regression fails before the fix and passes allfour layouts
after it; native production bed/geometry changes were verified. The first
test attempt used an invalid callback and is retained as a test diagnostic.
TypeScript/build and the full sixteen-fix regression pass614checks with
zero failures and zero page errors (`all-sixteen-fixes/report.json`).
'''
if '## TIFF, layer boundaries' not in text:text+=note
p.write_text(text,encoding='utf-8')
p=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(p.read_text(encoding='utf-8'))
for item in env['dirty_source']:item['sha256']=hashlib.sha256((root/item['path']).read_bytes()).hexdigest()
if not any(x['path']=='src/cad-inspect-ui.ts' for x in env['dirty_source']):env['dirty_source'].append({'path':'src/cad-inspect-ui.ts','sha256':hashlib.sha256((root/'src/cad-inspect-ui.ts').read_bytes()).hexdigest()})
env['fix_count']=16;env['recorded']=ledger['updated'];env['latest_regression']={'report':'test-results/audit-2026-11-05/all-sixteen-fixes/report.json','passed':614,'failed':0,'page_errors':0}
env.pop('latest_full_regression_note',None);p.write_text(json.dumps(env,indent=2)+'\n')
