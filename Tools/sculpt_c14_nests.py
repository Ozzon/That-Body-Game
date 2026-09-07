"""Fused organic thought nests with a carved bowl, based on Figma ref-275."""
from pathlib import Path
import numpy as np,json
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes
OUT=Path(__file__).resolve().parents[1]/'Art/BrainCraft/Source/C14'
step=6.;xs=np.arange(-460,461,step);ys=np.arange(-370,461,step);zs=np.arange(-200,681,step);X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij')
def ellipsoid(p,r):return (np.sqrt(((X-p[0])/r[0])**2+((Y-p[1])/r[1])**2+((Z-p[2])/r[2])**2)-1)*min(r)
def union(a,b,k):q=np.clip(.5+.5*(b-a)/k,0,1);return b*(1-q)+a*q-k*q*(1-q)
for idx in range(3):
    field=ellipsoid((0,155,220),(328,230,338))
    for layer,count in [(0,17),(1,14)]:
        for j in range(count):
            a=j*np.pi*2/count+.11*idx+(layer*.18);r=53+14*np.sin(j*1.73+idx)
            p=(np.cos(a)*(268 if layer==0 else 291),(-42 if layer==0 else 152)+20*np.sin(a*3+idx),220+np.sin(a)*(282 if layer==0 else 298))
            field=union(field,ellipsoid(p,(r,94 if layer==0 else 90,r*1.17)),23)
    # A tapered welcoming aperture, with its lower edge below ground level.
    cavity=ellipsoid((0,-110,207),(209,427,243));field=np.maximum(field,-cavity);field=gaussian_filter(field,.5)
    v,f,_,_=marching_cubes(field,0,spacing=(step,step,step));v+=np.array([xs[0],ys[0],zs[0]])
    signed=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6
    if signed<0:f=f[:,::-1]
    normals=np.zeros_like(v);face=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
    for j in range(3):np.add.at(normals,f[:,j],face)
    normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],.0001)
    front=np.clip((160-v[:,1])/310,0,1);color=np.array([.425,.15,.235])[None,:]*(1-front[:,None]) + np.array([.31,.105,.38])[None,:]*front[:,None]
    color*=((.94+.05*np.sin(v[:,2]/103+idx))[:,None])
    np.savez_compressed(OUT/f'Nest{idx}.npz',v=v,f=f,n=normals,c=color)
    print('C14_LIVING_NEST',idx,len(v),len(f),'volume',abs(float(signed)),flush=True)
