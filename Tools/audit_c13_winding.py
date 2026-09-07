import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/BrainCraft/Brain_Craft_C13.blend'))
out={}
for o in bpy.data.objects:
    if not o.name.startswith('SM_Craft_Terrain'):continue
    top=[f for f in o.data.polygons if f.material_index==0]
    out[o.name]=dict(top_faces=len(top),down_faces=sum(f.normal.z<0 for f in top),mean_z=sum(f.normal.z for f in top)/len(top))
(ROOT/'Art/BrainCraft/Source/C13/winding-audit.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out),flush=True)
