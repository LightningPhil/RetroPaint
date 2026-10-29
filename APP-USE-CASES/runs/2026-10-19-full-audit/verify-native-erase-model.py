from pathlib import Path
from datetime import datetime,timezone
from native_erase_oracle import destination_out_valid
import json,numpy as np
root=Path(__file__).resolve().parent;probe=json.loads((root/'headless/ERASER-repeat-alpha/report.json').read_text(encoding='utf-8'));previous=None;count=0;max_ideal=0
for sample in probe['samples']:
    if sample['pass']==1:previous=np.array([229,57,53,255],dtype=np.uint8)
    current=np.array(sample['source_RGBA'],dtype=np.uint8);assert destination_out_valid(previous,current).all(),sample;count+=1;max_ideal=max(max_ideal,float(np.abs((current[:3].astype(float)-[229,57,53])*current[3]/255).max()));previous=current
assert count==2032 and max_ideal>1
report=dict(at=datetime.now(timezone.utc).isoformat(),status='Independent native integer model verified, not an acceptance result',actual_application_free_native_operations=count,invalid_integer_common_factor_transitions=0,maximum_invalid_single_rounding_assumption_error=max_ideal,method='Decode native RGBA into associated bytes by exact nearest integer division. Each destination-out must remove only pigment/alpha and admit one common inverse-coverage factor for every component, with the same single8-bit unit quantization at each operation. Integer interval intersections avoid floating or enlarged final-pixel thresholds. Repeated rounding is validated operation by operation, rather than assuming a path is composited once.',scope='Application-free2032 native observations only. Actual app calls must independently chain from the known source to an end image byte-for-byte/RGBA identical to the uninstrumented run before this model can resolve its colour diagnosis.')
(root/'evidence/NATIVE-destination-out-integer-model.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
