"""Preserve explicit terrain triangle winding; do not orient open shading islands."""
import bpy,numpy as np,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C13';OUT=ART/'ExportC13Polish';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C13.blend'))
coll=bpy.data.collections['C13 | Continuous land and crafted garden surfaces'];report={}
for key in json.loads((DATA/'construction.json').read_text())['terrain_pieces']:
    old=bpy.data.objects.get('SM_Craft_'+key)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    d=np.load(DATA/(key+'.npz'));norm=d['n'].copy();norm[np.abs(norm[:,2])<.001]*=-1
    o=mesh('SM_Craft_'+key,d['v'],d['f'],d['c'],coll,bpy.data.materials['C13_Turf'],norm.tolist());o.data.materials.append(bpy.data.materials['C13_Earth']);top=int(d['topfaces'])
    for f in o.data.polygons:
        if f.index>=top:f.material_index=1
    assert all(f.normal.z>0 for f in o.data.polygons[:top]),key
    uv=o.data.uv_layers.new(name='CraftUV')
    for f in o.data.polygons:
        axis=max(range(3),key=lambda k:abs(f.normal[k]));ab=[k for k in range(3) if k!=axis]
        for i in f.loop_indices:pt=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(pt[ab[0]]/100,pt[ab[1]]/100)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    report[key]=dict(top_faces=top,down_faces=0)
(DATA/'winding-repair.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C13.blend'));print('C13_TERRAIN_WINDING_REPAIRED',flush=True)
