import bpy,bmesh,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C17'
keep=ART/'Reviews/C17/r01';keep.mkdir(exist_ok=True)
if not (keep/'Brain_Craft_C17-r01.blend').exists():shutil.copy2(ART/'Brain_Craft_C17.blend',keep/'Brain_Craft_C17-r01.blend')
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C17.blend'));report={}
for key in ['TreeWood','RootBed']:
    obj=bpy.data.objects['SM_Craft_C17_'+key];bm=bmesh.new();bm.from_mesh(obj.data)
    if key=='TreeWood':
        seen=set();islands=[]
        for v in bm.verts:
            if v in seen:continue
            stack=[v];island=[];seen.add(v)
            while stack:
                a=stack.pop();island.append(a)
                for e in a.link_edges:
                    b=e.other_vert(a)
                    if b not in seen:seen.add(b);stack.append(b)
            islands.append(island)
        largest=max(islands,key=len);loose=[v for island in islands if island is not largest for v in island]
        report['removed_voxel_tip_fragments']=len(islands)-1;report['removed_vertices']=len(loose)
        if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    else:
        if sum(f.normal.z for f in bm.faces)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    for f in obj.data.polygons:f.use_smooth=True
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(ART/'ExportC17'/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    report[key]=dict(vertices=len(obj.data.vertices),down_faces=sum(f.normal.z<-.5 for f in obj.data.polygons))
patch=json.loads((DATA/'patch.json').read_text());shutil.copy2(DATA/'patch.json',keep/'patch-r01.json');empty=[]
for e in patch['changed']:
    obj=bpy.data.objects.get(e['name'])
    if obj and not obj.data.vertices:empty.append(e['name']);bpy.data.objects.remove(obj,do_unlink=True)
patch['changed']=[e for e in patch['changed'] if e['name'] not in empty]
for e in patch['changed']:
    obj=bpy.data.objects[e['name']];e['vertices']=len(obj.data.vertices);e['triangles']=sum(len(p.vertices)-2 for p in obj.data.polygons)
(DATA/'patch.json').write_text(json.dumps(patch,indent=2));report['empty_foliage_removed']=empty
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C17.blend'));(DATA/'geometry-repair-r02.json').write_text(json.dumps(report,indent=2));print('C17_TREE_REPAIR_READY',json.dumps(report),flush=True)
