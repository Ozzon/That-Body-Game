import bpy,bmesh,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'Art/BrainCraft/Source/C17'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/BrainCraft/Brain_Craft_C17.blend'))
report={}
for key in ['TreeWood','TreeLeaves','RootBed']:
    o=bpy.data.objects['SM_Craft_C17_'+key];bm=bmesh.new();bm.from_mesh(o.data);visited=set();sizes=[]
    for v in bm.verts:
        if v in visited:continue
        stack=[v];visited.add(v);size=0
        while stack:
            a=stack.pop();size+=1
            for e in a.link_edges:
                b=e.other_vert(a)
                if b not in visited:visited.add(b);stack.append(b)
        sizes.append(size)
    report[key]=dict(vertices=len(bm.verts),faces=len(bm.faces),components=len(sizes),largest_component_fraction=max(sizes)/len(bm.verts),non_manifold_edges=sum(not e.is_manifold for e in bm.edges),down_facing_faces=sum(f.normal.z<-.5 for f in bm.faces))
    bm.free()
(DATA/'geometry-inspection-r01.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
