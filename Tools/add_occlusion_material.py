import unreal
lib=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/Materials/M_Toon')
mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
visibility=lib.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-550,650)
visibility.set_editor_property('parameter_name','Visibility');visibility.set_editor_property('default_value',1.0)
dither=lib.create_material_expression(mat,unreal.MaterialExpressionMaterialFunctionCall,-220,650)
dither.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'))
lib.connect_material_expressions(visibility,'',dither,'Alpha Threshold')
lib.connect_material_property(dither,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
lib.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.log('BODY_OCCLUSION_MATERIAL_READY')
