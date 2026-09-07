"""A deep cortical mantle with carved gyri, fitted to the actual garden edge."""
from pathlib import Path
import numpy as np,math,json
from scipy.ndimage import map_coordinates,gaussian_filter1d
from scipy.spatial import cKDTree
from brain_craft_layout import OUTLINE,curve
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/BrainCraft/Source/C14'
terrain=np.load(OUT/'terrain.npz');H=terrain['h'];xs=terrain['x'];ys=terrain['y'];step=xs[1]-xs[0]
outline=curve(OUTLINE,30);angles=np.mod(np.arctan2(outline[:,1],outline[:,0]),math.tau);radii=np.linalg.norm(outline,axis=1);sort=np.argsort(angles);angles=angles[sort];radii=radii[sort]
n=1440;m=192;a=np.arange(n)*math.tau/n;t=np.arange(m)/m
r=np.interp(a,np.r_[angles-math.tau,angles,angles+math.tau],np.tile(radii,3))-18;r=gaussian_filter1d(r,1.0,mode='wrap')
ix=r*np.cos(a);iy=r*np.sin(a);base=map_coordinates(H,[(ix-xs[0])/step,(iy-ys[0])/step],order=1,mode='nearest')+2
base=gaussian_filter1d(base,1.3,mode='wrap');edge=np.column_stack([ix,iy]);segment=np.linalg.norm(np.roll(edge,-1,axis=0)-edge,axis=1);s=np.r_[0,np.cumsum(segment[:-1])];length=segment.sum()
strokes=[];count=86;stride=length/count
for k in range(count):
    u=k*stride;phase=k*.79
    pts=[(u+math.sin(j*.83+phase)*stride*.34+math.sin(j*1.27-phase)*stride*.15,j*165) for j in range(23)]
    strokes.extend(curve(pts,12,False))
    for branch in range(3):
        j=3+branch*6+(k%3);v=j*165;du=math.sin(j*.83+phase)*stride*.34+math.sin(j*1.27-phase)*stride*.15
        pts=[(u+du,v),(u+du+stride*.27,v+40),(u+du+stride*.52,v-20),(u+du+stride*.66,v+60)]
        strokes.extend(curve(pts,12,False))
strokes=np.array(strokes);tree=cKDTree(np.vstack([strokes-[length,0],strokes,strokes+[length,0]]));U,T=np.meshgrid(s,t,indexing='ij');V=T*3700
dist=tree.query(np.column_stack([U.ravel(),V.ravel()]))[0].reshape(n,m)
ridge=104*np.sin(np.minimum(dist/106,1)*math.pi*.5)
theta=math.tau*T;width=980+85*np.sin(a[:,None]*3+.7)+60*np.sin(a[:,None]*7)
offset=width*.5*(1-np.cos(theta));crossz=-280*offset/width+np.where(T<.5,820*np.sin(theta),1120*np.sin(theta))
radius=r[:,None]+offset;x=radius*np.cos(a[:,None]);y=radius*np.sin(a[:,None]);z=base[:,None]+crossz;verts=np.stack([x,y,z],axis=-1)
ta=np.roll(verts,-1,axis=0)-np.roll(verts,1,axis=0);tt=np.roll(verts,-1,axis=1)-np.roll(verts,1,axis=1);normal=np.cross(tt,ta);normal/=np.maximum(np.linalg.norm(normal,axis=-1)[...,None],.001)
# Displace along the volume's surface, so side folds have depth too. Fade to
# zero at the walking edge, keeping the floor/wall meeting continuous.
fade=np.abs(np.sin(theta))**.7;verts+=normal*((ridge-38)*fade)[...,None]
ta=np.roll(verts,-1,axis=0)-np.roll(verts,1,axis=0);tt=np.roll(verts,-1,axis=1)-np.roll(verts,1,axis=1);normal=np.cross(tt,ta);normal/=np.maximum(np.linalg.norm(normal,axis=-1)[...,None],.001)
pigment=.92+.035*np.sin(U/610+T*6)+.045*np.sin(U/1430-T*4)+.07*np.minimum(dist/106,1);color=np.array([.43,.155,.225])*pigment[...,None]
keys=[]
for q,(sx,sy) in enumerate([(1,1),(-1,1),(-1,-1),(1,-1)]):
    indices=np.arange(q*n//4,(q+1)*n//4+1)%n;vv=verts[indices].reshape(-1,3).tolist();nn=normal[indices].reshape(-1,3).tolist();cc=color[indices].reshape(-1,3).tolist();ff=[]
    for i in range(len(indices)-1):
        for j in range(m):jj=(j+1)%m;aa=i*m+j;bb=i*m+jj;dd=(i+1)*m+j;ee=(i+1)*m+jj;ff.extend([[aa,bb,ee],[aa,ee,dd]])
    for ring,sign in [(0,-1),(len(indices)-1,1)]:
        source=verts[indices[ring]];center=source.mean(0);k0=len(vv);norm=np.array([-math.sin(a[indices[ring]]),math.cos(a[indices[ring]]),0])*sign;vv.append(center.tolist());nn.append(norm.tolist());cc.append([.40,.14,.18])
        for p in source:vv.append(p.tolist());nn.append(norm.tolist());cc.append([.40,.14,.18])
        for j in range(m):f=[k0,k0+1+j,k0+1+(j+1)%m];ff.append(f if sign==1 else f[::-1])
    key=f'Cortex{sx}{sy}';keys.append(key);np.savez_compressed(OUT/(key+'.npz'),v=np.array(vv,np.float32),f=np.array(ff,np.int32),n=np.array(nn,np.float32),c=np.array(cc,np.float32))
(OUT/'mantle-construction.json').write_text(json.dumps(dict(keys=keys,fold_lines=count,branch_folds=count*3,nominal_crown_rise_cm=820,nominal_belly_depth_cm=1120,art_accepted=False),indent=2));print('C14_DEEP_MANTLE_SCULPTED',flush=True)
