import unreal, os

root=unreal.Paths.project_dir()
unreal.EditorAssetLibrary.make_directory('/Game/Materials')
unreal.EditorAssetLibrary.make_directory('/Game/Maps')
unreal.EditorAssetLibrary.make_directory('/Game/Audio')
palette={
 'Tissue':(0.42,0.16,0.18),'Cavity':(0.12,0.065,0.105),
 'Peach':(0.91,0.48,0.36),'Coral':(0.83,0.25,0.24),
 'Teal':(0.13,0.39,0.36),'Lilac':(0.49,0.32,0.66),
 'Cream':(0.95,0.81,0.60),'Navy':(0.019,0.033,0.057),
 'Gold':(0.97,0.62,0.18),'Blood':(0.46,0.075,0.11),
 'Sky':(0.31,0.70,0.79),'Sage':(0.43,0.60,0.35),
 'Plum':(0.23,0.16,0.32),'Blue':(0.08,0.27,0.48),
 'Stone':(0.73,0.63,0.45),'Glow':(0.29,0.88,0.76)
}
lib=unreal.MaterialEditingLibrary
for name,c in {'Toon':(1.0,1.0,1.0)}.items():
 path='/Game/Materials/M_'+name
 mat=unreal.load_asset(path)
 if not mat: mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_'+name,'/Game/Materials',unreal.Material,unreal.MaterialFactoryNew())
 lib.delete_all_material_expressions(mat)
 mat.set_editor_property('two_sided',True)
 mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
 color=lib.create_material_expression(mat,unreal.MaterialExpressionVectorParameter,-600,0)
 color.set_editor_property('parameter_name','Color')
 color.set_editor_property('default_value',unreal.LinearColor(*c,1))
 normal=lib.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS,-600,170)
 custom=lib.create_material_expression(mat,unreal.MaterialExpressionCustom,-280,0)
 custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
 custom.set_editor_property('description','Three soft cel-shading bands')
 a=unreal.CustomInput();a.set_editor_property('input_name','C')
 b=unreal.CustomInput();b.set_editor_property('input_name','N')
 custom.set_editor_property('inputs',[a,b])
 custom.set_editor_property('code','float d=dot(normalize(N),normalize(float3(-0.35,-0.45,0.82))); float band=d>0.55?1.08:(d>0.02?0.82:0.49); return C*band;')
 lib.connect_material_expressions(color,'',custom,'C');lib.connect_material_expressions(normal,'',custom,'N')
 lib.connect_material_property(custom,'',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-200,220);rough.set_editor_property('r',0.83)
 lib.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 ambient=lib.create_material_expression(mat,unreal.MaterialExpressionMultiply,-80,340)
 lib.connect_material_expressions(custom,'',ambient,'A')
 amount=lib.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-300,440)
 amount.set_editor_property('parameter_name','InnerLight');amount.set_editor_property('default_value',0.13)
 lib.connect_material_expressions(amount,'',ambient,'B')
 lib.connect_material_property(ambient,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 lib.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)

master=unreal.load_asset('/Game/Materials/M_Toon')
for name,c in palette.items():
 mat=unreal.load_asset('/Game/Materials/M_'+name)
 if not mat:mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_'+name,'/Game/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
 lib.set_material_instance_parent(mat,master)
 lib.set_material_instance_vector_parameter_value(mat,'Color',unreal.LinearColor(*c,1))
 lib.set_material_instance_scalar_parameter_value(mat,'InnerLight',1.2 if name=='Glow' else 0.32 if name=='Gold' else 0.13)
 unreal.EditorAssetLibrary.save_loaded_asset(mat)

for name in ['Breath','Heart','Chime','Swat']:
 task=unreal.AssetImportTask();task.set_editor_property('filename',os.path.join(root,'Tools','Audio',name+'.wav'))
 task.set_editor_property('destination_path','/Game/Audio');task.set_editor_property('automated',True);task.set_editor_property('save',True);task.set_editor_property('replace_existing',True)
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level('/Game/Maps/BodyGarden')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.EditorAssetLibrary.save_directory('/Game',only_if_is_dirty=False,recursive=True)
unreal.log('BODY_CONTENT_CREATED')
