"""One authoritative gate/encounter layout; gate mouths face into the garden."""
import numpy as np,json
from pathlib import Path
from scipy.ndimage import map_coordinates
from brain_craft_layout import fields
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'Art/BrainCraft/Source/C11';t=np.load(DATA/'terrain.npz')
def height(x,y):return float(map_coordinates(t['h'],[[(x-t['x'][0])/14],[(y-t['y'][0])/14]],order=1)[0])
old=json.loads((DATA/'portals.json').read_text());new=[]
for name,x,y,yaw,color in [('First light',-2390,-2260,90,'Dawn'),('Spring of ideas',-1480,2510,0,'Spring'),('Memory grove',2320,1690,-70,'Memory')]:new.append(dict(name=name,p=[x,y,round(height(x,y),2)],yaw=yaw,color=color))
(DATA/'gate-move.json').write_text(json.dumps(dict(old=old,new=new),indent=2));(DATA/'portals.json').write_text(json.dumps(new,indent=2))
thoughts=[(-1770,-2060),(-1420,2160),(1960,1400),(1850,1220),(-1580,2160),(-1700,-1900)]
layout={'gates':new,'thoughts':[[x,y,height(x,y)+95] for x,y in thoughts]};(DATA/'encounters.json').write_text(json.dumps(layout,indent=2))
lines=['// Generated from the C11 border-gate and encounter layout.','namespace CraftLayout {','static const FVector Portals[]={'+','.join('FVector(%.2f,%.2f,%.2f)'%tuple(e['p']) for e in new)+'};','static const FVector Thoughts[]={'+','.join('FVector(%.2f,%.2f,%.2f)'%tuple(p) for p in layout['thoughts'])+'};','}']
(ROOT/'Source/ThatBodyGame/BrainCraftLayout.inl').write_text('\n'.join(lines))
d=np.load(ROOT/'Art/BrainCraft/Source/navigation.npz');X,Y=np.meshgrid(d['x'],d['y'],indexing='ij');mask=d['walk'].copy()
for e in new:
    a=np.radians(e['yaw']);dx=X-e['p'][0];dy=Y-e['p'][1];lx=np.cos(a)*dx+np.sin(a)*dy;ly=-np.sin(a)*dx+np.cos(a)*dy;mask&=~((np.abs(lx)<300)&(ly>-150)&(ly<170))
np.savez_compressed(DATA/'navigation.npz',x=d['x'],y=d['y'],walk=mask,h=d['h']);print(json.dumps(layout),flush=True)
