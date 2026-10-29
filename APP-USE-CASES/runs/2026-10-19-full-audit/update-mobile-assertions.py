from pathlib import Path
import re

root=Path(__file__).resolve().parents[3]
path=root/'tests/mobile.ts'
source=path.read_text(encoding='utf-8')
pattern=r"assert\((page|panel|el\('#cad[^']+'\))\.scrollHeight<=\1\.clientHeight\+2,([^;]*?)\)"
prefix,checks=source.split("await run('CAD every tool category",1)
checks,count=re.subn(pattern,r'checkCadPage(\1,\2)',checks)
assert count in [0,14],count
source=prefix+"await run('CAD every tool category"+checks
source=source.replace('CAD every tool category and sketch stage fits without scrolling at this viewport','CAD every tool category and sketch stage keeps full controls reachable at this viewport')
source=source.replace('CAD finish history reselects original edges and safely rejects impossible radii without scrolling','CAD finish history reselects original edges and safely rejects impossible radii with reachable controls')
path.write_text(source,encoding='utf-8')
print('Updated',count,'CAD-only assertions: retain desktop fit; compact panels require unscaled 44px reachable controls')
