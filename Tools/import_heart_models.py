import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());base='/Game/HeartModels'
unreal.EditorAssetLibrary.make_directory(base);lib=unreal.MaterialEditingLibrary
def newmat(name):
    mat=unreal.load_asset(base+'/'+name)
    if not mat:mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,base,unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(mat);return mat
mat=newmat('M_HeartAuthored');mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
v=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-600,0)
assert lib.connect_material_property(v,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-200,200);r.set_editor_property('r',.48)
lib.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
a=lib.create_material_expression(mat,unreal.MaterialExpressionMultiply,-200,350);a.set_editor_property('const_b',.22)
assert lib.connect_material_expressions(v,'',a,'A');lib.connect_material_property(a,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
vis=lib.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-500,600);vis.set_editor_property('parameter_name','Visibility');vis.set_editor_property('default_value',1.)
d=lib.create_material_expression(mat,unreal.MaterialExpressionMaterialFunctionCall,-200,600);d.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'))
lib.connect_material_expressions(vis,'',d,'Alpha Threshold');lib.connect_material_property(d,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
lib.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
glow=newmat('M_Heartbeat');glow.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
c=lib.create_material_expression(glow,unreal.MaterialExpressionConstant3Vector,-100,0);c.set_editor_property('constant',unreal.LinearColor(4,1.2,.13,1));lib.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
lib.recompile_material(glow);unreal.EditorAssetLibrary.save_loaded_asset(glow)
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for key in ['A','B','C']:
    art=root/'Art/HeartModels'/key;manifest=json.loads((art/'Export/asset-manifest.json').read_text());folder=base+'/'+key
    unreal.EditorAssetLibrary.make_directory(folder)
    for name in manifest['assets']:
        ui=unreal.FbxImportUI();ui.set_editor_property('import_mesh',True);ui.set_editor_property('import_materials',False);ui.set_editor_property('import_textures',False);ui.set_editor_property('import_as_skeletal',False);ui.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
        data=ui.static_mesh_import_data;data.set_editor_property('combine_meshes',True);data.set_editor_property('vertex_color_import_option',unreal.VertexColorImportOption.REPLACE);data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS);data.set_editor_property('auto_generate_collision',False);data.set_editor_property('generate_lightmap_u_vs',False)
        task=unreal.AssetImportTask();task.set_editor_property('filename',str(art/'Export'/(name+'.fbx')));task.set_editor_property('destination_path',folder);task.set_editor_property('destination_name',name);task.set_editor_property('automated',True);task.set_editor_property('replace_existing',True);task.set_editor_property('save',True);task.set_editor_property('options',ui)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=unreal.load_asset(folder+'/'+name)
        if not mesh:raise RuntimeError('Missing model '+key+' / '+name)
        for i in range(mesh.get_num_sections(0)):mesh.set_material(i,glow if name.endswith('PulseSeed') else mat)
        mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    path='/Game/Maps/HeartStudy'+key
    if unreal.EditorAssetLibrary.does_asset_exist(path):levels.load_level(path)
    else:levels.new_level(path)
    for actor in actors.get_all_level_actors():
        if any(str(t) in ['HeartPart','HeartPreview'] for t in actor.tags):actors.destroy_actor(actor)
    for name in manifest['assets']:
        actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.tags=['HeartPart'];actor.set_actor_label(name.removeprefix('SM_Heart_'))
        comp=actor.static_mesh_component;comp.set_mobility(unreal.ComponentMobility.MOVABLE);comp.set_static_mesh(unreal.load_asset(folder+'/'+name));actor.set_actor_scale3d(unreal.Vector(1,-1,1))
    light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,2500),unreal.Rotator(-52,-38,0));light.tags=['HeartPreview'];light.light_component.set_intensity(3.5)
    fill=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,2500),unreal.Rotator(-48,135,0));fill.tags=['HeartPreview'];fill.light_component.set_intensity(.65)
    levels.save_current_level();unreal.log('HEART_MODEL_IMPORTED '+key)
unreal.log('HEART_THREE_MODELS_READY')
