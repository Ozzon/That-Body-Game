"""C10 replaces blurred terrain overlays with authored geometric cover and soil.

All scene edits remain native meshes; source textures are material inputs.
"""
import bpy,bmesh,numpy as np,math,json,sys,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,merge,sweep,block,leaf,ellipsoid
from brain_craft_layout import *
ART=ROOT/'Art/BrainCraft';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C09.blend'));M={m.name:m for m in bpy.data.materials};env=bpy.data.collections['01 | Sculpted hemisphere topology'];props=bpy.data.collections['04 | Thought ecology'];changed=[]
manifest=json.loads((ART/'asset-manifest.json').read_text());rng=random.Random(10091)
def uv(o,size=300):
    lay=o.data.uv_layers.new(name='CraftUV')
    for face in o.data.polygons:
        axis=max(range(3),key=lambda k:abs(face.normal[k]));ab=[k for k in range(3) if k!=axis]
        for li in face.loop_indices:
            p=o.data.vertices[o.data.loops[li].vertex_index].co;lay.data[li].uv=(p[ab[0]]/size,p[ab[1]]/size)
def add(o,key,tags=None,spawn=True):
    o.name='SM_Craft_'+key
    if not o.data.uv_layers:uv(o)
    manifest[:]=[e for e in manifest if e['key']!=key];manifest.append(dict(name=o.name,key=key,spawn=spawn,tags=tags or [],materials=[m.name for m in o.data.materials]));changed.append(o);return o
def remove(key):
    o=bpy.data.objects.get('SM_Craft_'+key)
    if o:bpy.data.objects.remove(o,do_unlink=True)
    manifest[:]=[e for e in manifest if e['key']!=key]
def simplemat(key,color):
    m=bpy.data.materials.get(key) or bpy.data.materials.new(key);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.82;M[key]=m;return m
atlas=bpy.data.images.load(str(ART/'Textures/T_C10_Garden_Atlas.png'))
for key,off,scale in [('GardenSoil',(0,.5,0),300),('GardenStone',(.5,.5,0),300),('GardenMoss',(0,0,0),160),('GardenSand',(.5,0,0),210)]:
    m=simplemat(key,(.32,.27,.17));n=m.node_tree.nodes;l=m.node_tree.links;co=n.new('ShaderNodeTexCoord');fac=n.new('ShaderNodeVectorMath');fac.operation='FRACTION';l.new(co.outputs['UV'],fac.inputs[0]);sz=n.new('ShaderNodeVectorMath');sz.operation='SCALE';sz.inputs[3].default_value=.48;l.new(fac.outputs[0],sz.inputs[0]);ad=n.new('ShaderNodeVectorMath');ad.operation='ADD';ad.inputs[1].default_value=(off[0]+.01,off[1]+.01,0);l.new(sz.outputs[0],ad.inputs[0]);im=n.new('ShaderNodeTexImage');im.image=atlas;l.new(ad.outputs[0],im.inputs['Vector']);l.new(im.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
grass=simplemat('GardenGrass',(.14,.29,.16));n=grass.node_tree.nodes;l=grass.node_tree.links;vc=n.new('ShaderNodeVertexColor');vc.layer_name='HeartColor';l.new(vc.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
simplemat('GardenTurf',(.09,.15,.055))
# One continuous displaced soil substrate eliminates the separate smeared strip
# and its visible polygon edges. Under dense planting, moss has actual volume.
remove('EarthPath');o=bpy.data.objects['SM_Craft_Ground'];o.data.materials.clear();o.data.materials.append(M['GardenSoil']);o.data.materials.append(M['GardenStone']);o.data.materials.append(M['GardenTurf']);turf=np.load(ART/'Source/C10/turf-mask.npz')['turf']
for face in o.data.polygons:
    if face.normal.z>.7 and sum(bool(turf[i]) for i in face.vertices)>=3:face.material_index=2
changed.append(o)
for e in manifest:
    if e['key']=='Ground':e['materials']=['GardenSoil','GardenStone','GardenTurf']
for key in ['Paving','CrossingBeds','StreamBanks','RetainingWalls']:
    o=bpy.data.objects.get('SM_Craft_'+key)
    if o:
        for i,m in enumerate(o.data.materials):
            if m.name=='Stone':o.data.materials[i]=M['GardenStone']
        changed.append(o)
        for e in manifest:
            if e['key']==key:e['materials']=[m.name for m in o.data.materials]
# Close the fitted slabs and orient each connected stone outward. Shapely's
# clipped boundaries are clockwise, which previously left top faces culled in UE.
o=bpy.data.objects['SM_Craft_Paving'];bm=bmesh.new();bm.from_mesh(o.data);boundary=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=boundary,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
# Separate portal stops with explicit front landings. Transform all pieces as
# one authored assembly; the front normal follows the local approach.
dest=json.loads((ART/'Source/C10/portal-layout.json').read_text())
for i,e in enumerate(dest):
    old=np.array(NESTS[i]);new=np.array(e['p']);a=math.radians(e['yaw']);rot=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    for key in [f'Nest{i}',f'NestGlow{i}',f'NestSurround{i}',f'NestRoots{i}']:
        o=bpy.data.objects.get('SM_Craft_'+key)
        for p in o.data.vertices:p.co=rot@(np.array(p.co)-old)+new
        o.data.update();changed.append(o)
# Ground-cover geometry: tapered curved grass with rooted normals, and tiny
# broad-leaf rosettes at damp edges. The walkable centers stay physically open.
d=np.load(ART/'Source/C10/cover-points.npz');buckets={i:[[],[],[]] for i in range(4)};moss=[]
for idx,(p,sc,angle) in enumerate(zip(d['p'],d['scale'],d['angle'])):
    bucket=int(p[0]>0)+2*int(p[1]>0);V,F,C=buckets[bucket];hue=.5+.5*math.sin(idx*1.37)
    for blade in range(14):
        a=angle+blade*2.399;base=p+np.array([math.cos(a)*21*sc,math.sin(a)*21*sc,0]);direction=np.array([math.cos(a),math.sin(a),0]);side=np.array([-math.sin(a),math.cos(a),0]);height=(30+(blade%4)*8)*sc;width=(6.2+blade%3)*sc;k0=len(V)
        for j in range(6):
            t=j/5;tip=base+direction*(t*t*height*.42)+np.array([0,0,height*t]);w=width*(1-t)**.65
            for k in [-1,0,1]:
                q=tip+side*w*k;q[2]-=abs(k)*w*.23;V.append(q);C.append((.065+.045*t+.02*hue,.16+.10*t+.02*hue,.035+.035*t))
            if j:
                for k in range(2):q=k0+(j-1)*3+k;F.append((q,q+1,q+4,q+3))
    if idx%4==0:
        for k in range(7):
            a=angle+k*2.399;moss.append(leaf('Damp-bank moss rosette',p+np.array([0,0,2]),(math.cos(a),math.sin(a),.24),26*sc,12*sc,(1,1,1),props,M['GardenMoss'],.18))
for i,(V,F,C) in buckets.items():
    o=mesh('Grass cover',V,F,C,env,grass)
    # Preserve readable top lighting on thin foliage; actual silhouette is bent.
    o.data.normals_split_custom_set_from_vertices([(0,0,1)]*len(V));add(o,'GardenGrass'+str(i),['GroundCover'])
if moss:add(merge(moss,'Moss leaf cushions'),'GardenMossCushions',['GroundCover'])
# The combed sand belongs to a protected arrival pocket and has actual carved
# ridges. It is separated from the main route by a few low grouping stones.
remove('RakedSand');remove('SandGrooves');cx,cy,cz=-1610,-2500,143;V=[];F=[]
rows=94;cols=68
for i in range(rows):
    u=-1+2*i/(rows-1)
    for j in range(cols):
        t=-1+2*j/(cols-1);x=cx+u*240;y=cy+t*math.sqrt(max(.001,1-u*u))*180;r=math.hypot((x-cx)*.8,y-cy);z=cz+2.8*math.cos(r*.36)+3.5*(1-u*u)*(1-t*t);V.append((x,y,z))
        if i and j:q=(i-1)*cols+j-1;F.append((q,q+cols,q+cols+1,q+1))
add(mesh('Sculpted combed sand',V,F,(1,1,1),props,M['GardenSand']),'RakedSand',['Ground'])
rocks=[]
for i,(x,y,s) in enumerate([(-1480,-2490,1),(-1530,-2540,.63),(-1450,-2550,.4)]):
    rocks.append(ellipsoid('Contemplation stone',(x,y,cz+29*s),(57*s,40*s,61*s),(1,1,1),props,M['GardenStone'],i,32,20))
add(merge(rocks,'Three grouped contemplation stones'),'SandGardenStones',[])
# A sheltered rest deck on the freed upper-right court makes a destination
# instead of the former three-portal row. Roof can fade independently.
cx,cy,cz=1220,1990,950;wood=[];roof=[]
for i in range(8):wood.append(block('Rest deck fitted boards',(cx-210+i*60,cy,cz+16),(58,350,28),(1,1,1),props,M['Bark'],0,6,i))
for sx in [-1,1]:
    for sy in [-1,1]:wood.append(sweep('Shelter curved post',[(cx+sx*215,cy+sy*145,cz),(cx+sx*214,cy+sy*145,cz+195),(cx+sx*230,cy+sy*160,cz+345)],[17,14,19],(1,1,1),props,M['Bark'],16,7,.04))
for sign in [-1,1]:
    for i in range(12):
        x=cx-315+i*57;pts=[(x,cy,cz+454),(x,cy+sign*100,cz+435),(x,cy+sign*220,cz+376),(x,cy+sign*280,cz+400)];roof.append(sweep('Swept shelter roof rib',pts,[12,12,12,9],(1,1,1),props,M['Sage'],12,7))
    V=[];F=[]
    for i in range(25):
        u=i/24;x=cx-350+700*u
        for j in range(17):
            t=j/16;z=cz+455-90*math.sin(t*math.pi*.65)+max(0,t-.72)*110;V.append((x,cy+sign*t*300,z))
            if i and j:q=(i-1)*17+j-1;face=(q,q+17,q+18,q+1);F.append(face if sign>0 else face[::-1])
    roof.append(mesh('Layered curved shelter roof',V,F,(1,1,1),props,M['Sage']))
wood.append(block('Quiet resting seat',(cx,cy+82,cz+61),(340,65,25),(1,1,1),props,M['Bark'],0,8,4))
add(merge(wood,'Rest shelter carved framework'),'RestShelter',['Interactive']);add(merge(roof,'Rest shelter layered roof'),'RestShelterRoof',['Occluder'])
# Every changed slot is recorded for deterministic Unreal readback.
for o in changed:
    for e in manifest:
        if e['name']==o.name:e['materials']=[m.name for m in o.data.materials]
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'Export'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
(ART/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(ART/'Source/C10/changed-assets.json').write_text(json.dumps(list(dict.fromkeys(o.name for o in changed))))
scene=bpy.context.scene;scene.cycles.samples=32;bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C10.blend'));print('C10_SAVED',flush=True)
if '--render' in sys.argv:scene.render.filepath=str(ART/'Brain-C10-Actual-Model.png');bpy.ops.render.render(write_still=True)
print('C10_DONE',flush=True)
