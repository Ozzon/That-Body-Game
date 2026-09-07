"""Fully modeled brain garden: fused cortex, terrain, hero tree and distinct garden spaces."""
import bpy,numpy as np,math,json,sys,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from brain_garden_layout import *
from garden_model import collection,material,mesh,merge,ellipsoid,sweep,leaf,block
from organ_math import distance,curve
ART=ROOT/'Art/BrainGarden';EXPORT=ART/'Export';EXPORT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
surface=material('Garden | painted sculpt',0,.59);foliage=material('Leaves | warm translucence',.08,.46);watermat=material('Synapse water | luminous teal',.34,.22);glow=material('Awareness | golden light',1.8,.45)
cortex=collection('01 CORTEX | continuous sculpted brain folds');garden=collection('02 TERRAIN | planted paths and terraces');tree=collection('03 AWARENESS TREE | bark, roots, branches');canopy=collection('04 CANOPY | individual pointed leaves');structures=collection('05 GARDENS | library, focus and pools');plants=collection('06 PLANTING | bed compositions');stage=collection('07 REVIEW | lighting and cameras')
exports=[]
def add(o,key,tags=(),kind='Surface'):exports.append(dict(object=o,key=key,tags=list(tags),material=kind));return o
d=np.load(ART/'Source/brain_cortex.npz');V,F,N,C=[d[k] for k in ['vertices','faces','normals','colors']];mid=V[F].mean(axis=1)
ground_faces=(N[F].mean(axis=1)[:,2]>.60)&(inner_distance(mid[:,0],mid[:,1])<-55)&(mid[:,2]<floor_height(mid[:,0],mid[:,1])+TERRAIN_LIFT+45)
part=np.where(ground_faces,0,1+(mid[:,0]>0).astype(int)*2+(mid[:,1]>0).astype(int))
for i,name in enumerate(['Ground','CortexFrontRight','CortexFrontLeft','CortexBackRight','CortexBackLeft']):
    f=F[part==i];ids,inv=np.unique(f.ravel(),return_inverse=True);o=mesh('SM_BrainGarden_'+name,V[ids].tolist(),inv.reshape(-1,3).tolist(),C[ids],cortex,surface,N[ids].tolist());add(o,'Cortex',['Ground'] if i==0 else [])

# A mature, asymmetric tree with exposed roots and twisting bark, centered in the garden.
bark=(.46,.255,.085);gold=(.96,.56,.115);parts=[]
trunk=[(0,0,85),(-40,0,355),(55,22,660),(10,10,930),(30,35,1200)]
parts.append(sweep('Living trunk',trunk,[165,138,106,72,25],bark,tree,surface,36,12,.075))
branches=[([(5,0,465),(-60,-110,710),(-50,-340,900),(-170,-600,1050)],[108,85,51,9]),
          ([(10,0,690),(120,185,870),(80,430,1150),(180,655,1270)],[87,68,41,8]),
          ([(10,0,855),(200,-90,1050),(420,-280,1240),(575,-330,1330)],[78,53,32,7]),
          ([(20,10,940),(-190,100,1110),(-340,350,1320),(-460,480,1430)],[67,48,28,5]),
          ([(0,0,630),(-210,60,790),(-360,250,920),(-620,290,1020)],[75,57,32,7]),
          ([(20,20,1060),(160,80,1280),(195,300,1450)],[56,32,5])]
twigtips=[]
for j,(p,r) in enumerate(branches):
    parts.append(sweep('Primary limb '+str(j),p,r,bark,tree,surface,28,10,.072));last=np.array(p[-1]);before=np.array(p[-2]);direction=(last-before)/np.linalg.norm(last-before)
    for k in range(3):
        start=np.array(p[-2])*(.2+k*.2)+last*(.8-k*.2);side=np.array([math.cos(j+k*2.2),math.sin(j+k*2.2),.35]);tip=start+direction*(160+25*k)+side*160
        parts.append(sweep('Leaf-bearing twig',[start.tolist(),((start+tip)/2+np.array([0,0,45])).tolist(),tip.tolist()],[24,15,3],bark,tree,surface,16,6,.055));twigtips.append(tip)
    twigtips.append(last)
for j in range(10):
    a=j*math.tau/10;r=340+35*math.sin(j*2.8)
    p=[(0,0,180),(math.cos(a)*140,math.sin(a)*140,105),(math.cos(a+.10)*260,math.sin(a+.1)*260,74),(math.cos(a+.12)*r,math.sin(a+.12)*r,65)]
    parts.append(sweep('Exposed root '+str(j),p,[68,54,31,4],bark,tree,surface,24,8,.06))
o=merge(parts,'SM_BrainGarden_TreeTrunk')
# Voxel union produces actual continuous branch junctions and integrated roots.
bpy.context.view_layer.objects.active=o
modifier=o.modifiers.new('Fused root and branch sculpture','REMESH');modifier.mode='VOXEL';modifier.voxel_size=12;modifier.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=modifier.name)
modifier=o.modifiers.new('Hand-softened junctions','SMOOTH');modifier.factor=.64;modifier.iterations=5;bpy.ops.object.modifier_apply(modifier=modifier.name)
for a in list(o.data.color_attributes):o.data.color_attributes.remove(a)
v=np.array([list(v.co) for v in o.data.vertices]);a=np.arctan2(v[:,1],v[:,0]);rib=(.5+.5*np.cos(a*9-v[:,2]/75))**5
cc=np.array([.41,.205,.063])[None,:]*(.86+.29*rib[:,None]+.10*np.clip(v[:,2,None]/1300,0,1))
col=o.data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='POINT');col.data.foreach_set('color',np.column_stack([cc,np.ones(len(v))]).ravel())
add(o,'TreeTrunk',['Interactive'])

# Warm spiral channels and buds, seated on the bark rather than floating through it.
parts=[]
for j in range(3):
    pts=[]
    for t in np.linspace(0,1,24):
        z=220+t*600;a=math.pi+j*math.tau/3+.45*math.sin(t*4);r=147-52*t
        center=np.array([-40+95*t if t<.74 else 40,12*t,z])
        pts.append(tuple(center+np.array([math.cos(a)*r,math.sin(a)*r,0])))
    parts.append(sweep('Carved amber channel',pts,[5.4,4.1,2.5],(.94,.40,.055),tree,glow,12,2,.01))
for j in range(13):
    t=(j+.3)/13;z=240+t*680;a=math.pi+1.7*math.sin(j*2.3);r=143-48*t
    x=math.cos(a)*r+20*math.sin(t*5);y=math.sin(a)*r
    parts.append(leaf('Amber bark bud',(x,y,z),(0,0,1),27+j%3*6,9,(.98,.51,.09),tree,glow,.12))
add(merge(parts,'SM_BrainGarden_BarkInlay'),'TreeGlow',['Interactive'],'Glow')

rng=random.Random(73);leaves=[[],[],[],[]]
for j,tip in enumerate(twigtips+[[15,0,1390],[-240,-280,1230],[300,400,1320]]):
    for k in range(24):
        a=k*2.399+j*.7;rad=70+85*rng.random();pos=np.array(tip)+np.array([math.cos(a)*rad,math.sin(a)*rad,(rng.random()-.45)*125])
        direction=(math.cos(a)*.9,math.sin(a)*.9,.35+rng.random()*.75);color=(.72+rng.random()*.24,.40+rng.random()*.22,.065+rng.random()*.055)
        o=leaf('Golden leaf',pos,direction,90+rng.random()*65,27+rng.random()*15,color,canopy,foliage,.24);leaves[(pos[0]>0)*2+(pos[1]>0)].append(o)
for i,items in enumerate(leaves):add(merge(items,'SM_BrainGarden_Canopy'+str(i)),'Canopy',(), 'Foliage')

# Fitted 3D polygon masonry follows every terrace and shares one route mask.
stone=(.42,.285,.15)
d=np.load(ART/'Source/garden_masonry.npz')
add(mesh('SM_BrainGarden_FittedMasonry',d['vertices'].tolist(),d['faces'].tolist(),d['colors'],garden,surface),'Paths')
# Pools and the narrow flowing synapse stream sit below their modeled banks.
from mathutils.geometry import tessellate_polygon
pool=curve(POOL,10);poly=[Vector((x,y,29)) for x,y in pool];tri=tessellate_polygon([poly]);look={tuple(p):i for i,p in enumerate(poly)}
V=[tuple(p) for p in poly];F=[tuple(p if isinstance(p,int) else look[tuple(p)] for p in t) for t in tri];C=[(.035,.27,.33)]*len(V)
o=mesh('SM_BrainGarden_SynapsePool',V,F,C,structures,watermat);add(o,'Water',(), 'Water')
pts=curve(STREAM,18,False);V=[];F=[];C=[]
for i,p in enumerate(pts):
    d=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)];side=np.array([-d[1],d[0]])/np.linalg.norm(d)
    for f in [-1,-.72,.72,1]:
        q=p+side*86*f;V.append((q[0],q[1],float(height(*q))-35));C.append((.055,.30,.33) if abs(f)>.8 else (.045,.37,.44))
    if i:
        for j in range(3):a=(i-1)*4+j;F.append((a,a+4,a+5,a+1))
add(mesh('SM_BrainGarden_CalmStream',V,F,C,structures,watermat),'Water',(), 'Water')

# Four arched stone crossings, each with low side parapets and a broad walkway.
bridge_parts=[]
for b in BRIDGES:
    pts=curve(b['points'],14,False);lengths=np.linalg.norm(np.diff(pts,axis=0),axis=1);total=lengths.sum();cum=np.r_[0,np.cumsum(lengths)];n=max(4,int(total/78))
    vv=[];ff=[]
    for i,p in enumerate(pts):
        dr=pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)];side=np.array([-dr[1],dr[0]])/np.linalg.norm(dr);_,hh=bridge_values(p[0],p[1]);zz=float(hh)
        for s,dz in [(-1,-20),(1,-20),(-1,-92),(1,-92)]:q=p+side*s*b['width']/2;vv.append((q[0],q[1],zz+dz))
        if i:
            a=(i-1)*4;ff.extend([(a,a+4,a+5,a+1),(a+2,a+6,a+4,a),(a+1,a+5,a+7,a+3)])
    bridge_parts.append(mesh('Continuous arch bridge',vv,ff,(.44,.23,.175),structures,surface))
    for i in range(n):
        t=(i+.5)*total/n;k=min(len(pts)-2,max(0,np.searchsorted(cum,t)-1));u=(t-cum[k])/lengths[k];p=pts[k]*(1-u)+pts[k+1]*u;d=pts[k+1]-pts[k];d/=np.linalg.norm(d);side=np.array([-d[1],d[0]]);ang=math.atan2(d[1],d[0]);_,hh=bridge_values(np.array([p[0]]),np.array([p[1]]));z=float(hh[0]);w=b['width']
        for row in range(3):
            q=p+side*(row-1)*(w-50)/3;bridge_parts.append(block('Arch bridge stone',(q[0],q[1],z-6),(total/n-1,(w-50)/3-2,29),(.52,.31,.235),structures,surface,ang,6,i+row))
        for s in [-1,1]:
            q=p+side*s*(w/2+5);bridge_parts.append(block('Bridge parapet',(q[0],q[1],z+34),(total/n-2,48,95),(.60,.245,.20),structures,surface,ang,9,i+s))
add(merge(bridge_parts,'SM_BrainGarden_StoneBridges'),'Bridges',['LightBridge'])

# Terrace edges and the pool's low retaining wall are authored masonry with route openings.
walls=[]
for zone in [z for z in ZONES if z['key'] in ['Library','Focus']]+[dict(key='Pool',center=[1070,55],radii=[580,530])]:
    c=zone['center'];r=zone['radii'];num=35
    for i in range(num):
        a=i*math.tau/num;x=c[0]+r[0]*math.cos(a);y=c[1]+r[1]*math.sin(a)
        if inner_distance(x,y)>-160 or any(distance(np.array([x]),np.array([y]),curve(p['points'],10,False),False)[0]<p['width']/2+65 for p in PATHS+BRIDGES) or (zone['key']=='Library' and y>-1450) or (zone['key']=='Focus' and x<780):continue
        z=float(height(x,y))+30;ang=math.atan2(r[1]*math.cos(a),-r[0]*math.sin(a));color=(.47,.35,.21) if zone['key']!='Worry' else (.36,.19,.35)
        walls.append(block('Garden wall',(x,y,z),(96,65,75),color,structures,surface,ang,9,i))
add(merge(walls,'SM_BrainGarden_TerraceWalls'),'GardenWalls')

# Thought library: a real curved shelf, hand-bound books and an open-book lectern.
parts=[];lx,ly=-700,-1510;lz=float(height(lx,ly));wood=(.34,.18,.085)
for x in [-330,0,330]:
    xx=lx+x;yy=ly-145+.0008*x*x
    parts.append(block('Library back',(xx,yy,lz+145),(295,48,240),wood,structures,surface,0,10))
    for z in [lz+38,lz+134,lz+234]:parts.append(block('Library shelf',(xx,yy+28,z),(315,108,25),(.42,.24,.10),structures,surface,0,5))
    for i in range(6):
        for row in range(2):
            col=[(.48,.15,.13),(.17,.28,.29),(.43,.32,.15),(.29,.18,.35)][(i+row)%4];bx=xx-115+i*43;bz=lz+76+row*94
            parts.append(block('Memory volume',(bx,yy+52,bz),(30,56,65+i%3*10),col,structures,surface,.015*(i-2),4))
parts.append(block('Reading pedestal',(lx-100,ly+170,lz+57),(235,180,105),wood,structures,surface,.1,15))
for s in [-1,1]:
    o=block('Open book page',(lx-100+s*51,ly+170,lz+120),(102,145,12),(.78,.64,.40),structures,surface,.10+s*.12,3);parts.append(o)
    for j in range(4):parts.append(block('Page inscription',(lx-100+s*51,ly+132+j*22,lz+127),(72,3,2),(.30,.20,.10),structures,surface,.1,0))
add(merge(parts,'SM_BrainGarden_ThoughtLibrary'),'Library',['Interactive'])

# Focus terrace: a sculpted lotus and circular pavilion floor, no generic marker sphere.
parts=[];fx,fy=840,1360;fz=float(height(fx,fy))
for r,z,n in [(225,fz+10,20),(152,fz+45,16)]:
    for i in range(n):a=i*math.tau/n;parts.append(block('Focus dais',(fx+r*math.cos(a),fy+r*math.sin(a),z),(65,math.tau*r/n-2,35),(.59,.40,.205),structures,surface,a,7,i))
parts.append(ellipsoid('Lotus base',(fx,fy,fz+80),(128,128,48),(.37,.43,.13),structures,surface))
add(merge(parts,'SM_BrainGarden_FocusDais'),'Focus',['Interactive']);parts=[]
for i in range(9):
    a=i*math.tau/9;parts.append(leaf('Lotus petal',(fx,fy,fz+105),(math.cos(a),math.sin(a),.75),160,52,(.85,.49,.105),structures,foliage,.45))
add(merge(parts,'SM_BrainGarden_FocusPetals'),'FocusPetals',['Interactive'])

# Folded cerebellum at the garden's edge. Deliberate close parallel folia distinguish it.
parts=[]
for j in range(10):
    y=1090+j*66;pts=[(-1780,y,90),(-1540,y-35,170+22*math.sin(j)),(-1290,y+5,195),(-1080,y+40,130)]
    parts.append(sweep('Cerebellar folium',pts,[45,67,63,34],(.34,.15,.37),structures,surface,22,8,.018))
parts.append(sweep('Cerebellar arbor',[(-1790,1600,120),(-1510,1480,250),(-1270,1260,295),(-1080,1180,260)],[38,29,20,9],(.61,.40,.34),structures,surface,20,8,.025))
add(merge(parts,'SM_BrainGarden_Cerebellum'),'Cerebellum')

# Planting comes in placed beds around landmarks, leaving the walking routes uncluttered.
def on_path(x,y,margin=40):
    if 420<math.hypot(x,y)<740:return True
    return any(distance(np.array([x]),np.array([y]),curve(p['points'],8,False),False)[0]<p['width']/2+margin for p in PATHS+BRIDGES)
plant_groups=[[],[],[],[]];rocks=[]
beds=[(-1440,-450,230,250),(-200,-1790,240,120),(830,-1650,300,140),(1100,1660,200,120),(-200,1850,270,120)]
for bi,(cx,cy,rx,ry) in enumerate(beds):
    for i in range(33):
        a=rng.random()*math.tau;r=math.sqrt(rng.random());x=cx+math.cos(a)*rx*r;y=cy+math.sin(a)*ry*r
        if inner_distance(x,y)>-155 or waters(x,y)<125 or on_path(x,y):continue
        z=float(height(x,y));group=(x>0)*2+(y>0)
        if i%4==0:
            rocks.append(ellipsoid('Bed stone',(x,y,z+28),(55,43,35),(.31,.33,.23),plants,surface,bi+i,16,9));continue
        for j in range(7):
            aa=j*2.399+i*.7;col=(.20+rng.random()*.13,.29+rng.random()*.14,.065+rng.random()*.06)
            plant_groups[group].append(leaf('Garden leaf',(x,y,z+2),(math.cos(aa),math.sin(aa),.55),64+rng.random()*64,15+rng.random()*15,col,plants,surface,.38))
        if i%3:
            for flower in range(3):
                xx=x+rng.uniform(-32,32);yy=y+rng.uniform(-32,32);zz=z+74+rng.random()*45
                plant_groups[group].append(sweep('Flower stem',[(xx,yy,z+5),(xx-6,yy,zz)],[3.3,2],(.21,.32,.085),plants,surface,7,2,0))
                color=[(.74,.22,.42),(.53,.33,.63),(.85,.58,.16),(.29,.47,.63)][(bi+i)%4]
                for j in range(5):
                    aa=j*math.tau/5;plant_groups[group].append(leaf('Blossom petal',(xx,yy,zz),(math.cos(aa),math.sin(aa),.30),33,15,color,plants,foliage,.25))
                plant_groups[group].append(ellipsoid('Flower heart',(xx,yy,zz+6),(9,9,8),(.87,.59,.17),plants,surface,0,10,6))
for i,g in enumerate(plant_groups):
    if g:add(merge(g,'SM_BrainGarden_PlantedBed'+str(i)),'Planting')
if rocks:add(merge(rocks,'SM_BrainGarden_BedStones'),'Planting')

# Two small blossom trees in the idea grove complement the single dominant central tree.
for j,(x,y) in enumerate([(700,-1640),(1120,-1390)]):
    z=float(height(x,y));parts=[sweep('Idea tree trunk',[(x,y,z),(x-25,y,z+170),(x+15,y,z+360)],[32,24,8],(.37,.205,.095),plants,surface,20,8,.08)]
    for k in range(5):
        a=k*math.tau/5;tip=(x+math.cos(a)*120,y+math.sin(a)*120,z+310+45*math.sin(k))
        parts.append(sweep('Idea branch',[(x,y,z+165),tip],[18,4],(.37,.205,.095),plants,surface,12,6,.05))
        for n in range(8):
            aa=n*2.4;p=(tip[0]+math.cos(aa)*70,tip[1]+math.sin(aa)*70,tip[2]+rng.uniform(-30,65));parts.append(leaf('Idea blossom leaf',p,(math.cos(aa),math.sin(aa),.65),65,27,(.56+rng.random()*.16,.20+rng.random()*.10,.43+rng.random()*.14),plants,foliage,.25))
    add(merge(parts,'SM_BrainGarden_IdeaTree'+str(j)),'IdeaTrees')

# Five squat lanterns guide junctions, spaced deliberately rather than scattered everywhere.
parts=[];lights=[]
for i,(x,y) in enumerate([(-1710,220),(-720,-740),(1170,-700),(1140,760),(-860,850)]):
    z=float(height(x,y));parts.append(block('Lantern foot',(x,y,z+16),(70,70,34),(.39,.30,.20),structures,surface,0,9));parts.append(block('Lantern cap',(x,y,z+100),(68,68,23),(.42,.30,.15),structures,surface,0,8))
    for a in range(4):parts.append(block('Lantern post',(x+22*(1 if a%2 else -1),y+22*(1 if a<2 else -1),z+62),(8,8,62),(.36,.25,.12),structures,surface,0,2))
    lights.append(ellipsoid('Lantern flame',(x,y,z+62),(18,18,27),(.96,.55,.10),structures,glow,0,16,10))
add(merge(parts,'SM_BrainGarden_PathLanterns'),'Lanterns');add(merge(lights,'SM_BrainGarden_LanternLight'),'LanternGlow',(),'Glow')

# Three hand-modeled bright thoughts. Their soft star outlines and tiny faces
# are the carryable inhabitants in the reference, sized to Attention's arms.
for k,(sx,sy) in enumerate(MEMORIES):
    sz=float(height(sx,sy))+110;parts=[];vv=[];ff=[];cc=[]
    contour=[]
    for j in range(10):
        a=math.pi/2+j*math.tau/10;r=65 if j%2==0 else 35
        contour.append((math.cos(a)*r,math.sin(a)*r))
    contour=curve(contour,5,True);n=len(contour)
    for xx,scale in [(24,.87),(0,1),(-24,.87)]:
        for y,z in contour:vv.append((sx+xx,sy+y*scale,sz+z*scale));cc.append((.99,.55,.085))
    for layer in range(2):
        for j in range(n):a=layer*n+j;b=layer*n+(j+1)%n;ff.append((a,b,b+n,a+n))
    vv.extend([(sx+33,sy,sz),(sx-33,sy,sz)]);cc.extend([(.99,.70,.21),(.99,.70,.21)])
    for j in range(n):ff.extend([(3*n,(j+1)%n,j),(3*n+1,2*n+j,2*n+(j+1)%n)])
    parts.append(mesh('Soft bright thought',vv,ff,cc,structures,glow))
    for eye in [-1,1]:
        parts.append(ellipsoid('Bright thought eye',(sx-31,sy+eye*15,sz+5),(4,6,9),(.045,.02,.065),structures,surface,0,12,8))
        parts.append(ellipsoid('Eye glint',(sx-35,sy+eye*15-1,sz+8),(1.4,2,2.4),(.95,.90,.60),structures,surface,0,8,6))
    parts.append(sweep('Thought smile',[(sx-34,sy-8,sz-11),(sx-36,sy,sz-16),(sx-34,sy+8,sz-11)],[2,2,2],(.10,.045,.02),structures,surface,8,4,0))
    add(merge(parts,'SM_BrainGarden_BrightThought'+str(k)),'BrightThought'+str(k),['Interactive'],'Glow')

# A return route grows across the stream after three stars reach the tree.
# Its deck and native clearance use the same two endpoints and sine arch.
parts=[];start=np.array([-350.,-520.]);end=np.array([-450.,-1280.]);dr=end-start;side=np.array([-dr[1],dr[0]])/np.linalg.norm(dr)
rootz0=float(height(*start))+12;rootz1=float(height(*end))+12
vv=[];ff=[]
for i,t in enumerate(np.linspace(0,1,25)):
    center=start+dr*t;zz=rootz0+(rootz1-rootz0)*t+75*math.sin(t*math.pi)
    for d,dz in [(-205,0),(205,0),(-205,-46),(205,-46)]:q=center+side*d;vv.append((q[0],q[1],zz+dz))
    if i:
        a=(i-1)*4;ff.extend([(a,a+4,a+5,a+1),(a,a+2,a+6,a+4),(a+1,a+5,a+7,a+3)])
parts.append(mesh('Root shortcut deck',vv,ff,(.31,.20,.10),structures,surface))
for sign in [-1,1]:
    pts=[]
    for t in np.linspace(0,1,12):
        q=start+dr*t+side*sign*224;zz=rootz0+(rootz1-rootz0)*t+75*math.sin(t*math.pi)+20;pts.append((q[0],q[1],zz))
    parts.append(sweep('Living bridge root',pts,[30,44,35],(.34,.19,.065),structures,surface,20,3,.09))
add(merge(parts,'SM_BrainGarden_RootShortcut'),'RootShortcut',['LightBridge'])

manifest=[]
for e in exports:
    o=e['object'];bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    if e['key']!='Cortex':
        for v in o.data.vertices:v.co.z+=TERRAIN_LIFT
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    manifest.append(dict(name=o.name,key=e['key'],tags=e['tags'],material=e['material']))
(ART/'asset-manifest.json').write_text(json.dumps(manifest,indent=2))
print('BRAIN_GARDEN_EXPORTS_READY',len(manifest),flush=True)

def area(name,pos,energy,size,color,target=(0,0,250)):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Large soft morning key',(-2700,-2200,4800),170000000,2900,(1,.86,.77));area('Lavender fill',(1500,3100,3000),100000000,2800,(.72,.79,1));area('Golden rim',(2200,-1500,3000),140000000,1800,(1,.67,.40),(0,0,600))
scene.world.color=(.12,.12,.15)
stage_mat=material('Midnight review stage',0,.9);o=ellipsoid('Review background',(0,0,-420),(15000,15000,70),(.018,.025,.052),stage,stage_mat,0,64,12)
camera_data=bpy.data.cameras.new('Brain garden full level');camera=bpy.data.objects.new('Brain garden full level',camera_data);stage.objects.link(camera);camera.location=(-6300,-360,5400);target=Vector((0,0,320));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=6400;camera_data.clip_end=40000;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ART/'Brain-garden-source.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Garden.blend'));print('BRAIN_GARDEN_EDITABLE_SAVED',flush=True);bpy.ops.render.render(write_still=True);print('BRAIN_GARDEN_RENDERED',flush=True)
camera.location=(-3050,-2050,2590);target=Vector((-120,-200,660));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=3150
scene.render.filepath=str(ART/'Brain-tree-craft.png');bpy.ops.render.render(write_still=True);print('BRAIN_TREE_CRAFT_RENDERED',flush=True)
