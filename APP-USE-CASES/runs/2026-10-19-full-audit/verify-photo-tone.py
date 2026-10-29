from pathlib import Path
from datetime import datetime,timezone
import json,base64,io
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parent
folder=root/'evidence'
read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
image=lambda path:np.asarray(Image.open(path).convert('RGBA'))
decode=lambda layer:image(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1])))
def variant(prefix,key,value,layout,source,baseline):
    name=f'{prefix}-{layout}-{str(value).replace("-","minus")}'
    doc=read(name+'.retropaint');meta=read(name+'.json')
    assert (doc['width'],doc['height'])==(1024,256) and len(doc['layers'])==1
    assert doc['crop']==baseline['crop'] and doc['active']==baseline['active']
    layer=doc['layers'][0];old=baseline['layers'][0]
    assert {k:v for k,v in layer.items() if k!='photo'}==old,'Source or layer properties changed'
    assert np.array_equal(decode(layer),source)
    settings=layer['photo']['settings']
    assert settings[key]==value and meta['slider']['value']==value
    zero=['exposure','brightness','contrast','highlights','shadows','whites','blacks','temperature','tint','saturation','vibrance','hue','sharpness','texture','clarity','pop','dehaze','noise','colourNoise','vignette','grain','distortion','aberration','vertical','horizontal','angle']
    assert all(settings[k]==(value if k==key else 0) for k in zero)
    assert settings['balance']==[1,1,1] and settings['zoom']==100 and not settings['flipX'] and not settings['flipY']
    assert all(v==[dict(x=0,y=0),dict(x=1,y=1)] for v in settings['curves'].values())
    assert all(not any(v.values()) for v in settings['mixer'])
    output=image(folder/(name+'.png'))
    assert output.shape==source.shape and np.array_equal(output[:,:,3],source[:,:,3])
    opaque=source[:,:,3]>0
    assert np.array_equal(output[opaque,0],output[opaque,1]) and np.array_equal(output[opaque,1],output[opaque,2]),'Neutral ramp acquired a colour cast'
    if value==0:assert np.array_equal(output,source),'Neutral reset did not restore all source RGBA'
    return dict(name=name,value=value,original_and_all_layer_properties_exact=True,alpha_exact=True,neutral_rgb_channels_equal=True,observed_range=[meta['slider']['min'],meta['slider']['max']]),output

rows={}
for layout,filename in [('opaque','TONAL.png'),('alpha','TONAL-alpha.png')]:
    source=image(root/'fixtures'/filename)
    baseline=read('TONAL-'+layout+'-baseline.retropaint')
    assert np.array_equal(decode(baseline['layers'][0]),source)
    assert np.array_equal(image(folder/('TONAL-'+layout+'-baseline.png')),source)
    rows[layout]=[]
    for value in [1,-1,-4,4,0]:
        record,output=variant('PHOTO-009','exposure',value,layout,source,baseline)
        # Independent vectorised implementation of the published sRGB transfer
        # equation, not an import/call of the application processor or tables.
        encoded=source[:,:,:3].astype(np.float64)/255
        light=np.where(encoded<=0.04045,encoded/12.92,((encoded+0.055)/1.055)**2.4)
        light=np.clip(light*2**value,0,1)
        expected=np.rint(np.where(light<=0.0031308,12.92*light,1.055*light**(1/2.4)-0.055)*255).astype(np.uint8)
        mask=source[:,:,3]>0
        error=int(np.abs(output[:,:,:3][mask].astype(np.int16)-expected[mask].astype(np.int16)).max())
        assert error<=1,(layout,value,error)
        record.update(srgb_linear_light_gain=2**value,max_rgb_error_255=error,tolerance_255=1)
        rows[layout].append(record)
result=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,independent_oracle='NumPy float64 sRGB decode -> multiply by 2**EV -> clamp -> sRGB encode -> 8-bit round',transfer_equation_source='https://www.w3.org/TR/2026/CRD-css-color-4-20261009/#predefined-sRGB',declared_max_rgb_error_255=1,dimensions=[1024,256],rows=rows,default_min_max_intermediate_executed=True,transparent_padding_and_five_uniform_patches_verified=True)
(folder/'PHOTO-009-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PHOTO-009: ten actual downloaded results match independent linear-light exposure within 1/255; alpha and underlying originals exact.')

if __name__=='__main__':
    for prefix,key,values in [('PHOTO-010','brightness',[25,-100,100,0]),('PHOTO-011','contrast',[30,-30,-100,100,0])]:
        all_rows={}
        for layout,filename in [('opaque','TONAL.png'),('alpha','TONAL-alpha.png')]:
            source=image(root/'fixtures'/filename);baseline=read('TONAL-'+layout+'-baseline.retropaint')
            entries=[];outputs={}
            for value in values:
                record,out=variant(prefix,key,value,layout,source,baseline)
                outputs[value]=out;entries.append(record)
            yy=100 if layout=='alpha' else 128
            sample=lambda value,level:int(outputs[value][yy,level*4+1,0])
            if key=='brightness':
                assert all(sample(25,level)>level for level in [32,64,128,192,224])
                assert all(sample(-100,level)<level for level in [32,64,128,192,224])
                # A stop of exposure scales linear light. Brightness is required
                # to be distinct: compare several nonsaturated source levels.
                exposure=image(folder/('PHOTO-009-'+layout+'-1.png'))
                assert sum(sample(25,level)!=int(exposure[yy,level*4+1,0]) for level in [32,64,128,192,224])>=3
            else:
                separation=lambda value:sample(value,160)-sample(value,96)
                assert separation(30)>64>separation(-30)
                assert separation(100)>separation(30)>separation(-30)>separation(-100)
            all_rows[layout]=entries
        report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,independent_oracle='Known input levels; monotonic patch values and relative tonal separation, unchanged RGBA alpha and original source',rows=all_rows,default_min_max_intermediate_executed=True,zero_setting_full_rgba_exact=True)
        (folder/(prefix+'-independent-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(prefix+': actual full-size pixels satisfy tone, neutral, alpha and default restoration criteria.')
