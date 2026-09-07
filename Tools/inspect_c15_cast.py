import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/BrainCraft/Brain_Craft_C15.blend'))
report={}
for kind in ['Cloud','Wisp','Star','Knot']:
    body=bpy.data.objects['SM_Craft_Thought'+kind];body.data.calc_loop_triangles()
    v=np.array([p.co[:] for p in body.data.vertices]);f=np.array([p.vertices[:] for p in body.data.loop_triangles]);tri=v[f]
    volume=np.sum(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])))/6
    facekey='Bright' if kind=='Star' else kind;face=bpy.data.objects['SM_Craft_ThoughtFace'+facekey]
    tree=BVHTree.FromPolygons([Vector(p) for p in v],f.tolist(),all_triangles=True)
    front=[]
    for p in face.data.vertices:
        hit=tree.ray_cast(Vector((250,p.co.y,p.co.z)),Vector((-1,0,0)),500)
        if hit[0] is not None:front.append(float(p.co.x-hit[0].x))
    report[kind]=dict(vertices=len(v),triangles=len(f),signed_volume_cm3=float(volume),bounds_cm=[v.min(0).tolist(),v.max(0).tolist()],face_vertices_behind_body=sum(x<-.5 for x in front),face_samples=len(front),minimum_face_clearance_cm=min(front) if front else None)
(ROOT/'Art/BrainCraft/Source/C15/cast-inspection.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
