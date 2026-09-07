import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());art=root/'Art/BodyAdventure';base='/Game/BodyAdventure'
lib=unreal.MaterialEditingLibrary;assets=unreal.EditorAssetLibrary
assets.make_directory(base)
def mat(name):
    m=unreal.load_asset(base+'/'+name)
    if not m:m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,base,unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(m);return m
surface=mat('M_Organ');surface.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
v=lib.create_material_expression(surface,unreal.MaterialExpressionVertexColor,-500,0);assert lib.connect_material_property(v,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=lib.create_material_expression(surface,unreal.MaterialExpressionConstant,-200,150);r.set_editor_property('r',.65);lib.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
a=lib.create_material_expression(surface,unreal.MaterialExpressionMultiply,-200,300);a.set_editor_property('const_b',.20);assert lib.connect_material_expressions(v,'',a,'A');lib.connect_material_property(a,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
vis=lib.create_material_expression(surface,unreal.MaterialExpressionScalarParameter,-500,600);vis.set_editor_property('parameter_name','Visibility');vis.set_editor_property('default_value',1.)
d=lib.create_material_expression(surface,unreal.MaterialExpressionMaterialFunctionCall,-200,600);d.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));lib.connect_material_expressions(vis,'',d,'Alpha Threshold');lib.connect_material_property(d,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
lib.recompile_material(surface);assets.save_loaded_asset(surface)
light=mat('M_LightPath');light.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
c=lib.create_material_expression(light,unreal.MaterialExpressionVertexColor,-400,0);mul=lib.create_material_expression(light,unreal.MaterialExpressionMultiply,-150,0);mul.set_editor_property('const_b',1.25);assert lib.connect_material_expressions(c,'',mul,'A');lib.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);lib.recompile_material(light);assets.save_loaded_asset(light)
glow=unreal.load_asset('/Game/HeartModels/M_Heartbeat')
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
manifest=json.loads((art/'asset-manifest.json').read_text())
for entry in manifest:
    if entry.get('existing'):continue
    name=entry['name'];ui=unreal.FbxImportUI();ui.set_editor_property('import_mesh',True);ui.set_editor_property('import_materials',False);ui.set_editor_property('import_textures',False);ui.set_editor_property('import_as_skeletal',False);ui.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
    data=ui.static_mesh_import_data;data.set_editor_property('combine_meshes',True);data.set_editor_property('vertex_color_import_option',unreal.VertexColorImportOption.REPLACE);data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS);data.set_editor_property('auto_generate_collision',False);data.set_editor_property('generate_lightmap_u_vs',False)
    task=unreal.AssetImportTask();task.set_editor_property('filename',str(art/'Export'/(name+'.fbx')));task.set_editor_property('destination_path',base+'/Models');task.set_editor_property('destination_name',name);task.set_editor_property('automated',True);task.set_editor_property('replace_existing',True);task.set_editor_property('save',True);task.set_editor_property('options',ui);unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.load_asset(base+'/Models/'+name)
    if not mesh:raise RuntimeError('Missing authored model '+name)
    for slot in range(mesh.get_num_sections(0)):mesh.set_material(slot,light if entry['material']=='Light' else glow if entry['material']=='Glow' else surface)
    mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assets.save_loaded_asset(mesh)
    unreal.log('ADVENTURE_IMPORTED '+name)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);path='/Game/Maps/BodyAdventure'
if assets.does_asset_exist(path):levels.load_level(path)
else:levels.new_level(path)
for actor in actors.get_all_level_actors():
    if 'AdventureMesh' in [str(t) for t in actor.tags] or 'HeartPreview' in [str(t) for t in actor.tags]:actors.destroy_actor(actor)
for entry in manifest:
    mesh=unreal.load_asset(entry.get('existing',base+'/Models/'+entry['name']))
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*entry['position']));actor.set_actor_label(entry['key']+' / '+entry['name'].removeprefix('SM_'));actor.tags=['AdventureMesh',entry['key']]+entry['tags']
    comp=actor.static_mesh_component;comp.set_mobility(unreal.ComponentMobility.MOVABLE);comp.set_static_mesh(mesh);actor.set_actor_scale3d(unreal.Vector(1,-1,1))
    for i in range(mesh.get_num_sections(0)):comp.set_material(i,light if entry['material']=='Light' else glow if entry['material']=='Glow' else surface)
for rot,intensity in [(unreal.Rotator(-52,-38,0),2.5),(unreal.Rotator(-45,140,0),.6)]:
    a=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,10000),rot);a.tags=['HeartPreview'];a.light_component.set_intensity(intensity)
levels.save_current_level();unreal.log('BODY_ADVENTURE_WORLD_SAVED '+str(len(manifest))+' editable mesh actors')
