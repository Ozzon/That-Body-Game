"""Fit the cortical mantle to every real outer traversal clearance."""
import json,numpy as np
from pathlib import Path
from scipy.ndimage import gaussian_filter1d
from brain_craft_layout import fields,OUTLINE,curve
from shapely.geometry import Polygon
from shapely import contains_xy
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/BrainCraft/Source/C11'
n=1440;m=120;a=np.arange(n)*np.pi*2/n;r=np.linspace(.50,1.24,120);A,R=np.meshgrid(a,r,indexing='ij');X=3100*R*np.cos(A);Y=3410*R*np.sin(A);dd,hh,_=fields(X,Y)
# Each radial rim starts beyond the outermost traversable piece, with 130 cm
# additional clearance; smooth the safe envelope only outward.
inside=contains_xy(Polygon(curve(OUTLINE,10)).buffer(-25),X,Y)
inner=np.max(np.where((dd<180)|inside,R,.5),axis=1);inner=np.maximum(inner,gaussian_filter1d(inner,5,mode='wrap'))+.025
zbase=np.zeros(n)
for i in range(n):
    x=3100*(inner[i]-.055)*np.cos(a[i]);y=3410*(inner[i]-.055)*np.sin(a[i]);zbase[i]=float(fields(x,y)[1])
zbase=gaussian_filter1d(zbase,6,mode='wrap');V=[];F=[];C=[]
for i,angle in enumerate(a):
    for j in range(m):
        t=j/(m-1);radius=inner[i]+.265*np.sin(t*np.pi);x=3100*radius*np.cos(angle);y=3410*radius*np.sin(angle)
        u=angle*35+1.8*np.sin(t*np.pi*5+angle*3);v=t*np.pi*6+.9*np.sin(angle*13)
        fold=(.5+.5*np.cos(u+np.sin(v)*1.2))**.44;across=(.5+.5*np.cos(v+.4*np.sin(u*1.7)))**.4
        relief=fold*across*340;z=zbase[i]+95+240*np.sin(t*np.pi*1.5)-660*t+relief*np.sin(t*np.pi)**.55
        V.append((x,y,z));shade=.83+.17*fold*across;C.append((.49*shade,.18*shade,.23*shade))
        if j:q=i*m+j-1;ni=((i+1)%n)*m+j-1;F.append((q,ni,ni+1,q+1))
np.savez_compressed(OUT/'CortexShell.npz',v=np.array(V),f=np.array(F),c=np.array(C));print('C11_MANTLE_CLEARANCE_FITTED',float(inner.min()),float(inner.max()),flush=True)
