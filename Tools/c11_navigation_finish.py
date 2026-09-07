"""Bake reference routes against the modeled water banks and border gates."""
import numpy as np,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'Art/BrainCraft/Source/C11';d=np.load(DATA/'navigation.npz');X,Y=np.meshgrid(d['x'],d['y'],indexing='ij');mask=d['walk'].copy();h=d['h'].copy()
for r in json.loads((DATA/'garden-access.json').read_text()):
    if r['name']!='Spring promenade':continue
    p=np.array(r['points']);nearest=np.full(X.shape,1e9);hh=h.copy()
    for a,b in zip(p,p[1:]):
        v=b-a;t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/(v[0]**2+v[1]**2+1e-9),0,1);dd=np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1]);m=dd<nearest;hh=np.where(m,a[2]+t*v[2],hh);nearest=np.minimum(nearest,dd)
    m=nearest<r['width']/2-52;mask|=m;h=np.where(m,np.maximum(h,hh),h)
for x,y,radius in [(-1680,1780,338),(-1680,1280,358),(-1990,1890,140),(1480,1980,140)]:mask&=np.hypot(X-x,Y-y)>radius
np.savez_compressed(DATA/'navigation.npz',x=d['x'],y=d['y'],walk=mask,h=h)
print('C11_NATIVE_OBSTACLE_CLEARANCES',int(mask.sum()))
