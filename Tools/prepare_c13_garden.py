"""One continuous authored terrain, traversable banks and restrained garden paths."""
from pathlib import Path
import json, math
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates, distance_transform_edt, label
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, LineString, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import contains_xy
from brain_craft_layout import fields, water, OUTLINE, ROUTES, LOTUS, curve, distance

ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/BrainCraft';OUT=ART/'Source/C13';OUT.mkdir(exist_ok=True)
STEP=20.;xs=np.arange(-3300,3301,STEP);ys=np.arange(-3500,3501,STEP);X,Y=np.meshgrid(xs,ys,indexing='ij')
outline=Polygon(curve(OUTLINE,12));inside=contains_xy(outline.buffer(-12),X,Y)
d,h,rd=fields(X,Y);upper=gaussian_filter(h,1.5)
low=gaussian_filter(h-180-np.clip(d+60,0,1100)*.25,5)
bank=np.clip((d-12)/330,0,1);bank=bank*bank*(3-2*bank)
H=upper*(1-bank)+low*bank
# The old ramps were separate sheets underneath the upper floor. Grade the
# actual ground down through each opening, with broad rounded earth shoulders.
access=[]
for name,xy,width in [
    ('Front fern walk',[(-1450,-1680),(-1280,-1840),(-1030,-2020),(-920,-1800)],280),
    ('Western moss walk',[(-2180,-1150),(-1950,-1040),(-1770,-820),(-1570,-650)],290),
    ('Northern quiet walk',[(20,2450),(20,2250),(60,2000),(0,1640)],330),
    ('Eastern iris walk',[(780,-1250),(1000,-1100),(1190,-880),(1100,-650)],290),
    ('Spring promenade',[(-1040,650),(-980,1100),(-1000,1500),(-1060,1880),(-1420,2180)],360)]:
    points=curve(xy,20,False);coords=[(points[:,0]-xs[0])/STEP,(points[:,1]-ys[0])/STEP]
    z0=map_coordinates(upper,coords,order=1,mode='nearest');z1=map_coordinates(low,coords,order=1,mode='nearest')
    along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))];t=along/along[-1];t=t*t*(3-2*t)
    z=z0 if name=='Spring promenade' else z0[0]*(1-t)+z1[-1]*t
    access.append(dict(name=name,points=np.column_stack([points,z]).tolist(),width=width))
for r in access:
    points=np.array(r['points']);nearest=np.full_like(H,1e9);z=np.zeros_like(H)
    for a,b in zip(points,points[1:]):
        dv=b-a;t=np.clip(((X-a[0])*dv[0]+(Y-a[1])*dv[1])/max(np.dot(dv[:2],dv[:2]),.01),0,1)
        dd=np.hypot(X-a[0]-t*dv[0],Y-a[1]-t*dv[1]);m=dd<nearest
        z[m]=(a[2]+t*dv[2])[m];nearest=np.minimum(nearest,dd)
    w=r['width']/2
    influence=np.clip((w+180-nearest)/180,0,1);influence=influence*influence*(3-2*influence)
    H=H*(1-influence)+z*influence
# A coherent network: narrower paths leave planted banks and useful sightlines.
# Open handling courts keep the physical thoughts clear of edging and plants.
routes=[LineString(curve(r['points'],18,False)[:,:2]).buffer(140 if r['key']!='MemoryWalk' else 145) for r in ROUTES]
routes+=[LineString(np.array(r['points'])[:,:2]).buffer(r['width']/2-24) for r in access]
routes+=[Point(0,90).buffer(785).difference(Point(0,90).buffer(525)),Point(0,-365).buffer(215),Point(LOTUS[:2]).buffer(425),Point(-1770,-2210).buffer(300)]
portals=json.loads((ART/'Source/C11/portals.json').read_text())
for e in portals:
    a=math.radians(e['yaw']);p=np.array(e['p'][:2]);front=p+np.array([math.sin(a),-math.cos(a)])*230
    routes.append(LineString([p,front]).buffer(220));routes.append(Point(front).buffer(250))
paved=unary_union(routes).intersection(outline.buffer(-40))
pathmask=contains_xy(paved,X,Y);pathdist=distance_transform_edt(~pathmask)*STEP
# Soft banks receive low sculpted tufts at 60–220 cm scale. Walking lines stay
# level across the path width; this is baked mesh displacement, not painted shade.
fade=np.clip((pathdist-20)/150,0,1)
relief=(8*np.sin(X/83+np.sin(Y/190)) + 5*np.sin(Y/59+X/260)+13*np.sin(X/215)*np.cos(Y/173))*fade
H+=relief
# Contained shallow streams have a physical bed. Existing solid bridges remain.
w=water(X,Y);wet=np.clip(-w/80,0,1);H-=wet*(1-pathmask.astype(float))*45
H=gaussian_filter(H,.85)
# Preserve the full core route and its handling courts. These are the hard
# construction datum; the banks adjust to meet them, never cut through them.
primary=unary_union([LineString(curve(r['points'],18,False)[:,:2]).buffer(185) for r in ROUTES]+[Point(0,90).buffer(790).difference(Point(0,90).buffer(310)),Point(-1770,-2210).buffer(300),Point(LOTUS[:2]).buffer(430)])
fixed=contains_xy(primary,X,Y)&inside
H[fixed]=upper[fixed]
# Project height differences to a walkable grade. Outside the protected route,
# adjust both sides of a bank; next to a path, adjust only the garden side.
for iteration in range(180):
    for di,dj in [(1,0),(0,1),(1,1),(1,-1)]:
        aa=(slice(0,-di or None),slice(None,-dj)) if dj>0 else (slice(0,-di or None),slice(-dj,None)) if dj<0 else (slice(0,-di or None),slice(None))
        bb=(slice(di,None),slice(dj,None)) if dj>=0 else (slice(di,None),slice(None,dj))
        a=H[aa];b=H[bb];fa=fixed[aa];fb=fixed[bb];limit=STEP*math.hypot(di,dj)*.68
        delta=b-a;excess=np.sign(delta)*np.maximum(np.abs(delta)-limit,0);both=~fa&~fb
        a+=excess*np.where(both,.5,np.where(~fa,1,0));b-=excess*np.where(both,.5,np.where(~fb,1,0))
gx,gy=np.gradient(H,STEP);slope=np.hypot(gx,gy)
normals=np.stack([-gx,-gy,np.ones_like(H)],axis=-1);normals/=np.linalg.norm(normals,axis=-1)[...,None]
np.savez_compressed(OUT/'terrain.npz',x=xs,y=ys,h=H,inside=inside,path=pathmask,wet=wet)

def height(p):
    p=np.asarray(p);sh=p.shape[:-1];q=p.reshape(-1,2)
    v=map_coordinates(H,[(q[:,0]-xs[0])/STEP,(q[:,1]-ys[0])/STEP],order=1,mode='nearest')
    return v.reshape(sh)

# Separate, solid landscape pieces give Lumen manageable surface-cache bounds.
# Analytic shared edge normals keep their top surface visually continuous.
meshes=[]
for bx in range(0,len(xs)-1,55):
    for by in range(0,len(ys)-1,55):
        ex=min(bx+55,len(xs)-1);ey=min(by+55,len(ys)-1)
        mask=inside[bx:ex+1,by:ey+1];ij=np.argwhere(mask);ids=np.full(mask.shape,-1,int);ids[mask]=np.arange(len(ij))
        if len(ij)<4:continue
        xx=X[bx:ex+1,by:ey+1][mask];yy=Y[bx:ex+1,by:ey+1][mask];zz=H[bx:ex+1,by:ey+1][mask]
        V=np.column_stack([xx,yy,zz]).tolist();N=normals[bx:ex+1,by:ey+1][mask].tolist()
        macro=.5+.22*np.sin(xx/610+.8)*np.cos(yy/530)+.12*np.sin(xx/230+yy/440)
        moss=np.column_stack([.060+.028*macro,.135+.054*macro,.055+.018*macro])
        damp=np.exp(-np.square((xx+1680)/780)-np.square((yy-1100)/1250))
        moss[:,0]*=1-.14*damp;moss[:,2]*=1+.28*damp
        C=moss.tolist();F=[]
        for i,j in np.argwhere(mask[:-1,:-1]&mask[1:,:-1]&mask[1:,1:]&mask[:-1,1:]):F.append([int(ids[i,j]),int(ids[i+1,j]),int(ids[i+1,j+1]),int(ids[i,j+1])])
        if not F:continue
        edges={}
        for face in F:
            for a,b in zip(face,face[1:]+face[:1]):
                key=tuple(sorted((a,b)))
                if key in edges:del edges[key]
                else:edges[key]=(a,b)
        bottom=min(zz)-110;topfaces=len(F);lower={}
        for a,b in edges.values():
            # Independent side normals prevent the old vertical striped walls.
            p=np.array(V[a]);q=np.array(V[b]);nn=np.cross(q-p,[0,0,-1]);nn/=max(np.linalg.norm(nn),.001)
            start=len(V);V.extend([V[b],V[a],[*p[:2],bottom],[*q[:2],bottom]])
            N.extend([nn.tolist()]*4);C.extend([(.08,.075,.06)]*4);F.append([start,start+1,start+2,start+3])
            for k in [a,b]:
                if k not in lower:lower[k]=len(V);V.append([V[k][0],V[k][1],bottom]);N.append([0,0,-1]);C.append([.08,.075,.06])
        # A bottom copy closes every patch for distance-field lighting.
        topcount=len(ij);bstart=len(V)
        V.extend([[V[k][0],V[k][1],bottom] for k in range(topcount)]);N.extend([[0,0,-1]]*topcount);C.extend([[.08,.075,.06]]*topcount)
        for face in F[:topfaces]:F.append([bstart+k for k in reversed(face)])
        name=f'Terrain{bx//55}_{by//55}';np.savez_compressed(OUT/(name+'.npz'),v=np.array(V,np.float32),f=np.array(F,np.int32),c=np.array(C,np.float32),n=np.array(N,np.float32),topfaces=topfaces)
        meshes.append(name)
print('C13_CONTINUOUS_TERRAIN',len(meshes),flush=True)
# Course laid stones have controlled sizes, small joints, and actual rounded
# edges. Variations follow the individual stone, never a repeating global stamp.
rng=np.random.default_rng(13091);seeds=[]
for i,x in enumerate(np.arange(-3270,3290,91)):
    for y in np.arange(-3480,3490,76):seeds.append((x+rng.uniform(-17,17),y+(i%2)*38+rng.uniform(-15,15)))
vor=Voronoi(seeds);stones=[]
for p,region in zip(seeds,vor.point_region):
    if not paved.buffer(85).contains(Point(p)):continue
    region=vor.regions[region]
    if not region or -1 in region:continue
    clipped=Polygon(vor.vertices[region]).intersection(paved).buffer(-1.35,join_style=2)
    polys=[clipped] if clipped.geom_type=='Polygon' else list(clipped.geoms) if clipped.geom_type=='MultiPolygon' else []
    for poly in polys:
        if poly.area<700:continue
        xy=np.array(orient(poly,sign=1).exterior.coords[:-1]);stones.append(dict(xy=xy.tolist(),z=(height(xy)-3).tolist(),tone=float(rng.uniform(.9,1.09)),seed=len(stones)))
(OUT/'paving.json').write_text(json.dumps(stones))
# Widely spaced islands of fern, iris and clover. Keep all approach lines clear.
cx,cy=np.meshgrid(np.arange(-3000,3000,52),np.arange(-3260,3200,52),indexing='ij');xx=cx.ravel()+rng.uniform(-21,21,cx.size);yy=cy.ravel()+rng.uniform(-21,21,cx.size)
valid=contains_xy(outline.buffer(-120),xx,yy)&~contains_xy(paved.buffer(30),xx,yy)
valid&=(np.hypot(xx,yy-90)>315)&(np.hypot((xx+1920)/340,(yy+2240)/290)>1)
ww=water(xx,yy);valid&=ww>40
for p,r in [((-1680,1780),355),((-1680,1280),375),((1580,-1390),490)]:valid&=np.hypot(xx-p[0],yy-p[1])>r
community=(np.sin(xx/247+np.sin(yy/370))+.6*np.cos(yy/153-xx/660))
valid&=(community>.1)&(rng.random(len(xx))<.64)
P=np.column_stack([xx[valid],yy[valid]]);Z=height(P)
np.savez_compressed(OUT/'planting.npz',p=np.column_stack([P,Z]),kind=rng.choice(4,len(P),p=[.57,.23,.15,.05]),scale=rng.uniform(.72,1.25,len(P)),angle=rng.uniform(0,math.tau,len(P)))
# World-grid evidence records continuity independently of the native collider.
walk=inside&(slope<.78);components,count=label(walk);largest=1+np.argmax(np.bincount(components.ravel())[1:]);connected=walk&(components==largest)
report=dict(version='C13',terrain_pieces=meshes,stones=len(stones),plant_clusters=len(P),terrain_extent_cm=[float(H[inside].min()),float(H[inside].max())],standable_area_m2=float(walk.sum()*STEP*STEP/10000),largest_surface_component_fraction=float(connected.sum()/walk.sum()),art_accepted=False)
(OUT/'construction.json').write_text(json.dumps(report,indent=2));(OUT/'portals.json').write_text(json.dumps(portals,indent=2));(OUT/'garden-access.json').write_text(json.dumps(access,indent=2))
print(json.dumps(report),flush=True)
