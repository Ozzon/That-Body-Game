"""Soft joined cloud volumes based on Figma ref-275's thought cast."""
from pathlib import Path
import numpy as np
from skimage.measure import marching_cubes
from scipy.ndimage import gaussian_filter
OUT=Path(__file__).resolve().parents[1]/'Art/BrainCraft/Source/C11'
for key,size,count in [('ThoughtCloud',1.,24),('ThoughtWisp',.47,13)]:
    step=2.3;xs=np.arange(-100,101,step);X,Y,Z=np.meshgrid(xs,xs,xs,indexing='ij');field=np.ones(X.shape,np.float32)*1e3
    # A rounded dense core supports unequal curls on the silhouette. Smooth
    # union joins them into one editable closed body, avoiding intersecting balls.
    centers=[(0,0,0,47)]
    for k in range(count):
        z=1-2*(k+.5)/count;a=k*2.399;rr=np.sqrt(1-z*z);centers.append((rr*np.cos(a)*42,rr*np.sin(a)*52,z*40,21+5*np.sin(k*1.3)))
    for x,y,z,r in centers:
        d=np.sqrt((X-x)**2+((Y-y)*.86)**2+(Z-z)**2)-r;kk=9.;q=np.clip(.5+.5*(d-field)/kk,0,1);field=d*(1-q)+field*q-kk*q*(1-q)
    field=gaussian_filter(field,.45);v,f,n,_=marching_cubes(field,0,spacing=(step,step,step));v=(v+xs[0])*size
    np.savez_compressed(OUT/(key+'.npz'),v=v,f=f,n=-n);print(key,len(v),len(f),flush=True)
