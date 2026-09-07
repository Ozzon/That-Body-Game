"""Import the reference-led brain into the existing world without changing the heart."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());art=root/'Art/BrainGarden';base='/Game/BrainGarden'
assets=unreal.EditorAssetLibrary;lib=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
assets.make_directory(base)
materials={}
for kind,rough,emission in [('Surface',.59,.12),('Foliage',.46,.20),('Water',.24,.48),('Glow',.40,2.8)]:
    name='M_Garden'+kind;m=unreal.load_asset(base+'/'+name)
    if not m:m=at.create_asset(name,base,unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(m);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property('two_sided',kind in ['Foliage','Water'])
    v=lib.create_material_expression(m,unreal.MaterialExpressionVertexColor,-600,0);assert lib.connect_material_property(v,'',unreal.MaterialProperty.MP_BASE_COLOR)
    r=lib.create_material_expression(m,unreal.MaterialExpressionConstant,-180,180);r.set_editor_property('r',rough);lib.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
    power=lib.create_material_expression(m,unreal.MaterialExpressionScalarParameter,-600,350);power.set_editor_property('parameter_name','LifeGlow');power.set_editor_property('default_value',emission)
    mul=lib.create_material_expression(m,unreal.MaterialExpressionMultiply,-200,300);lib.connect_material_expressions(v,'',mul,'A');lib.connect_material_expressions(power,'',mul,'B');lib.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    vis=lib.create_material_expression(m,unreal.MaterialExpressionScalarParameter,-600,550);vis.set_editor_property('parameter_name','Visibility');vis.set_editor_property('default_value',1.)
    d=lib.create_material_expression(m,unreal.MaterialExpressionMaterialFunctionCall,-200,600);d.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));lib.connect_material_expressions(vis,'',d,'Alpha Threshold');lib.connect_material_property(d,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
    lib.recompile_material(m);assets.save_loaded_asset(m);materials[kind]=m
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
manifest=json.loads((art/'asset-manifest.json').read_text())
for e in manifest:
    name=e['name'];ui=unreal.FbxImportUI();ui.set_editor_property('import_mesh',True);ui.set_editor_property('import_materials',False);ui.set_editor_property('import_textures',False);ui.set_editor_property('import_as_skeletal',False);ui.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
    data=ui.static_mesh_import_data;data.set_editor_property('combine_meshes',True);data.set_editor_property('vertex_color_import_option',unreal.VertexColorImportOption.REPLACE);data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS);data.set_editor_property('auto_generate_collision',False);data.set_editor_property('generate_lightmap_u_vs',False)
    task=unreal.AssetImportTask();task.set_editor_property('filename',str(art/'Export'/(name+'.fbx')));task.set_editor_property('destination_path',base+'/Models');task.set_editor_property('destination_name',name);task.set_editor_property('automated',True);task.set_editor_property('replace_existing',True);task.set_editor_property('save',True);task.set_editor_property('options',ui);at.import_asset_tasks([task])
    mesh=unreal.load_asset(base+'/Models/'+name)
    if not mesh:raise RuntimeError('Missing brain model '+name)
    for slot in range(mesh.get_num_sections(0)):mesh.set_material(slot,materials[e['material']])
    mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assets.save_loaded_asset(mesh)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
# The organ interior is a full independent location. Preserve the prior body map.
levels.load_level('/Game/Maps/BodyAdventure')
def heart_signature():
    return sorted((a.get_actor_label(),a.static_mesh_component.static_mesh.get_path_name(),str(a.get_actor_transform())) for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and 'Heart' in [str(x) for x in a.tags])
heart_before=heart_signature()
if assets.does_asset_exist('/Game/Maps/BrainGarden'):levels.load_level('/Game/Maps/BrainGarden')
else:levels.new_level('/Game/Maps/BrainGarden')
for a in actors.get_all_level_actors():
    if any(t in [str(x) for x in a.tags] for t in ['Brain','BrainTree','BrainGarden']):actors.destroy_actor(a)
for e in manifest:
    if not e.get('spawn',True):continue
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(9250,0,220));a.set_actor_label('Brain garden / '+e['key']+' / '+e['name']);a.tags=['AdventureMesh','BrainGarden',e['key']]+e['tags']
    c=a.static_mesh_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(unreal.load_asset(base+'/Models/'+e['name']));a.set_actor_scale3d(unreal.Vector(1,-1,1))
    if e['key']=='RootShortcut':c.set_visibility(False)
# Update only the connecting light paths, using the corrected deck orientation.
ui=unreal.FbxImportUI();ui.set_editor_property('import_materials',False);ui.set_editor_property('import_textures',False);ui.set_editor_property('import_mesh',True);ui.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
ui.static_mesh_import_data.set_editor_property('vertex_color_import_option',unreal.VertexColorImportOption.REPLACE)
ui.static_mesh_import_data.set_editor_property('combine_meshes',True)
task=unreal.AssetImportTask();task.set_editor_property('filename',str(root/'Art/BodyAdventure/Export/SM_Adventure_LightBridges.fbx'));task.set_editor_property('destination_path','/Game/BodyAdventure/Models');task.set_editor_property('destination_name','SM_Adventure_LightBridges');task.set_editor_property('automated',True);task.set_editor_property('replace_existing',True);task.set_editor_property('save',True);task.set_editor_property('options',ui);at.import_asset_tasks([task])
bridge=unreal.load_asset('/Game/BodyAdventure/Models/SM_Adventure_LightBridges');bridge.set_material(0,unreal.load_asset('/Game/BodyAdventure/M_LightPath'));assets.save_loaded_asset(bridge)
levels.save_current_level()
levels.load_level('/Game/Maps/BodyAdventure');assert heart_before==heart_signature(),'Approved heart changed during brain-only import'
levels.load_level('/Game/Maps/BrainGarden')
report=dict(brain_assets=len(manifest),brain_actors=sum(e.get('spawn',True) for e in manifest),approved_heart_unchanged=True,approved_heart_actor_count=len(heart_before),map='/Game/Maps/BrainGarden',all_models_loaded=all(assets.does_asset_exist(base+'/Models/'+e['name']) for e in manifest),art_accepted=False)
(art/'unreal-import-report.json').write_text(json.dumps(report,indent=2))
unreal.log('BRAIN_GARDEN_IMPORTED '+json.dumps(report))
