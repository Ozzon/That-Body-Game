"""Author C11's complete garden as editable meshes with fitted construction.

The previous playable package is immutable. This writes a separate source scene.
"""
import bpy,bmesh,numpy as np,math,json,sys,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,merge,sweep,block,leaf,ellipsoid,collection
from organ_math import curve
from brain_craft_layout import TREE,LOTUS,SHORTCUT
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C11';EXPORT=ART/'ExportC11';EXPORT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C10.blend'))
old=json.loads((ART/'asset-manifest.json').read_text());manifest=[];rng=random.Random(1129)
# Retain the tailored editable costume rig, but replace the complete environment
# and every thought with this candidate's geometry and material system.
for o in list(bpy.data.objects):
    if o.type=='MESH' and not o.name.startswith('SM_Craft_Attention'):bpy.data.objects.remove(o,do_unlink=True)
for e in old:
    if e['key'].startswith('Attention'):manifest.append(e)
env=collection('C11 | Living terraced garden');hero=collection('C11 | Trees and ecology');cast=collection('C11 | Thought creatures');arch=collection('C11 | Fitted garden architecture')
M={}
palette={
'Turf':((.12,.225,.068),.89),'Paving':((.43,.39,.31),.70),'Coping':((.57,.49,.35),.57),'Masonry':((.29,.29,.26),.82),
'Tissue':((.48,.17,.20),.43),'Grass':((.13,.30,.055),.70),'LeafGreen':((.10,.28,.075),.48),'LeafGold':((.66,.42,.055),.40),
'PetalPink':((.55,.16,.32),.45),'PetalIvory':((.74,.68,.36),.44),'BarkWood':((.23,.12,.045),.77),'BarkRidge':((.34,.21,.075),.68),
'Sand':((.54,.52,.40),.91),'WaterBlue':((.016,.20,.25),.15),'WaterFoam':((.33,.74,.69),.34),'PortalDawn':((.78,.38,.075),.27),
'PortalSpring':((.06,.54,.54),.27),'PortalMemory':((.34,.13,.56),.27),'RoofTeal':((.035,.17,.18),.39),'ThoughtGold':((.95,.60,.12),.34),
'ThoughtCloud':((.28,.24,.46),.42),'ThoughtWisp':((.25,.58,.64),.25),'ThoughtKnot':((.57,.24,.12),.52),
'FaceInk':((.017,.022,.035),.31),'FaceWhite':((.93,.93,.78),.26),'FaceBlush':((.76,.22,.13),.6)}
for key,(col,rough) in palette.items():
    name='C11_'+key;m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
    vc=n.new('ShaderNodeVertexColor');vc.layer_name='HeartColor';l.new(vc.outputs['Color'],p.inputs['Base Color']);M[key]=m
    if key.startswith('Portal'):l.new(vc.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=1.6
def color(key):return palette[key][0]
def raw(name,v,f,ma,coll=env,c=None):return mesh(name,v,f,c if c is not None else color(ma),coll,M[ma])
def tube(name,p,r,ma,coll=arch,sub=6,sides=16,ridge=0):return sweep(name,p,r,color(ma),coll,M[ma],sides,sub,ridge)
def brick(name,p,s,ma,angle=0,bevel=7,seed=0):return block(name,p,s,np.array(color(ma))*(.9+.15*math.sin(seed*2.77)),arch,M[ma],angle,bevel,seed)
def orb(name,p,s,ma,coll=hero,seed=0,seg=24,rings=16):return ellipsoid(name,p,s,color(ma),coll,M[ma],seed,seg,rings)
def blade(name,p,d,l,w,ma,coll=hero,curl=.2):return leaf(name,p,d,l,w,color(ma),coll,M[ma],curl)
def uv(o):
    if o.data.uv_layers:return
    lay=o.data.uv_layers.new(name='CraftUV')
    for f in o.data.polygons:
        axis=max(range(3),key=lambda k:abs(f.normal[k]));ab=[k for k in range(3) if k!=axis]
        for li in f.loop_indices:
            p=o.data.vertices[o.data.loops[li].vertex_index].co;lay.data[li].uv=(p[ab[0]]/200,p[ab[1]]/200)
def add(o,key,tags=None,spawn=True):
    o.name='SM_Craft_'+key;uv(o);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    manifest.append(dict(name=o.name,key=key,spawn=spawn,tags=tags or [],materials=[m.name for m in o.data.materials]));return o
def finish(parts,key,tags=None,spawn=True):return add(merge(parts,key),key,tags,spawn)
terrain=np.load(DATA/'terrain.npz');hg=terrain['h'];xs=terrain['x'];ys=terrain['y']
def height(x,y):
    a=np.clip((x-xs[0])/14,0,len(xs)-1.001);b=np.clip((y-ys[0])/14,0,len(ys)-1.001);i=int(a);j=int(b);u=a-i;v=b-j
    return float(hg[i,j]*(1-u)*(1-v)+hg[i+1,j]*u*(1-v)+hg[i,j+1]*(1-u)*v+hg[i+1,j+1]*u*v)
# The connected collision surface has real gentle relief, continuous green
# ground cover, and a distinct dark mineral foundation beneath each terrace.
d=np.load(ART/'Source/C09/Ground.npz');v=d['v'];c=np.tile(color('Turf'),(len(v),1));variation=.91+.09*np.sin(v[:,0]/311)*np.cos(v[:,1]/227);c*=variation[:,None]
o=raw('Evergreen sculpted terraces',v,d['f'],'Turf',c=c);o.data.materials.append(M['Masonry'])
for f in o.data.polygons:
    if f.normal.z<.4:f.material_index=1
add(o,'Ground',['Ground'])
d=np.load(ART/'Source/C09/CrossingBeds.npz');add(raw('Continuous supported bridges',d['v'],d['f'],'Masonry'),'CrossingBeds',['Ground'])
# Fitted closed flagstones: real worn bevel, shallow crown, correct top winding.
V=[];F=[];C=[]
for idx,s in enumerate(json.loads((DATA/'paving.json').read_text())):
    xy=np.array(s['xy']);z=np.array(s['z']);ct=xy.mean(0);n=len(xy);base=len(V)
    for layer in range(4):
        q=xy if layer<2 else ct+(xy-ct)*(.94 if layer==2 else .90);zz=z+[-14,-4,0,1.2][layer]
        for p,zz0 in zip(q,zz):V.append((*p,zz0));C.append(np.array(color('Paving'))*s['tone']*(.89 if layer<2 else 1))
    for layer in range(3):
        for i in range(n):j=(i+1)%n;F.append((base+layer*n+i,base+layer*n+j,base+(layer+1)*n+j,base+(layer+1)*n+i))
    F.append(tuple(base+3*n+i for i in range(n)));F.append(tuple(base+i for i in reversed(range(n))))
add(raw('Hand-fitted worn flagstones',V,F,'Paving',c=C),'Paving',['Ground'])
# Sculptural masonry courses, shorter than a character near the walkway.
walls=[];coping=[]
for i,e in enumerate(json.loads((DATA/'masonry.json').read_text())):
    x,y,z=e['p'];a=e['angle'];depth=150 if e['kind']=='stream' else min(450,z+220)
    for row in range(int(depth/80)):
        off=24 if row%2 else -24;walls.append(brick('Garden retaining course',(x+math.cos(a)*off,y+math.sin(a)*off,z-row*77-48),(103,74,78),'Masonry',a,9,i+row))
    coping.append(brick('Rolled coping edge',(x,y,z+3),(106,89,30),'Coping',a,8,i))
finish(walls,'RetainingWalls',['Occluder']);finish(coping,'TerraceCoping',[])
# Rim tissue remains outside the traversal network, sculpted as one continuous
# convoluted mantle. Split quadrants only for character occlusion fading.
d=np.load(DATA/'CortexShell.npz');v=d['v'];f=d['f'];c=d['c'];cent=v[f].mean(1)
for ix in [-1,1]:
    for iy in [-1,1]:
        ff=f[(cent[:,0]*ix>=0)&(cent[:,1]*iy>=0)];used,inv=np.unique(ff,return_inverse=True);o=raw('Sculpted brain mantle',v[used],inv.reshape(-1,4),'Tissue',c=c[used]);add(o,f'Cortex{ix}{iy}',['Occluder'])
print('C11_ARCHITECTURE_READY',flush=True)
# Three complete, different gateways. Each local construction is transformed
# exactly once from this source-of-truth layout, including its luminous surface.
for idx,e in enumerate(json.loads((DATA/'portals.json').read_text())):
    origin=np.array(e['p']);a=math.radians(e['yaw']);ma='Portal'+e['color'];parts=[]
    # Rounded arch voussoirs with backed side faces; a real open landing.
    for side in [-1,1]:
        for row in range(3):parts.append(brick('Portal tapered jamb',(side*182,0,45+row*83),(93,130,86),'Masonry',0,13,idx+row))
    for i in range(15):
        t=(i+.5)*math.pi/15;parts.append(brick('Portal radial keystone',(182*math.cos(t),0,252+178*math.sin(t)),(84,132,93),'Coping',0,11,i))
        o=parts[-1];pivot=Vector((182*math.cos(t),0,252+178*math.sin(t)))
        # Fitted wedge orientation in the vertical arch plane.
        for vert in o.data.vertices:
            p=vert.co-pivot;vert.co=pivot+Vector((p.x*math.cos(t-math.pi/2)-p.z*math.sin(t-math.pi/2),p.y,p.x*math.sin(t-math.pi/2)+p.z*math.cos(t-math.pi/2)))
    for side in [-1,1]:parts.append(tube('Portal organic rooted frame',[(side*238,70,-25),(side*236,58,170),(side*199,61,350),(side*72,70,465)],[35,29,21,2],'BarkWood',sub=8,sides=18,ridge=.035))
    parts.append(brick('Portal threshold',(0,-78,8),(326,120,28),'Coping',0,9,idx))
    frame=merge(parts,'Portal complete frame')
    verts=[(0,41,203)];faces=[]
    for i in range(97):
        t=i*math.tau/96;verts.append((149*math.cos(t),42,203+195*math.sin(t)))
        if i:faces.append((0,i+1,i))
    glow=raw('Portal shimmering interior',verts,faces,ma,arch)
    for o,key,tags in [(frame,'Nest'+str(idx),['Interactive']),(glow,'NestGlow'+str(idx),['Interactive','Glow'])]:
        for p in o.data.vertices:
            x,y,z=p.co;p.co=(origin[0]+x*math.cos(a)-y*math.sin(a),origin[1]+x*math.sin(a)+y*math.cos(a),origin[2]+z)
        add(o,key,tags)
# Carved round basin helper and continuous water sheets follow physical banks.
def basin(key,p,r,hdrop,ma='WaterBlue'):
    x,y,z=p;parts=[]
    for row in range(max(1,int(hdrop/72))):
        for i in range(32):
            a=math.tau*(i+.5+(row%2)*.5)/32;parts.append(brick('Basin curved stone course',(x+r*math.cos(a),y+r*math.sin(a),z-row*70-28),(2*math.pi*r/32+3,63,73),'Masonry',a+math.pi/2,10,i+row))
    for i in range(32):
        a=math.tau*(i+.5)/32;parts.append(brick('Basin fitted rim',(x+r*math.cos(a),y+r*math.sin(a),z+13),(2*math.pi*r/32+2,88,35),'Coping',a+math.pi/2,9,i))
    finish(parts,key+'Bank',['Interactive']);V=[(x,y,z-10)];F=[]
    for i in range(129):
        a=i*math.tau/128;V.append((x+(r-26)*math.cos(a),y+(r-26)*math.sin(a),z-10))
        if i:F.append((0,i,i+1))
    add(raw('Reflective contained water',V,F,ma),key+'Water',['Water'])
basin('UpperSpring',(-1680,1780,1400),245,360);basin('MiddleSpring',(-1680,1280,1200),265,180)
d=np.load(ART/'Source/Water.npz');add(raw('Contained stream and release pool',d['v'],d['f'],'WaterBlue'),'Water',['Water'])
for idx,(x,y,z,run,drop,width) in enumerate([(-1680,1540,1388,140,195,125),(-1680,1025,1188,120,130,155)]):
    V=[];F=[]
    for i in range(34):
        t=i/33
        for j in range(19):
            u=j/18;V.append((x+(u-.5)*width,y-run*t,z-drop*(t*t*(3-2*t))+math.sin(u*math.pi*9)*1.5))
            if i and j:q=(i-1)*19+j-1;F.append((q,q+1,q+20,q+19))
    add(raw('Arcing sheet waterfall',V,F,'WaterBlue'),f'Cascade{idx}',['Water'])
    foam=[]
    for k in range(8):
        a=k*2.399;foam.append(orb('Foam at impact',(x+math.cos(a)*width*.35,y-run+math.sin(a)*25,z-drop+4),(20,12,2),'WaterFoam',seg=16,rings=10))
    finish(foam,f'CascadeFoam{idx}')
# Substantial lotus architecture, petals separate for the gameplay response.
lx,ly,lz=LOTUS;plinth=[]
for row,(r,zz) in enumerate([(240,13),(200,35),(145,56)]):
    for i in range(24):
        a=(i+.5)*math.tau/24;plinth.append(brick('Lotus carved concentric step',(lx+r*math.cos(a),ly+r*math.sin(a),lz+zz),(r*math.tau/24+4,84,27),'Coping',a+math.pi/2,8,i+row))
finish(plinth,'LotusPlinth',['Interactive'])
add(orb('Lotus seed pearl',(lx,ly,lz+114),(49,49,63),'ThoughtWisp'),'LotusSeed',['Interactive'])
for i in range(9):
    a=i*math.tau/9;pts=[];o=blade('Sculpted lotus petal',(0,0,0),(math.cos(a),math.sin(a),.12),165,58,'PetalPink',cast,.43);add(o,'LotusPetal'+str(i),[],False)
# A broad raked sand bed belongs to the entrance garden, offset from the walking
# line, with stones in a three-part composition and modeled combed ridges.
cx,cy=-1920,-2240;V=[];F=[]
for i in range(121):
    x=-1+2*i/120
    for j in range(101):
        y=-1+2*j/100;xx=cx+x*285;yy=cy+y*math.sqrt(max(0,1-x*x))*230;r=math.hypot((xx-cx)*.8,yy-cy)
        V.append((xx,yy,height(xx,yy)+6+1.8*math.cos(r*.39)))
        if i and j:q=(i-1)*101+j-1;F.append((q,q+101,q+102,q+1))
add(raw('Combed entrance sand bed',V,F,'Sand'),'RakedSand',['Ground']);stones=[]
for x,y,s in [(cx-85,cy+20,1),(cx-25,cy+50,.64),(cx-55,cy-38,.42)]:stones.append(orb('Contemplation grouping',(x,y,height(x,y)+29*s),(49*s,35*s,64*s),'Masonry',seed=int(x),seg=32,rings=24))
finish(stones,'SandGardenStones')
# An airy awareness tree. Branches have taper, twists and actual bark flutes;
# leaf clusters sit on terminal branch fans, retaining light between crowns.
def tree(key,origin,scale,leafmat,branch_count=7):
    origin=np.array(origin);wood=[];leaves=[];ridges=[]
    def point(p):return tuple(origin+np.array(p)*scale)
    trunk=[(0,0,0),(-24,8,155),(32,-18,350),(-12,0,515),(20,18,680)]
    wood.append(tube('Awareness sculpted trunk',[point(p) for p in trunk],[98*scale,79*scale,57*scale,39*scale,8*scale],'BarkWood',hero,sub=12,sides=32,ridge=.055))
    for k in range(11):
        a=k*math.tau/11;pts=[point((math.cos(a)*r+cx,math.sin(a)*r+cy,z)) for cx,cy,z,r in [(0,0,7,105),(-24,8,155,80),(32,-18,350,57),(-12,0,500,35)]];ridges.append(tube('Sculpted bark ridge',pts,[8*scale,5*scale,2*scale,.6*scale],'BarkRidge',hero,sub=9,sides=8))
    for k in range(8):
        a=k*2.399;wood.append(tube('Root flare',[point((math.cos(a)*310,math.sin(a)*250,4)),point((math.cos(a)*165,math.sin(a)*145,19)),point((math.cos(a)*74,math.sin(a)*74,85))],[2*scale,26*scale,39*scale],'BarkWood',hero,sub=8,sides=20,ridge=.055))
    for k in range(branch_count):
        a=k*2.399+.2;end=np.array((math.cos(a)*(335+k%3*33),math.sin(a)*(330+k%3*25),560+(k%3)*105));start=np.array((10,0,260+(k%3)*75));mid=(start+end)/2+np.array((20,-15,-15))
        wood.append(tube('Reaching bough',[point(start),point(mid),point(end)],[45*scale,27*scale,4*scale],'BarkWood',hero,sub=10,sides=24,ridge=.045))
        for twig in range(7):
            aa=a+(twig-3)*.22;tip=end+np.array((math.cos(aa)*145,math.sin(aa)*145,30+(twig%3)*30));fork=end-np.array((math.cos(a)*70,math.sin(a)*70,35))
            wood.append(tube('Terminal fan twig',[point(fork),point((fork+tip)/2),point(tip)],[9*scale,4*scale,.3*scale],'BarkWood',hero,sub=5,sides=10))
            for j in range(17):
                angle=j*2.399+twig;p=tip+np.array((math.cos(angle)*(30+j*4),math.sin(angle)*(30+j*4),math.sin(j*2)*26));direction=(math.cos(angle),math.sin(angle),.25+float(j%3)*.22);leaves.append(blade('Individual curved garden leaf',point(p),direction,(47+j%4*8)*scale,(19+j%4*3)*scale,leafmat,hero,.2))
    finish(wood+ ridges,key+'Wood',['Interactive']);finish(leaves,key+'Leaves',['Occluder','Foliage'])
tree('Tree',(0,90,520),1.16,'LeafGold',8)
tree('SpringCherry',(-1990,1890,1100),.60,'PetalPink',6)
tree('MemoryWillow',(1480,1980,950),.57,'LeafGreen',6)
tree('ArrivalCherry',(-2200,-1650,height(-2200,-1650)),.40,'PetalPink',5)
tree('PoolWillow',(2130,-1830,height(2130,-1830)),.43,'LeafGreen',5)
# A low root collar protects the trunk while leaving a broad interaction court.
planter=[]
for i in range(32):
    a=(i+.5)*math.tau/32;planter.append(brick('Tree root garden collar',(300*math.cos(a),90+300*math.sin(a),535),(64,68,38),'Coping',a+math.pi/2,8,i))
finish(planter,'TreePlanter',['Interactive'])
print('C11_LANDMARKS_READY',flush=True)
# Ground cover is rooted mesh foliage, with ordered plant communities rather
# than random tall decorations in movement lanes.
d=np.load(DATA/'planting.npz');buckets={i:[[],[],[]] for i in range(4)};herbs=[];flowers=[]
for idx,(p,sc,a) in enumerate(zip(d['p'],d['scale'],d['angle'])):
    bucket=int(p[0]>0)+2*int(p[1]>0);V,F,C=buckets[bucket]
    for k in range(12):
        aa=a+k*2.399;pos=p+np.array((math.cos(aa)*18*sc,math.sin(aa)*18*sc,7));side=np.array((-math.sin(aa),math.cos(aa),0));axis=np.array((math.cos(aa),math.sin(aa),0));high=(27+k%4*8)*sc;width=(5+k%3)*sc;base=len(V)
        for j in range(5):
            t=j/4;center=pos+axis*(t*t*high*.48)+np.array((0,0,t*high));ww=width*(1-t)**.7
            for sign in [-1,0,1]:V.append(center+side*ww*sign-np.array((0,0,abs(sign)*ww*.32)));C.append(np.array(color('Grass'))*(.69+.48*t+.07*math.sin(idx)))
            if j:
                for sign in range(2):q=base+(j-1)*3+sign;F.append((q,q+1,q+4,q+3))
    if idx%13==0:
        for k in range(7):
            aa=a+k*2.399;herbs.append(blade('Hosta leaf rosette',p+np.array((0,0,12)),(math.cos(aa),math.sin(aa),.38),59*sc,23*sc,'LeafGreen',hero,.27))
        if idx%39==0:
            for k in range(5):
                aa=a+k*math.tau/5;flowers.append(blade('Garden blossom petal',p+np.array((0,0,55*sc)),(math.cos(aa),math.sin(aa),.3),24*sc,12*sc,'PetalIvory' if p[1]<0 else 'PetalPink',hero,.28))
for i,(V,F,C) in buckets.items():
    o=raw('Rooted grass meadow',V,F,'Grass',c=C)
    # Blend the true folded blade normal with its canopy normal: shaped lighting
    # and coherent foliage shading both survive at the gameplay camera.
    o.data.update();norm=[tuple((vert.normal*.45+Vector((0,0,.55))).normalized()) for vert in o.data.vertices];o.data.normals_split_custom_set_from_vertices(norm)
    uv2=o.data.uv_layers.new(name='RootWeight')
    for li,loop in enumerate(o.data.loops):uv2.data[li].uv=(0,(loop.vertex_index%15)//3/4)
    add(o,'GardenGrass'+str(i),['GroundCover'])
finish(herbs,'GardenPocketLeaves',['Foliage']);finish(flowers,'GardenPocketFlowers',['Foliage'])
# A curved teal-roofed garden shelter on the memory terrace gives it a use and
# silhouette beyond its thought portal. Scale leaves a clear walking frontage.
cx,cy,cz=1200,2040,950;parts=[];roof=[]
for i in range(10):parts.append(brick('Shelter deck plank',(cx-240+i*54,cy,cz+14),(52,350,25),'BarkWood',0,4,i))
for sx in [-1,1]:
    for sy in [-1,1]:parts.append(tube('Carved shelter support',[(cx+sx*238,cy+sy*140,cz),(cx+sx*231,cy+sy*140,cz+200),(cx+sx*242,cy+sy*150,cz+365)],[19,16,22],'BarkWood',sub=7,sides=20))
for sign in [-1,1]:
    for k in range(15):
        x=cx-355+k*51;path=[(x,cy,cz+493),(x,cy+sign*130,cz+462),(x,cy+sign*250,cz+400),(x,cy+sign*325,cz+430)];roof.append(tube('Curved glazed roof tile',path,[28,27,25,22],'RoofTeal',sub=12,sides=16))
parts.append(brick('Sheltered contemplation bench',(cx,cy+80,cz+63),(335,80,24),'BarkWood',0,7,1));finish(parts,'RestShelter',['Interactive']);finish(roof,'RestShelterRoof',['Occluder'])
# Root crossing is modeled as a broad curved walkway with low woven rails.
points=curve(SHORTCUT,24,False);V=[];F=[];edges=[]
for i,p in enumerate(points):
    t=points[min(i+1,len(points)-1)]-points[max(0,i-1)];side=np.array((-t[1],t[0],0));side/=np.linalg.norm(side)
    for j in range(15):
        u=(j/14-.5)*460;V.append(p+side*u+np.array((0,0,14*math.cos(u/230*math.pi/2))))
        if i and j:q=(i-1)*15+j-1;F.append((q,q+15,q+16,q+1))
add(raw('Broad root return crossing',V,F,'BarkWood'),'RootBridge',['Ground','Shortcut'])
for sign in [-1,1]:
    pts=[]
    for i,p in enumerate(points):
        t=points[min(i+1,len(points)-1)]-points[max(0,i-1)];side=np.array((-t[1],t[0],0));side/=np.linalg.norm(side);pts.append(p+side*sign*230+np.array((0,0,43)))
    edges.append(tube('Living root balustrade',pts,[27,34,27],'BarkRidge',sub=2,sides=16,ridge=.03))
finish(edges,'RootBridgeEdges',['Shortcut'])
# Four expressive thought bodies. Rounded stars, coherent soft clouds, a seed
# spirit and woven knot each have a different silhouette and PBR surface.
for kind,key,ma in [(0,'ThoughtStar','ThoughtGold'),(1,'ThoughtCloud','ThoughtCloud'),(2,'ThoughtWisp','ThoughtWisp')]:
    V=[];F=[];C=[];rows=48;cols=120
    for i in range(rows+1):
        lat=math.pi*i/rows
        for j in range(cols):
            a=math.tau*j/cols;ring=math.sin(lat)
            if kind==0:r=43+15*math.cos(5*a-math.pi/2)*ring**2;x=25*math.cos(lat);y=r*ring*math.cos(a);z=r*ring*math.sin(a)
            elif kind==1:r=1+.14*math.cos(a*3+.4)*ring**2+.065*math.sin(a*7)*ring;x=43*math.cos(lat)*r;y=70*ring*math.cos(a)*r;z=48*ring*math.sin(a)*r+8*ring
            else:r=1+.06*math.cos(a*3);x=26*math.cos(lat);y=32*ring*math.cos(a)*r;z=48*ring*math.sin(a)+17*(max(0,math.cos(lat)))**3
            V.append((x,y,z));C.append(np.array(color(ma))*(.86+.14*(z+70)/140))
            if i<rows:q=i*cols+j;n=i*cols+(j+1)%cols;F.append((q,n,n+cols,q+cols))
    add(raw('Sculpted thought creature',V,F,ma,cast,C),key,[],False)
knot=[]
for loop in range(3):
    a=loop*math.tau/3;pts=[]
    for t in np.linspace(0,math.tau,161):
        x=37*math.cos(t);y=28*math.sin(t);z=13*math.sin(2*t);pts.append((x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),z))
    knot.append(tube('Over-under thought knot',pts,[9,9,9],'ThoughtKnot',cast,sub=2,sides=16,ridge=.025))
finish(knot,'ThoughtKnot',[],False)
for variant,x,y,z in [('Bright',26,13,4),('Cloud',43,18,0),('Wisp',26,10,4),('Knot',27,11,1)]:
    parts=[]
    for side in [-1,1]:
        parts.append(orb('Thought eye',(x,side*y,z),(2.5,4.4,6.2),'FaceInk',cast,seg=24,rings=16));parts.append(orb('Eye catchlight',(x+2.4,side*y-1,z+2),(1.2,1.2,1.6),'FaceWhite',cast,seg=16,rings=12))
        parts.append(orb('Soft cheek',(x-1,side*(y+10),z-10),(1.9,5.4,2.8),'FaceBlush',cast,seg=16,rings=12))
    smile=[(x+1,10*math.sin(t),z-13-3*math.cos(t)) for t in np.linspace(-.7,.7,17)];parts.append(tube('Little contented mouth',smile,[1,1,1],'FaceInk',cast,sub=2,sides=8));finish(parts,'ThoughtFace'+variant,[],False)
# Bring the costume meshes into the same material language. Retain tailored
# seams and thickness while repairing all outward normals before export.
for e in manifest:
    if e['key'].startswith('Attention'):
        o=bpy.data.objects[e['name']];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
# Close thin authored shells without inflating or remeshing their silhouettes.
for e in manifest:
    o=bpy.data.objects[e['name']]
    if e['key'] in ['RootBridge','RestShelterRoof']:
        solid=o.modifiers.new('Authored thickness','SOLIDIFY');solid.thickness=14 if e['key']=='RootBridge' else 4;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=solid.name)
    uv(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    e['materials']=[m.name for m in o.data.materials]
(DATA/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(DATA/'materials.json').write_text(json.dumps({k:dict(color=v[0],roughness=v[1]) for k,v in palette.items()},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));print('C11_WORLD_AUTHORED',len(manifest),flush=True)
