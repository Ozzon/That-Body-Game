import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());art=root/'Art/BrainCraft';data=art/'Source/C11';A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();base='/Game/BrainCraft'
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
changed=json.loads((data/'contact-patch.json').read_text());manifest=json.loads((data/'asset-manifest.json').read_text())
for e in manifest:
    if e['key'] not in changed:continue
    ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;d=ui.static_mesh_import_data;d.combine_meshes=True;d.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;d.auto_generate_collision=False;d.generate_lightmap_u_vs=False
    t=unreal.AssetImportTask();t.filename=str(art/'ExportC11'/(e['name']+'.fbx'));t.destination_path=base+'/Models';t.destination_name=e['name'];t.automated=True;t.replace_existing=True;t.save=True;t.options=ui;AT.import_asset_tasks([t]);m=unreal.load_asset(base+'/Models/'+e['name'])
    for i,s in enumerate(m.get_editor_property('static_materials')):
        key=str(s.get_editor_property('material_slot_name')).split('.')[0];mat=unreal.load_asset(base+'/Materials/M_Craft_'+key);assert mat,key;m.set_material(i,mat)
    m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(m)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Maps/BrainCraft')
actorlib=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);existing={str(t) for actor in actorlib.get_all_level_actors() if 'BrainCraft' in [str(t) for t in actor.tags] for t in actor.tags}
for e in manifest:
    if e['key'] not in changed or not e['spawn'] or e['key'] in existing:continue
    actor=actorlib.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));actor.set_actor_label('BrainCraft / '+e['key']);actor.tags=['BrainCraft',e['key']]+e['tags'];actor.set_actor_scale3d(unreal.Vector(1,-1,1));comp=actor.static_mesh_component;comp.set_static_mesh(unreal.load_asset(base+'/Models/'+e['name']));comp.set_collision_profile_name('BlockAll');comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if 'Ground' in e['tags'] else unreal.CollisionEnabled.NO_COLLISION)
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if 'BrainCraft' not in [str(t) for t in actor.tags]:continue
    c=actor.static_mesh_component
    source=next((e for e in manifest if e['name']==c.static_mesh.get_name()),None)
    if source:actor.tags=['BrainCraft',source['key']]+source['tags']
    for i,s in enumerate(c.static_mesh.get_editor_property('static_materials')):c.set_material(i,s.get_editor_property('material_interface'))
levels.save_current_level()
for path in ([] if 'C11GeometryOnly' in unreal.SystemLibrary.get_command_line() else A.list_assets(base+'/Materials',recursive=False)):
    m=unreal.load_asset(path)
    if isinstance(m,unreal.Material):errors=L.recompile_material(m);assert not errors,(path,errors);A.save_loaded_asset(m)
readback={}
for actor in actorlib.get_all_level_actors():
    tags=[str(t) for t in actor.tags]
    for key in ['Nest0','Nest1','Nest2']:
        if key in tags:
            center,extent=actor.get_actor_bounds(False);readback[key]=dict(center=[center.x,center.y,center.z],extent=[extent.x,extent.y,extent.z])
(data/'border-gate-readback.json').write_text(json.dumps(readback,indent=2))
unreal.log('C11_PATCH_GPU_FINALIZED')
if 'C11GeometryOnly' not in unreal.SystemLibrary.get_command_line():exec(compile((root/'Tools/c11_surface_finish.py').read_text(),str(root/'Tools/c11_surface_finish.py'),'exec'))
if 'C11Moss' in unreal.SystemLibrary.get_command_line():exec(compile((root/'Tools/c11_moss_finish.py').read_text(),str(root/'Tools/c11_moss_finish.py'),'exec'))
