"""C13 modular garden import and physically shaded, authored material families."""
import unreal,json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());DATA=ROOT/'Art/BrainCraft/Source/C13';BASE='/Game/BrainCraft';L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools()
def ex(m,c):return L.create_material_expression(m,c)
def prop(n,p):assert L.connect_material_property(n,'',p)
def const(m,v):n=ex(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',v);return n
def custom(m,code,args,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    n=ex(m,unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',kind);inputs=[]
    for key in args:i=unreal.CustomInput();i.set_editor_property('input_name',key);inputs.append(i)
    n.set_editor_property('inputs',inputs)
    for key,(v,out) in args.items():assert L.connect_material_expressions(v,out,n,key)
    return n
noise='''struct NField {
float hash(float3 p){p=frac(p*.1031);p+=dot(p,p.yzx+33.33);return frac((p.x+p.y)*p.z);}
float value(float3 p){float3 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(lerp(hash(i),hash(i+float3(1,0,0)),f.x),lerp(hash(i+float3(0,1,0)),hash(i+float3(1,1,0)),f.x),f.y),lerp(lerp(hash(i+float3(0,0,1)),hash(i+float3(1,0,1)),f.x),lerp(hash(i+float3(0,1,1)),hash(i+float3(1,1,1)),f.x),f.y),f.z);}
float fbm(float3 p){return value(p)*.58+value(p*2.07)*.28+value(p*4.31)*.14;}
};NField g;
'''
spec={'Turf':.85,'Stone':.61,'Earth':.94,'Grass':.68,'Fern':.53,'Clover':.62,'Iris':.48,'Coping':.59,'Masonry':.75,'BarkWood':.74,'BarkRidge':.67,'Tissue':.49,'WaterBlue':.15,'LeafGold':.48,'LeafGreen':.53,'PetalPink':.55,'PetalIvory':.58,'ThoughtGold':.34,'ThoughtCloud':.65,'ThoughtWisp':.35,'ThoughtKnot':.49}
foliage={'Grass','Fern','Clover','Iris','LeafGold','LeafGreen','PetalPink','PetalIvory'};report={};materials={}
for key,roughness in spec.items():
    if 'C13GeometryOnly' in unreal.SystemLibrary.get_command_line():
        materials[key]=unreal.load_asset(BASE+'/Materials/M_Craft_C13_'+key);assert materials[key],key;continue
    name='M_Craft_C13_'+key;m=unreal.load_asset(BASE+'/Materials/'+name) or AT.create_asset(name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew());L.delete_all_material_expressions(m)
    m.set_editor_property('tangent_space_normal',False);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);m.set_editor_property('two_sided',key in foliage or key=='WaterBlue')
    model=unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE if key in foliage else unreal.MaterialShadingModel.MSM_SUBSURFACE if key=='Tissue' else unreal.MaterialShadingModel.MSM_DEFAULT_LIT
    m.set_editor_property('shading_model',model)
    p=ex(m,unreal.MaterialExpressionWorldPosition);n=ex(m,unreal.MaterialExpressionVertexNormalWS);vc=ex(m,unreal.MaterialExpressionVertexColor);tm=ex(m,unreal.MaterialExpressionTime);uv=ex(m,unreal.MaterialExpressionTextureCoordinate)
    code='return C.rgb;'
    height='return g.fbm(P/5)*.16;'
    if key=='Turf':
        code=noise+'float patch=g.fbm(P/145);float fiber=g.value(P/3.1);return C.rgb*lerp(float3(.84,.93,.90),float3(1.14,1.08,.88),smoothstep(.2,.8,patch))*(.96+.08*fiber);'
        height='float pixel=max(length(ddx(P)),length(ddy(P)));return g.fbm(P/37)*2.9+g.fbm(P/3.4)*.55/(1+pixel/5);'
    elif key in {'Stone','Coping','Masonry'}:
        code=noise+'float wear=g.fbm(P/75);float grain=g.value(P/2.7);return C.rgb*(.91+.15*wear+.025*grain)*float3(.92,.99,1.02);'
        height='float pixel=max(length(ddx(P)),length(ddy(P)));return g.fbm(P/24)*.52+g.value(P/2.4)*.14/(1+pixel/3);'
    elif key=='Earth':code=noise+'return C.rgb*(.88+.24*g.fbm(P/75));';height='return g.fbm(P/9)*.35;'
    elif key in {'BarkWood','BarkRidge'}:
        code=noise+'return C.rgb*float3(.92,1.07,1.10)*(.86+.22*g.fbm(P/65));'
        height='return pow(saturate(.5+.5*sin(P.x*.19+P.y*.14+sin(P.z*.025)*1.6)),5)*.6+g.value(P/5)*.11;'
    elif key=='Tissue':code=noise+'return C.rgb*float3(.67,.62,.73)*(.95+.10*g.fbm(P/135));';height='return g.fbm(P/16)*.12;'
    elif key=='WaterBlue':code='return C.rgb*float3(.60,.72,.86);';height='return sin(P.x*.020+P.y*.013+T*.8)*1.5+sin(P.y*.027-P.x*.018-T*.65)*.75;'
    elif key in foliage:
        code='return C.rgb*float3(.86,.96,.88);'
        height='float vein=pow(saturate(1-abs(UV.x-.5)*18),2);return vein*.08+sin(UV.y*42+abs(UV.x-.5)*16)*.025;'
    elif key.startswith('Thought'):code='return C.rgb*.84;';height='return 0;'
    col=custom(m,code,{'P':(p,''),'C':(vc,'')});prop(col,unreal.MaterialProperty.MP_BASE_COLOR)
    ht=custom(m,noise+height,{'P':(p,''),'T':(tm,''),'UV':(uv,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    norm=custom(m,'float3 nn=normalize(N);float3 dx=ddx(P),dy=ddy(P);float3 r1=cross(dy,nn),r2=cross(nn,dx);float det=dot(dx,r1);return normalize(abs(det)*nn-sign(det)*(ddx(H)*r1+ddy(H)*r2));',{'N':(n,''),'P':(p,''),'H':(ht,'')});prop(norm,unreal.MaterialProperty.MP_NORMAL)
    rough=custom(m,noise+f'return clamp({roughness}+(g.fbm(P/38)-.5)*.14,.1,.98);',{'P':(p,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1);prop(rough,unreal.MaterialProperty.MP_ROUGHNESS);prop(const(m,.38 if key in {'Turf','Earth'} else .5),unreal.MaterialProperty.MP_SPECULAR)
    if key in foliage or key=='Tissue':
        sub=custom(m,'return C*float3(.70,.83,.48)*.48;' if key in foliage else 'return C*float3(.55,.23,.16);',{'C':(col,'')});prop(sub,unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
        if key=='Tissue':prop(const(m,.85),unreal.MaterialProperty.MP_OPACITY)
    if key in foliage:
        weight=ex(m,unreal.MaterialExpressionTextureCoordinate);weight.set_editor_property('coordinate_index',1 if key in {'Grass','Clover','Fern','Iris'} else 0)
        touch=ex(m,unreal.MaterialExpressionVectorParameter);touch.set_editor_property('parameter_name','AttentionPosition');touch.set_editor_property('default_value',unreal.LinearColor(0,0,-10000,1))
        motion='float w=saturate(UV.y);float2 d=P.xy-A.xy;float touch=saturate(1-length(d)/100)*saturate(1-abs(P.z-A.z)/120);float wind=sin(P.x*.003+P.y*.002+T*1.25)*2.3+sin(P.y*.009-T*1.7)*.8;return float3((float2(wind,wind*.55)+normalize(d+.01)*touch*18)*w*w,-touch*6*w*w);'
        wave=custom(m,motion,{'P':(p,''),'A':(touch,''),'UV':(weight,''),'T':(tm,'')});prop(wave,unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    if key in {'ThoughtGold','ThoughtWisp'}:
        life=ex(m,unreal.MaterialExpressionScalarParameter);life.set_editor_property('parameter_name','LifeGlow');life.set_editor_property('default_value',.18)
        emission=custom(m,'return C*G*.22;',{'C':(col,''),'G':(life,'')});prop(emission,unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    visibility=ex(m,unreal.MaterialExpressionScalarParameter);visibility.set_editor_property('parameter_name','Visibility');visibility.set_editor_property('default_value',1)
    dither=ex(m,unreal.MaterialExpressionMaterialFunctionCall);dither.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));assert L.connect_material_expressions(visibility,'',dither,'Alpha Threshold');assert L.connect_material_property(dither,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
    L.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);errors=list(map(str,L.recompile_material(m)));assert not errors,(key,errors);A.save_loaded_asset(m);materials[key]=m;report[key]=errors

unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
patch=json.loads((DATA/'patch.json').read_text());manifest=json.loads((DATA/'asset-manifest.json').read_text())
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for e in manifest:
    if e['key'] not in patch['changed']:continue
    ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    d=ui.static_mesh_import_data;d.combine_meshes=True;d.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;d.auto_generate_collision=False;d.generate_lightmap_u_vs=False
    t=unreal.AssetImportTask();t.filename=str(ROOT/'Art/BrainCraft/ExportC13'/(e['name']+'.fbx'));t.destination_path=BASE+'/Models';t.destination_name=e['name'];t.automated=True;t.replace_existing=True;t.save=True;t.options=ui;AT.import_asset_tasks([t]);m=unreal.load_asset(BASE+'/Models/'+e['name']);assert m
    for i,slot in enumerate(m.get_editor_property('static_materials')):
        key=str(slot.get_editor_property('material_slot_name')).split('.')[0].removeprefix('C13_');assert key in materials,key;m.set_material(i,materials[key])
    m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    if e['key'].startswith(('Terrain','Paving')):
        bs=sms.get_lod_build_settings(m,0);bs.set_editor_property('distance_field_resolution_scale',1.0);bs.set_editor_property('max_lumen_mesh_cards',24);sms.set_lod_build_settings(m,0,bs)
    A.save_loaded_asset(m)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Maps/BrainCraft')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in actors.get_all_level_actors():
    if 'BrainCraft' not in [str(t) for t in actor.tags]:continue
    if any(key in [str(t) for t in actor.tags] for key in patch['remove']+patch['changed']):actors.destroy_actor(actor)
for e in manifest:
    if e['key'] not in patch['changed'] or not e['spawn']:continue
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label('BrainCraft / '+e['key']);actor.tags=['BrainCraft',e['key']]+e['tags'];actor.set_actor_scale3d(unreal.Vector(1,-1,1));c=actor.static_mesh_component;c.set_static_mesh(unreal.load_asset(BASE+'/Models/'+e['name']));c.set_collision_profile_name('BlockAll');c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if 'Ground' in e['tags'] else unreal.CollisionEnabled.NO_COLLISION)
# Keep one shared material family on existing water, cortical tissue, garden
# stonework, trees and thoughts. Runtime spawned thoughts read the mesh slots.
for e in manifest:
    m=unreal.load_asset(BASE+'/Models/'+e['name'])
    if not m:continue
    updated=False
    for i,slot in enumerate(m.get_editor_property('static_materials')):
        old=slot.get_editor_property('material_interface');key=old.get_name().removeprefix('M_Craft_C11_') if old else ''
        if key in materials:m.set_material(i,materials[key]);updated=True
    if updated:A.save_loaded_asset(m)
for actor in actors.get_all_level_actors():
    if 'BrainCraft' not in [str(t) for t in actor.tags]:continue
    c=actor.static_mesh_component
    for i,slot in enumerate(c.static_mesh.get_editor_property('static_materials')):c.set_material(i,slot.get_editor_property('material_interface'))
levels.save_current_level();(DATA/'material-readback.json').write_text(json.dumps(report,indent=2));unreal.log('C13_MODULAR_GARDEN_IMPORTED')
