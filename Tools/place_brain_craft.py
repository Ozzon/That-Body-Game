"""Place already imported craft assets without rebuilding their materials."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());art=root/'Art/BrainCraft';base='/Game/BrainCraft';assets=unreal.EditorAssetLibrary
manifest=json.loads((art/'asset-manifest.json').read_text());actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if assets.does_asset_exist('/Game/Maps/BrainCraft'):levels.load_level('/Game/Maps/BrainCraft')
else:levels.new_level('/Game/Maps/BrainCraft')
for a in actors.get_all_level_actors():
    if 'BrainCraft' in [str(t) for t in a.tags]:actors.destroy_actor(a)
for e in manifest:
    if not e['spawn']:continue
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label('BrainCraft / '+e['key']);a.tags=['BrainCraft',e['key']]+e['tags'];c=a.static_mesh_component
    m=unreal.load_asset(base+'/Models/'+e['name']);assert m,e['name'];c.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(1,-1,1))
    c.set_collision_profile_name('BlockAll')
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if any(t in e['tags'] for t in ['Ground','Occluder','Interactive']) else unreal.CollisionEnabled.NO_COLLISION)
    if 'Shortcut' in e['tags']:c.set_visibility(False);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();mode=unreal.load_class(None,'/Script/ThatBodyGame.BrainCraftGameMode');assert mode;world.get_world_settings().set_editor_property('default_game_mode',mode)
levels.save_current_level();report=dict(map='/Game/Maps/BrainCraft',models=len(manifest),spawned=sum(e['spawn'] for e in manifest),mode=mode.get_path_name(),art_accepted=False);(art/'unreal-import-report.json').write_text(json.dumps(report,indent=2));unreal.log('CRAFT_IMPORTED '+json.dumps(report))
