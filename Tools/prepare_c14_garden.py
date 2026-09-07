"""A continuous north garden slope and three entrances anchored to the cortex."""
from pathlib import Path
import json,math
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter
from shapely.geometry import Polygon,Point,LineString
from brain_craft_layout import OUTLINE,curve
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/BrainCraft';OLD=ART/'Source/C13';OUT=ART/'Source/C14';OUT.mkdir(exist_ok=True)
d=np.load(OLD/'terrain.npz');xs=d['x'];ys=d['y'];step=xs[1]-xs[0];X,Y=np.meshgrid(xs,ys,indexing='ij');H=d['h'].copy();prior=H.copy()
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def sample(h,p):p=np.asarray(p);return map_coordinates(h,[(p[...,0]-xs[0])/step,(p[...,1]-ys[0])/step],order=1,mode='nearest')
# The previous bank's protected ring preserved 46-50 degree facets. Its new
# approach is a broad 17-25 degree meadow slope, continuous with the tree ring.
profile=np.interp(Y,[600,1650,2100],[520,866,1060])
weight=(1-smooth((np.abs(X)-360)/460))*smooth((Y-500)/240)*(1-smooth((Y-1740)/400))
H=H*(1-weight)+profile*weight
outline=Polygon(curve(OUTLINE,30));edge=outline.exterior;gates=[]
for i,e in enumerate(json.loads((OLD/'portals.json').read_text())):
    old=np.array(e['p'][:2]);b=edge.interpolate(edge.project(Point(old)));border=np.array(b.coords[0]);out=(border-old);out/=np.linalg.norm(out)
    p=border-out*110;start=old-out*160;z0=float(sample(H,start[None,:])[0]);z1=float(sample(H,p[None,:])[0]);dv=p-start;length=np.linalg.norm(dv)
    t=np.clip(((X-start[0])*dv[0]+(Y-start[1])*dv[1])/(length*length),0,1);dist=np.hypot(X-start[0]-t*dv[0],Y-start[1]-t*dv[1])
    w=1-smooth((dist-175)/200);target=z0+(z1-z0)*smooth(t);H=H*(1-w)+target*w
    gates.append(dict(name=e['name'],color=e['color'],p=[float(p[0]),float(p[1]),z1],outward=out.tolist(),border=border.tolist(),approach_start=[*start.tolist(),z0],approach_length_cm=float(length),distance_to_outline_cm=float(edge.distance(Point(p))),opening_width_cm=360,opening_height_cm=410))
H=gaussian_filter(H,.38);delta=H-prior;gx,gy=np.gradient(H,step);N=np.stack([-gx,-gy,np.ones_like(H)],axis=-1);N/=np.linalg.norm(N,axis=-1)[...,None]
np.savez_compressed(OUT/'terrain.npz',x=xs,y=ys,h=H,inside=d['inside'],path=d['path'],wet=d['wet'],delta=delta)
changed=[]
for key in json.loads((OLD/'construction.json').read_text())['terrain_pieces']:
    a=np.load(OLD/(key+'.npz'));v=a['v'].copy();n=a['n'].copy();f=a['f'];top=int(a['topfaces']);top_ids=np.unique(f[:top]);change=sample(delta,v[:,:2])
    if np.max(np.abs(change[top_ids]))<.04:continue
    top_old=sample(prior,v[:,:2]);is_top=np.abs(v[:,2]-top_old)<.05;v[is_top,2]+=change[is_top]
    for axis in range(3):n[top_ids,axis]=sample(N[:,:,axis],v[top_ids,:2])
    bottom=float(v[top_ids,2].min()-110);is_bottom=(n[:,2]<-.99)|(np.abs(v[:,2]-a['v'][top_ids,2].min()+110)<.05);v[is_bottom,2]=bottom
    np.savez_compressed(OUT/(key+'.npz'),v=v,f=f,n=n,c=a['c'],topfaces=top);changed.append(key)
np.savez_compressed(OUT/'terrain.npz',x=xs,y=ys,h=H,inside=d['inside'],path=d['path'],wet=d['wet'],delta=delta)
for e in gates:e['p'][2]=float(sample(H,np.array(e['p'][:2])[None,:])[0])
(OUT/'portals.json').write_text(json.dumps(gates,indent=2))
bank=(np.abs(X)<300)&(Y>740)&(Y<1680);slope=np.hypot(gx,gy)
report=dict(changed_terrain=changed,northern_walk_max_degrees=float(np.degrees(np.arctan(slope[bank].max()))),gate_border_offsets_cm=[e['distance_to_outline_cm'] for e in gates],art_accepted=False)
(OUT/'construction.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
