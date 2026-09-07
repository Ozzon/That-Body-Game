"""Editable C06 scene: incised cortex, fitted terraces, crafted props and cast.
Run with Blender 5.1. Units are centimeters to match Unreal.
"""
import bpy,bmesh,sys,json,math,random,numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import collection,mesh,merge,sweep,leaf,block,ellipsoid
from brain_craft_layout import *
ART=ROOT/'Art/BrainCraft';EXPORT=ART/'Export';EXPORT.mkdir(parents=True,exist_ok=True);TEX=ART/'Textures'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
env=collection('01 | Sculpted hemisphere topology');stone=collection('02 | Fitted terraces and crossings');hero=collection('03 | Awareness tree');props=collection('04 | Thought ecology');cast=collection('05 | Attention and thoughts');stage=collection('06 | Review lighting')
M={};manifest=[];rng=random.Random(63)

def mat(name,c1,c2,rough=.7,emission=0,scale=7,bump=.12):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=.7
    coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['UV'],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.name='SurfacePigment';ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*c1,1);ramp.color_ramp.elements[1].position=.83;ramp.color_ramp.elements[1].color=(*c2,1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
    p.inputs['Roughness'].default_value=rough
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=scale*6;fine.inputs['Detail'].default_value=2;l.new(coord.outputs['UV'],fine.inputs['Vector'])
    bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.17;bn.inputs['Distance'].default_value=bump*.018;l.new(fine.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs['Normal'],p.inputs['Normal'])
    if emission:l.new(ramp.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=emission
    M[name]=m;return m

mat('Cortex',(.34,.10,.145),(.62,.255,.29),.48,scale=9,bump=.2)
p=M['Cortex'].node_tree.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.08
im=M['Cortex'].node_tree.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(TEX/'T_Cortex_Painted_BaseColor.png'));M['Cortex'].node_tree.links.new(im.outputs['Color'],p.inputs['Base Color'])
mat('Stone',(.21,.155,.235),(.49,.37,.40),.79,scale=8,bump=.55)
mat('Trim',(.39,.23,.13),(.72,.52,.29),.68,scale=12,bump=.3)
mat('Moss',(.055,.105,.055),(.18,.265,.095),.96,scale=19,bump=.65)
pm=M['Moss'].node_tree.nodes.get('Principled BSDF');im=M['Moss'].node_tree.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(TEX/'T_Moss_Painted_BaseColor.png'));M['Moss'].node_tree.links.new(im.outputs['Color'],pm.inputs['Base Color'])
mat('Earth',(.26,.175,.10),(.46,.34,.205),.94,scale=42,bump=.32)
mat('Bark',(.12,.055,.019),(.42,.245,.070),.78,scale=8,bump=.7)
# Directional bark grain is in UV space, aligned down each branch.
nm=M['Bark'].node_tree.nodes;lk=M['Bark'].node_tree.links;mapping=nm.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(18,1.6,1)
uv=next(n for n in nm if n.type=='TEX_COORD');lk.new(uv.outputs['UV'],mapping.inputs[0])
for n in nm:
    if n.type=='TEX_NOISE':lk.new(mapping.outputs[0],n.inputs['Vector'])
mat('Leaf',(.50,.23,.025),(.96,.64,.14),.49,.12,scale=16,bump=.12)
mat('Light',(.9,.48,.085),(1,.85,.32),.35,3,scale=5,bump=.01)
mat('Water',(.018,.115,.18),(.055,.38,.43),.19,.15,scale=9,bump=.06)
mat('Foam',(.30,.62,.68),(.63,.91,.88),.55,.3,scale=9,bump=.015)
mat('Violet',(.12,.045,.22),(.27,.13,.43),.56,.14,scale=8,bump=.1)
mat('Current',(.12,.05,.48),(.38,.21,.95),.4,2.3,scale=5,bump=.01)
mat('Sage',(.085,.15,.135),(.245,.335,.24),.85,scale=38,bump=.04)
mat('Linen',(.45,.345,.17),(.74,.65,.42),.89,scale=50,bump=.04)
mat('Leather',(.09,.065,.045),(.23,.16,.09),.76,scale=18,bump=.03)
mat('Face',(.8,.39,.10),(1,.77,.32),.5,.6,scale=8,bump=.01)
mat('Ink',(.015,.009,.02),(.045,.025,.065),.45,scale=12,bump=.01)
mat('Fern',(.035,.115,.065),(.20,.37,.12),.7,scale=9,bump=.05)
mat('Blossom',(.23,.055,.28),(.63,.22,.46),.62,scale=12,bump=.04)

# Purpose-made painted material atlas. UV remapping stays in material nodes;
# the generated source bitmap is preserved without raster editing.
atlas_image=bpy.data.images.load(str(TEX/'T_C07_Painted_Atlas.png'))
for key,offset in [('Cortex',(0,.5,0)),('Stone',(.5,.5,0)),('Bark',(0,0,0)),('Sage',(.5,0,0))]:
    m=M[key];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');coord=n.new('ShaderNodeTexCoord');fract=n.new('ShaderNodeVectorMath');fract.operation='FRACTION';l.new(coord.outputs['UV'],fract.inputs[0]);scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.49;l.new(fract.outputs[0],scale.inputs[0]);addv=n.new('ShaderNodeVectorMath');addv.operation='ADD';addv.inputs[1].default_value=tuple(x+.005 if i<2 else x for i,x in enumerate(offset));l.new(scale.outputs[0],addv.inputs[0]);im=n.new('ShaderNodeTexImage');im.image=atlas_image;l.new(addv.outputs[0],im.inputs['Vector']);l.new(im.outputs['Color'],p.inputs['Base Color'])
    if key=='Sage':
        tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.52,.80,.84,1);l.new(im.outputs['Color'],tint.inputs[1]);l.new(tint.outputs[0],p.inputs['Base Color'])
    p.inputs['Roughness'].default_value={'Cortex':.62,'Stone':.78,'Bark':.67,'Sage':.89}[key]

def uv_project(o,scale=300):
    me=o.data;uv=me.uv_layers.new(name='CraftUV')
    for poly in me.polygons:
        norm=poly.normal;axis=max(range(3),key=lambda k:abs(norm[k]));ab=[k for k in range(3) if k!=axis]
        for k in poly.loop_indices:
            v=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(v[ab[0]]/scale,v[ab[1]]/scale)

def add(o,key,spawn=True,tags=None):
    o.name='SM_Craft_'+key
    if not o.data.uv_layers:uv_project(o,280 if key.startswith('Attention') else 380)
    manifest.append(dict(name=o.name,key=key,spawn=spawn,tags=tags or [],materials=[m.name for m in o.data.materials],object=o));return o

def raw(name,v,f,ma,coll=props):return mesh(name,v,f,(1,1,1),coll,M[ma])
def tube(name,pts,rs,ma,coll=props,sides=16,sub=8,ridge=0):return sweep(name,pts,rs,(1,1,1),coll,M[ma],sides,sub,ridge)
def orb(name,p,s,ma,coll=props,seg=24):return ellipsoid(name,p,s,(1,1,1),coll,M[ma],0,seg,16)

# The source meshes have real cortex topography and exposed support faces.
for file in sorted((ART/'Source').glob('*.npz')):
    if file.stem=='navigation':continue
    d=np.load(file);key=file.stem;ma='Cortex' if key.startswith('Cortex') else 'Moss' if key=='Ground' else 'Earth' if key=='EarthPath' else 'Water'
    o=raw(key,d['v'],d['f'],ma,env)
    if key=='Ground':
        o.data.materials.append(M['Stone'])
        for poly in o.data.polygons:
            if poly.normal.z<.45:poly.material_index=1
    if key=='EarthPath' and 'blend' in d:
        b=d['blend'];o.data.color_attributes['HeartColor'].data.foreach_set('color',np.column_stack([b,b,b,np.ones(len(b))]).ravel())
    if key.startswith('Cortex'):
        # Relax boundary stair steps on the authored quad surface; no inflated tubes.
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
        mod=o.modifiers.new('Cortex surface polish','SMOOTH');mod.factor=.35;mod.iterations=2
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    add(o,key,tags=['Ground'] if key in ['Ground','EarthPath'] else ['Water'] if key=='Water' else ['Occluder'])

parts=[]
for i,s in enumerate(json.loads((ART/'Source/paving.json').read_text())):
    xy=np.array(s['xy']);z=np.array(s['z']);c=xy.mean(axis=0);n=len(xy);v=[];f=[]
    for inset,dz in [(0,-17),(0,-3),(.035,2)]:
        for j,p in enumerate(xy):q=p+(c-p)*inset;v.append((q[0],q[1],z[j]+dz))
    for row in range(2):
        for j in range(n):k=(j+1)%n;f.append((row*n+j,row*n+k,(row+1)*n+k,(row+1)*n+j))
    f.append(tuple(range(2*n,3*n)));parts.append(raw('Fitted paving stone',v,f,'Stone',stone))
add(merge(parts,'Paving'),'Paving',tags=['Ground'])

def masonry_ring(center,radius,count,height=60,width=75,ma='Trim'):
    parts=[];x,y,z=center
    for i in range(count):
        a=i*math.tau/count;pts=[]
        for r,zz in [(radius-width/2,z),(radius+width/2,z),(radius-width/2,z+height),(radius+width/2,z+height)]:
            for t in [a+.012,a+math.tau/count-.012]:pts.append((x+r*math.cos(t),y+r*math.sin(t),zz))
        o=raw('Fitted radial coping',pts,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],ma,stone)
        mod=o.modifiers.new('Worn rolled edges','BEVEL');mod.width=5;mod.segments=3;parts.append(o)
    return parts

add(merge(masonry_ring((TREE[0],TREE[1],TREE[2]+1),340,25,40,54),'Tree planter'),'TreePlanter',tags=['Interactive'])
add(merge(masonry_ring((1580,-1390,335),270,22,34,64),'Lotus coping'),'LotusCoping',tags=['Ground'])

# Deliberate low terrace parapets. Gaps are cut wherever an actual path crosses.
parapets=[]
for district in DISTRICTS:
    cx,cy,zz=district['p'];rx,ry=district['r'];steps=int(math.tau*(rx+ry)/2/140)
    for k in range(steps):
        a=k*math.tau/steps;x=cx+rx*math.cos(a);y=cy+ry*math.sin(a);dd,_,rd=fields(x,y)
        # Test connection clearance a little outside the district, excluding court ring.
        conn=1e9
        for r in ROUTES:conn=min(conn,float(distance(x,y,curve(r['points'],8,False),False)-r['width']/2))
        if conn<105 or (district['key']=='Awareness') or (district['key']=='Arrival' and math.sin(a)<-.55):continue
        # Low fitted bank edges only where water needs containment.
        if district['key'] not in ['Spring','Release']:continue
        for row in range(1):parapets.append(block('Retaining voussoir',(x,y,zz+21+row*42),(135,65,41),(1,1,1),stone,M['Stone'],a+math.pi/2,9,k))
add(merge(parapets,'Garden retaining walls'),'RetainingWalls',tags=['Occluder'])

exec(compile((ROOT/'Tools/craft_terrace_details.py').read_text(),str(ROOT/'Tools/craft_terrace_details.py'),'exec'))

# Rooted, asymmetrical awareness tree. Each major branch is an authored gesture.
trunks=[];tx,ty,tz=TREE
for i in range(3):
    a=i*math.tau/3
    pts=[(tx+85*math.cos(a),ty+85*math.sin(a),tz),(tx+50*math.cos(a+.8),ty+50*math.sin(a+.8),tz+270),(tx+55*math.cos(a+2),ty+55*math.sin(a+2),tz+550),(tx+130*math.cos(a+2.6),ty+130*math.sin(a+2.6),tz+770)]
    trunks.append(tube('Twisted trunk',pts,[95,89,63,20],'Bark',hero,32,12,.045))
for i in range(9):
    a=i*math.tau/9+.12;dx,dy=math.cos(a),math.sin(a)
    trunks.append(tube('Sculpted spreading root',[(tx+35*dx,ty+35*dy,tz+240),(tx+160*dx,ty+160*dy,tz+65),(tx+260*dx+20,ty+260*dy,tz+22),(tx+330*dx,ty+330*dy,tz+12)],[60,50,24,3],'Bark',hero,22,9,.06))
branchends=[]
for i in range(5):
    a=i*2.4;end=np.array((240*math.cos(a),ty+240*math.sin(a),tz+1200+(i%2)*90))
    trunks.append(tube('Upper crown leader',[(0,ty,tz+570),(105*math.cos(a-.2),ty+105*math.sin(a-.2),tz+890),end],[47,31,6],'Bark',hero,22,10,.06));branchends.append(end)
for i in range(11):
    a=i*2.4;reach=460+(i%3)*85;z0=tz+460+(i%4)*80;end=np.array((reach*math.cos(a),ty+reach*math.sin(a),tz+960+(i%3)*85))
    mid=np.array((reach*.6*math.cos(a-.23),ty+reach*.6*math.sin(a-.23),z0+170))
    trunks.append(tube('Directional crown limb',[(0,ty,z0),mid,end],[53,35,8],'Bark',hero,22,10,.05));branchends.append(end)
    for sign in [-1,1]:
        b=a+sign*.45;tip=end+np.array((130*math.cos(b),130*math.sin(b),45))
        trunks.append(tube('Forked crown twig',[mid,mid*.25+end*.75,tip],[20,12,2],'Bark',hero,14,7,.035));branchends.append(tip)
o=merge(trunks,'Fused awareness wood');bpy.context.view_layer.objects.active=o
rem=o.modifiers.new('Fused roots and branch shoulders','REMESH');rem.mode='VOXEL';rem.voxel_size=5.5;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
smooth=o.modifiers.new('Sculpt polish','SMOOTH');smooth.factor=.5;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name)
add(o,'TreeWood',tags=['Interactive'])
fol=[];veins=[]
for i,end in enumerate(branchends):
    for j in range(38):
        a=j*2.399+i*.65;spread=math.sqrt(j/38)*150;start=end+np.array((math.cos(a)*spread,math.sin(a)*spread,(j%7)*16-40));di=np.array((math.cos(a+.3),math.sin(a+.3),.18+(j%3)*.24));length=61+(i%4)*11
        fol.append(leaf('Sculpted pointed leaf',start,di,length,24,(1,1,1),hero,M['Leaf'],.28))
        d=di/np.linalg.norm(di);veins.append(tube('Leaf midrib',[start,start+d*length*.55+np.array((0,0,15)),start+d*length*.93],[2.3,1.8,.2],'Trim',hero,6,4))
add(merge(fol,'Golden airy canopy'),'TreeLeaves',tags=['Occluder','Foliage']);add(merge(veins,'Leaf veins'),'LeafVeins',tags=['Occluder','Foliage'])
glow=[]
for i in range(5):
    a=i*math.tau/5;pts=[]
    for k in range(18):
        z=tz+35+k*42;r=110-k*3;ang=a+k*.16;pts.append((r*math.cos(ang),ty+r*math.sin(ang),z))
    glow.append(tube('Inlaid root light',pts,[3,4,2],'Light',hero,8,3))
add(merge(glow,'Tree light channels'),'TreeLight',tags=['Interactive','Glow'])

# Nest portals are structural, open-centered funnels with radial ridges.
for i,(x,y,z) in enumerate(NESTS):
    v=[];f=[];rings=16;sides=64
    for j in range(rings):
        t=j/(rings-1);r=105+95*t;yy=y+55-130*t
        for k in range(sides):
            a=k*math.tau/sides;rr=r+7*math.sin(11*a+t*3)*t;v.append((x+rr*math.cos(a),yy,z+185+rr*math.sin(a)))
            if j:q=(j-1)*sides+k;w0=(j-1)*sides+(k+1)%sides;f.append((q,w0,w0+sides,q+sides))
    add(raw('Thought nest',v,f,'Violet'),'Nest%d'%i,tags=['Interactive'])
    parts=[]
    for k in range(4):
        aa=k*1.65;pts=[(x+(45+t*9)*math.cos(aa+t*.35),y-83,z+185+(45+t*9)*math.sin(aa+t*.35)) for t in range(13)]
        parts.append(tube('Nest spiral energy',pts,[2,3,1],'Current',props,8,3))
    add(merge(parts,'Nest energy'),'NestGlow%d'%i,tags=['Interactive','Glow'])

# Lotus petals open separately in play; each retains an actual pivot at its root.
x,y,z=LOTUS
for i in range(9):
    a=i*math.tau/9;di=(math.cos(a),math.sin(a),.7)
    o=leaf('Focus lotus petal',(0,0,0),di,135,50,(1,1,1),props,M['Current'],.35);add(o,'LotusPetal%d'%i,False)
parts=masonry_ring((x,y,z+36),150,18,38,100,'Stone');add(merge(parts,'Lotus plinth'),'LotusPlinth',tags=['Interactive'])
add(orb('Lotus warm seed',(x,y,z+140),(32,32,50),'Light'),'LotusSeed',tags=['Interactive'])

# Dormant root bridge is a real walkable span, and appears after restoration.
pts=curve(SHORTCUT,18,False);v=[];f=[]
for i,p in enumerate(pts):
    tang=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)];side=np.array((-tang[1],tang[0],0));side/=np.linalg.norm(side)
    for sign in [-1,1]:v.append(tuple(p+side*sign*255))
    if i:q=2*(i-1);f.append((q,q+1,q+3,q+2))
add(raw('Root crossing deck',v,f,'Bark'),'RootBridge',tags=['Shortcut','Ground'])
rails=[]
for sign in [-1,1]:
    q=pts.copy();q[:,0]+=sign*210;q[:,2]+=25;rails.append(tube('Living root handrail',q[::3],[22,32,20],'Bark',props,14,4,.06))
add(merge(rails,'Root bridge edges'),'RootBridgeEdges',tags=['Shortcut'])

# Bounded planted beds: grouped leaf rosettes, never scattered onto the promenade.
plants=[];flowers=[]
for d in DISTRICTS:
    cx,cy,z=d['p'];rx,ry=d['r']
    for i in range(28):
        a=i*2.399;rr=.78+.13*(i%3)/2;x=cx+rx*rr*math.cos(a);y=cy+ry*rr*math.sin(a);_,zz,rd=fields(x,y)
        if rd<85 or water(x,y)<65:continue
        for j in range(5):
            b=j*math.tau/5;plants.append(leaf('Bed leaf',(x,y,float(zz)+4),(math.cos(b),math.sin(b),.6),45+(i%4)*7,18,(1,1,1),props,M['Moss'],.45))
        if i%3==0:
            for j in range(5):
                b=j*math.tau/5;flowers.append(leaf('Neural flower petal',(x,y,float(zz)+44),(math.cos(b),math.sin(b),.28),24,12,(1,1,1),props,M['Current'],.2))
add(merge(plants,'Selected garden beds'),'GardenBeds');add(merge(flowers,'Neural flowers'),'Flowers')

# Planted masses are composed as garden beds, with clear ground around them.
# Each fern has a bending rachis and separate, tapered leaflets. Shrub crowns are
# actual leaves on branching stems rather than opaque spheres.
ferns=[];fern_stems=[];bloom=[]
beds=[(-1420,-2120,180,170),(-1990,1870,190,180),(-1630,2040,180,130),(-1050,1450,160,190),(-535,120,130,210),(560,30,140,200),(1640,2160,220,140),(2060,1760,160,180),(1990,-1820,140,170),(1130,-1650,140,140)]
for bed_id,(bx,by,rx,ry) in enumerate(beds):
    for plant in range(17):
        a=plant*2.399;rr=math.sqrt(plant/17);x=bx+rx*rr*math.cos(a);y=by+ry*rr*math.sin(a);dd,zz,rd=fields(x,y)
        if dd>-55 or water(x,y)<55:continue
        pathdist=min(float(distance(x,y,curve(r['points'],10,False),False)) for r in ROUTES)
        if pathdist<180 or abs(math.hypot(x,y)-780)<172:continue
        z=float(zz)+3
        for frond in range(5):
            a=frond*math.tau/5+plant*.73;length=100+(plant%3)*22;dx,dy=math.cos(a),math.sin(a);points=[]
            for k in range(9):
                t=k/8;points.append((x+dx*length*t,y+dy*length*t,z+math.sin(t*math.pi*.78)*length*.63))
            fern_stems.append(tube('Fern rachis',points,[1.9,1.4,.15],'Fern',props,6,3))
            for k in range(1,8):
                t=k/8;p=points[k]
                for sign in [-1,1]:
                    b=a+sign*1.04;ferns.append(leaf('Tapered fern leaflet',p,(math.cos(b),math.sin(b),.17),36*(1-t*.8),9*(1-t*.5),(1,1,1),props,M['Fern'],.22))
        if plant%4==0:
            for j in range(5):
                aa=j*math.tau/5;bloom.append(leaf('Garden bell petal',(x,y,z+104),(math.cos(aa),math.sin(aa),.7),23,12,(1,1,1),props,M['Blossom'],.5))
if ferns:add(merge(ferns+fern_stems,'Composed fern beds'),'FernBeds')
if bloom:add(merge(bloom,'Flower bed accents'),'GardenBlossoms')

# Arrival has a deliberately built arched threshold, sized for the actual capsule.
gate=[];gx,gy,gz=-1700,-2730,140
for side in [-1,1]:
    for row in range(4):gate.append(block('Gate pier',(gx+side*213,gy,gz+row*63+31),(85,130,62),(1,1,1),stone,M['Stone'],0,7,row))
for i in range(13):
    a=i*math.pi/13;b=(i+1)*math.pi/13;v=[]
    for yy in [gy-65,gy+65]:
        for r in [172,256]:
            for t in [a+.012,b-.012]:v.append((gx+r*math.cos(t),yy,gz+246+r*math.sin(t)))
    gate.append(raw('Arch wedge',v,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],'Trim',stone))
add(merge(gate,'Welcoming threshold'),'ArrivalGate',tags=['Interactive'])

# A sculpted star: five soft tapered lobes, rounded front and back, expressive face.
def star():
    v=[];f=[];sides=100;rows=24
    for j in range(rows+1):
        b=math.pi*j/rows
        for k in range(sides):
            a=k*math.tau/sides;rad=49*(.72+.28*math.cos(5*(a-math.pi/2)));v.append((18*math.cos(b),rad*math.sin(b)*math.cos(a),rad*math.sin(b)*math.sin(a)))
            if j<rows:q=j*sides+k;w=j*sides+(k+1)%sides;f.append((q,w,w+sides,q+sides))
    return raw('Bright thought body',v,f,'Light',cast)
add(star(),'ThoughtStar',False)
# These separate eye meshes also allow blinks and mood shifts in native animation.
for kind,scale in [('Bright',(2.8,4.1,7)),('Cloud',(4,5,8))]:
    fx=46 if kind=='Cloud' else 20
    parts=[orb('Eye',(fx,s*13,5),scale,'Ink',cast,20) for s in [-1,1]]
    for side in [-1,1]:parts.append(orb('Thought eye glint',(fx+scale[0]+.6,side*13-1,8),(1.2,1.5,2.3),'Foam',cast,12))
    parts.append(tube('Little smile',[(fx,-9,-9),(fx+2,0,-14),(fx,9,-9)],[1.3,1.3,1.3],'Ink',cast,8,7))
    add(merge(parts,'Thought face'),'ThoughtFace'+kind,False)
parts=[]
for i in range(12):
    a=i*2.4;z=(i%3-1)*19;parts.append(orb('Cloud lobe',(10*math.cos(i),41*math.cos(a),z),(35,30,31),'Violet',cast))
cloud=merge(parts,'Heavy cloud');bpy.context.view_layer.objects.active=cloud;mod=cloud.modifiers.new('Fused velvety cloud','REMESH');mod.mode='VOXEL';mod.voxel_size=2.2;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name);mod=cloud.modifiers.new('Cloud softness','SMOOTH');mod.factor=.55;mod.iterations=4;bpy.ops.object.modifier_apply(modifier=mod.name);add(cloud,'ThoughtCloud',False)
parts=[]
for i in range(3):
    pts=[]
    for k in range(31):
        t=k*math.tau/30;a=t+i*2.1;r=37+5*math.sin(3*t);pts.append((12*math.sin(t*2+i),r*math.cos(a),r*math.sin(a)))
    parts.append(tube('Persistent thought fold',pts,[8,11,8],'Trim',cast,14,3,.03))
add(merge(parts,'Persistent knot'),'ThoughtKnot',False)
v=[];f=[]
for j in range(33):
    t=j/32;z=-64+t*111;rr=34*math.sin(math.pi*t)**.65*(.35+.65*min(1,t*2.5));cy=22*(1-t)**3
    for k in range(64):
        a=k*math.tau/64;v.append((rr*.64*math.cos(a),cy+rr*math.sin(a),z))
        if j:q=(j-1)*64+k;n=(j-1)*64+(k+1)%64;f.append((q,n,n+64,q+64))
add(raw('Soft floating worry wisp',v,f,'Current',cast),'ThoughtWisp',False)

exec(compile((ROOT/'Tools/craft_garden_details.py').read_text(),str(ROOT/'Tools/craft_garden_details.py'),'exec'))

# The tailored hero is authored independently from environment geometry.
exec(compile((ROOT/'Tools/craft_attention.py').read_text(),str(ROOT/'Tools/craft_attention.py'),'exec'))

print('CRAFT_GEOMETRY_READY',flush=True)
# UV material tiles are baked from the actual source node networks. Rich materials
# remain editable in Blender; Unreal receives albedo and tangent normal textures.
bpy.ops.mesh.primitive_plane_add(size=2,location=(18000,0,0));bake=bpy.context.object
scene.render.engine='CYCLES';scene.cycles.samples=8
for name,m in M.items():
    if '--reuse-textures' in sys.argv and all((TEX/('T_'+name+'_'+k+'.png')).exists() for k in ['BaseColor','Normal']):continue
    bake.data.materials.clear();bake.data.materials.append(m);bpy.ops.object.select_all(action='DESELECT');bake.select_set(True);bpy.context.view_layer.objects.active=bake
    p=m.node_tree.nodes.get('Principled BSDF');target=m.node_tree.nodes.new('ShaderNodeTexImage');target.name='ExportBake'
    for kind in ['BaseColor','Normal']:
        image=bpy.data.images.new('T_'+name+'_'+kind,1024,1024,alpha=False);target.image=image;m.node_tree.nodes.active=target
        if kind=='BaseColor':
            scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True;bpy.ops.object.bake(type='DIFFUSE')
        else:image.colorspace_settings.name='Non-Color';bpy.ops.object.bake(type='NORMAL')
        image.filepath_raw=str(TEX/('T_'+name+'_'+kind+'.png'));image.file_format='PNG';image.save()
    m.node_tree.nodes.remove(target)
    print('CRAFT_MATERIAL_BAKED',name,flush=True)
bpy.data.objects.remove(bake,do_unlink=True)

# The path fades into living ground using authored edge weights, so its geometry
# never creates a hard-edged ribbon of uniform concrete-like color.
em=M['Earth'];nodes=em.node_tree.nodes;links=em.node_tree.links;p=nodes.get('Principled BSDF');pig=nodes.get('SurfacePigment');vc=nodes.new('ShaderNodeVertexColor');vc.layer_name='HeartColor';moss=nodes.new('ShaderNodeTexImage');moss.image=bpy.data.images.load(str(TEX/'T_Moss_Painted_BaseColor.png'));mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';links.new(vc.outputs['Color'],mix.inputs[0]);links.new(moss.outputs['Color'],mix.inputs[1]);links.new(pig.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],p.inputs['Base Color'])

for e in manifest:
    o=e.pop('object');bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
(ART/'asset-manifest.json').write_text(json.dumps(manifest,indent=2))
(ART/'material-manifest.json').write_text(json.dumps({k:dict(roughness=m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value,emission=m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value) for k,m in M.items()},indent=2))

# Lighting review rig: broad colored shadows, local motivated pools, readable paint.
def area(name,pos,energy,size,color,target=(0,0,300)):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Broad warm garden key',(-3400,-4000,6200),220000000,3400,(1,.85,.72));area('Lavender sky fill',(3000,2800,5300),190000000,3600,(.59,.64,1));area('Soft gold tree bounce',(0,0,1600),16000000,750,(1,.59,.22),(0,0,350))
area('Cool spring bounce',(-1600,1400,1200),7000000,700,(.12,.57,1),(-1400,1000,450));area('Nest violet ambience',(1700,1900,1150),4500000,700,(.45,.16,1),(1650,1600,650))
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.022,.032,.068,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45
camera_data=bpy.data.cameras.new('Full brain geography');camera=bpy.data.objects.new('Full brain geography',camera_data);stage.objects.link(camera);camera.location=(-900,-8800,9800);target=Vector((0,100,680));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=8750;camera_data.clip_end=40000;scene.camera=camera
for e in manifest:
    if not e['spawn']:bpy.data.objects[e['name']].hide_render=True
# A render-only instance of the same articulated Attention parts establishes real
# player scale. It is excluded from every asset export and is not game evidence.
at=Vector((-370,-520,TREE[2]+4))
for key,offset in [('AttentionBody',(0,0,0)),('AttentionHead',(0,0,0)),('AttentionEyes',(0,0,0)),('AttentionCape',(0,0,0)),('AttentionArmL',(0,-37,103)),('AttentionArmR',(0,37,103)),('AttentionBootL',(0,-17,13)),('AttentionBootR',(0,17,13))]:
    source=bpy.data.objects['SM_Craft_'+key];o=source.copy();o.data=source.data;stage.objects.link(o);o.name='Review scale / '+key;o.hide_render=False;o.location=at+Vector(offset);o.rotation_euler.z=-math.pi/2
scene.render.resolution_x=1800;scene.render.resolution_y=1500;scene.render.resolution_percentage=100;scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ART/'Brain-C07-Actual-Model.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft.blend'));print('CRAFT_EDITABLE_SAVED',flush=True);bpy.ops.render.render(write_still=True)
camera.location=(-2450,-1450,3090);target=Vector((-1350,1130,980));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=3300;scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.filepath=str(ART/'Brain-C07-Spring-Terraces.png');bpy.ops.render.render(write_still=True);print('CRAFT_RENDERS_READY',flush=True)
