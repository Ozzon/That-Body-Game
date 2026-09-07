"""Rounded cortical relief in an injective radial cross-section.

The C14 normal displacement moved vertices between angular slices and folded
the mesh back over itself. Here every angular slice stays in its own plane;
positive cross-section radii preserve a continuous, closed tissue envelope.
"""
from pathlib import Path
import json, math
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d, map_coordinates
from scipy.spatial import cKDTree
from brain_craft_layout import OUTLINE, curve

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Art/BrainCraft/Source/C15'; OUT.mkdir(exist_ok=True)
terrain=np.load(ROOT/'Art/BrainCraft/Source/C14/terrain.npz')
outline=curve(OUTLINE,30)
angles=np.mod(np.arctan2(outline[:,1],outline[:,0]),math.tau)
radii=np.linalg.norm(outline,axis=1);order=np.argsort(angles)
angles=angles[order];radii=radii[order]
n=1440;m=192;a=np.arange(n)*math.tau/n;t=np.arange(m)/m
r=gaussian_filter1d(np.interp(a,np.r_[angles-math.tau,angles,angles+math.tau],np.tile(radii,3))-18,2,mode='wrap')
edge=np.column_stack([r*np.cos(a),r*np.sin(a)])
step=terrain['x'][1]-terrain['x'][0]
base=map_coordinates(terrain['h'],[(edge[:,0]-terrain['x'][0])/step,(edge[:,1]-terrain['y'][0])/step],order=1,mode='nearest')+2
base=gaussian_filter1d(base,2,mode='wrap')
segment=np.linalg.norm(np.roll(edge,-1,axis=0)-edge,axis=1)
s=np.r_[0,np.cumsum(segment[:-1])];length=segment.sum();strokes=[]
count=68;stride=length/count
for k in range(count):
    phase=k*.79;u=k*stride
    points=[(u+math.sin(j*.79+phase)*stride*.28+math.sin(j*1.17-phase)*stride*.12,j*155) for j in range(26)]
    strokes.extend(curve(points,14,False))
    # Alternating short branches interrupt the long folds into rounded lobes.
    for j in [4+k%3,13+k%2,21-k%2]:
        x,y=points[j]
        strokes.extend(curve([(x,y),(x+stride*.26,y+30),(x+stride*.52,y-25)],14,False))
strokes=np.array(strokes);tree=cKDTree(np.vstack([strokes-[length,0],strokes,strokes+[length,0]]))
U,T=np.meshgrid(s,t,indexing='ij');theta=T*math.tau
dist=tree.query(np.column_stack([U.ravel(),(T*3900).ravel()]))[0].reshape(n,m)
relief=gaussian_filter(112*np.sin(np.minimum(dist/128,1)*math.pi*.5)-28,(1.4,1.1),mode='wrap')
relief*=np.abs(np.sin(theta))**1.2
width=1000+65*np.sin(a[:,None]*3+.7)+45*np.sin(a[:,None]*7)
radial=width*.5+relief
vertical=np.where(T<.5,815,1090)+relief
radius=r[:,None]+width*.5-radial*np.cos(theta)
z=base[:,None]-140+140*np.cos(theta)+vertical*np.sin(theta)
v=np.stack([radius*np.cos(a[:,None]),radius*np.sin(a[:,None]),z],axis=-1)
ta=np.roll(v,-1,axis=0)-np.roll(v,1,axis=0)
tt=np.roll(v,-1,axis=1)-np.roll(v,1,axis=1)
normal=np.cross(tt,ta);normal/=np.maximum(np.linalg.norm(normal,axis=-1)[...,None],1e-8)
# Monotone polar angle around each cross-section is the construction invariant.
cross_r=radius-(r[:,None]+width*.5);cross_z=z-(base[:,None]-140)
angle=np.unwrap(np.arctan2(cross_z,cross_r),axis=1)
assert np.max(np.diff(angle,axis=1))<0, 'Cross-section folds back on itself'
pigment=.95+.027*np.sin(U/830+T*5)+.025*np.sin(U/1480-T*3)
color=np.array([.46,.185,.235])*pigment[...,None]
keys=[]
for q,(sx,sy) in enumerate([(1,1),(-1,1),(-1,-1),(1,-1)]):
    ids=np.arange(q*n//4,(q+1)*n//4+1)%n
    vv=v[ids].reshape(-1,3).tolist();nn=normal[ids].reshape(-1,3).tolist();cc=color[ids].reshape(-1,3).tolist();ff=[]
    for i in range(len(ids)-1):
        for j in range(m):
            jj=(j+1)%m;aa=i*m+j;bb=i*m+jj;dd=(i+1)*m+j;ee=(i+1)*m+jj
            ff.extend([[aa,bb,ee],[aa,ee,dd]])
    for ring,sign in [(0,-1),(len(ids)-1,1)]:
        source=v[ids[ring]];center=source.mean(0);k0=len(vv)
        norm=np.array([-math.sin(a[ids[ring]]),math.cos(a[ids[ring]]),0])*sign
        vv.append(center.tolist());nn.append(norm.tolist());cc.append([.42,.16,.21])
        for p in source:vv.append(p.tolist());nn.append(norm.tolist());cc.append([.42,.16,.21])
        for j in range(m):
            face=[k0,k0+1+j,k0+1+(j+1)%m];ff.append(face if sign==1 else face[::-1])
    key=f'Cortex{sx}{sy}';keys.append(key)
    np.savez_compressed(OUT/(key+'.npz'),v=np.array(vv,np.float32),f=np.array(ff,np.int32),n=np.array(nn,np.float32),c=np.array(cc,np.float32))
report=dict(keys=keys,fold_lines=count,positive_cross_section_radii=True,angular_slices_preserved=True,max_cross_section_angle_delta=float(np.max(np.diff(angle,axis=1))),art_accepted=False)
(OUT/'cortex-construction.json').write_text(json.dumps(report,indent=2))
print('C15_CORTEX_READY',json.dumps(report),flush=True)
