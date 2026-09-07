"""Sculpt the cortex as one fused, folded volume and author a contoured garden floor."""
from pathlib import Path
import json,numpy as np,trimesh
from skimage.measure import marching_cubes
from PIL import Image
from scipy.ndimage import label
from organ_math import smoothmax,curve
from brain_garden_layout import *
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/BrainGarden/Source';OUT.mkdir(parents=True,exist_ok=True)
step=18;xs=np.arange(-2682,2683,step,dtype=np.float32);ys=np.arange(-3078,3079,step,dtype=np.float32);zs=np.arange(-540,1081,step,dtype=np.float32)
X,Y=np.meshgrid(xs,ys,indexing='ij');Z=zs[None,None,:]
theta=np.arctan2(Y/RY,X/RX);oval=(np.sqrt((X/RX)**2+(Y/RY)**2)-1)*RX
oval+=24*np.cos(theta*6)+18*np.sin(theta*11)
top=210+220*np.sqrt(np.maximum(0,1-(X/RX)**2-(Y/RY)**2))+np.clip(X/RX,-1,1)*120
field=smoothmax(oval[:,:,None]+np.maximum(-Z,0)**2/1100,Z-top[:,:,None],90);field=smoothmax(field,-430-Z,120)
cavity=smoothmax(inner_distance(X,Y)[:,:,None],floor_height(X,Y)[:,:,None]+TERRAIN_LIFT-Z,38);field=smoothmax(field,-cavity,45)
# One purposefully placed brainstem entrance; the entire garden is open above it.
gate=np.maximum(np.abs(Y)-260,np.abs(X+2090)-410)
opening=smoothmax(gate[:,:,None],208-Z,35);opening=smoothmax(opening,Z-485,35);field=smoothmax(field,-opening,40)

def capsule(a,b,r):
    global field
    low=np.minimum(a,b)-r-55;high=np.maximum(a,b)+r+55
    ix0=max(0,int((low[0]-xs[0])/step));ix1=min(len(xs),int((high[0]-xs[0])/step)+2)
    iy0=max(0,int((low[1]-ys[0])/step));iy1=min(len(ys),int((high[1]-ys[0])/step)+2)
    iz0=max(0,int((low[2]-zs[0])/step));iz1=min(len(zs),int((high[2]-zs[0])/step)+2)
    xx=xs[ix0:ix1,None,None]-a[0];yy=ys[None,iy0:iy1,None]-a[1];zz=zs[None,None,iz0:iz1]-a[2];v=b-a;t=np.clip((xx*v[0]+yy*v[1]+zz*v[2])/(v@v+1e-8),0,1)
    d=np.sqrt((xx-t*v[0])**2+(yy-t*v[1])**2+(zz-t*v[2])**2)-r
    current=field[ix0:ix1,iy0:iy1,iz0:iz1];field[ix0:ix1,iy0:iy1,iz0:iz1]=-smoothmax(-current,-d,55)

folds=[]
# Three interlocking layers, each offset and with different courses. Gyri are
# rounded ridges across a tissue mass; there is no repeated crown-shaped rim.
for band,(rr,zbase,count,radius) in enumerate([(.986,110,19,103),(.941,320,22,120),(.818,448,20,126)]):
    for i in range(count):
        a=-np.pi+(i+.28*band)*np.pi*2/count
        length=.19+.055*np.sin(i*2.71+band)
        pts=[]
        for j,t in enumerate(np.linspace(-1,1,7)):
            angle=a+t*length
            rad=rr+(.028+.012*np.sin(i*3.7))*np.sin(t*3.3+i*1.9+band)
            z=zbase+100*np.cos(a)+47*np.sin(t*2.7+i*1.7)+20*np.cos(t*5+i)
            pts.append([RX*rad*np.cos(angle),RY*rad*np.sin(angle),z])
        p=curve(pts,5,False);folds.append(pts)
        for j,(u,v) in enumerate(zip(p,p[1:])):capsule(u,v,radius+13*np.sin(i*2.1+j*.15))
# Higher frontal folds at the back frame the pool and make a pair of hemispheres.
for side in [-1,1]:
    for j in range(6):
        x=1530+j*113;y=side*(520+78*np.sin(j*1.8))
        pts=[[x-100,y-side*300,505],[x-145,y-side*40,690-j*20],[x+10,y+side*190,685-j*18],[x+70,y+side*370,470]]
        p=curve(pts,7,False);folds.append(pts)
        for u,v in zip(p,p[1:]):capsule(u,v,105)
# Recut the arrival arch after all cortical folds are fused.
field=smoothmax(field,-opening,40)
# A central rear fissure separates the two cerebral hemispheres, as in the board.
cleft=np.maximum(np.abs(Y)-42,1700-X)
field=smoothmax(field,-smoothmax(cleft[:,:,None],260-Z,20),22)

v,f,_,_=marching_cubes(field,0,spacing=(step,step,step),allow_degenerate=False);v+=np.array([xs[0],ys[0],zs[0]])
m=trimesh.Trimesh(v,f,process=True);trimesh.repair.fix_normals(m);trimesh.smoothing.filter_taubin(m,lamb=.38,nu=.4,iterations=4)
v=np.array(m.vertices,np.float32);f=np.array(m.faces,np.int32);n=np.array(m.vertex_normals,np.float32)
floor=np.clip((n[:,2]-.6)/.4,0,1)*np.clip((floor_height(v[:,0],v[:,1])+TERRAIN_LIFT+65-v[:,2])/55,0,1)*(inner_distance(v[:,0],v[:,1])<-70)
rose=np.array([.52,.12,.17]);peach=np.array([.72,.245,.28]);wine=np.array([.24,.045,.085])
lift=np.clip((v[:,2]+60)/470,0,1)[:,None];c=wine*(1-lift)+rose*lift
shine=np.clip(n[:,2],0,1)[:,None]*.4;c=c*(1-shine)+peach*shine
ground=np.tile([.14,.235,.082],(len(v),1))
for z in ZONES:
    weight=blend((1.1-ellipse(v[:,0],v[:,1],z['center'],z['radii']))/.45)[:,None]
    ground=ground*(1-weight)+np.array(z['color'])*weight
c=c*(1-floor[:,None])+ground*floor[:,None]
grain=(.97+.022*np.sin(v[:,0]/62+v[:,1]/57)+.018*np.sin(v[:,0]/120-v[:,2]/43))[:,None];c=np.clip(c*grain,0,1)
np.savez_compressed(OUT/'brain_cortex.npz',vertices=v,faces=f,normals=n,colors=c)
navx=np.arange(-2500,2501,20);navy=np.arange(-2800,2801,20);NX,NY=np.meshgrid(navx,navy,indexing='ij');walk,h=navigation(NX,NY);components,count=label(walk)
np.savez_compressed(OUT/'navigation.npz',walk=walk,height=h,xs=navx,ys=navy)
Image.fromarray(np.uint8(walk.T[::-1])*255).save(OUT/'walkable.png')
(OUT/'sculpt-report.json').write_text(json.dumps(dict(vertices=len(v),triangles=len(f),watertight=bool(m.is_watertight),navigation_components=int(count),folds=len(folds),tree=[0,0],sources=[358,384,307]),indent=2))
print('BRAIN_CORTEX_READY',len(f),'triangles',count,'navigation regions',flush=True)
