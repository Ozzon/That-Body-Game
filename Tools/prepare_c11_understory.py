"""A planted valley supports the terrace composition instead of empty black gaps."""
import numpy as np,json
from pathlib import Path
from scipy.ndimage import gaussian_filter
from brain_craft_layout import fields,OUTLINE,curve,distance
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/BrainCraft/Source/C11';step=28.;xs=np.arange(-3240,3250,step);ys=np.arange(-3460,3470,step);X,Y=np.meshgrid(xs,ys,indexing='ij');d,h,_=fields(X,Y);inside=distance(X,Y,curve(OUTLINE,10))<-20
Z=gaussian_filter(h-190-np.clip(d+100,0,1100)*.32,4);Z+=12*np.sin(X/240)*np.sin(Y/170)
ids=np.full(X.shape,-1,int);ids[inside]=np.arange(inside.sum());V=np.column_stack([X[inside],Y[inside],Z[inside]]);F=[]
for i,j in np.argwhere(inside[:-1,:-1]&inside[1:,:-1]&inside[1:,1:]&inside[:-1,1:]):F.append((ids[i,j],ids[i+1,j],ids[i+1,j+1],ids[i,j+1]))
np.savez_compressed(OUT/'Understory.npz',v=V,f=np.array(F));mask=inside&(d>175)&(d<1000);rng=np.random.default_rng(1181);points=np.argwhere(mask);points=points[::25];P=np.array([(X[i,j]+rng.uniform(-15,15),Y[i,j]+rng.uniform(-15,15),Z[i,j]) for i,j in points]);np.savez_compressed(OUT/'understory-plants.npz',p=P);print('C11_UNDERSTORY',len(V),len(P),flush=True)
