"""Build explicit surface topology, fitted paving and shared navigation for C06."""
import json, numpy as np
from pathlib import Path
from scipy.ndimage import distance_transform_edt, gaussian_filter, label, map_coordinates
from skimage.measure import marching_cubes
from PIL import Image
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely import contains_xy
from organ_math import curve, distance
from brain_craft_layout import *

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/BrainCraft/Source';OUT.mkdir(parents=True,exist_ok=True)
STEP=14.;xs=np.arange(-3240,3241,STEP);ys=np.arange(-3460,3461,STEP);X,Y=np.meshgrid(xs,ys,indexing='ij')
inside=distance(X,Y,curve(OUTLINE,10))<0
d,h,road=fields(X,Y);w=water(X,Y)
# Height changes come from authored route grades; blend only their adjoining joints.
h=gaussian_filter(h,2.1)
floor=(d<110)&inside
watermask=(w<0)&(d<110)&inside
ground=floor&(w>-10)
# Cortex is one bounded surface with grooves incised INTO it. Its topology never
# crosses the inner edge; no capsules or overhanging primitive lobes are used.
shortcut_distance=distance(X,Y,curve(SHORTCUT,14,False),False)
cortex=inside&(d>60)&(shortcut_distance>310)
from_inner=distance_transform_edt(cortex)*STEP
from_outer=distance_transform_edt(inside)*STEP
shoulder=np.minimum(np.clip(from_inner/210,0,1),np.clip(from_outer/300,0,1))
outer_roll=np.clip(from_outer/240,0,1);outer_roll=outer_roll*outer_roll*(3-2*outer_roll)
base=-170+(h+125+540*np.sin(shoulder*np.pi/2))*outer_roll
groove=np.full_like(X,1e6)
for side in [-1,1]:
    for row in range(19):
        yy=-3060+row*350
        points=[]
        for j in range(11):
            xx=side*(130+j*320);yyy=yy+105*np.sin(j*.95+row*1.23)+70*np.sin(j*1.9+row)
            points.append((xx,yyy))
        groove=np.minimum(groove,distance(X,Y,curve(points,5,False),False))
    for col in range(7):
        xx=side*(330+col*400)
        points=[(xx+90*np.sin(j*1.35+col),-3050+j*590) for j in range(11)]
        # Interrupted secondary sulci give the long convolutions branching logic.
        for p in [points[:4],points[5:]]:groove=np.minimum(groove,distance(X,Y,curve(p,6,False),False))
depth=95*np.exp(-np.square(groove/25))+55*np.exp(-np.square(groove/69))
# Image-generated sculpt field is sampled as actual vertex relief, not a flat
# color illusion. Macro form and safe garden boundary remain authored geometry.
height_asset=ROOT/'Art/BrainCraft/Textures/T_Cortex_Folds_Height.png'
if height_asset.exists():
    hm=np.asarray(Image.open(height_asset).convert('L'),float)/255
    hm=gaussian_filter(hm,6);hm=(hm-hm.min())/(hm.max()-hm.min())
    sx=(X/1600)%1*(hm.shape[1]-1);sy=(Y/1600)%1*(hm.shape[0]-1)
    relief=map_coordinates(hm,[sy.ravel(),sx.ravel()],order=1,mode='wrap').reshape(X.shape)
    Z=base+(relief-.52)*250*np.sin(shoulder*np.pi/2)-depth*.16*np.sin(shoulder*np.pi/2)
else:Z=base-depth*np.sin(shoulder*np.pi/2)

def surface(name,mask,z,bottom=None):
    ids=np.full(mask.shape,-1,np.int32);ij=np.argwhere(mask);ids[mask]=np.arange(len(ij))
    verts=np.column_stack([X[mask],Y[mask],np.broadcast_to(z,X.shape)[mask]]).tolist();faces=[]
    for i,j in np.argwhere(mask[:-1,:-1]&mask[1:,:-1]&mask[1:,1:]&mask[:-1,1:]):
        faces.append([int(ids[i,j]),int(ids[i+1,j]),int(ids[i+1,j+1]),int(ids[i,j+1])])
    if bottom is not None:
        edges={};oriented={}
        for f in faces:
            for a,b in zip(f,f[1:]+f[:1]):
                edge=tuple(sorted((a,b)));edges[edge]=edges.get(edge,0)+1;oriented[edge]=(a,b)
        # Separate boundary vertices make a deliberate vertical support under each terrace.
        lowers={}
        for edge,count in edges.items():
            if count!=1:continue
            a,b=oriented[edge]
            for k in [a,b]:
                if k not in lowers:lowers[k]=len(verts);verts.append([verts[k][0],verts[k][1],bottom])
            faces.append([b,a,lowers[a],lowers[b]])
    np.savez_compressed(OUT/(name+'.npz'),v=np.asarray(verts,np.float32),f=np.asarray(faces,np.int32))
    return len(verts),len(faces)*2

report={}
# A closed, rounded volume replaces the straight extruded tissue walls. Folds
# continue down the sides as real surface relief; all districts stay cut clear.
cs=28.;cx=xs[::2];cy=ys[::2];cz=np.arange(-360,2401,cs)
cm=cortex[::2,::2];top=Z[::2,::2]
sd=(distance_transform_edt(~cm)-distance_transform_edt(cm))*cs
sd=gaussian_filter(sd,1.1)
XX,YY=np.meshgrid(cx,cy,indexing='ij')
volume=np.empty((len(cx),len(cy),len(cz)),np.float32)
for k,zz in enumerate(cz):
    # Rounded gyri on the vertical tissue faces, with asymmetric long furrows.
    u=(YY/1480+XX/3900)%1*(hm.shape[1]-1);vv=((zz+120)/1170+XX/5300)%1*(hm.shape[0]-1)
    side_relief=map_coordinates(hm,[vv.ravel(),u.ravel()],order=1,mode='wrap').reshape(XX.shape)
    lateral=sd+(side_relief-.47)*110
    lower=-250+100*(1-np.clip(np.hypot(XX/3400,YY/3700),0,1))
    vertical=np.maximum(zz-top,lower-zz)
    # Smooth maximum makes rolled shoulders and a rounded underside.
    bevel=105.;volume[:,:,k]=np.maximum(lateral,vertical)+bevel*np.log1p(np.exp(-np.abs(lateral-vertical)/bevel))
vv,ff,nn,_=marching_cubes(volume,level=0,spacing=(cs,cs,cs));vv+=np.array([cx[0],cy[0],cz[0]])
for ix in [-1,1]:
    for iy in [-1,1]:
        centers=vv[ff].mean(axis=1);chosen=(centers[:,0]*ix>=0)&(centers[:,1]*iy>=0);faces=ff[chosen];used,inv=np.unique(faces,return_inverse=True)
        name='Cortex%d%d'%(ix,iy);np.savez_compressed(OUT/(name+'.npz'),v=vv[used].astype(np.float32),f=inv.reshape(-1,3).astype(np.int32));report[name]=(len(used),len(faces))
report['Ground']=surface('Ground',ground,h,-150)
report['Water']=surface('Water',watermask,h-42)
earthdist=np.full_like(X,1e6)
for r in ROUTES:earthdist=np.minimum(earthdist,distance(X,Y,curve(r['points'],12,False),False))
earthdist=np.minimum(earthdist,np.abs(np.hypot(X,Y)-780))
earthmask=earthdist<210
earthmask&=floor&(w>0)
report['EarthPath']=surface('EarthPath',earthmask,h+2)
e=np.load(OUT/'EarthPath.npz');blend=np.clip((210-earthdist[earthmask])/100,0,1);blend=blend*blend*(3-2*blend);np.savez_compressed(OUT/'EarthPath.npz',v=e['v'],f=e['f'],blend=blend)

# Fitted polygon stones clipped to the full road union, including junctions.
polys=[]
# Masonry belongs to water crossings, the small lotus plinth, and a narrow
# gathering ring. Most of the garden becomes planted ground and soft earth.
waterpoly=unary_union([Point(-1600,1430).buffer(480),LineString(curve([(-1630,1510),(-1930,900),(-1700,380),(-1210,-50),(-970,-630)],12,False)).buffer(135),Point(LOTUS[:2]).buffer(700).difference(Point(LOTUS[:2]).buffer(460))])
for r in ROUTES:
    line=LineString(curve(r['points'],12,False)[:,:2]);polys.append(line.buffer(r['width']/2-18,join_style=1).intersection(waterpoly))
    # Infrequent broad stepping slabs in soft earth, rather than a solid roadway.
    for s in np.arange(140,line.length,390):
        p=line.interpolate(s);polys.append(p.buffer(68,resolution=6))
polys.append(Point(0,90).buffer(510).difference(Point(0,90).buffer(440)))
polys.append(Point(LOTUS[:2]).buffer(305))
paved=unary_union(polys)
rng=np.random.default_rng(6309);seeds=[]
for x in np.arange(-3100,3200,132):
    for y in np.arange(-3300,3400,145):seeds.append([x+rng.uniform(-28,28),y+rng.uniform(-30,30)])
voro=Voronoi(seeds);stones=[]
for seed,reg in zip(seeds,voro.point_region):
    reg=voro.regions[reg]
    if not reg or -1 in reg:continue
    if not paved.buffer(200).contains(Point(seed)):continue
    poly=Polygon(voro.vertices[reg]).intersection(paved).buffer(-4,join_style=2)
    for poly in ([poly] if poly.geom_type=='Polygon' else list(poly.geoms) if poly.geom_type=='MultiPolygon' else []):
        if poly.area<1700:continue
        coords=np.asarray(poly.exterior.coords[:-1]);_,zz,_=fields(coords[:,0],coords[:,1]);stones.append(dict(xy=coords.round(2).tolist(),z=(zz+5).round(2).tolist()))
(OUT/'paving.json').write_text(json.dumps(stones))
# Navigation is derived from the same location definition. Native character still
# collides with actual triangles; this grid is a route audit and recovery aid.
nx=np.arange(-3200,3201,40);ny=np.arange(-3400,3401,40);a,b=np.meshgrid(nx,ny,indexing='ij');ok,hh=walk(a,b)
hh=map_coordinates(h,[(a-xs[0])/STEP,(b-ys[0])/STEP],order=1)
gx,gy=np.gradient(hh,40);slope=np.degrees(np.arctan(np.hypot(gx,gy)));ok&=slope<39
components,n=label(ok);sizes=np.bincount(components.ravel());largest=1+np.argmax(sizes[1:]);island=ok&(components==largest)
np.savez_compressed(OUT/'navigation.npz',x=nx,y=ny,walk=island,h=hh)
report.update(stones=len(stones),navigable_area_m2=float(island.sum()*40*40/1e4),connected_fraction=float(island.sum()/max(ok.sum(),1)),designed_path_width_cm=510,character_diameter_cm=68,terrain_elevation_cm=[140,520,950,1100],maximum_navigable_slope_degrees=float(slope[island].max()),reference='Concept/Brain-Location-Key-Art.png',art_accepted=False)
(OUT/'construction-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
