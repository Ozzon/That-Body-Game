import unreal,json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());DATA=ROOT/'Art/BrainCraft/Source/C15';BASE='/Game/BrainCraft';A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
def node(m,c):return L.create_material_expression(m,c)
def prop(n,p):assert L.connect_material_property(n,'',p)
def scalar(m,v,p):
    n=node(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',v);prop(n,p)
def custom(m,code,args,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    n=node(m,unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',kind);inputs=[]
    for key in args:i=unreal.CustomInput();i.set_editor_property('input_name',key);inputs.append(i)
    n.set_editor_property('inputs',inputs)
    for key,v in args.items():assert L.connect_material_expressions(v,'',n,key)
    return n
materials={};errors={}
for key in ['Tissue','Water']:
    name='M_Craft_C15_'+key+('R2' if key=='Water' else '');m=unreal.load_asset(BASE+'/Materials/'+name)
    if not m:
        m=AT.create_asset(name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);m.set_editor_property('tangent_space_normal',False)
        m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_SUBSURFACE if key=='Tissue' else unreal.MaterialShadingModel.MSM_DEFAULT_LIT);m.set_editor_property('two_sided',key=='Water')
        vc=node(m,unreal.MaterialExpressionVertexColor);n=node(m,unreal.MaterialExpressionVertexNormalWS);p=node(m,unreal.MaterialExpressionWorldPosition)
        if key=='Tissue':
            prop(vc,unreal.MaterialProperty.MP_BASE_COLOR);prop(n,unreal.MaterialProperty.MP_NORMAL)
            sub=custom(m,'return C*.30;',{'C':vc});prop(sub,unreal.MaterialProperty.MP_SUBSURFACE_COLOR);scalar(m,.85,unreal.MaterialProperty.MP_OPACITY)
            scalar(m,.52,unreal.MaterialProperty.MP_ROUGHNESS);scalar(m,.32,unreal.MaterialProperty.MP_SPECULAR)
        else:
            uv=node(m,unreal.MaterialExpressionTextureCoordinate);t=node(m,unreal.MaterialExpressionTime)
            col=custom(m,'float edge=pow(saturate(abs(UV.x*2-1)),12);float glint=pow(saturate(sin(UV.y*13-T*1.3+sin(UV.x*17))),28)*.10;return lerp(C.rgb,float3(.18,.34,.30),edge*.30)+glint*float3(.08,.13,.11);',{'C':vc,'UV':uv,'T':t});prop(col,unreal.MaterialProperty.MP_BASE_COLOR)
            h=custom(m,'return sin(P.x*.034+P.y*.023+T*1.1)*.7+sin(P.y*.051-P.x*.021-T*.8)*.35;',{'P':p,'T':t},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
            norm=custom(m,'float3 nn=normalize(N);float3 dx=ddx(P),dy=ddy(P);float3 r1=cross(dy,nn),r2=cross(nn,dx);float det=dot(dx,r1);return normalize(abs(det)*nn-sign(det)*(ddx(H)*r1+ddy(H)*r2));',{'N':n,'P':p,'H':h});prop(norm,unreal.MaterialProperty.MP_NORMAL)
            scalar(m,.20,unreal.MaterialProperty.MP_ROUGHNESS);scalar(m,.65,unreal.MaterialProperty.MP_SPECULAR)
        visibility=node(m,unreal.MaterialExpressionScalarParameter);visibility.set_editor_property('parameter_name','Visibility');visibility.set_editor_property('default_value',1)
        dither=node(m,unreal.MaterialExpressionMaterialFunctionCall);dither.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));L.connect_material_expressions(visibility,'',dither,'Alpha Threshold');L.connect_material_property(dither,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
    errors[key]=list(map(str,L.recompile_material(m)));assert not errors[key],errors[key];A.save_loaded_asset(m);materials[key]=m
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');patch=json.loads((DATA/'patch.json').read_text())
if '-C15SurfacesOnly' in unreal.SystemLibrary.get_command_line():patch['changed']=[e for e in patch['changed'] if not e['key'].startswith('Cortex')]
for e in patch['changed']:
    key=e['key'];ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    d=ui.static_mesh_import_data;d.combine_meshes=True;d.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;d.auto_generate_collision=False;d.generate_lightmap_u_vs=False
    t=unreal.AssetImportTask();t.filename=str(ROOT/'Art/BrainCraft/ExportC15'/('SM_Craft_'+key+'.fbx'));t.destination_path=BASE+'/Models';t.destination_name='SM_Craft_'+key;t.automated=True;t.replace_existing=True;t.save=True;t.options=ui;AT.import_asset_tasks([t]);m=unreal.load_asset(BASE+'/Models/SM_Craft_'+key);assert m
    for i,slot in enumerate(m.get_editor_property('static_materials')):
        family=e['material']
        if family=='Terrain':family=str(slot.get_editor_property('material_slot_name')).split('.')[0].removeprefix('C13_')
        mat=materials.get(family) or unreal.load_asset(BASE+'/Materials/M_Craft_C13_'+family);assert mat,family;m.set_material(i,mat)
    m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    bs=sms.get_lod_build_settings(m,0);bs.set_editor_property('max_lumen_mesh_cards',32);bs.set_editor_property('distance_field_resolution_scale',1);sms.set_lod_build_settings(m,0,bs);A.save_loaded_asset(m)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Maps/BrainCraft');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
keys={e['key'] for e in patch['changed']}
for actor in actors.get_all_level_actors():
    tags=set(map(str,actor.tags))
    if 'BrainCraft' not in tags:continue
    component=actor.get_component_by_class(unreal.StaticMeshComponent)
    mesh_key=component.static_mesh.get_name().removeprefix('SM_Craft_') if component and component.static_mesh else ''
    if mesh_key in keys|set(patch['remove']):actors.destroy_actor(actor)
for e in patch['changed']:
    if not e.get('spawn',True):continue
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label('BrainCraft / '+e['key']);actor.tags=['BrainCraft',e['key']]+e['tags'];actor.set_actor_scale3d(unreal.Vector(1,-1,1));c=actor.static_mesh_component;c.set_static_mesh(unreal.load_asset(BASE+'/Models/SM_Craft_'+e['key']));c.set_collision_profile_name('BlockAll');c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if any(t in e['tags'] for t in ['Ground','Occluder']) else unreal.CollisionEnabled.NO_COLLISION)
# A consistent physical water family is shared by the springs and cascades.
# Restore the four existing water pieces removed by r01's ambiguous "Water"
# category/key match. Subsequent imports identify assets by mesh name.
existing={a.static_mesh_component.static_mesh.get_name() for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh}
for key in ['UpperSpringWater','MiddleSpringWater','Cascade0','Cascade1']:
    if 'SM_Craft_'+key in existing:continue
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label('BrainCraft / '+key);actor.tags=['BrainCraft',key,'Water'];actor.set_actor_scale3d(unreal.Vector(1,-1,1));c=actor.static_mesh_component;c.set_static_mesh(unreal.load_asset(BASE+'/Models/SM_Craft_'+key));c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
for actor in actors.get_all_level_actors():
    if 'BrainCraft' not in list(map(str,actor.tags)) or 'Water' not in list(map(str,actor.tags)):continue
    c=actor.static_mesh_component
    for i,_ in enumerate(c.static_mesh.get_editor_property('static_materials')):c.set_material(i,materials['Water'])
levels.save_current_level();(DATA/'native-readback.json').write_text(json.dumps(dict(imported=sorted(keys),removed=patch['remove'],material_errors=errors,art_accepted=False),indent=2));unreal.log('C15_GARDEN_NATIVE_READY')
