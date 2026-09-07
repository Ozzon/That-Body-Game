"""Closed cortical mantle fitted directly to the garden's real terrain edge."""
from pathlib import Path
import numpy as np, math, json
from scipy.ndimage import map_coordinates, gaussian_filter1d
from scipy.spatial import cKDTree
from brain_craft_layout import OUTLINE,curve
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/BrainCraft/Source/C13'
terrain=np.load(OUT/'terrain.npz');H=terrain['h'];xs=terrain['x'];ys=terrain['y'];step=xs[1]-xs[0]
outline=curve(OUTLINE,30);angles=np.mod(np.arctan2(outline[:,1],outline[:,0]),math.tau);radii=np.hypot(outline[:,0],outline[:,1]);sort=np.argsort(angles);angles=angles[sort];radii=radii[sort]
n=1080;m=128;a=np.arange(n)*math.tau/n;t=np.arange(m)/m
r=np.interp(a,np.r_[angles-math.tau,angles,angles+math.tau],np.tile(radii,3))-18;r=gaussian_filter1d(r,1.0,mode='wrap')
ix=r*np.cos(a);iy=r*np.sin(a);base=map_coordinates(H,[(ix-xs[0])/step,(iy-ys[0])/step],order=1,mode='nearest')+2
base=gaussian_filter1d(base,1.3,mode='wrap');edge=np.column_stack([ix,iy]);segment=np.linalg.norm(np.roll(edge,-1,axis=0)-edge,axis=1);s=np.r_[0,np.cumsum(segment[:-1])];length=segment.sum()
# The folded surface is carved by continuous sulci across a closed volume.
# Irregular S-curves and short branches create long gyri rather than a grid of
# disconnected lobes or tubes. All furrows fade out at the walking boundary.
strokes=[];count=49;stride=length/count
for k in range(count):
    u=k*stride;phase=k*.79
    pts=[(u+math.sin(j*1.1+phase)*stride*.22+math.sin(j*.6-phase)*stride*.12,j*160) for j in range(8)]
    strokes.extend(curve(pts,15,False))
    if k%3!=0:
        v=330 if k%2 else 720
        pts=[(u+stride*.07,v),(u+stride*.27,v+70),(u+stride*.48,v+35),(u+stride*.60,v+100)]
        strokes.extend(curve(pts,18,False))
strokes=np.array(strokes);periodic=np.vstack([strokes-[length,0],strokes,strokes+[length,0]]);tree=cKDTree(periodic)
U,T=np.meshgrid(s,t,indexing='ij');V=T*2200
dist=tree.query(np.column_stack([U.ravel(),V.ravel()]))[0].reshape(n,m)
ridge=100*np.sin(np.minimum(dist/145,1)*math.pi*.5)
theta=2*math.pi*T;width=730+65*np.sin(a[:,None]*3+.7)+35*np.sin(a[:,None]*7)
offset=width*.5*(1-np.cos(theta))
crossz=-230*offset/width+np.where(T<.5,370*np.sin(theta),400*np.sin(theta))
fade=np.maximum(0,np.sin(theta))**.85
crossz+=(ridge-42)*fade
# Sculpted relief is within the outer wall; nothing enters the walking space.
radius=r[:,None]+offset
x=radius*np.cos(a[:,None]);y=radius*np.sin(a[:,None]);z=base[:,None]+crossz
verts=np.stack([x,y,z],axis=-1)
ta=np.roll(verts,-1,axis=0)-np.roll(verts,1,axis=0);tt=np.roll(verts,-1,axis=1)-np.roll(verts,1,axis=1)
norm=np.cross(tt,ta);norm/=np.maximum(np.linalg.norm(norm,axis=-1)[...,None],.001)
pigment=.94+.035*np.sin(U/550+T*9)+.025*np.sin(U/1370-T*4);color=np.array([.43,.155,.215])*pigment[...,None]
keys=[]
for q,(sx,sy) in enumerate([(1,1),(-1,1),(-1,-1),(1,-1)]):
    start=q*n//4;end=(q+1)*n//4;indices=np.arange(start,end+1)%n;vv=verts[indices].reshape(-1,3).tolist();nn=norm[indices].reshape(-1,3).tolist();cc=color[indices].reshape(-1,3).tolist();ff=[]
    for i in range(len(indices)-1):
        for j in range(m):
            jj=(j+1)%m;aa=i*m+j;bb=i*m+jj;dd=(i+1)*m+j;ee=(i+1)*m+jj;ff.extend([[aa,bb,ee],[aa,ee,dd]])
    # Separate caps close each streaming/fading quadrant without creasing its
    # shared outer silhouette; original analytic normals remain on the surface.
    for ring,sign in [(0,-1),(len(indices)-1,1)]:
        source=verts[indices[ring]];center=source.mean(0);k0=len(vv);normal=np.array([-math.sin(a[indices[ring]]),math.cos(a[indices[ring]]),0])*sign
        vv.append(center.tolist());nn.append(normal.tolist());cc.append([.40,.14,.18])
        for p in source:vv.append(p.tolist());nn.append(normal.tolist());cc.append([.40,.14,.18])
        for j in range(m):
            f=[k0,k0+1+j,k0+1+(j+1)%m];ff.append(f if sign==1 else f[::-1])
    key=f'Cortex{sx}{sy}';keys.append(key);np.savez_compressed(OUT/(key+'.npz'),v=np.array(vv,np.float32),f=np.array(ff,np.int32),n=np.array(nn,np.float32),c=np.array(cc,np.float32))
(OUT/'cortex-construction.json').write_text(json.dumps(dict(keys=keys,closed_quadrants=True,inner_boundary='C13 terrain / authored brain outline',fold_strokes=count,walking_intrusion_cm=0,art_accepted=False),indent=2))
print('C13_CORTEX_SCULPTED',keys,flush=True)
