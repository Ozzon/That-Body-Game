import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/HeartBaseline'
bpy.ops.wm.open_mainfile(filepath=str(ART/'Heart_Baseline.blend'))
for ob in list(bpy.data.objects):
    if not ob.name.startswith('SM_Heart_'):continue
    if not ob.data.color_attributes.get('HeartColor'):
        attr=ob.data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='CORNER')
        for poly in ob.data.polygons:
            color=ob.data.materials[poly.material_index].diffuse_color
            for loop in poly.loop_indices:attr.data[loop].color=color
    bpy.ops.object.select_all(action='DESELECT');ob.hide_set(False);ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.export_scene.fbx(filepath=str(ART/'Export'/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',bake_space_transform=False,mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False)
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Heart_Baseline.blend'))
print('HEART_VERTEX_PALETTE_READY',flush=True)
