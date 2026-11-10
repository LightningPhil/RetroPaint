"""Close actual Save/export format branches after independent decode and reopens."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];r=json.loads((root/'test-results/audit-2026-11-05/mouse/format43-verification.json').read_bytes());assert r['status']=='Pass'
notes={
'FILE-006':'Main toolbarSAVEactualdownload on4layerMIXhalfCharacter while rulersandselectionhandlesvisible. PNG960x640compositionexactoutsideanalyticDogstampbounds, knownhalf-opacityRed/Greenexact, editableprojectunchanged, noeditingoverlays, actualOpenimagePNG roundtripexact. AdditionalBackdropPhotoLab+1EVDone/save: independentlinear-sRGBdoubling predicts45,186,255, completecompositeexactoutsideDogbounds, sources/otherlayersunchanged, savedrecipeprojectandPNGnative-reopens exact. InitialasyncPhotoexportcompletioncheckedbeforefileappeared, thenwaitedthroughactualreadyUIwithoutreclicking.',
'FILE-007':'Two-layerPATCHPaperhiddenviaLayers; PNG/WebP/TIFF realdownloadsindependentlydecode960x640withfullRGBAexact(includingallalphaandsemiRed128). ActualWebPoutputisRGBAexactforthisfixture; lossyWebPcapabilitynotgeneralized. NativeOpenimageandPNG/projectretentionexactforeach. Contrastingblack/whitecompositesvisuallyinspected; sourceprojectunchangedaftereveryexport.',
'FILE-008':'TransparentPATCHJPEGand24bitRGBBMPgenuineformats960x640withopaqueWhitematte. BMPeveryRGBbyteexactindependentcomposite. JPEGpredeclaredMAE<=3/PSNR>=32dB/interiorMAE<=3max8/clearmattewithin2; measuredwholeMAE0.1234668andPSNR43.463879dB, interiorswithinbudget; edgechromaRGBdifferencesrecorded(max102notpixelidentity). Transparenteditableprojectunchangedafterboth; actualOpenimage reimports independentlydecodedoutput, nativePNGroundtripsverified.',
'FILE-009':'COLOURrichsourcewith11hue/neutraltiles×alpha0/64/127/128/192/255plusopaqueRGBgradient. RealGIFdecodedP256entries,oneframe,alphaexactbinarythreshold128. OpaquequantisationmaxRGB31/31/85withinpredeclared37/37/85;191997opaqueRGBpixelschanged,RGBMAE10.19/10.10/21.18. Explicitlypalette-limitedstill,nottruecolour,exactblack,partialalphaoranimation. NativeOpenimageandPNG/projectroundtripofrichGIFexact. PATCHbinaryalphaexportalsoexactpolicy; black/whitebackgroundcontactsheetvisuallyinspected.'}
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
 if c['id'] not in notes:continue
 c['status']='Pass'
 if notes[c['id']] not in c['observations']:c['observations'].append(notes[c['id']])
 for name in ['format43-verification.json','format43-evidence.json','format43-contrasting-backgrounds.png','save43-before-main-button.jpg','save43-photo-live-result.jpg']:
  path='test-results/audit-2026-11-05/mouse/'+name
  if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':89,'Partial':257,'Blocked':3}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**85 Pass, 261 Partial','**89 Pass, 257 Partial')
if '## FILE-006–009: real image exports' not in text:text+='\n## FILE-006–009: real image exports\n\n'+'\n\n'.join(k+': '+v for k,v in notes.items())+'\n'
rp.write_text(text,encoding='utf-8');print(counts)
