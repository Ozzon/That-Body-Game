"""C11 physically lit surfaces and native model import, with source readback."""
import unreal,json,math
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C11';BASE='/Game/BrainCraft';L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools()
def ex(m,c):return L.create_material_expression(m,c)
def wire(a,out,b,pin):assert L.connect_material_expressions(a,out,b,pin)
def prop(a,out,p):assert L.connect_material_property(a,out,p)
def const(m,v):n=ex(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',v);return n
def scalar(m,key,v):n=ex(m,unreal.MaterialExpressionScalarParameter);n.set_editor_property('parameter_name',key);n.set_editor_property('default_value',v);return n
def custom(m,code,args,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    n=ex(m,unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',kind);inputs=[]
    for key in args:i=unreal.CustomInput();i.set_editor_property('input_name',key);inputs.append(i)
    n.set_editor_property('inputs',inputs)
    for key,(node,out) in args.items():wire(node,out,n,key)
    return n
def material(key):
    name='M_Craft_'+key;m=unreal.load_asset(BASE+'/Materials/'+name) or AT.create_asset(name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew());L.delete_all_material_expressions(m);return m
noise='''struct GardenNoise {
float hash(float3 p){p=frac(p*.1031);p+=dot(p,p.yzx+33.33);return frac((p.x+p.y)*p.z);}
float value(float3 p){float3 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(lerp(hash(i),hash(i+float3(1,0,0)),f.x),lerp(hash(i+float3(0,1,0)),hash(i+float3(1,1,0)),f.x),f.y),lerp(lerp(hash(i+float3(0,0,1)),hash(i+float3(1,0,1)),f.x),lerp(hash(i+float3(0,1,1)),hash(i+float3(1,1,1)),f.x),f.y),f.z);}
float fbm(float3 p){return value(p)*.58+value(p*2.07)*.28+value(p*4.31)*.14;}
}; GardenNoise g;
'''
report={};palette=json.loads((DATA/'materials.json').read_text())
for key,spec in palette.items():
    m=material('C11_'+key);m.set_editor_property('tangent_space_normal',False);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
    foliage=key in ['LeafGreen','LeafGold','Grass','PetalPink','PetalIvory'];m.set_editor_property('two_sided',foliage or key.startswith('Portal') or key=='WaterBlue')
    if foliage:m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
    elif key=='Tissue':m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_SUBSURFACE)
    else:m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    pos=ex(m,unreal.MaterialExpressionWorldPosition);norm=ex(m,unreal.MaterialExpressionVertexNormalWS);vc=ex(m,unreal.MaterialExpressionVertexColor);tm=ex(m,unreal.MaterialExpressionTime);uv=ex(m,unreal.MaterialExpressionTextureCoordinate)
    visibility=scalar(m,'Visibility',1);dither=ex(m,unreal.MaterialExpressionMaterialFunctionCall);dither.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));wire(visibility,'',dither,'Alpha Threshold');prop(dither,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
    # Three distinct scales: modeled silhouette, restrained pigment variation,
    # then microstructure. Nothing bakes light or stains across the terrain.
    scale=370 if key=='Turf' else 140 if key in ['Tissue','BarkWood','BarkRidge'] else 65
    code=noise+f'float n=g.fbm(P/{scale}.0); return C.rgb*(.91+.18*n);'
    if key=='Turf':code=noise+'float n=g.fbm(P/410);float grass=g.value(P/8);return C.rgb*lerp(float3(.80,.88,.73),float3(1.15,1.15,.91),smoothstep(.22,.74,n))*(.96+.08*grass);'
    if key=='WaterBlue':code='float rip=sin(P.x*.018+T*.7)*sin(P.y*.022-T*.55);return C.rgb*(.88+rip*.10);'
    col=custom(m,code,{'C':(vc,''),'P':(pos,''),'T':(tm,'')});prop(col,'',unreal.MaterialProperty.MP_BASE_COLOR)
    amp=.18 if key in ['Paving','Coping','Masonry'] else .12 if key=='Turf' else .045
    height=custom(m,noise+f'return g.fbm(P/{4 if key in ["Paving","Masonry"] else 8}.0)*{amp};',{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    if key in ['BarkWood','BarkRidge']:height=custom(m,'return sin(P.z*.13+sin(P.x*.09)*3+P.y*.05)*.13;',{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    if key=='WaterBlue':height=custom(m,'return sin(P.x*.026+P.y*.017+T*1.15)*1.1+sin(P.y*.039-P.x*.022-T*.9)*.65;',{'P':(pos,''),'T':(tm,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    normal=custom(m,'float3 n=normalize(N);float3 x=ddx(P),y=ddy(P);float3 r1=cross(y,n),r2=cross(n,x);float d=dot(x,r1);return normalize(abs(d)*n-sign(d)*(ddx(H)*r1+ddy(H)*r2));',{'N':(norm,''),'P':(pos,''),'H':(height,'')});prop(normal,'',unreal.MaterialProperty.MP_NORMAL)
    rough=custom(m,noise+f'return clamp({spec["roughness"]}+(g.value(P/19)-.5)*.09,.08,.97);',{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1);prop(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);prop(const(m,.5),'',unreal.MaterialProperty.MP_SPECULAR)
    if foliage or key=='Tissue':
        sub=custom(m,'return C*float3(.75,.62,.40);' if key=='Tissue' else 'return C*.54;',{'C':(col,'')});prop(sub,'',unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
        if key=='Tissue':prop(const(m,.78),'',unreal.MaterialProperty.MP_OPACITY)
    if foliage:
        touch=ex(m,unreal.MaterialExpressionVectorParameter);touch.set_editor_property('parameter_name','AttentionPosition');touch.set_editor_property('default_value',unreal.LinearColor(0,0,-10000,1))
        weight=ex(m,unreal.MaterialExpressionTextureCoordinate);weight.set_editor_property('coordinate_index',1 if key=='Grass' else 0)
        if key=='Grass':code='float t=saturate(UV.y);float2 d=P.xy-A.xy;float b=saturate(1-length(d)/110)*saturate(1-abs(P.z-A.z)/130);float wind=sin(P.x*.004+P.y*.002+T*1.4)*5+sin(P.y*.014-T*2.4)*2;return float3((float2(wind,wind*.6)+normalize(d+.001)*b*28)*t*t,-b*12*t*t);'
        else:code='return float3(sin(P.x*.009+T*1.1)*2.4,cos(P.y*.01+T*.8)*1.8,sin(P.y*.007+P.x*.01+T*1.4)*1.2);'
        wpo=custom(m,code,{'P':(pos,''),'A':(touch,''),'UV':(weight,''),'T':(tm,'')});prop(wpo,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    if key.startswith('Portal'):
        # Local geometry UV maps the vertical arch. Animated annular swirls are
        # contained inside its aperture; each gateway retains its own hue.
        code='float2 q=UV*.65;float r=length(frac(q)-.5);float a=atan2(q.y-.5,q.x-.5);float swirl=pow(saturate(.5+.5*sin(r*38-a*3-T*1.5)),7);return C*(.15+swirl*2.5);'
        glow=custom(m,code,{'C':(vc,''),'UV':(uv,''),'T':(tm,'')});prop(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    elif key in ['ThoughtGold','ThoughtWisp','WaterFoam']:
        power=scalar(m,'LifeGlow',.22 if key=='ThoughtGold' else .12);glow=custom(m,'return C*G*.33;',{'C':(col,''),'G':(power,'')});prop(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    L.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);errors=L.recompile_material(m);report[key]=list(map(str,errors));assert not errors,(key,errors);A.save_loaded_asset(m)
# Tailored costume surfaces: wool/linen/leather, with fine woven response. This
# replaces the old noisy atlas but preserves authored seams and embroidery.
for key,col,rough in [('Sage',(.065,.19,.15),.76),('Linen',(.61,.58,.39),.86),('Leather',(.10,.055,.029),.54),('Face',(.88,.52,.17),.48),('Ink',(.013,.019,.027),.3),('Trim',(.64,.40,.12),.48)]:
    m=material(key);m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_CLOTH if key in ['Sage','Linen'] else unreal.MaterialShadingModel.MSM_DEFAULT_LIT);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_OPAQUE);m.set_editor_property('two_sided',True)
    c=ex(m,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(*col,1));prop(c,'',unreal.MaterialProperty.MP_BASE_COLOR);prop(const(m,rough),'',unreal.MaterialProperty.MP_ROUGHNESS);prop(const(m,.5),'',unreal.MaterialProperty.MP_SPECULAR)
    if key in ['Sage','Linen']:prop(c,'',unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
    errors=L.recompile_material(m);assert not errors,(key,errors);A.save_loaded_asset(m)
# Native deferred lighting remains responsible for shading and reflections.
# This mild luminance ramp only organizes shadow values and tint, preserving
# highlights and avoiding quantization of material colors.
m=material('CelLighting');m.set_editor_property('material_domain',unreal.MaterialDomain.MD_POST_PROCESS);m.set_editor_property('blendable_location',unreal.BlendableLocation.BL_SCENE_COLOR_BEFORE_DOF)
sc=ex(m,unreal.MaterialExpressionSceneTexture);sc.set_editor_property('scene_texture_id',unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0);df=ex(m,unreal.MaterialExpressionSceneTexture);df.set_editor_property('scene_texture_id',unreal.SceneTextureId.PPI_DIFFUSE_COLOR);depth=ex(m,unreal.MaterialExpressionSceneTexture);depth.set_editor_property('scene_texture_id',unreal.SceneTextureId.PPI_SCENE_DEPTH)
code='float l=max(dot(L.rgb/max(B.rgb,.05),float3(.2126,.7152,.0722)),.01);float e=log2(l)*2;float band=exp2((floor(e)+smoothstep(.2,.8,frac(e)))/2);float mask=(1-smoothstep(2,4,l))*step(.04,dot(B.rgb,1.0/3.0));float3 result=L.rgb*lerp(1,band/l,mask*.35);result*=lerp(float3(.80,.87,1.05),float3(1.02,1,.97),smoothstep(.1,.95,l));return D.r>28000?float3(.012,.023,.041):result;'
n=custom(m,code,{'L':(sc,'Color'),'B':(df,'Color'),'D':(depth,'Color')});prop(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);errors=L.recompile_material(m);assert not errors,errors;A.save_loaded_asset(m)
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
manifest=json.loads((DATA/'asset-manifest.json').read_text())
for e in manifest:
    ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    data=ui.static_mesh_import_data;data.combine_meshes=True;data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;data.auto_generate_collision=False;data.generate_lightmap_u_vs=False
    t=unreal.AssetImportTask();t.filename=str(ART/'ExportC11'/(e['name']+'.fbx'));t.destination_path=BASE+'/Models';t.destination_name=e['name'];t.automated=True;t.replace_existing=True;t.save=True;t.options=ui;AT.import_asset_tasks([t]);mesh=unreal.load_asset(BASE+'/Models/'+e['name']);assert mesh,e['key']
    for i,s in enumerate(mesh.get_editor_property('static_materials')):
        key=str(s.get_editor_property('material_slot_name')).split('.')[0];mat=unreal.load_asset(BASE+'/Materials/M_Craft_'+key);assert mat,(e['key'],key);mesh.set_material(i,mat)
    mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Maps/BrainCraft')
for actor in actors.get_all_level_actors():
    if 'BrainCraft' in [str(t) for t in actor.tags]:actors.destroy_actor(actor)
readback={}
for e in manifest:
    if not e['spawn']:continue
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label('BrainCraft / '+e['key']);actor.tags=['BrainCraft',e['key']]+e['tags'];actor.set_actor_scale3d(unreal.Vector(1,-1,1));comp=actor.static_mesh_component;mesh=unreal.load_asset(BASE+'/Models/'+e['name']);comp.set_static_mesh(mesh)
    for i,s in enumerate(mesh.get_editor_property('static_materials')):comp.set_material(i,s.get_editor_property('material_interface'))
    comp.set_collision_profile_name('BlockAll');comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if any(t in e['tags'] for t in ['Ground','Interactive','Occluder']) else unreal.CollisionEnabled.NO_COLLISION)
    if 'Shortcut' in e['tags']:comp.set_visibility(False);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    if e['key'].startswith('Nest'):
        bounds=actor.get_actor_bounds(False);readback[e['key']]=dict(center=[bounds[0].x,bounds[0].y,bounds[0].z],extent=[bounds[1].x,bounds[1].y,bounds[1].z])
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,'/Script/ThatBodyGame.BrainCraftGameMode'));levels.save_current_level()
for path in A.list_assets(BASE+'/Materials',recursive=False):
    mat=unreal.load_asset(path)
    if isinstance(mat,unreal.Material):errors=L.recompile_material(mat);assert not errors,(path,errors);A.save_loaded_asset(mat)
(DATA/'unreal-readback.json').write_text(json.dumps(dict(models=len(manifest),portals=readback,material_errors=report,art_accepted=False),indent=2));unreal.log('C11_NATIVE_WORLD_READY')
