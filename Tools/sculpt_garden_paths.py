"""Fitted polygonal masonry: one continuous route surface, no overlapping block strips."""
from pathlib import Path
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from brain_garden_layout import *

out=Path(__file__).resolve().parents[1]/'Art/BrainGarden/Source'
garden=Polygon(curve(GARDEN_EDGE,8)).buffer(-75)
water=Polygon(curve(POOL)).union(LineString(curve(STREAM,18,False)).buffer(104))
bridges=unary_union([LineString(curve(b['points'],18,False)).buffer(b['width']/2+20) for b in BRIDGES])
routes=unary_union([LineString(curve(p['points'],18,False)).buffer(p['width']/2) for p in PATHS])
court=Point(0,0).buffer(715,64).difference(Point(0,0).buffer(368,64))
shape=routes.union(court).intersection(garden).difference(water.union(bridges))
rng=np.random.default_rng(9404)
sites=np.array([(x+rng.uniform(-26,26)/LEVEL_SCALE,y+rng.uniform(-26,26)/LEVEL_SCALE) for x in np.arange(-3000,3000,108/LEVEL_SCALE) for y in np.arange(-3000,3000,108/LEVEL_SCALE)])
vor=Voronoi(sites)
V=[];F=[];C=[]
def slab(poly,basecolor,top=10,depth=34):
    if poly.area<160:return
    ring=np.asarray(poly.exterior.coords)[:-1]
    if len(ring)<3:return
    # Shapely operations can reverse winding. Counterclockwise means +Z in both exporters.
    if np.sum(ring[:,0]*np.roll(ring[:,1],-1)-ring[:,1]*np.roll(ring[:,0],-1))<0:ring=ring[::-1]
    ctr=ring.mean(axis=0);start=len(V);n=len(ring)
    for lift,inset in [(-depth,0),(top-5,0),(top,3.6)]:
        for p in ring:
            d=ctr-p;q=p+d*min(.12,inset/(np.linalg.norm(d)+.01));V.append((q[0],q[1],float(height(*q))+lift));C.append(basecolor*(.75 if lift<0 else .96 if inset==0 else 1.03))
    for layer in range(2):
        for j in range(n):
            a=start+layer*n+j;b=start+layer*n+(j+1)%n;c=b+n;d=a+n;F.extend([(a,b,c),(a,c,d)])
    for j in range(1,n-1):F.append((start+2*n,start+2*n+j,start+2*n+j+1))
count=0
for i,site in enumerate(sites):
    ids=vor.regions[vor.point_region[i]]
    if not ids or -1 in ids:continue
    cell=Polygon(vor.vertices[ids]).intersection(shape)
    if cell.is_empty:continue
    pieces=list(cell.geoms) if cell.geom_type=='MultiPolygon' else [cell]
    for piece in pieces:
        if piece.geom_type!='Polygon':continue
        # Each slab follows the terrain at all corners and fits its neighbors.
        inset=piece.buffer(-1.7,join_style=2)
        if inset.is_empty or inset.geom_type!='Polygon':continue
        col=np.array([.40,.255,.17])*(1+rng.uniform(-.08,.08))
        if site[0]>500 and site[1]>700:col=np.array([.49,.33,.16])*(1+rng.uniform(-.06,.06))
        slab(inset,col);count+=1
np.savez_compressed(out/'garden_masonry.npz',vertices=np.array(V,np.float32),faces=np.array(F,np.int32),colors=np.clip(C,0,1))
print('FITTED_GARDEN_MASONRY',count,'stones',len(F),'triangles',flush=True)
