import bpy,bmesh,json,numpy as np,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C11';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));coll=bpy.data.collections['C11 | Living terraced garden'];mat=bpy.data.materials['C11_Tissue'];d=np.load(DATA/'CortexShell.npz');v=d['v'];f=d['f'];c=d['c'];cent=v[f].mean(1);changed=json.loads((DATA/'contact-patch.json').read_text())
for ix in [-1,1]:
    for iy in [-1,1]:
        key=f'Cortex{ix}{iy}';name='SM_Craft_'+key;old=bpy.data.objects.get(name)
        if old:bpy.data.objects.remove(old,do_unlink=True)
        ff=f[(cent[:,0]*ix>=0)&(cent[:,1]*iy>=0)];used,inv=np.unique(ff,return_inverse=True);o=mesh(name,v[used],inv.reshape(-1,4),c[used],coll,mat);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();uv=o.data.uv_layers.new(name='CraftUV')
        for i,loop in enumerate(o.data.loops):p=o.data.vertices[loop.vertex_index].co;uv.data[i].uv=(p.x/300,p.y/300)
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'ExportC11'/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR');changed.append(key)
(DATA/'contact-patch.json').write_text(json.dumps(changed));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));print('C11_MANTLE_PATCHED',flush=True)
