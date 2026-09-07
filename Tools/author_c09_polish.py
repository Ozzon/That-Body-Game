"""Correct sculpt normals, displaced terrain, spatially composed planting beds."""
import bpy,numpy as np,math,json,sys,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,merge,leaf,sweep,block
from brain_craft_layout import *
ART=ROOT/'Art/BrainCraft';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C08.blend'));M={m.name:m for m in bpy.data.materials};env=bpy.data.collections['01 | Sculpted hemisphere topology'];props=bpy.data.collections['04 | Thought ecology'];changed=[]
manifest=json.loads((ART/'asset-manifest.json').read_text())
def uv_project(o,size):
    uv=o.data.uv_layers.new(name='CraftUV')
    for poly in o.data.polygons:
        axis=max(range(3),key=lambda i:abs(poly.normal[i]));ab=[i for i in range(3) if i!=axis]
        for loop in poly.loop_indices:
            p=o.data.vertices[o.data.loops[loop].vertex_index].co;uv.data[loop].uv=(p[ab[0]]/size,p[ab[1]]/size)
def replace(key,d,mat,n=None):
    name='SM_Craft_'+key;o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
    o=mesh(name,d['v'],d['f'],(1,1,1),env,M[mat],n);uv_project(o,1100 if mat=='Cortex' else 380);changed.append(o);return o
for file in (ART/'Source/C08').glob('Cortex*.npz'):
    d=np.load(file);replace(file.stem,d,'Cortex',-d['n'])
for key in ['Ground','EarthPath','CrossingBeds']:
    d=np.load(ART/'Source/C09'/(key+'.npz'));o=replace(key,d,'Moss' if key=='Ground' else 'Earth' if key=='EarthPath' else 'Stone')
    if key=='Ground':
        o.data.materials.append(M['Stone'])
        for p in o.data.polygons:
            if p.normal.z<.45:p.material_index=1
    if key=='EarthPath':
        g=1-d['grass'];o.data.color_attributes['HeartColor'].data.foreach_set('color',np.column_stack([g,g,g,np.ones(len(g))]).ravel())
    if key=='CrossingBeds':manifest.append(dict(name=o.name,key=key,spawn=True,tags=['Ground'],materials=['Stone']))
# Pathside repetition removed. Each planting pocket has an environmental reason:
# damp spring edges, shaded roots, nest alcove corners or protected lotus banks.
for key in ['PathsidePlanting','PathsideBlossoms']:
    o=bpy.data.objects.get('SM_Craft_'+key)
    if o:bpy.data.objects.remove(o,do_unlink=True)
    manifest=[e for e in manifest if e['key']!=key]
sites=[(-2100,1750,140,190,'spring bank'),(-2040,1090,95,180,'stream bank'),(-1710,430,95,130,'stream bend'),(-1020,-660,95,110,'stream end'),(-530,320,155,120,'shaded tree roots'),(440,490,170,120,'shaded tree roots'),(-550,560,140,120,'root bed'),(1140,2130,125,110,'nest alcove'),(2150,1700,130,140,'nest alcove'),(1860,-1810,115,95,'lotus bank'),(1160,-1430,95,130,'lotus bank'),(-2040,-2400,140,130,'arrival alcove')]
rng=random.Random(902);green=[];flowers=[];stones=[]
for si,(x,y,rx,ry,why) in enumerate(sites):
    for i in range(28):
        a=i*2.399;rr=math.sqrt((i+.5)/28);xx=x+rx*rr*math.cos(a);yy=y+ry*rr*math.sin(a);dd,z,road=fields(xx,yy)
        if dd>-20 or water(xx,yy)<30 or road<-160 or math.hypot(xx,yy-90)<365:continue
        z=float(z)+8
        for j in range(5):
            aa=j*2.399+i;green.append(leaf(why,(xx,yy,z),(math.cos(aa),math.sin(aa),.65),rng.uniform(35,67),rng.uniform(10,20),(1,1,1),props,M['Fern'],.32))
        if i%6==0:
            for j in range(5):
                aa=j*math.tau/5;flowers.append(leaf('A sheltered blossom',(xx,yy,z+42),(math.cos(aa),math.sin(aa),.4),18,12,(1,1,1),props,M['Blossom'],.28))
    # Three grouped rocks anchor a bed, rather than scattered obstacles in paths.
    for i in range(3):
        a=(si*.73+i*.5);xx=x+rx*.75*math.cos(a);yy=y+ry*.8*math.sin(a);dd,z,road=fields(xx,yy)
        if road>-130 and water(xx,yy)>50:stones.append(block('Mossy garden bed stone',(xx,yy,float(z)+13),(46+i*12,38+i*8,34+i*9),(1,1,1),props,M['Stone'],a,11,si+i))
for parts,key in [(green,'GardenPocketLeaves'),(flowers,'GardenPocketFlowers'),(stones,'GardenPocketStones')]:
    if parts:
        o=merge(parts,'SM_Craft_'+key);uv_project(o,160);changed.append(o);manifest.append(dict(name=o.name,key=key,spawn=True,tags=['Foliage'] if 'Stones' not in key else [],materials=[m.name for m in o.data.materials]))
# Soften the deliberately authored surfaces; fine terrain detail comes from
# silhouette-changing geometry and local pigment, not harsh contrast noise.
for key,c in [('Moss',(.15,.255,.105,1)),('Earth',(.43,.31,.19,1)),('Leaf',(.78,.46,.055,1)),('Water',(.045,.29,.32,1))]:
    m=M[key];p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=c
    for link in list(p.inputs['Base Color'].links):m.node_tree.links.remove(link)
    p.inputs['Roughness'].default_value=.8 if key!='Water' else .28
    if key=='Leaf':p.inputs['Emission Color'].default_value=c;p.inputs['Emission Strength'].default_value=.08
for o in changed:
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'Export'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
(ART/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(ART/'Source/C09/changed-assets.json').write_text(json.dumps([o.name for o in changed]));(ART/'Source/C09/planting-plan.json').write_text(json.dumps(sites,indent=2))
scene=bpy.context.scene;scene.cycles.samples=32;scene.render.filepath=str(ART/'Brain-C09-Actual-Model.png');bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C09.blend'));print('C09_SAVED',flush=True);bpy.ops.render.render(write_still=True);print('C09_DONE',flush=True)
