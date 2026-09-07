import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir())
for name in ['import_c10_materials.py','import_c10_geometry.py']:
    p=root/'Tools'/name;exec(compile(p.read_text(),str(p),'exec'))
# Recompile final usage permutations after every asset and component is placed.
for path in unreal.EditorAssetLibrary.list_assets('/Game/BrainCraft/Materials',recursive=False):
    m=unreal.load_asset(path)
    if isinstance(m,unreal.Material):
        errors=unreal.MaterialEditingLibrary.recompile_material(m);assert not errors,(path,list(errors));unreal.EditorAssetLibrary.save_loaded_asset(m)
unreal.log('C10_FINAL_IMPORT_COMPLETE')
