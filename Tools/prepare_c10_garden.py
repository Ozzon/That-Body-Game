"""Vegetation ecology and revised portal approaches on the real displaced floor."""
import numpy as np,json
from pathlib import Path
from scipy.spatial import cKDTree
from brain_craft_layout import *
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/BrainCraft';OUT=ART/'Source/C10';OUT.mkdir(parents=True,exist_ok=True)
PORTALS=[dict(name='Dawn alcove',p=(-2130,-2020,140),yaw=90),dict(name='Spring of ideas',p=(-1040,1760,1100),yaw=0),dict(name='Memory shelter',p=(2050,1700,950),yaw=-25)]
(OUT/'portal-layout.json').write_text(json.dumps(PORTALS,indent=2))
d=np.load(ART/'Source/C09/Ground.npz');v=d['v'];v=v[v[:,2]>-100];tree=cKDTree(v[:,:2]);rng=np.random.default_rng(1009)
xx,yy=np.meshgrid(np.arange(-3000,3000,34),np.arange(-3250,3250,34),indexing='ij');x=xx.ravel()+rng.uniform(-12,12,xx.size);y=yy.ravel()+rng.uniform(-12,12,xx.size)
dist,z,rd=fields(x,y);wt=water(x,y);dd=np.full(len(x),1e6)
for r in ROUTES:dd=np.minimum(dd,distance(x,y,curve(r['points'],12,False),False))
dd=np.minimum(dd,np.abs(np.hypot(x,y)-780))
# Broken, sculpted green edges arise from actual blades and rosettes. No broad
# green overlay or blurred color strip remains on the trail itself.
variation=25*np.sin(x/139+y/173)+18*np.sin(x/81-y/129)
ok=(dist<-25)&(wt>40)&(dd>119+variation)&(np.hypot(x,y-90)>355)&(np.hypot(x-LOTUS[0],y-LOTUS[1])>365)
ok&=(np.hypot((x+1610)/250,(y+2500)/185)>1.1)
for e in PORTALS:
    a=np.radians(e['yaw']);dx=x-e['p'][0];dy=y-e['p'][1];lx=np.cos(a)*dx+np.sin(a)*dy;ly=-np.sin(a)*dx+np.cos(a)*dy;ok&=~((np.abs(lx)<340)&(ly>-470)&(ly<130))
x=x[ok];y=y[ok];error,ix=tree.query(np.column_stack([x,y]));z=v[ix,2];ok=error<25;x=x[ok];y=y[ok];z=z[ok]
np.savez_compressed(OUT/'cover-points.npz',p=np.column_stack([x,y,z]),scale=rng.uniform(.72,1.26,len(x)),angle=rng.uniform(0,np.pi*2,len(x)))
ground=np.load(ART/'Source/C09/Ground.npz');cover=cKDTree(np.column_stack([x,y]));near,_=cover.query(ground['v'][:,:2]);np.savez_compressed(OUT/'turf-mask.npz',turf=near<32)
# Exclude the physically solid portal backs and feet from routes. The wide
# front landings remain available for collecting and handling a thought.
nav=np.load(ART/'Source/navigation.npz');mask=nav['walk'].copy();X,Y=np.meshgrid(nav['x'],nav['y'],indexing='ij')
for e in PORTALS:
    a=np.radians(e['yaw']);dx=X-e['p'][0];dy=Y-e['p'][1];lx=np.cos(a)*dx+np.sin(a)*dy;ly=-np.sin(a)*dx+np.cos(a)*dy
    mask&=~((np.abs(lx)<335)&(ly>-150)&(ly<140))
np.savez_compressed(OUT/'navigation.npz',x=nav['x'],y=nav['y'],walk=mask,h=nav['h'])
(OUT/'ecology-report.json').write_text(json.dumps(dict(grass_clusters=len(x),placement='moist banks and soft margins, excluded portal landings, sand and clear paths',portal_min_spacing_cm=min(np.linalg.norm(np.array(a['p'])-np.array(b['p'])) for i,a in enumerate(PORTALS) for b in PORTALS[i+1:]),art_accepted=False),indent=2))
print('C10_COVER',len(x))
