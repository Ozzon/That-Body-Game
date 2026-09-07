"""Dedicated painted ground shaders, geometric foliage and real normal relief."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());art=root/'Art/BrainCraft';base='/Game/BrainCraft';lib=unreal.MaterialEditingLibrary;assets=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
def ex(m,c):return lib.create_material_expression(m,c)
def wire(a,out,b,pin):assert lib.connect_material_expressions(a,out,b,pin)
def prop(a,out,p):assert lib.connect_material_property(a,out,p)
def constant(m,x):a=ex(m,unreal.MaterialExpressionConstant);a.set_editor_property('r',x);return a
def scalar(m,key,x):a=ex(m,unreal.MaterialExpressionScalarParameter);a.set_editor_property('parameter_name',key);a.set_editor_property('default_value',x);return a
def custom(m,code,nodes,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    a=ex(m,unreal.MaterialExpressionCustom);a.set_editor_property('code',code);a.set_editor_property('output_type',kind);inputs=[]
    for k in nodes:i=unreal.CustomInput();i.set_editor_property('input_name',k);inputs.append(i)
    a.set_editor_property('inputs',inputs)
    for k,(n,p) in nodes.items():wire(n,p,a,k)
    return a
t=unreal.AssetImportTask();t.filename=str(art/'Textures/T_C10_Garden_Atlas.png');t.destination_path=base+'/Textures';t.destination_name='T_C10_Garden_Atlas';t.automated=True;t.replace_existing=True;t.save=True;at.import_asset_tasks([t]);atlas=unreal.load_asset(base+'/Textures/T_C10_Garden_Atlas')
report={}
for key,offset,size,rough in [('GardenSoil',(0,0),160,.89),('GardenStone',(.5,0),320,.76),('GardenMoss',(0,.5),140,.91),('GardenSand',(.5,.5),210,.94),('GardenGrass',(0,0),260,.75),('GardenTurf',(0,.5),140,.93)]:
    name='M_Craft_'+key;m=unreal.load_asset(base+'/Materials/'+name) or at.create_asset(name,base+'/Materials',unreal.Material,unreal.MaterialFactoryNew());lib.delete_all_material_expressions(m);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_OPAQUE);m.set_editor_property('two_sided',key=='GardenGrass');m.set_editor_property('tangent_space_normal',False)
    wp=ex(m,unreal.MaterialExpressionWorldPosition);vn=ex(m,unreal.MaterialExpressionVertexNormalWS);vc=ex(m,unreal.MaterialExpressionVertexColor)
    if key=='GardenGrass':
        color=custom(m,'return C.rgb*float3(.62,.72,.42);',{'C':(vc,'')});prop(color,'',unreal.MaterialProperty.MP_BASE_COLOR);prop(vn,'',unreal.MaterialProperty.MP_NORMAL)
        # Normals point upward to avoid dark paper-blade undersides; the folded
        # mesh still supplies parallax, curvature and a readable rooted silhouette.
        tip=ex(m,unreal.MaterialExpressionTextureCoordinate);tip.set_editor_property('coordinate_index',1);time=ex(m,unreal.MaterialExpressionTime);bend=ex(m,unreal.MaterialExpressionVectorParameter);bend.set_editor_property('parameter_name','AttentionPosition');bend.set_editor_property('default_value',unreal.LinearColor(0,0,-10000,0))
        wpo=custom(m,'float t=saturate(UV.y); float2 delta=P.xy-B.xy; float touch=saturate(1-length(delta)/105)*saturate(1-abs(P.z-B.z)/140); float2 push=normalize(delta+float2(.001,.001))*touch*32; float wind=sin(P.x*.004+P.y*.002+T*1.4)*7+sin(P.y*.01-T*2.2)*3; return float3((float2(wind,wind*.55)+push)*t*t,-touch*15*t*t);',{'P':(wp,''),'B':(bend,''),'T':(time,''),'UV':(tip,'')});prop(wpo,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
        glow=custom(m,'return C*.07;',{'C':(color,'')});prop(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        tex=ex(m,unreal.MaterialExpressionTextureObject);tex.set_editor_property('texture',atlas)
        # Mirrored projection avoids boundary seams without smearing texture
        # layers together. Stone projects by the dominant geometric normal.
        plane='float2 p=abs(N.z)>.55?P.xy:abs(N.x)>abs(N.y)?P.yz:P.xz;' if key=='GardenStone' else 'float2 p=P.xy;'
        finish='return lerp(float3(.28,.235,.16),c*float3(.9,.98,1.1),.46);' if key=='GardenSoil' else 'return float3(.055,.095,.027)*( .88+dot(c,float3(.3,.4,.3))*.45);' if key=='GardenTurf' else 'return c;'
        code=plane+f' float2 q=1-abs(frac(p/{size}.0*.5)*2-1); q=q*.48+float2({offset[0]+.01},{offset[1]+.01}); float3 c=Texture2DSample(Tex,TexSampler,q).rgb; '+finish
        color=custom(m,code,{'P':(wp,''),'N':(vn,''),'Tex':(tex,'')});prop(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
        h=custom(m,'return dot(C,float3(.2126,.7152,.0722))*.7;',{'C':(color,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
        normal=custom(m,'float3 n=normalize(N);float3 x=ddx(P),y=ddy(P);float3 r1=cross(y,n),r2=cross(n,x);float d=dot(x,r1);return normalize(abs(d)*n-sign(d)*(ddx(H)*r1+ddy(H)*r2));',{'P':(wp,''),'N':(vn,''),'H':(h,'')});prop(normal,'',unreal.MaterialProperty.MP_NORMAL)
    prop(constant(m,rough),'',unreal.MaterialProperty.MP_ROUGHNESS);prop(constant(m,.19),'',unreal.MaterialProperty.MP_SPECULAR)
    errors=lib.recompile_material(m);report[key]=[str(e) for e in errors];assert not errors,(key,report[key]);assets.save_loaded_asset(m)
(art/'Source/C10/material-compile-report.json').write_text(json.dumps(report,indent=2));unreal.log('C10_SURFACE_MATERIALS_COMPILED')
