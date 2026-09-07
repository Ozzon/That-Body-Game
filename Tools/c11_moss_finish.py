"""Painted botanical ground color with dynamic physical shading and fine relief."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());base='/Game/BrainCraft';L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
def ex(m,c):return L.create_material_expression(m,c)
def prop(n,p):assert L.connect_material_property(n,'',p)
def node(m,code,args,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    n=ex(m,unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',kind);ii=[]
    for key in args:i=unreal.CustomInput();i.set_editor_property('input_name',key);ii.append(i)
    n.set_editor_property('inputs',ii)
    for key,(v,o) in args.items():assert L.connect_material_expressions(v,o,n,key)
    return n
t=unreal.AssetImportTask();t.filename=str(root/'Art/BrainCraft/Textures/T_C11_Moss_BaseColor.png');t.destination_path=base+'/Textures';t.destination_name='T_C11_Moss_BaseColor';t.automated=True;t.replace_existing=True;t.save=True;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);texture=unreal.load_asset(base+'/Textures/T_C11_Moss_BaseColor');assert texture
texture.set_editor_property('srgb',True);texture.set_editor_property('lod_group',unreal.TextureGroup.TEXTUREGROUP_WORLD);A.save_loaded_asset(texture)
m=unreal.load_asset(base+'/Materials/M_Craft_C11_Turf');p=ex(m,unreal.MaterialExpressionWorldPosition);norm=ex(m,unreal.MaterialExpressionVertexNormalWS);tex=ex(m,unreal.MaterialExpressionTextureObject);tex.set_editor_property('texture',texture)
col=node(m,'float3 a=Texture2DSample(T,TSampler,P.xy/265).rgb;float large=.94+.06*sin(P.x/420)*sin(P.y/370);return a*float3(.83,1.05,1.07)*large;',{'P':(p,''),'T':(tex,'')});prop(col,unreal.MaterialProperty.MP_BASE_COLOR)
h=node(m,'return dot(Texture2DSample(T,TSampler,P.xy/265).rgb,float3(.21,.72,.07))*3.5;',{'P':(p,''),'T':(tex,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
n=node(m,'float3 n=normalize(N);float3 x=ddx(P),y=ddy(P);float3 r1=cross(y,n),r2=cross(n,x);float d=dot(x,r1);return normalize(abs(d)*n-sign(d)*(ddx(H)*r1+ddy(H)*r2));',{'N':(norm,''),'P':(p,''),'H':(h,'')});prop(n,unreal.MaterialProperty.MP_NORMAL)
rough=node(m,'return .86+clamp(H*.055,0,.10);',{'H':(h,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1);prop(rough,unreal.MaterialProperty.MP_ROUGHNESS)
wpo=node(m,'float h=dot(Texture2DSampleLevel(T,TSampler,P.xy/265,0).rgb,float3(.21,.72,.07));return N*saturate(N.z)*clamp((h-.18)*6,-1,2);',{'N':(norm,''),'P':(p,''),'T':(tex,'')});prop(wpo,unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
errors=list(map(str,L.recompile_material(m)));assert not errors,errors;A.save_loaded_asset(m)
(root/'Art/BrainCraft/Source/C11/moss-finish-readback.json').write_text(json.dumps(dict(texture=texture.get_path_name(),errors=errors,shader_displacement_cm=[-1,2],baked_terrain_relief_cm=20),indent=2));unreal.log('C11_BOTANICAL_SURFACE_READY')
