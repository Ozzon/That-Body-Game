"""Continuous rounded gyri without interpreting illustrated shadows as height.

The grayscale experiment produced pointed rock-like shapes. This replacement
uses long curved folds in a signed volume; it leaves the playable floor intact.
"""
import numpy as np,json
from pathlib import Path
from scipy.ndimage import distance_transform_edt,gaussian_filter
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
from organ_math import curve,distance
from brain_craft_layout import fields,OUTLINE,SHORTCUT
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/BrainCraft/Source/C08';OUT.mkdir(exist_ok=True)
step=22.;xs=np.arange(-3260,3261,step);ys=np.arange(-3480,3481,step);X,Y=np.meshgrid(xs,ys,indexing='ij')
d,h,road=fields(X,Y);h=gaussian_filter(h,8)
inside=distance(X,Y,curve(OUTLINE,14))<0
mask=inside&(d>60)&(distance(X,Y,curve(SHORTCUT,16,False),False)>310)
sd=(distance_transform_edt(~mask)-distance_transform_edt(mask))*step;sd=gaussian_filter(sd,1)
lines=[]
# Long, joined folds run across each hemisphere with interrupted secondary
# branches. Radius and phase vary by row; no independently scattered primitives.
for side in [-1,1]:
    for row in range(20):
        yy=-3400+row*355;pts=[]
        for col in range(15):
            xx=side*(col*248+30);oy=100*np.sin(col*.8+row*.93)+53*np.sin(col*1.7-row*.47)
            pts.append((xx,yy+oy))
        for start,end in [(0,6),(7,15)] if row%3==1 else [(0,15)]:lines.extend(curve(pts[start:end],14,False))
    for col in range(6):
        xx=side*(300+col*510)
        for row in [2,7,12,17]:
            yy=-3300+row*355;lines.extend(curve([(xx-60,yy),(xx+70,yy+115),(xx+50,yy+210)],12,False))
tree=cKDTree(np.asarray(lines)[:,:2]);dd=tree.query(np.column_stack([X.ravel(),Y.ravel()]))[0].reshape(X.shape)
radius=182+15*np.sin(X/810+Y/960)
folds=175*(.5+.5*np.cos(np.pi*np.clip(dd/radius,0,1)))
# The inner garden edge is a low rounded bank. Outer tissue is substantial but
# remains below a cliff-like silhouette; clear elevations belong to the garden.
rim=np.clip(-sd/210,0,1);top=h+120+folds*rim+135*np.sin(rim*np.pi/2)
zzs=np.arange(-320,2101,step);volume=np.empty((len(xs),len(ys),len(zzs)),np.float32)
for k,z in enumerate(zzs):
    bulge=32+28*np.cos(z/116+Y/290+1.1*np.sin(X/390))
    lateral=sd-bulge
    vertical=np.maximum(z-top,-210-z)
    bevel=68.;volume[:,:,k]=np.maximum(lateral,vertical)+bevel*np.log1p(np.exp(-np.abs(lateral-vertical)/bevel))
volume=gaussian_filter(volume,.65)
v,f,n,_=marching_cubes(volume,0,spacing=(step,step,step));v+=np.array([xs[0],ys[0],zzs[0]])
# Split only AFTER smoothing. No per-quarter modifier may pull apart the seam.
centers=v[f].mean(axis=1);report={}
for ix in [-1,1]:
    for iy in [-1,1]:
        ff=f[(centers[:,0]*ix>=0)&(centers[:,1]*iy>=0)];used,inv=np.unique(ff,return_inverse=True);key=f'Cortex{ix}{iy}';np.savez_compressed(OUT/(key+'.npz'),v=v[used].astype(np.float32),f=inv.reshape(-1,3).astype(np.int32),n=n[used]);report[key]=[len(used),len(ff)]
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(report)
