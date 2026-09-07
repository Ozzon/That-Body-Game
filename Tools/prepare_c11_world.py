"""C11 construction data: fitted walkways, coherent planting, sculpted rim.

Coordinates in cm. Navigation follows the collision carrier, not the picture.
"""
import sys,json,math
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.spatial import Voronoi,cKDTree
from shapely.geometry import Polygon,LineString,Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import contains_xy
from skimage.measure import find_contours
from brain_craft_layout import *
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/BrainCraft';OUT=ART/'Source/C11';OUT.mkdir(parents=True,exist_ok=True)
xs=np.arange(-3240,3241,14.);ys=np.arange(-3460,3461,14.);X,Y=np.meshgrid(xs,ys,indexing='ij')
d,h,rd=fields(X,Y);h=gaussian_filter(h,2.1);w=water(X,Y)
def height(p):
    p=np.asarray(p);shape=p.shape[:-1];q=p.reshape(-1,2);v=map_coordinates(h,[(q[:,0]+3240)/14,(q[:,1]+3460)/14],order=1,mode='nearest');return v.reshape(shape) if shape else float(v[0])
np.savez_compressed(OUT/'terrain.npz',x=xs,y=ys,h=h)
portals=[dict(name='First light',p=(-2130,-2020,140),yaw=90,color='Dawn'),dict(name='Spring of ideas',p=(-1040,1760,1100),yaw=0,color='Spring'),dict(name='Memory grove',p=(2050,1700,950),yaw=-25,color='Memory')]
(OUT/'portals.json').write_text(json.dumps(portals,indent=2))
paths=[]
for r in ROUTES:paths.append(LineString(curve(r['points'],14,False)[:,:2]).buffer(190 if r['key']!='MemoryWalk' else 155))
paths.extend([Point(0,90).buffer(700).difference(Point(0,90).buffer(302)),Point(LOTUS[:2]).buffer(460),Point(-1770,-2210).buffer(325)])
for e in portals:
    a=math.radians(e['yaw']);front=np.array(e['p'][:2])+np.array([math.sin(a),-math.cos(a)])*330
    paths.append(Point(front).buffer(275))
inside=Polygon(curve(OUTLINE,10));paved=unary_union(paths).intersection(inside.buffer(-160))
seeds=[];rng=np.random.default_rng(1117)
for x in np.arange(-3100,3200,102):
    for y in np.arange(-3320,3400,110):seeds.append([x+rng.uniform(-21,21),y+rng.uniform(-23,23)])
vor=Voronoi(seeds);stones=[]
for p,reg in zip(seeds,vor.point_region):
    if not paved.buffer(130).contains(Point(p)):continue
    reg=vor.regions[reg]
    if not reg or -1 in reg:continue
    clipped=Polygon(vor.vertices[reg]).intersection(paved).buffer(-2.1,join_style=2)
    polys=[clipped] if clipped.geom_type=='Polygon' else list(clipped.geoms) if clipped.geom_type=='MultiPolygon' else []
    for poly in polys:
        if poly.area<650:continue
        xy=np.array(orient(poly,sign=1).exterior.coords[:-1]);zz=height(xy)
        # Reject unsupported decorative slabs outside the established terrain.
        dd,_,_=fields(xy.mean(0)[0],xy.mean(0)[1])
        if dd>95:continue
        stones.append(dict(xy=xy.tolist(),z=(zz+9).tolist(),tone=float(rng.uniform(.82,1.16))))
(OUT/'paving.json').write_text(json.dumps(stones))
# A sculpted evergreen substrate covers the full terrain. Planted margins have
# staggered tufts, flower clusters, and shrub canopies at distinct scales.
xx,yy=np.meshgrid(np.arange(-3020,3050,39),np.arange(-3250,3230,39),indexing='ij');x=xx.ravel()+rng.uniform(-14,14,xx.size);y=yy.ravel()+rng.uniform(-14,14,xx.size)
dd,_,_=fields(x,y);ww=water(x,y);pave_mask=contains_xy(paved.buffer(18),x,y)
valid=(dd<65)&(ww>35)&~pave_mask&(np.hypot(x,y-90)>320)
for e in portals:
    a=np.radians(e['yaw']);dx=x-e['p'][0];dy=y-e['p'][1];lx=np.cos(a)*dx+np.sin(a)*dy;ly=-np.sin(a)*dx+np.cos(a)*dy
    valid&=~((np.abs(lx)<330)&(ly>-510)&(ly<200))
valid&=(np.hypot((x+1920)/295,(y+2240)/240)>1)
p=np.column_stack([x[valid],y[valid]]);plant_count=len(p);z=height(p);np.savez_compressed(OUT/'planting.npz',p=np.column_stack([p,z]),scale=rng.uniform(.78,1.26,len(p)),angle=rng.uniform(0,math.tau,len(p)))
# Continuous fitted retaining courses follow terrace edges and water margins.
lines=[]
for source,kind in [(d,'terrace'),(w,'stream')]:
    for c in find_contours(source,65 if kind=='terrace' else 15):
        xy=np.column_stack([xs[0]+c[:,0]*14,ys[0]+c[:,1]*14]);line=LineString(xy).simplify(18)
        if line.length<320:continue
        p=np.array([line.interpolate(s).coords[0] for s in np.arange(0,line.length,100)])
        for i,q in enumerate(p):
            if not inside.buffer(-110).contains(Point(q)):continue
            if kind=='stream' and paved.buffer(30).contains(Point(q)):continue
            tangent=p[min(i+1,len(p)-1)]-p[max(0,i-1)];lines.append(dict(p=[*q,float(height(q))],angle=math.atan2(tangent[1],tangent[0]),kind=kind))
(OUT/'masonry.json').write_text(json.dumps(lines))
# High-resolution closed shell with modeled convolutions. Its boundary is the
# OUTER envelope only; no tissue fingers enter the playable courts.
V=[];F=[];C=[];n=720;m=66
for i in range(n):
    a=math.tau*i/n
    notch=1-.065*math.exp(-(math.cos(a)/.12)**2)
    for j in range(m):
        t=j/(m-1);r=.83+.245*math.sin(t*math.pi);x=3100*r*math.cos(a)*notch;y=3410*r*math.sin(a)
        base=140+900*(.5+.5*math.sin(a))
        # Rounded cross-section, with longitudinal and branching grooves that
        # cut a woven pattern into a continuous surface rather than tubes.
        u=a*16+1.2*math.sin(t*math.pi*6+a*3);v=t*math.pi*5+.65*math.sin(a*21)
        fold=(.5+.5*math.cos(u+math.sin(v)*1.3))**.40
        across=(.5+.5*math.cos(v+.4*math.sin(u*1.7)))**.4
        relief=(fold*across)*82
        z=base+240*math.cos(t*math.pi)-700*math.sin(t*math.pi)+relief
        V.append((x,y,z));shade=.78+.22*fold*across;C.append((.49*shade,.18*shade,.23*shade))
        if j:q=i*m+j-1;ni=((i+1)%n)*m+j-1;F.append((q,ni,ni+1,q+1))
# Inner and lower lips are closed to an inset base; shell is a continuous ribbon.
np.savez_compressed(OUT/'CortexShell.npz',v=np.array(V),f=np.array(F),c=np.array(C))
nav=np.load(ART/'Source/C10/navigation.npz');np.savez_compressed(OUT/'navigation.npz',**dict(nav))
report=dict(version='C11',fitted_stones=len(stones),plant_clusters=plant_count,masonry_segments=len(lines),portals=portals,minimum_portal_spacing_cm=min(float(np.linalg.norm(np.array(a['p'])-np.array(b['p']))) for i,a in enumerate(portals) for b in portals[i+1:]),reference='ref-384 and Brain-Location-Key-Art',art_accepted=False)
(OUT/'construction.json').write_text(json.dumps(report,indent=2));print('C11_PREPARED',json.dumps(report),flush=True)
