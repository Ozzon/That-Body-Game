import bpy,json,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/BrainCraft/Brain_Craft_C15.blend'))
report={}
for key in ['AttentionCape','AttentionBody','AttentionHead','AttentionEyes']:
    o=bpy.data.objects['SM_Craft_'+key];v=np.array([p.co[:] for p in o.data.vertices])
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();me.calc_loop_triangles()
    tri=np.array([f.vertices[:] for f in me.loop_triangles]);p=np.array([p.co[:] for p in me.vertices])
    # Duplicate triangles with different winding/materials are a source of flicker.
    rounded=np.round(p,4);_,ids=np.unique(rounded,axis=0,return_inverse=True)
    canonical=np.sort(ids[tri],axis=1);_,counts=np.unique(canonical,axis=0,return_counts=True)
    report[key]={'bounds':[v.min(0).tolist(),v.max(0).tolist()], 'source_vertices':len(v),
                 'evaluated_triangles':len(tri),'coincident_triangles':int(sum(counts-1)),
                 'materials':[m.name for m in o.data.materials],
                 'modifiers':[m.type for m in o.modifiers]}
    e.to_mesh_clear()
(ROOT/'Art/BrainCraft/Source/C16/costume-inspection.json').write_text(json.dumps(report,indent=2))
print('C16_COSTUME_INSPECTION',json.dumps(report),flush=True)
