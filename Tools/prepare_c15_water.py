"""One descending spring channel and a grounded lotus moat.

The physical bed and the visible water share a single height profile. Existing
path crossings retain their walkable deck; the stream passes below those decks.
"""
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter1d, distance_transform_edt
from scipy.spatial import cKDTree
from brain_craft_layout import curve
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'Art/BrainCraft/Source/C14';OUT=ROOT/'Art/BrainCraft/Source/C15'
d=np.load(OLD/'terrain.npz');H=d['h'].copy();prior=H.copy();xs=d['x'];ys=d['y'];step=xs[1]-xs[0]
X,Y=np.meshgrid(xs,ys,indexing='ij')
def sample(h,p):
    p=np.asarray(p);return map_coordinates(h,[(p[...,0]-xs[0])/step,(p[...,1]-ys[0])/step],order=1,mode='nearest')
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
xy=curve([(-1680,975),(-1870,780),(-1790,450),(-1590,155),(-1250,-150),(-970,-630)],42,False)
along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]
level=gaussian_filter1d(sample(H,xy)+9,4)
level=np.minimum.accumulate(np.minimum(level,1056)+along*.035)-along*.035
width=92+17*np.sin(along/350)+30*np.exp(-((along-along[-1])/250)**2)
tree=cKDTree(xy);dist,idx=tree.query(np.column_stack([X.ravel(),Y.ravel()]));dist=dist.reshape(H.shape);idx=idx.reshape(H.shape)
bed=level[idx]-32;influence=1-smooth((dist-width[idx]*.75)/100)
crossing=d['path']&(dist<width[idx]+70)
# Smooth bank shoulders grow into the existing landscape. Preserve the path
# surface so crossings are navigable while we form their stone side arches.
path_fade=smooth(distance_transform_edt(~d['path'])*step/135)
influence*=path_fade
H=H*(1-influence)+bed*influence
moat_r=np.sqrt(((X-1580)/1.02)**2+(Y+1390)**2)
moat_influence=(1-smooth((np.abs(moat_r-570)-46)/155))*path_fade
H=H*(1-moat_influence)+285*moat_influence
# Limit the bank's actual mesh grade, not just the width of its blend mask.
# Existing paved deck samples are fixed; adjacent earth gives way gradually.
changed_mask=np.abs(H-prior)>.02
editable=(distance_transform_edt(~changed_mask)*step<280)&(~d['path'])
for iteration in range(100):
    for di,dj in [(1,0),(0,1),(1,1),(1,-1)]:
        aa=(slice(0,-di or None),slice(None,-dj)) if dj>0 else (slice(0,-di or None),slice(-dj,None)) if dj<0 else (slice(0,-di or None),slice(None))
        bb=(slice(di,None),slice(dj,None)) if dj>=0 else (slice(di,None),slice(None,dj))
        av=H[aa];bv=H[bb];ea=editable[aa];eb=editable[bb]
        diff=bv-av;excess=np.sign(diff)*np.maximum(np.abs(diff)-step*np.hypot(di,dj)*.60,0)
        av+=excess*np.where(ea&eb,.5,np.where(ea,1,0));bv-=excess*np.where(ea&eb,.5,np.where(eb,1,0))
delta=H-prior;gx,gy=np.gradient(H,step);N=np.stack([-gx,-gy,np.ones_like(H)],axis=-1);N/=np.linalg.norm(N,axis=-1)[...,None]
np.savez_compressed(OUT/'terrain.npz',x=xs,y=ys,h=H,inside=d['inside'],path=d['path'],wet=d['wet'],delta=delta)
changed=[]
for src in sorted(OLD.glob('Terrain*.npz')):
    if src.stem.lower()=='terrain':continue
    a=np.load(src);v=a['v'].copy();n=a['n'].copy();f=a['f'];top=int(a['topfaces']);topids=np.unique(f[:top]);change=sample(delta,v[:,:2])
    if np.max(np.abs(change[topids]))<.06:continue
    istop=np.abs(v[:,2]-sample(prior,v[:,:2]))<.08
    v[istop,2]+=change[istop]
    for axis in range(3):n[topids,axis]=sample(N[:,:,axis],v[topids,:2])
    np.savez_compressed(OUT/src.name,v=v,f=f,n=n,c=a['c'],topfaces=top);changed.append(src.stem)
tangent=np.gradient(xy,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];side=np.column_stack([-tangent[:,1],tangent[:,0]])
np.savez_compressed(OUT/'watercourse.npz',xy=xy,level=level,width=width,side=side,along=along)
report=dict(terrain=changed,stream_length_cm=float(along[-1]),maximum_water_rise_cm=float(np.diff(level).max()),maximum_terrain_cut_cm=float(-delta.min()),crossing_decks_preserved=True,art_accepted=False)
(OUT/'water-construction.json').write_text(json.dumps(report,indent=2));print('C15_WATER_PROFILE_READY',json.dumps(report),flush=True)
