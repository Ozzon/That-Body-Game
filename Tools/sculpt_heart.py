"""Build the authored heart volume from explicit silhouette, chamber and portal drawings.

Coordinates are Unreal centimeters: +X is the atrial end, -X is the apex.
The four drawings and arched openings are editable art source, not runtime primitives.
"""
from pathlib import Path
import json,sys,heapq
from heart_model_layouts import get_layout
import numpy as np
from skimage.measure import marching_cubes
import trimesh
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
VARIANT=sys.argv[1] if len(sys.argv)>1 else 'A'
SPEC=get_layout(VARIANT)
OUT=ROOT/'Art/HeartModels'/VARIANT/'Source'
OUT.mkdir(parents=True,exist_ok=True)
outline=[[-1140,95],[-965,-425],[-570,-855],[-40,-1010],[515,-960],[950,-705],[1080,-350],[910,-95],[735,10],[920,160],[1080,515],[800,890],[260,1030],[-320,940],[-845,580]]
rooms={
 'RightAtrium':[[190,-150],[130,-560],[360,-795],[740,-680],[915,-370],[740,-145],[450,-105]],
 'LeftAtrium':[[190,155],[420,105],[845,250],[920,490],[655,835],[245,810],[120,550]],
 'RightVentricle':[[-130,-115],[-545,-110],[-855,-275],[-760,-530],[-430,-815],[-55,-835],[50,-505]],
 'LeftVentricle':[[-180,110],[35,190],[80,560],[-140,800],[-520,625],[-940,190],[-655,90]],
}
doors=[{'center':[75,-390],'radii':[245,150],'axis':0},
       {'center':[65,390],'radii':[240,150],'axis':0},
       {'center':[460,0],'radii':[155,255],'axis':1},
       {'center':[-460,30],'radii':[155,265],'axis':1},
       {'center':[-965,125],'radii':[340,165],'axis':0}]

# The accepted image is broad across the ventricles. Keep wall thickness independent
# of this increase in floor area; scaling a thick shell uniformly would stay chunky.
def room_scale(p):return [p[0]*(1.40 if p[0]<0 else 1.05),p[1]*1.45]
outline=[room_scale(p) for p in outline]
rooms={n:[room_scale(p) for p in p] for n,p in rooms.items()}
for door in doors:
    door['radii']=[door['radii'][0]*(1.4 if door['center'][0]<0 else 1.12),door['radii'][1]*1.45]
    door['center']=room_scale(door['center'])

# Each model has a separate drawing and a separate editable sculpt.
outline=SPEC['outline'];rooms=SPEC['rooms'];doors=SPEC['doors']

def curve(points,sub=12):
    p=np.array(points,dtype=np.float32); out=[]
    for i in range(len(p)):
        a,b,c,d=p[(i-1)%len(p)],p[i],p[(i+1)%len(p)],p[(i+2)%len(p)]
        for t in np.linspace(0,1,sub,endpoint=False):
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return np.array(out)

def polygon_distance(x,y,points):
    d=np.full(np.broadcast_shapes(x.shape,y.shape),1e12,dtype=np.float32)
    inside=np.zeros_like(d,dtype=bool)
    for a,b in zip(points,np.roll(points,-1,axis=0)):
        vx,vy=b-a; wx=x-a[0];wy=y-a[1]
        t=np.clip((wx*vx+wy*vy)/(vx*vx+vy*vy+1e-10),0,1)
        d=np.minimum(d,(wx-t*vx)**2+(wy-t*vy)**2)
        inside^=((a[1]>y)!=(b[1]>y))&(x<(vx*(y-a[1])/(vy+1e-8)+a[0]))
    return np.sqrt(d)*np.where(inside,-1,1)

def smoothmax(a,b,k=32):
    h=np.maximum(k-np.abs(a-b),0)/k
    return np.maximum(a,b)+h*h*k*.25

def box_distance(x,y,c,r):
    dx=np.abs(x-c[0])-r[0];dy=np.abs(y-c[1])-r[1]
    return np.hypot(np.maximum(dx,0),np.maximum(dy,0))+np.minimum(np.maximum(dx,dy),0)

def surface_coordinate(x,y,points):
    best=np.full(len(x),1e12,dtype=np.float32);along=np.zeros(len(x),dtype=np.float32);length=0
    for a,b in zip(points,np.roll(points,-1,axis=0)):
        vx,vy=b-a;segment=np.hypot(vx,vy);t=np.clip(((x-a[0])*vx+(y-a[1])*vy)/(segment*segment),0,1)
        d=(x-a[0]-t*vx)**2+(y-a[1]-t*vy)**2;mask=d<best
        along[mask]=length+t[mask]*segment;best=np.minimum(best,d);length+=segment
    return np.sqrt(best),along

def fascia(u,v):
    # Long, staggered muscle cells follow each chamber's own boundary.
    uu=u/108+.13*np.sin(v/170);vv=v/178
    ix=np.floor(uu);iy=np.floor(vv);first=np.full(len(u),100.);second=first.copy()
    for dx in [-1,0,1]:
        for dy in [-1,0,1]:
            gx=ix+dx;gy=iy+dy
            jx=.18*np.sin(gx*13.7+gy*8.1);jy=.12*np.cos(gx*9.1-gy*15.2)
            d=(uu-gx-.5-jx)**2+(vv-gy-.5-jy)**2
            second=np.minimum(second,np.maximum(first,d));first=np.minimum(first,d)
    return np.exp(-((np.sqrt(second)-np.sqrt(first))/.047)**2)

STEP=10
xs=np.arange(-2220,1741,STEP,dtype=np.float32)
ys=np.arange(-1740,1761,STEP,dtype=np.float32)
zs=np.arange(-300,731,STEP,dtype=np.float32)
X,Y=np.meshgrid(xs,ys,indexing='ij')
Z=zs[None,None,:]
outer=polygon_distance(X,Y,curve(outline))
tops=420+np.clip(X/1700,-1,1)*90+30*np.abs(Y/1400)
entrance=SPEC['doors'][-1] if VARIANT!='A' else SPEC['doors'][-2]
tops+=100*np.exp(-((X-entrance['center'][0])/320)**2-((Y-SPEC['entrance_y'])/350)**2)
if SPEC['divider']=='open':tops=np.where(outer<-250,188+np.clip(X/1000,0,1)*80,tops-45)
if SPEC['divider']=='anatomical':tops+=45*np.exp(-((Y-500)/600)**2)
ground=58+np.clip((X-150)/650,0,1)*105 if SPEC['floor']=='terraced' else np.full_like(X,58)
# A rounded muscular base with a thicker left ventricle; not an extruded outline.
taper=np.maximum(-Z,0)**2/1200
field=smoothmax(outer[:,:,None]+taper,Z-tops[:,:,None],54)
field=smoothmax(field,-205-Z,65)
raw=[polygon_distance(X,Y,curve(p)) for p in rooms.values()]
fields=[]
for i,(n,p) in enumerate(rooms.items()):
    Other=np.minimum.reduce([d for j,d in enumerate(raw) if i!=j])
    D=np.maximum.reduce([raw[i]-65,(raw[i]-Other+115)*.5,outer+115])
    fields.append(D)
    # Each open room flares very slightly upward and rolls smoothly into the floor.
    cavity=smoothmax(D[:,:,None]-(Z-65)*.045,ground[:,:,None]-Z,38)
    field=smoothmax(field,-cavity,28)

for door in doors:
    C,R,axis=door['center'],door['radii'],door['axis']
    horizontal=box_distance(X,Y,C,R)
    across=(Y-C[1])/R[1] if axis==0 else (X-C[0])/R[0]
    ceiling=240+120*np.sqrt(np.maximum(1-np.clip(across,-1,1)**2,0))
    cavity=smoothmax(horizontal[:,:,None],ground[:,:,None]-Z,25)
    cavity=smoothmax(cavity,Z-ceiling[:,:,None],20)
    field=smoothmax(field,-cavity,28)

# Very restrained sculpting: large muscles, not surface noise or loose decorations.
muscle=2.3*np.sin(X[:,:,None]/94+Z/80)*np.sin(Y[:,:,None]/120-Z/105)
field+=muscle*np.clip((Z-95)/140,0,1)
v,f,n,_=marching_cubes(field,level=0,spacing=(STEP,STEP,STEP),allow_degenerate=False)
v+=np.array([xs[0],ys[0],zs[0]])
mesh=trimesh.Trimesh(v,f,process=True)
trimesh.repair.fix_normals(mesh)
trimesh.smoothing.filter_taubin(mesh,lamb=.38,nu=.4,iterations=5)
v=np.array(mesh.vertices,dtype=np.float32); f=np.array(mesh.faces,dtype=np.int32); n=np.array(mesh.vertex_normals,dtype=np.float32)

# Art-directed color massing: wine base, coral muscle, soft peach cut edge, warm quiet floors.
base=np.array([.28,.035,.032]);wall=np.array([.52,.10,.058]);peach=np.array([.72,.205,.105]);floor=np.array([.60,.18,.10])
col=np.tile(wall,(len(v),1))
low=np.clip((v[:,2]+120)/230,0,1)[:,None]
col=base*(1-low)+col*low
roomD=np.minimum.reduce([polygon_distance(v[:,0],v[:,1],curve(p)) for p in rooms.values()])
ds=[];us=[]
for p in rooms.values():
    d,u=surface_coordinate(v[:,0],v[:,1],curve(p));ds.append(d);us.append(u)
ds=np.array(ds);us=np.array(us);nearest=np.argmin(ds,axis=0);ix=np.arange(len(v))
innerU=us[nearest,ix];wallness=np.clip((v[:,2]-115)/65,0,1)*np.clip((.88-n[:,2])/.5,0,1)
carved=fascia(innerU,v[:,2])*wallness
v-=n*(carved*2.7)[:,None]
inner=np.clip((-roomD+50)/100,0,1)[:,None]
col=col*(1-inner*.42)+peach*inner*.42
flat=(np.clip((n[:,2]-.5)/.45,0,1)*np.clip((150-v[:,2])/70,0,1))[:,None]
col=col*(1-flat)+floor*flat
edge=(np.clip((n[:,2]-.05)/.95,0,1)*np.clip((v[:,2]-165)/130,0,1))[:,None]
col=col*(1-edge*.48)+peach*edge*.48
variation=(.98+.022*np.sin(v[:,0]/170)*np.cos(v[:,1]/220))[:,None]
col=np.clip(col*variation,0,1)
col*=1-carved[:,None]*.28
# Shallow concentric fascia on each chamber floor, carried by the material rather than loose props.
floor_centers=np.array(SPEC['centers'])
floor_crease=np.zeros(len(v))
for i,center in enumerate(floor_centers):
    dx=v[:,0]-center[0];dy=v[:,1]-center[1];r=np.hypot(dx,dy);a=np.arctan2(dy,dx)
    ring=np.floor(r/112);radial=np.exp(-(np.sin(np.pi*(r/112))/.08)**2)
    spokes=np.exp(-(np.sin((a+ring*.16)*(8+ring*2))/.06)**2)
    weight=(nearest==i)*np.clip((n[:,2]-.75)/.23,0,1)*np.clip((110-v[:,2])/30,0,1)
    floor_crease=np.maximum(floor_crease,np.maximum(radial,spokes*.6)*weight)
col*=1-floor_crease[:,None]*.24
np.savez_compressed(OUT/'heart_sculpt.npz',vertices=v,faces=f,normals=n,colors=col)

# Ground navigation is derived from the same chamber and opening drawings.
navx=xs;navy=ys
NX,NY=np.meshgrid(navx,navy,indexing='ij')
space=np.minimum.reduce(fields)
for door in doors:space=np.minimum(space,box_distance(X,Y,door['center'],door['radii']))
walk=space<-70
walk&=outer<-60
walk|=(X<entrance['center'][0])&(X>SPEC['spawn'][0]-100)&(np.abs(Y-SPEC['entrance_y'])<155)
chars=[''.join('1' if t else '0' for t in row) for row in walk]
header='// Generated from the authored chamber and portal drawings in Tools/sculpt_heart.py.\nnamespace HeartModel'+VARIANT+' {\n'
header+=f'static constexpr int HeartNavX={len(xs)}, HeartNavY={len(ys)}, HeartNavOriginX={int(xs[0])}, HeartNavOriginY={int(ys[0])};\n'
header+='static constexpr char HeartNav[HeartNavX][HeartNavY+1] = {\n'+'\n'.join('"'+row+'",' for row in chars)+'};\n'
header+='static constexpr float SpawnX='+str(SPEC['spawn'][0])+', SpawnY='+str(SPEC['spawn'][1])+';\n'
header+='static constexpr float StationX='+str(SPEC['station'][0])+', StationY='+str(SPEC['station'][1])+';\n'
header+='static constexpr float WallX='+str(SPEC['outline'][5][0])+', WallY='+str(SPEC['outline'][5][1])+';\n'

def nav_index(p):return (round((p[0]-xs[0])/STEP),round((p[1]-ys[0])/STEP))
def legal(p):return 0<=p[0]<walk.shape[0] and 0<=p[1]<walk.shape[1] and walk[p]
def snap(p):
    if legal(p):return p
    candidates=np.argwhere(walk);d=np.sum((candidates-np.array(p))**2,axis=1);return tuple(candidates[np.argmin(d)])
def clear(a,b):
    return all(legal((round(a[0]*(1-t)+b[0]*t),round(a[1]*(1-t)+b[1]*t))) for t in np.linspace(0,1,int(np.hypot(b[0]-a[0],b[1]-a[1])*2)+2))
def route(a,b):
    a=snap(nav_index(a));b=snap(nav_index(b));q=[(0,a)];cost={a:0};prev={};seen=set()
    while q:
        _,p=heapq.heappop(q)
        if p in seen:continue
        seen.add(p)
        if p==b:break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            n=(p[0]+dx,p[1]+dy)
            if not legal(n) or not legal((p[0]+dx,p[1])) or not legal((p[0],p[1]+dy)):continue
            d=cost[p]+(1.414 if dx and dy else 1)
            if d<cost.get(n,1e9):cost[n]=d;prev[n]=p;heapq.heappush(q,(d+np.hypot(n[0]-b[0],n[1]-b[1]),n))
    if b not in seen:raise RuntimeError(f'{VARIANT}: disconnected chambers {a} -> {b}')
    path=[b]
    while path[-1]!=a:path.append(prev[path[-1]])
    path=path[::-1];simple=[a];i=0
    while i<len(path)-1:
        j=len(path)-1
        while j>i+1 and not clear(path[i],path[j]):j-=1
        simple.append(path[j]);i=j
    return [[int(xs[i]),int(ys[j])] for i,j in simple[1:]]

st=SPEC['station'];standoff=[st[0]-190,st[1]-140]
goals=[SPEC['spawn'],SPEC['centers'][2],SPEC['centers'][0],SPEC['centers'][1],SPEC['centers'][3],SPEC['spawn'],standoff]
waypoints=[]
for a,b in zip(goals,goals[1:]):waypoints+=route(a,b)
header+='static const FVector Route[] = {'+','.join(f'FVector({p[0]},{p[1]},63)' for p in waypoints)+'};\n}\n'
(ROOT/f'Source/ThatBodyGame/HeartModel{VARIANT}Nav.inl').write_text(header)
Image.fromarray(np.uint8(walk.T[::-1,:])*255).save(OUT/'walkable-clearance.png')
layout={**SPEC,'variant':VARIANT,'units':'centimeters','floor_height':60,'minimum_door_width':310,'portal_headroom':360,'character_width':100,'wall_thickness_target':115,'mesh_vertices':len(v),'triangles':len(f),'watertight':bool(mesh.is_watertight),'input_test_route':waypoints}
(OUT/'heart-layout.json').write_text(json.dumps(layout,indent=2))
print('HEART_SCULPT_READY',json.dumps({k:layout[k] for k in ['mesh_vertices','triangles','watertight']}),flush=True)
