import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());report={}
for path in unreal.EditorAssetLibrary.list_assets('/Game/BrainCraft/Materials',recursive=False):
    m=unreal.load_asset(path)
    if not isinstance(m,unreal.Material):continue
    errors=unreal.MaterialEditingLibrary.recompile_material(m)
    report[m.get_name()]=[str(e) for e in errors] if errors else []
    unreal.log('CRAFT_SHADER_ERRORS '+m.get_name()+' '+str(report[m.get_name()]))
(root/'Art/BrainCraft/shader-diagnostic.json').write_text(json.dumps(report,indent=2))
