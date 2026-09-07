import bpy,numpy as np,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,collection
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C14';OUT=ART/'ExportC14Mantle';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C14.blend'));coll=collection('C14 | Oriented living nests');report={}
for idx,e in enumerate(json.loads((DATA/'portals.json').read_text())):
    key='Nest'+str(idx);old=bpy.data.objects.get('SM_Craft_'+key)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    p=np.array(e['p']);out=np.array([*e['outward'],0]);side=np.array([-out[1],out[0],0]);basis=np.stack([side,out,[0,0,1]],axis=1);a=np.load(DATA/(key+'.npz'));v=a['v']@basis.T+p;n=a['n']@basis.T;f=a['f'][:,::-1] if np.linalg.det(basis)<0 else a['f']
    volume=float(np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6);assert volume>0,(key,volume)
    o=mesh('SM_Craft_'+key,v,f,a['c'],coll,bpy.data.materials['C13_Tissue'],n.tolist());uv=o.data.uv_layers.new(name='CraftUV')
    for i,l in enumerate(o.data.loops):pt=o.data.vertices[l.vertex_index].co;uv.data[i].uv=(pt.x/180,pt.z/180)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR');report[key]=dict(outward_winding=True,closed_volume_cm3=volume)
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C14.blend'));(DATA/'nest-winding.json').write_text(json.dumps(report,indent=2));print('C14_NEST_WINDING_VERIFIED',flush=True)
