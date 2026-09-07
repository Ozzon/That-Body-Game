"""Versioned C17 environment assets and materials. Preserve the C16 package."""
import unreal,json,shutil
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());DATA=ROOT/'Art/BrainCraft/Source/C17';BASE='/Game/BrainCraft'
A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
def node(m,c):return L.create_material_expression(m,c)
def prop(n,p):assert L.connect_material_property(n,'',p)
def constant(m,v,p):
    n=node(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',v);prop(n,p)
def custom(m,code,args,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    n=node(m,unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',kind)
    inputs=[]
    for k in args:i=unreal.CustomInput();i.set_editor_property('input_name',k);inputs.append(i)
    n.set_editor_property('inputs',inputs)
    for k,v in args.items():assert L.connect_material_expressions(v,'',n,k)
    return n

texture_path=BASE+'/Textures/T_C17_Moss_BaseColor'
if not A.does_asset_exist(texture_path):
    task=unreal.AssetImportTask();task.filename=str(ROOT/'Art/BrainCraft/Textures/T_C17_Moss_BaseColor.png');task.destination_path=BASE+'/Textures';task.destination_name='T_C17_Moss_BaseColor';task.automated=True;task.save=True;AT.import_asset_tasks([task])
texture=unreal.load_asset(texture_path);assert texture
texture.set_editor_property('srgb',True);texture.set_editor_property('lod_group',unreal.TextureGroup.TEXTUREGROUP_WORLD);A.save_loaded_asset(texture)

field='''struct Field {
float hash(float3 p){p=frac(p*.1031);p+=dot(p,p.yzx+33.33);return frac((p.x+p.y)*p.z);}
float value(float3 p){float3 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(lerp(hash(i),hash(i+float3(1,0,0)),f.x),lerp(hash(i+float3(0,1,0)),hash(i+float3(1,1,0)),f.x),f.y),lerp(lerp(hash(i+float3(0,0,1)),hash(i+float3(1,0,1)),f.x),lerp(hash(i+float3(0,1,1)),hash(i+float3(1,1,1)),f.x),f.y),f.z);}
float height(float3 p){return value(p/17)*.38+value(p/3.6)*.12;}
};Field g;
'''
quilt='''struct MossQuilt {
float2 hash(float2 p){return frac(sin(float2(dot(p,float2(127.1,311.7)),dot(p,float2(269.5,183.3))))*43758.5453);}
float3 fetchColor(Texture2D tx,SamplerState ss,float2 uv){
float2 s=float2(uv.x-uv.y*.57735027,uv.y*1.15470054);float2 i=floor(s);float2 f=frac(s);float3 w;float2 a,b,c;
if(f.x+f.y<1){a=i;b=i+float2(1,0);c=i+float2(0,1);w=float3(1-f.x-f.y,f.x,f.y);}
else{a=i+1;b=i+float2(0,1);c=i+float2(1,0);w=float3(f.x+f.y-1,1-f.x,1-f.y);}
w=w*w;w/=dot(w,1.0);
float3 ca=Texture2DSampleGrad(tx,ss,uv+hash(a)*13.1,ddx(uv),ddy(uv)).rgb;
float3 cb=Texture2DSampleGrad(tx,ss,uv+hash(b)*13.1,ddx(uv),ddy(uv)).rgb;
float3 cc=Texture2DSampleGrad(tx,ss,uv+hash(c)*13.1,ddx(uv),ddy(uv)).rgb;
return ca*w.x+cb*w.y+cc*w.z;
}
};MossQuilt quilt;
'''
materials={};errors={}
for key in ['Bark','Leaf','Glow','Stone','Moss']:
    name='M_Craft_C17_'+key;m=unreal.load_asset(BASE+'/Materials/'+name) or AT.create_asset(name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew());L.delete_all_material_expressions(m)
    m.set_editor_property('tangent_space_normal',False);m.set_editor_property('two_sided',key=='Leaf');m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE if key=='Leaf' else unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    vc=node(m,unreal.MaterialExpressionVertexColor);p=node(m,unreal.MaterialExpressionWorldPosition);n=node(m,unreal.MaterialExpressionVertexNormalWS);tm=node(m,unreal.MaterialExpressionTime);uv=node(m,unreal.MaterialExpressionTextureCoordinate)
    col=vc;normal=n;rough=.65
    if key=='Moss':
        tex=node(m,unreal.MaterialExpressionTextureObject);tex.set_editor_property('texture',texture)
        col=custom(m,quilt+'float3 t=quilt.fetchColor(Tex,TexSampler,P.xy/420);float macro=.90+.10*sin(P.x*.0014+sin(P.y*.0011));float l=dot(t,float3(.23,.70,.07));return lerp(t,l.xxx,.16)*float3(.78,.94,1.17)*macro;',{'P':p,'Tex':tex})
        normal=custom(m,quilt+'''float3 nn=normalize(N);float3 t=normalize(cross(float3(0,1,0),nn));float3 b=cross(nn,t);float eps=1.2;
float h0=dot(quilt.fetchColor(Tex,TexSampler,(P+t*eps).xy/420),float3(.23,.70,.07));
float h1=dot(quilt.fetchColor(Tex,TexSampler,(P-t*eps).xy/420),float3(.23,.70,.07));
float h2=dot(quilt.fetchColor(Tex,TexSampler,(P+b*eps).xy/420),float3(.23,.70,.07));
float h3=dot(quilt.fetchColor(Tex,TexSampler,(P-b*eps).xy/420),float3(.23,.70,.07));
return normalize(nn-t*(h0-h1)*3.8/(2*eps)-b*(h2-h3)*3.8/(2*eps));''',{'N':n,'P':p,'Tex':tex})
        rough=.88
    elif key in ['Bark','Stone']:
        col=custom(m,field+'return C.rgb*(.91+.15*g.value(P/115)+.025*g.value(P/4));',{'C':vc,'P':p})
        normal=custom(m,field+'''float3 nn=normalize(N);float3 t=normalize(cross(abs(nn.z)<.85?float3(0,0,1):float3(0,1,0),nn));float3 b=cross(nn,t);float eps=1.2;
return normalize(nn-t*(g.height(P+t*eps)-g.height(P-t*eps))/(2*eps)-b*(g.height(P+b*eps)-g.height(P-b*eps))/(2*eps));''',{'N':n,'P':p})
        rough=.59 if key=='Bark' else .69
    elif key=='Leaf':
        col=custom(m,'float vein=exp(-abs(UV.x-.5)*80);float side=pow(saturate(.5+.5*cos(UV.y*60-abs(UV.x-.5)*31)),16)*.05;return C.rgb*(1+vein*.15+side);',{'C':vc,'UV':uv})
        prop(custom(m,'return C.rgb*float3(.68,.59,.27);',{'C':col}),unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
        prop(custom(m,'return C*.09;',{'C':col}),unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        prop(custom(m,'float w=UV.y*UV.y;float a=sin(P.x*.003+P.y*.002+T*1.1)*2.1;float flutter=sin(T*2.4+P.x*.03)*.75;return float3(a*w,a*w*.4,flutter*w);',{'P':p,'UV':uv,'T':tm}),unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
        rough=.43
    elif key=='Glow':
        life=node(m,unreal.MaterialExpressionScalarParameter);life.set_editor_property('parameter_name','LifeGlow');life.set_editor_property('default_value',.5)
        prop(custom(m,'return C*(1.2+G*.55)*(1+.10*sin(T*1.4));',{'C':vc,'G':life,'T':tm}),unreal.MaterialProperty.MP_EMISSIVE_COLOR);rough=.38
    prop(col,unreal.MaterialProperty.MP_BASE_COLOR);prop(normal,unreal.MaterialProperty.MP_NORMAL)
    constant(m,rough,unreal.MaterialProperty.MP_ROUGHNESS);constant(m,.35 if key=='Moss' else .46,unreal.MaterialProperty.MP_SPECULAR)
    visibility=node(m,unreal.MaterialExpressionScalarParameter);visibility.set_editor_property('parameter_name','Visibility');visibility.set_editor_property('default_value',1)
    dither=node(m,unreal.MaterialExpressionMaterialFunctionCall);dither.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));L.connect_material_expressions(visibility,'',dither,'Alpha Threshold');L.connect_material_property(dither,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
    errors[key]=list(map(str,L.recompile_material(m)));assert not errors[key],errors[key];A.save_loaded_asset(m);materials['C17_'+key]=m

patch=json.loads((DATA/'patch.json').read_text());unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
if '-C17RepairOnly' in unreal.SystemLibrary.get_command_line():patch['changed']=[e for e in patch['changed'] if e['key'] in ['TreeWood','RootBed']]
if '-C17PolishOnly' in unreal.SystemLibrary.get_command_line():patch['changed']=[e for e in patch['changed'] if e['key']=='LotusPlinth']
materials_only='-C17MaterialsOnly' in unreal.SystemLibrary.get_command_line()
if not materials_only:
    for e in patch['changed']:
        if '-C17ResumeImport' in unreal.SystemLibrary.get_command_line() and e['key'] not in ['TreeWood','RootBed'] and A.does_asset_exist(BASE+'/Models/'+e['name']):continue
        ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
        d=ui.static_mesh_import_data;d.combine_meshes=True;d.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;d.auto_generate_collision=False;d.generate_lightmap_u_vs=False
        task=unreal.AssetImportTask();task.filename=str(ROOT/'Art/BrainCraft/ExportC17'/(e['name']+'.fbx'));task.destination_path=BASE+'/Models';task.destination_name=e['name'];task.automated=True;task.replace_existing=True;task.save=True;task.options=ui;AT.import_asset_tasks([task])
        mesh=unreal.load_asset(BASE+'/Models/'+e['name']);assert mesh,e['name']
        for i,slot in enumerate(mesh.get_editor_property('static_materials')):
            family=str(slot.get_editor_property('material_slot_name')).split('.')[0];mat=materials.get(family)
            if not mat:mat=unreal.load_asset(BASE+'/Materials/M_Craft_'+family)
            assert mat,family;mesh.set_material(i,mat)
        mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        bs=sms.get_lod_build_settings(mesh,0);bs.set_editor_property('recompute_normals',False);bs.set_editor_property('max_lumen_mesh_cards',32);bs.set_editor_property('distance_field_resolution_scale',1.0);sms.set_lod_build_settings(mesh,0,bs);A.save_loaded_asset(mesh)
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Maps/BrainCraft');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    backup=DATA/'BrainCraft-before-C17.umap'
    if not backup.exists():shutil.copy2(ROOT/'Content/Maps/BrainCraft.umap',backup)
    replaced=set(patch['remove']);newnames={e['name'] for e in patch['changed']}
    for actor in actors.get_all_level_actors():
        if 'BrainCraft' not in list(map(str,actor.tags)):continue
        c=actor.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.static_mesh and (c.static_mesh.get_name().removeprefix('SM_Craft_') in replaced or c.static_mesh.get_name() in newnames):actors.destroy_actor(actor)
    for e in patch['changed']:
        actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label('BrainCraft C17 / '+e['key']);actor.tags=['BrainCraft','C17',e['key']]+e['tags'];actor.set_actor_scale3d(unreal.Vector(1,-1,1))
        c=actor.static_mesh_component;c.set_static_mesh(unreal.load_asset(BASE+'/Models/'+e['name']));c.set_collision_profile_name('BlockAll');c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if e['collision'] else unreal.CollisionEnabled.NO_COLLISION)
    levels.save_current_level()
(DATA/'native-readback.json').write_text(json.dumps(dict(material_errors=errors,models=len(patch['changed']),materials_only=materials_only,art_accepted=False),indent=2))
unreal.log('C17_GARDEN_NATIVE_READY')

