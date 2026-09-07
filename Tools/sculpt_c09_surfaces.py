"""Baked garden relief and continuous crossing beds; shared visible/collision mesh."""
import numpy as np,json
from pathlib import Path
from scipy.ndimage import gaussian_filter
from brain_craft_layout import *
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/BrainCraft';OUT=ART/'Source/C09';OUT.mkdir(parents=True,exist_ok=True)
def relief(x,y):
    # Long erosion swales support soft rounded moss cushions. Small soil relief
    # stays within 3 cm, well below the attention character's foot clearance.
    dd=np.full(np.broadcast_shapes(np.shape(x),np.shape(y)),1e6)
    for r in ROUTES:dd=np.minimum(dd,distance(x,y,curve(r['points'],12,False),False))
    dd=np.minimum(dd,np.abs(np.hypot(x,y)-780))
    grass=np.clip((dd-125)/135,0,1);grass=grass*grass*(3-2*grass)
    soil=1.25*np.sin(x/23+y/91)*np.sin(y/31)+.65*np.cos(x/11-y/49)
    cushion=8+8*np.sin(x/81+np.sin(y/175))*np.sin(y/76)+4*np.cos(x/37-y/63)
    return soil*(1-grass)+cushion*grass,grass
for key in ['Ground','EarthPath']:
    d=np.load(ART/'Source'/(key+'.npz'));v=d['v'].copy();dz,g=relief(v[:,0],v[:,1]);top=v[:,2]>-100;v[top,2]+=dz[top]
    # A real grass/soil edge with consistent height on both overlapping meshes.
    np.savez_compressed(OUT/(key+'.npz'),v=v,f=d['f'],grass=g)
# Paving only supplied disconnected tiles. The continuous stone bed below them
# now follows the complete route across each stream and lotus-ring crossing.
xs=np.arange(-3240,3241,14.);ys=np.arange(-3460,3461,14.);X,Y=np.meshgrid(xs,ys,indexing='ij');d,h,road=fields(X,Y);h=gaussian_filter(h,2.1);w=water(X,Y)
mask=(w<45)&(road<-15)&(d<20)&(distance(X,Y,curve(OUTLINE,10))<0)
ids=np.full(mask.shape,-1,int);ids[mask]=np.arange(mask.sum());v=np.column_stack([X[mask],Y[mask],h[mask]+1]).tolist();f=[]
for i,j in np.argwhere(mask[:-1,:-1]&mask[1:,:-1]&mask[1:,1:]&mask[:-1,1:]):f.append([int(ids[i,j]),int(ids[i+1,j]),int(ids[i+1,j+1]),int(ids[i,j+1])])
edges={}
for face in f:
    for a,b in zip(face,face[1:]+face[:1]):
        k=tuple(sorted((a,b)))
        if k in edges:del edges[k]
        else:edges[k]=(a,b)
lower={}
for a,b in edges.values():
    for k in [a,b]:
        if k not in lower:lower[k]=len(v);v.append([v[k][0],v[k][1],v[k][2]-45])
    f.append([b,a,lower[a],lower[b]])
np.savez_compressed(OUT/'CrossingBeds.npz',v=np.array(v),f=np.array(f))
(OUT/'displacement-report.json').write_text(json.dumps(dict(method='Baked geometric displacement; the same triangles provide collision',soil_relief_cm=2.6,moss_relief_cm=20,grid_cm=14,crossing_faces=len(f),art_accepted=False),indent=2))
print('C09_SURFACES',len(v),len(f))
