import unreal
lib=unreal.MaterialEditingLibrary
changes={'Tissue':(.57,.23,.25),'Cavity':(.24,.105,.16),'Stone':(.73,.53,.38),'Navy':(.022,.044,.063)}
for name,c in changes.items():
 mat=unreal.load_asset('/Game/Materials/M_'+name)
 lib.set_material_instance_vector_parameter_value(mat,'Color',unreal.LinearColor(*c,1))
 unreal.EditorAssetLibrary.save_loaded_asset(mat)
for name in ['Tissue','Cavity','Peach','Coral','Teal','Lilac','Cream','Blood','Sky','Sage','Plum','Blue','Stone']:
 mat=unreal.load_asset('/Game/Materials/M_'+name)
 lib.set_material_instance_scalar_parameter_value(mat,'InnerLight',.22)
 unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.log('BODY_PALETTE_REFINED')
