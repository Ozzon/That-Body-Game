"""Import the C14 connected garden and read back its native architecture."""
import unreal,json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());DATA=ROOT/'Art/BrainCraft/Source/C14';BASE='/Game/BrainCraft';A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
patch=json.loads((DATA/'patch.json').read_text());keys=patch['changed'];unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
for key in keys:
    if '-C14MaterialsOnly' in unreal.SystemLibrary.get_command_line():break
    ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    d=ui.static_mesh_import_data;d.combine_meshes=True;d.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;d.auto_generate_collision=False;d.generate_lightmap_u_vs=False
    task=unreal.AssetImportTask();task.filename=str(ROOT/'Art/BrainCraft/ExportC14'/('SM_Craft_'+key+'.fbx'));task.destination_path=BASE+'/Models';task.destination_name='SM_Craft_'+key;task.automated=True;task.replace_existing=True;task.save=True;task.options=ui;AT.import_asset_tasks([task]);m=unreal.load_asset(BASE+'/Models/SM_Craft_'+key)
    for i,s in enumerate(m.get_editor_property('static_materials')):
        name=str(s.get_editor_property('material_slot_name')).split('.')[0];mat=unreal.load_asset(BASE+'/Materials/M_Craft_'+name);assert mat,name;m.set_material(i,mat)
    m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    bs=sms.get_lod_build_settings(m,0);bs.set_editor_property('distance_field_resolution_scale',0 if key.startswith('Botany') else 1);bs.set_editor_property('max_lumen_mesh_cards',32 if key.startswith(('Cortex','Nest')) else 24);sms.set_lod_build_settings(m,0,bs);A.save_loaded_asset(m)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Maps/BrainCraft');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);found=set();gates={}
for actor in actors.get_all_level_actors():
    tags=[str(t) for t in actor.tags]
    if 'BrainCraft' not in tags:continue
    key=next((k for k in keys if k in tags),None)
    if not key:continue
    found.add(key);c=actor.static_mesh_component
    for i,s in enumerate(c.static_mesh.get_editor_property('static_materials')):c.set_material(i,s.get_editor_property('material_interface'))
    if key.startswith('Botany'):c.set_editor_property('affect_distance_field_lighting',False)
    if key.startswith('Nest'):
        tags=[t for t in tags if t!='Occluder'];actor.tags=tags;c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION if key.startswith('NestGlow') else unreal.CollisionEnabled.QUERY_AND_PHYSICS);center,extent=actor.get_actor_bounds(False);gates[key]={'center':[center.x,center.y,center.z],'extent':[extent.x,extent.y,extent.z],'tags':tags}
for key in keys:
    if key in found:continue
    assert key.startswith('Paving'),key
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label('BrainCraft / '+key);a.tags=['BrainCraft',key];a.set_actor_scale3d(unreal.Vector(1,-1,1));a.static_mesh_component.set_static_mesh(unreal.load_asset(BASE+'/Models/SM_Craft_'+key));a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
# Correct the swirl's local aperture coordinates. A bright coiled center sits
# inside a dark blue/violet recess; real geometry defines the surrounding lip.
for color in ['Dawn','Spring','Memory']:
    name='M_Craft_C14_Nest'+color;m=unreal.load_asset(BASE+'/Materials/'+name) or AT.create_asset(name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew());L.delete_all_material_expressions(m);m.set_editor_property('two_sided',True);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_OPAQUE);m.set_editor_property('tangent_space_normal',True)
    vc=L.create_material_expression(m,unreal.MaterialExpressionVertexColor);uv=L.create_material_expression(m,unreal.MaterialExpressionTextureCoordinate);tm=L.create_material_expression(m,unreal.MaterialExpressionTime)
    node=L.create_material_expression(m,unreal.MaterialExpressionCustom);node.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);node.set_editor_property('code','float2 q=(UV-.5)*2;float r=length(q);float a=atan2(q.y,q.x);float coil=pow(saturate(.5+.5*cos(r*18-a*3-T*1.35)),9);float core=exp(-r*r*16);float edge=1-smoothstep(.75,1,r);return C*(.07+(coil*1.8+core*2.0)*edge);')
    inputs=[]
    for name in ['C','UV','T']:i=unreal.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
    node.set_editor_property('inputs',inputs)
    for name,source in [('C',vc),('UV',uv),('T',tm)]:assert L.connect_material_expressions(source,'',node,name)
    assert L.connect_material_property(node,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    base=L.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);base.set_editor_property('constant',unreal.LinearColor(.025,.012,.065,1));L.connect_material_property(base,'',unreal.MaterialProperty.MP_BASE_COLOR)
    rough=L.create_material_expression(m,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.31);L.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    normal=L.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);normal.set_editor_property('constant',unreal.LinearColor(0,0,1,1));L.connect_material_property(normal,'',unreal.MaterialProperty.MP_NORMAL)
    errors=list(map(str,L.recompile_material(m)));assert not errors,(color,errors);A.save_loaded_asset(m)
    key='NestGlow'+str(['Dawn','Spring','Memory'].index(color));mesh=unreal.load_asset(BASE+'/Models/SM_Craft_'+key);mesh.set_material(0,m);A.save_loaded_asset(mesh)
    for actor in actors.get_all_level_actors():
        if key in [str(t) for t in actor.tags]:actor.static_mesh_component.set_material(0,m)
levels.save_current_level();(DATA/'native-readback.json').write_text(json.dumps(dict(imported=len(keys),gates=gates,art_accepted=False),indent=2));unreal.log('C14_CONNECTED_GARDEN_NATIVE_READY')
