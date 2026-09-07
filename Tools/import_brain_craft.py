"""C06 assets and map. Prior maps, approved heart, and rejected evidence untouched."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());art=root/'Art/BrainCraft';base='/Game/BrainCraft';lib=unreal.MaterialEditingLibrary;assets=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
for folder in ['Materials','Models','Textures']:assets.make_directory(base+'/'+folder)
def expr(m,cls,x=0,y=0):return lib.create_material_expression(m,cls,x,y)
def connect(a,out,b,pin):assert lib.connect_material_expressions(a,out,b,pin)
def prop(a,out,p):assert lib.connect_material_property(a,out,p)
def constant(m,v):n=expr(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',float(v));return n
def scalar(m,key,v):n=expr(m,unreal.MaterialExpressionScalarParameter);n.set_editor_property('parameter_name',key);n.set_editor_property('default_value',float(v));return n
def mul(m,a,b):n=expr(m,unreal.MaterialExpressionMultiply);connect(a,'',n,'A');connect(b,'',n,'B');return n

for file in (art/'Textures').glob('T_*_*.png'):
    if file.stem=='T_Cortex_Painted_BaseColor':continue
    task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=base+'/Textures';task.destination_name=file.stem;task.automated=True;task.replace_existing=True;task.save=True;at.import_asset_tasks([task])
    t=unreal.load_asset(base+'/Textures/'+file.stem)
    if file.stem.endswith('_Normal'):t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);t.set_editor_property('srgb',False);t.set_editor_property('flip_green_channel',True);assets.save_loaded_asset(t)

mats={}
for key,spec in json.loads((art/'material-manifest.json').read_text()).items():
    name='M_Craft_'+key;m=unreal.load_asset(base+'/Materials/'+name)
    if not m:m=at.create_asset(name,base+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(m);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);m.set_editor_property('two_sided',key in ['Leaf','Water','Sage','Current'])
    uv=expr(m,unreal.MaterialExpressionTextureCoordinate,-1000,0)
    if key=='Water':
        pan=expr(m,unreal.MaterialExpressionPanner);pan.set_editor_property('speed_x',.012);pan.set_editor_property('speed_y',.025);connect(uv,'',pan,'Coordinate');uv=pan
    tex=expr(m,unreal.MaterialExpressionTextureSample,-700,0);tex.set_editor_property('texture',unreal.load_asset(base+'/Textures/T_'+key+'_BaseColor'));connect(uv,'',tex,'UVs');prop(tex,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
    if key=='Earth':
        moss=expr(m,unreal.MaterialExpressionTextureSample);moss.set_editor_property('texture',unreal.load_asset(base+'/Textures/T_Moss_BaseColor'));connect(uv,'',moss,'UVs');vc=expr(m,unreal.MaterialExpressionVertexColor);blend=expr(m,unreal.MaterialExpressionLinearInterpolate);connect(moss,'RGB',blend,'A');connect(tex,'RGB',blend,'B');connect(vc,'R',blend,'Alpha');prop(blend,'',unreal.MaterialProperty.MP_BASE_COLOR)
    normal=expr(m,unreal.MaterialExpressionTextureSample,-700,220);normal.set_editor_property('texture',unreal.load_asset(base+'/Textures/T_'+key+'_Normal'));normal.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL);connect(uv,'',normal,'UVs')
    flat=expr(m,unreal.MaterialExpressionConstant3Vector);flat.set_editor_property('constant',unreal.LinearColor(0,0,1,1));normalblend=expr(m,unreal.MaterialExpressionLinearInterpolate);connect(flat,'',normalblend,'A');connect(normal,'RGB',normalblend,'B');connect(constant(m,.24 if key in ['Cortex','Stone','Moss'] else .4),'',normalblend,'Alpha');prop(normalblend,'',unreal.MaterialProperty.MP_NORMAL)
    if key in ['Cortex','Stone','Moss']:
        # Continuous world projection prevents per-polygon UV seams on sculpted
        # tissue and fitted terraces. Broad painted detail survives close cameras.
        texobj=expr(m,unreal.MaterialExpressionTextureObject);texobj.set_editor_property('texture',unreal.load_asset(base+'/Textures/T_'+key+'_BaseColor'));wp=expr(m,unreal.MaterialExpressionWorldPosition);wn=expr(m,unreal.MaterialExpressionPixelNormalWS);triplanar=expr(m,unreal.MaterialExpressionCustom);triplanar.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
        inputs=[]
        for kk in ['Tex','P','N']:
            ci=unreal.CustomInput();ci.set_editor_property('input_name',kk);inputs.append(ci)
        triplanar.set_editor_property('inputs',inputs);size={'Cortex':1100,'Stone':260,'Moss':380}[key];triplanar.set_editor_property('code',f'float3 w=pow(abs(N),6);w/=max(w.x+w.y+w.z,.001);float3 q=P/{size}.0;return Texture2DSample(Tex,TexSampler,q.yz).rgb*w.x+Texture2DSample(Tex,TexSampler,q.xz).rgb*w.y+Texture2DSample(Tex,TexSampler,q.xy).rgb*w.z;');connect(texobj,'',triplanar,'Tex');connect(wp,'',triplanar,'P');connect(wn,'',triplanar,'N');prop(triplanar,'',unreal.MaterialProperty.MP_BASE_COLOR)
    prop(constant(m,spec['roughness']),'',unreal.MaterialProperty.MP_ROUGHNESS);prop(constant(m,.28),'',unreal.MaterialProperty.MP_SPECULAR)
    power=scalar(m,'LifeGlow',spec['emission']);emit=expr(m,unreal.MaterialExpressionMultiply);connect(tex,'RGB',emit,'A');connect(power,'',emit,'B');prop(emit,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    visibility=scalar(m,'Visibility',1);d=expr(m,unreal.MaterialExpressionMaterialFunctionCall);d.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));connect(visibility,'',d,'Alpha Threshold');prop(d,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
    if key=='Leaf':
        # World-position-driven flex, anchored by a low amplitude so silhouettes stay legible.
        pos=expr(m,unreal.MaterialExpressionWorldPosition);tm=expr(m,unreal.MaterialExpressionTime);custom=expr(m,unreal.MaterialExpressionCustom);custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);custom.set_editor_property('code','return float3(sin(P.x*.007+T*1.3),cos(P.y*.009+T),sin(P.x*.005+P.y*.006+T*1.4)) * 2.5;')
        inputs=[]
        for name0,node,out in [('P',pos,''),('T',tm,'')]:
            ci=unreal.CustomInput();ci.set_editor_property('input_name',name0);inputs.append(ci)
        custom.set_editor_property('inputs',inputs);connect(pos,'',custom,'P');connect(tm,'',custom,'T');prop(custom,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    if key in ['Light','Current']:lib.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
    lib.recompile_material(m);assets.save_loaded_asset(m);mats[key]=m

# Light-band postprocess preserves albedo. Quantization acts on estimated diffuse
# illumination, with soft transitions, not on each painted RGB channel.
name='M_Craft_CelLighting';m=unreal.load_asset(base+'/Materials/'+name)
if not m:m=at.create_asset(name,base+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
lib.delete_all_material_expressions(m);m.set_editor_property('material_domain',unreal.MaterialDomain.MD_POST_PROCESS);m.set_editor_property('blendable_location',unreal.BlendableLocation.BL_SCENE_COLOR_BEFORE_DOF)
scene=expr(m,unreal.MaterialExpressionSceneTexture);scene.set_editor_property('scene_texture_id',unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
diffuse=expr(m,unreal.MaterialExpressionSceneTexture);diffuse.set_editor_property('scene_texture_id',unreal.SceneTextureId.PPI_DIFFUSE_COLOR)
custom=expr(m,unreal.MaterialExpressionCustom);custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
inputs=[]
for k in ['Lit','Paint']:
    i=unreal.CustomInput();i.set_editor_property('input_name',k);inputs.append(i)
custom.set_editor_property('inputs',inputs);custom.set_editor_property('code','float L=max(dot(Lit.rgb/max(Paint.rgb,float3(.075,.075,.075)),float3(.2126,.7152,.0722)),.001); float e=log2(L)*2.0; float f=frac(e); float band=exp2((floor(e)+smoothstep(.30,.70,f))/2.0); float valid=step(.04,dot(Paint.rgb,float3(.333,.333,.333)))*(1-smoothstep(3.0,7.0,L)); float ratio=lerp(1,band/L,valid*.55); float3 shade=lerp(float3(.90,.93,1.04),float3(1,1,1),smoothstep(.08,.7,L)); return Lit.rgb*ratio*lerp(float3(1,1,1),shade,valid*.35);')
connect(scene,'Color',custom,'Lit');connect(diffuse,'Color',custom,'Paint');prop(custom,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);lib.recompile_material(m);assets.save_loaded_asset(m)

unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
manifest=json.loads((art/'asset-manifest.json').read_text())
for e in manifest:
    ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    data=ui.static_mesh_import_data;data.combine_meshes=True;data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;data.auto_generate_collision=False;data.generate_lightmap_u_vs=False
    task=unreal.AssetImportTask();task.filename=str(art/'Export'/(e['name']+'.fbx'));task.destination_path=base+'/Models';task.destination_name=e['name'];task.automated=True;task.replace_existing=True;task.save=True;task.options=ui;at.import_asset_tasks([task])
    mesh=unreal.load_asset(base+'/Models/'+e['name']);assert mesh
    # Imported FBX material slots retain source names, including merged meshes.
    slots=mesh.get_editor_property('static_materials')
    for i,slot in enumerate(slots):
        key=str(slot.get_editor_property('material_slot_name'));key=key.split('.')[0]
        if key not in mats:key=e['materials'][min(i,len(e['materials'])-1)]
        mesh.set_material(i,mats[key])
    bs=mesh.get_editor_property('body_setup');bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assets.save_loaded_asset(mesh)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if assets.does_asset_exist('/Game/Maps/BrainCraft'):levels.load_level('/Game/Maps/BrainCraft')
else:levels.new_level('/Game/Maps/BrainCraft')
for a in actors.get_all_level_actors():
    if 'BrainCraft' in [str(t) for t in a.tags]:actors.destroy_actor(a)
for e in manifest:
    if not e['spawn']:continue
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label('BrainCraft / '+e['key']);a.tags=['BrainCraft',e['key']]+e['tags'];c=a.static_mesh_component;c.set_static_mesh(unreal.load_asset(base+'/Models/'+e['name']));a.set_actor_scale3d(unreal.Vector(1,-1,1))
    c.set_collision_profile_name('BlockAll')
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if any(t in e['tags'] for t in ['Ground','Occluder','Interactive']) else unreal.CollisionEnabled.NO_COLLISION)
    if 'Shortcut' in e['tags']:c.set_visibility(False);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,'/Script/ThatBodyGame.BrainCraftGameMode'))
levels.save_current_level();report=dict(map='/Game/Maps/BrainCraft',models=len(manifest),materials=len(mats)+1,spawned=sum(e['spawn'] for e in manifest),art_accepted=False);(art/'unreal-import-report.json').write_text(json.dumps(report,indent=2));unreal.log('CRAFT_IMPORTED '+json.dumps(report))
