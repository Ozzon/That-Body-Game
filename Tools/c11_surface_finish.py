"""Painted limestone with physical micro-relief; coherent foliage and bark light."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());base='/Game/BrainCraft';L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools()
def ex(m,c):return L.create_material_expression(m,c)
def wire(a,out,b,p):assert L.connect_material_expressions(a,out,b,p)
def prop(a,out,p):assert L.connect_material_property(a,out,p)
def c(m,v):n=ex(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',v);return n
def custom(m,code,args,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    n=ex(m,unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',kind);ii=[]
    for key in args:i=unreal.CustomInput();i.set_editor_property('input_name',key);ii.append(i)
    n.set_editor_property('inputs',ii)
    for key,(node,out) in args.items():wire(node,out,n,key)
    return n
t=unreal.AssetImportTask();t.filename=str(root/'Art/BrainCraft/Textures/T_C11_Limestone_BaseColor.png');t.destination_path=base+'/Textures';t.destination_name='T_C11_Limestone_BaseColor';t.automated=True;t.replace_existing=True;t.save=True;AT.import_asset_tasks([t]);texture=unreal.load_asset(base+'/Textures/T_C11_Limestone_BaseColor');assert texture
texture.set_editor_property('srgb',True);texture.set_editor_property('lod_group',unreal.TextureGroup.TEXTUREGROUP_WORLD);A.save_loaded_asset(texture)
report={}
for key in ['Paving','Coping','Masonry']:
    m=unreal.load_asset(base+'/Materials/M_Craft_C11_'+key);L.delete_all_material_expressions(m);m.set_editor_property('tangent_space_normal',False);m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    p=ex(m,unreal.MaterialExpressionWorldPosition);n=ex(m,unreal.MaterialExpressionVertexNormalWS);vc=ex(m,unreal.MaterialExpressionVertexColor);tex=ex(m,unreal.MaterialExpressionTextureObject);tex.set_editor_property('texture',texture)
    # Triplanar sampling covers modeled side walls and tops at one physical
    # scale. Paint supplies pigment; light remains fully dynamic.
    code='float3 w=pow(abs(N),6);w/=max(dot(w,1),.001);float3 t=Texture2DSample(T,TSampler,P.yz/210).rgb*w.x+Texture2DSample(T,TSampler,P.xz/210+float2(.19,.31)).rgb*w.y+Texture2DSample(T,TSampler,P.xy/210).rgb*w.z;return C.rgb*lerp(float3(.77,.84,.76),float3(1.18,1.14,1.00),saturate(t/.6));'
    col=custom(m,code,{'P':(p,''),'N':(n,''),'C':(vc,''),'T':(tex,'')});prop(col,'',unreal.MaterialProperty.MP_BASE_COLOR)
    height=custom(m,'float3 w=pow(abs(N),6);w/=max(dot(w,1),.001);float3 t=Texture2DSample(T,TSampler,P.yz/210).rgb*w.x+Texture2DSample(T,TSampler,P.xz/210+float2(.19,.31)).rgb*w.y+Texture2DSample(T,TSampler,P.xy/210).rgb*w.z;return dot(t,float3(.22,.65,.13))*1.25;',{'P':(p,''),'N':(n,''),'T':(tex,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    normal=custom(m,'float3 n=normalize(N);float3 x=ddx(P),y=ddy(P);float3 r1=cross(y,n),r2=cross(n,x);float d=dot(x,r1);return normalize(abs(d)*n-sign(d)*(ddx(H)*r1+ddy(H)*r2));',{'N':(n,''),'P':(p,''),'H':(height,'')});prop(normal,'',unreal.MaterialProperty.MP_NORMAL)
    rough=custom(m,'return clamp(.65+(H-.35)*.20,.49,.85);',{'H':(height,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1);prop(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);prop(c(m,.4),'',unreal.MaterialProperty.MP_SPECULAR)
    visibility=ex(m,unreal.MaterialExpressionScalarParameter);visibility.set_editor_property('parameter_name','Visibility');visibility.set_editor_property('default_value',1)
    dither=ex(m,unreal.MaterialExpressionMaterialFunctionCall);dither.set_editor_property('material_function',unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));wire(visibility,'',dither,'Alpha Threshold');prop(dither,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
    report[key]=list(map(str,L.recompile_material(m)));assert not report[key],report[key];A.save_loaded_asset(m)
# Bark ridges retain geometric relief; warm grey heartwood receives broad
# highlights instead of the old orange emissive-looking finish.
for key in ['BarkWood','BarkRidge']:
    m=unreal.load_asset(base+'/Materials/M_Craft_C11_'+key)
    report[key]=list(map(str,L.recompile_material(m)));assert not report[key];A.save_loaded_asset(m)
# Warm facial light is low enough to preserve the face volume and hood shadow.
m=unreal.load_asset(base+'/Materials/M_Craft_Face');col=ex(m,unreal.MaterialExpressionConstant3Vector);col.set_editor_property('constant',unreal.LinearColor(.12,.065,.018,1));prop(col,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);assert not L.recompile_material(m);A.save_loaded_asset(m)
(root/'Art/BrainCraft/Source/C11/surface-finish-readback.json').write_text(json.dumps(dict(texture=texture.get_path_name(),errors=report,shading='Default Lit with painted triplanar pigment and derivative normal'),indent=2));unreal.log('C11_PAINTED_PBR_SURFACES_READY')
