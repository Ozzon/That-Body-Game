"""C17 r03: a continuous, walkable lotus pedestal matching its visible steps."""
import bpy,bmesh,math,json,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,collection
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C17';keep=ART/'Reviews/C17/r02';keep.mkdir(exist_ok=True)
if not (keep/'Brain_Craft_C17-r02.blend').exists():shutil.copy2(ART/'Brain_Craft_C17.blend',keep/'Brain_Craft_C17-r02.blend')
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C17.blend'));coll=collection('C17 | Continuous lotus steps')
for name in ['SM_Craft_LotusPlinth','SM_Craft_C17_LotusPlinth']:
    if bpy.data.objects.get(name):bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
profile=[(370,328),(360,338),(303,338),(295,342),(290,354),(234,354),(226,358),(220,371),(174,371),(166,375),(160,389),(0,389),(0,315),(370,315)]
V=[];F=[];C=[];segments=288
for layer,(r,z) in enumerate(profile):
    for j in range(segments):
        a=j*math.tau/segments;V.append([1580+r*math.cos(a),-1390+r*math.sin(a),z]);tone=.89+.035*((j//9)%6);C.append([.205*tone,.181*tone,.135*tone])
for layer in range(len(profile)):
    next_layer=(layer+1)%len(profile)
    for j in range(segments):k=(j+1)%segments;F.append([layer*segments+j,layer*segments+k,next_layer*segments+k,next_layer*segments+j])
o=mesh('SM_Craft_C17_LotusPlinth',V,F,C,coll,bpy.data.materials['C17_Stone']);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
# Keep tread normals horizontal and let the sloped bevels catch light naturally.
for f in o.data.polygons:f.use_smooth=False
uv=o.data.uv_layers.new(name='CraftUV')
for i,l in enumerate(o.data.loops):v=o.data.vertices[l.vertex_index].co;uv.data[i].uv=(v.x/250,v.y/250)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(ART/'ExportC17'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
patch=json.loads((DATA/'patch.json').read_text());patch['changed']=[e for e in patch['changed'] if e['key']!='LotusPlinth']
patch['changed'].append(dict(key='LotusPlinth',name=o.name,tags=['Interactive','Ground'],collision=True,materials=['C17_Stone'],vertices=len(o.data.vertices),triangles=sum(len(p.vertices)-2 for p in o.data.polygons)))
patch['remove']=sorted(set(patch['remove']+['LotusPlinth']));(DATA/'patch.json').write_text(json.dumps(patch,indent=2))
(DATA/'lotus-steps-r03.json').write_text(json.dumps(dict(profile_cm=profile,max_tread_rise_cm=18,outer_radius_cm=370,previous_r02_roam_passed=False,reason='Overlapping block steps stopped the native character at the lotus plinth.'),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C17.blend'));print('C17_LOTUS_STEPS_READY',flush=True)
