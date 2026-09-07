"""Bring the fitted closed cortical sculpture into the editable level source."""
import bpy,numpy as np,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,collection
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C13';EXPORT=ART/'ExportC13Polish';EXPORT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C13.blend'))
coll=collection('C13 | Sculpted cortical envelope');m=bpy.data.materials.get('C13_Tissue') or bpy.data.materials.new('C13_Tissue');m.use_nodes=True
vc=m.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='HeartColor';p=m.node_tree.nodes.get('Principled BSDF');m.node_tree.links.new(vc.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.49
keys=json.loads((DATA/'cortex-construction.json').read_text())['keys']
for key in keys:
    old=bpy.data.objects.get('SM_Craft_'+key)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    d=np.load(DATA/(key+'.npz'));o=mesh('SM_Craft_'+key,d['v'],d['f'],d['c'],coll,m,d['n'].tolist());uv=o.data.uv_layers.new(name='CraftUV')
    for i,loop in enumerate(o.data.loops):pt=o.data.vertices[loop.vertex_index].co;uv.data[i].uv=(pt.x/180,pt.z/180)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C13.blend'));print('C13_CORTEX_EDITABLE_READY',flush=True)
