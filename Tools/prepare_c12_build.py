import unreal

cape = unreal.load_asset('/Game/BrainCraft/Models/SM_Craft_AttentionCape')
assert cape is not None
cape.set_editor_property('allow_cpu_access', True)
assert unreal.EditorAssetLibrary.save_loaded_asset(cape)
assert cape.get_editor_property('allow_cpu_access')
unreal.log('C12_CAPE_CPU_ACCESS_READY')
