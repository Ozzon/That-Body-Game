"""Import the fitted cortical envelope, then remove tiny plants from GI occluders."""
import unreal,json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());DATA=ROOT/'Art/BrainCraft/Source/C13';BASE='/Game/BrainCraft';A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
keys=json.loads((DATA/'cortex-construction.json').read_text())['keys']+json.loads((DATA/'construction.json').read_text())['terrain_pieces']
collision_only='-C13CollisionOnly' in unreal.SystemLibrary.get_command_line()
if collision_only:keys=['Terrain3_0','Terrain4_2']
for key in keys:
    ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    d=ui.static_mesh_import_data;d.combine_meshes=True;d.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;d.auto_generate_collision=False;d.generate_lightmap_u_vs=False
    task=unreal.AssetImportTask();task.filename=str(ROOT/'Art/BrainCraft/ExportC13Polish'/('SM_Craft_'+key+'.fbx'));task.destination_path=BASE+'/Models';task.destination_name='SM_Craft_'+key;task.automated=True;task.replace_existing=True;task.save=True;task.options=ui;AT.import_asset_tasks([task]);m=unreal.load_asset(BASE+'/Models/SM_Craft_'+key)
    for i,s in enumerate(m.get_editor_property('static_materials')):
        name=str(s.get_editor_property('material_slot_name')).split('.')[0];material=unreal.load_asset(BASE+'/Materials/M_Craft_'+name);assert material,name;m.set_material(i,material)
    m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    bs=sms.get_lod_build_settings(m,0);bs.set_editor_property('max_lumen_mesh_cards',32 if key.startswith('Cortex') else 24);sms.set_lod_build_settings(m,0,bs);A.save_loaded_asset(m)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Maps/BrainCraft');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);botany=[]
for actor in actors.get_all_level_actors():
    tags=[str(t) for t in actor.tags]
    if 'BrainCraft' not in tags:continue
    c=actor.static_mesh_component
    if any(key in tags for key in keys):
        for i,s in enumerate(c.static_mesh.get_editor_property('static_materials')):c.set_material(i,s.get_editor_property('material_interface'))
    if 'GroundCover' in tags and not collision_only:
        c.set_editor_property('affect_distance_field_lighting',False)
        m=c.static_mesh;bs=sms.get_lod_build_settings(m,0);bs.set_editor_property('distance_field_resolution_scale',0);sms.set_lod_build_settings(m,0,bs);A.save_loaded_asset(m);botany.append(m.get_name())
levels.save_current_level();(DATA/('collision-import.json' if collision_only else 'cortex-import.json')).write_text(json.dumps(dict(imported_meshes=keys,small_plants_excluded_from_gi_occlusion=botany,art_accepted=False),indent=2));unreal.log('C13_COLLISION_NATIVE_READY' if collision_only else 'C13_CORTEX_NATIVE_READY')
