import bpy,json,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'Tools'))
from brain_garden_layout import MEMORIES,height,TERRAIN_LIFT,LEVEL_SCALE
art=root/'Art/BrainGarden';bpy.ops.wm.open_mainfile(filepath=str(art/'Brain_Garden.blend'))
original=bpy.data.objects['SM_BrainGarden_BrightThought0'];o=original.copy();o.data=original.data.copy();o.name='SM_BrainGarden_CarryThought';bpy.context.scene.collection.objects.link(o)
x,y=MEMORIES[0];origin=Vector((x*LEVEL_SCALE,y*LEVEL_SCALE,float(height(x,y))+110+TERRAIN_LIFT))
for v in o.data.vertices:v.co-=origin
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(art/'Export'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',colors_type='LINEAR')
o.hide_render=True;o.hide_set(True)
manifest=json.loads((art/'asset-manifest.json').read_text());manifest=[e for e in manifest if e['name']!=o.name];manifest.append(dict(name=o.name,key='CarryThought',tags=['Interactive'],material='Glow',spawn=False));(art/'asset-manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(art/'Brain_Garden.blend'));print('CARRY_THOUGHT_EXPORTED',flush=True)
