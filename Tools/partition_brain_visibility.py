"""Separate the visible floor from occluding cortical walls without changing geometry."""
import bpy,numpy as np,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'Tools'))
from brain_garden_layout import inner_distance,floor_height,TERRAIN_LIFT
from garden_model import mesh
art=root/'Art/BrainGarden';bpy.ops.wm.open_mainfile(filepath=str(art/'Brain_Garden.blend'))
coll=bpy.data.collections['01 CORTEX | continuous sculpted brain folds'];mat=bpy.data.materials['Garden | painted sculpt']
for o in list(coll.objects):bpy.data.objects.remove(o,do_unlink=True)
d=np.load(art/'Source/brain_cortex.npz');V,F,N,C=[d[k] for k in ['vertices','faces','normals','colors']];mid=V[F].mean(axis=1)
ground=(N[F].mean(axis=1)[:,2]>.60)&(inner_distance(mid[:,0],mid[:,1])<-55)&(mid[:,2]<floor_height(mid[:,0],mid[:,1])+TERRAIN_LIFT+45)
part=np.where(ground,0,1+(mid[:,0]>0).astype(int)*2+(mid[:,1]>0).astype(int))
for i,name in enumerate(['Ground','CortexFrontRight','CortexFrontLeft','CortexBackRight','CortexBackLeft']):
    f=F[part==i];ids,inv=np.unique(f.ravel(),return_inverse=True);o=mesh('SM_BrainGarden_'+name,V[ids].tolist(),inv.reshape(-1,3).tolist(),C[ids],coll,mat,N[ids].tolist())
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(art/'Export'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',colors_type='LINEAR')
manifest=json.loads((art/'asset-manifest.json').read_text())
for e in manifest:
    if e['name']=='SM_BrainGarden_Ground':e['tags']=['Ground']
(art/'asset-manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(art/'Brain_Garden.blend'))
print('GARDEN_VISIBILITY_PARTITION',int(ground.sum()),'ground faces',int((~ground).sum()),'wall faces',flush=True)
