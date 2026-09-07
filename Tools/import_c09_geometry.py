import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());art=root/'Art/BrainCraft';base='/Game/BrainCraft';assets=unreal.EditorAssetLibrary;lib=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
manifest=json.loads((art/'asset-manifest.json').read_text());changed=json.loads((art/'Source/C09/changed-assets.json').read_text())
for e in manifest:
    if e['name'] not in changed:continue
    ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;data=ui.static_mesh_import_data;data.combine_meshes=True;data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;data.auto_generate_collision=False;data.generate_lightmap_u_vs=False
    task=unreal.AssetImportTask();task.filename=str(art/'Export'/(e['name']+'.fbx'));task.destination_path=base+'/Models';task.destination_name=e['name'];task.automated=True;task.replace_existing=True;task.save=True;task.options=ui;at.import_asset_tasks([task]);m=unreal.load_asset(base+'/Models/'+e['name'])
    for i,slot in enumerate(m.get_editor_property('static_materials')):
        key=str(slot.get_editor_property('material_slot_name')).split('.')[0];mat=unreal.load_asset(base+'/Materials/M_Craft_'+key)
        if not mat:mat=unreal.load_asset(base+'/Materials/M_Craft_'+e['materials'][min(i,len(e['materials'])-1)])
        assert mat;(m.set_material(i,mat))
    m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assets.save_loaded_asset(m)
exec(compile((root/'Tools/place_brain_craft.py').read_text(),str(root/'Tools/place_brain_craft.py'),'exec'))
report={}
for e in manifest:
    m=unreal.load_asset(base+'/Models/'+e['name']);report[e['name']]=[str(s.get_editor_property('material_interface').get_path_name()) if s.get_editor_property('material_interface') else None for s in m.get_editor_property('static_materials')]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if 'BrainCraft' not in [str(t) for t in a.tags]:continue
    comp=a.static_mesh_component
    for i,slot in enumerate(comp.static_mesh.get_editor_property('static_materials')):
        mat=slot.get_editor_property('material_interface')
        if mat:comp.set_material(i,mat)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(art/'material-readback-c09.json').write_text(json.dumps(report,indent=2))
for key in list(json.loads((art/'material-manifest.json').read_text())):
    m=unreal.load_asset(base+'/Materials/M_Craft_'+key);errors=lib.recompile_material(m);assert not errors,(key,list(errors));assets.save_loaded_asset(m)
unreal.log('C09_GEOMETRY_IMPORTED')

