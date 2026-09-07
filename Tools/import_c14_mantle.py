import unreal,json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());DATA=ROOT/'Art/BrainCraft/Source/C14';BASE='/Game/BrainCraft';A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
name='M_Craft_C14_Tissue';mat=unreal.load_asset(BASE+'/Materials/'+name) or AT.create_asset(name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew());L.delete_all_material_expressions(mat);mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_SUBSURFACE);mat.set_editor_property('tangent_space_normal',False)
vc=L.create_material_expression(mat,unreal.MaterialExpressionVertexColor);n=L.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS);L.connect_material_property(vc,'',unreal.MaterialProperty.MP_BASE_COLOR);L.connect_material_property(n,'',unreal.MaterialProperty.MP_NORMAL)
for prop,value in [(unreal.MaterialProperty.MP_ROUGHNESS,.62),(unreal.MaterialProperty.MP_SPECULAR,.30),(unreal.MaterialProperty.MP_OPACITY,.85)]:
    c=L.create_material_expression(mat,unreal.MaterialExpressionConstant);c.set_editor_property('r',value);L.connect_material_property(c,'',prop)
sub=L.create_material_expression(mat,unreal.MaterialExpressionMultiply);sub.set_editor_property('const_b',.32);L.connect_material_expressions(vc,'',sub,'A');L.connect_material_property(sub,'',unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
visibility=L.create_material_expression(mat,unreal.MaterialExpressionScalarParameter);visibility.set_editor_property('parameter_name','Visibility');visibility.set_editor_property('default_value',1)
dither=L.create_material_expression(mat,unreal.MaterialExpressionMaterialFunctionCall);dither.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));L.connect_material_expressions(visibility,'',dither,'Alpha Threshold');L.connect_material_property(dither,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
errors=list(map(str,L.recompile_material(mat)));assert not errors,errors;A.save_loaded_asset(mat)
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');keys=json.loads((DATA/'mantle-patch.json').read_text())
if '-C14NestsOnly' in unreal.SystemLibrary.get_command_line():keys=['Nest0','Nest1','Nest2']
for key in keys:
    ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    d=ui.static_mesh_import_data;d.combine_meshes=True;d.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;d.auto_generate_collision=False;d.generate_lightmap_u_vs=False
    t=unreal.AssetImportTask();t.filename=str(ROOT/'Art/BrainCraft/ExportC14Mantle'/('SM_Craft_'+key+'.fbx'));t.destination_path=BASE+'/Models';t.destination_name='SM_Craft_'+key;t.automated=True;t.replace_existing=True;t.save=True;t.options=ui;AT.import_asset_tasks([t]);m=unreal.load_asset(BASE+'/Models/SM_Craft_'+key)
    material=unreal.load_asset(BASE+'/Materials/M_Craft_C14_Nest'+['Dawn','Spring','Memory'][int(key[-1])]) if key.startswith('NestGlow') else mat
    for i,_ in enumerate(m.get_editor_property('static_materials')):m.set_material(i,material)
    m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);bs=sms.get_lod_build_settings(m,0);bs.set_editor_property('max_lumen_mesh_cards',32);bs.set_editor_property('distance_field_resolution_scale',1);sms.set_lod_build_settings(m,0,bs);A.save_loaded_asset(m)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Maps/BrainCraft');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in actors.get_all_level_actors():
    if not any(key in [str(t) for t in actor.tags] for key in keys):continue
    c=actor.static_mesh_component
    for i,s in enumerate(c.static_mesh.get_editor_property('static_materials')):c.set_material(i,s.get_editor_property('material_interface'))
levels.save_current_level();(DATA/'mantle-native-readback.json').write_text(json.dumps(dict(imported=keys,material_errors=errors,art_accepted=False),indent=2));unreal.log('C14_FINAL_TISSUE_NATIVE_READY')
