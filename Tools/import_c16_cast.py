"""Native C16 cast import; actor placements and terrain remain in the level."""
import unreal, json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir()); DATA=ROOT/'Art/BrainCraft/Source/C16'
BASE='/Game/BrainCraft'; A=unreal.EditorAssetLibrary; L=unreal.MaterialEditingLibrary
AT=unreal.AssetToolsHelpers.get_asset_tools(); sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

def node(m,c):return L.create_material_expression(m,c)
def prop(n,p):assert L.connect_material_property(n,'',p)
def const(m,v,p):
    n=node(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',v);prop(n,p)
def custom(m,code,args,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    n=node(m,unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',kind)
    inputs=[]
    for k in args:i=unreal.CustomInput();i.set_editor_property('input_name',k);inputs.append(i)
    n.set_editor_property('inputs',inputs)
    for k,v in args.items():assert L.connect_material_expressions(v,'',n,k)
    return n

materials={};errors={}
for key in ['Gold','Cloud','Wisp','Amber','Ink','Eye','Glint','Filament','Cheek']:
    name='M_Craft_C16_'+key;m=unreal.load_asset(BASE+'/Materials/'+name)
    if not m:m=AT.create_asset(name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    L.delete_all_material_expressions(m);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_OPAQUE)
    m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    vc=node(m,unreal.MaterialExpressionVertexColor);prop(vc,unreal.MaterialProperty.MP_BASE_COLOR)
    const(m,.40 if key=='Gold' else .24 if key in ['Ink','Glint'] else .44 if key=='Amber' else .65,unreal.MaterialProperty.MP_ROUGHNESS)
    const(m,.40,unreal.MaterialProperty.MP_SPECULAR)
    if key in ['Gold','Eye','Glint','Filament']:
        gain=node(m,unreal.MaterialExpressionScalarParameter);gain.set_editor_property('parameter_name','LifeGlow');gain.set_editor_property('default_value',.10 if key=='Gold' else .65 if key=='Eye' else .45)
        prop(custom(m,'return C*G*.2;' if key=='Gold' else 'return C*G;',{'C':vc,'G':gain}),unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    errors[key]=list(map(str,L.recompile_material(m)));assert not errors[key],errors[key]
    A.save_loaded_asset(m);materials['C16_'+key]=m

unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
patch=json.loads((DATA/'cast-patch.json').read_text());readback=[]
for e in patch['assets']:
    key=e['key'];ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    d=ui.static_mesh_import_data;d.combine_meshes=True;d.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;d.auto_generate_collision=False;d.generate_lightmap_u_vs=False
    t=unreal.AssetImportTask();t.filename=str(ROOT/'Art/BrainCraft/ExportC16'/('SM_Craft_'+key+'.fbx'));t.destination_path=BASE+'/Models';t.destination_name='SM_Craft_'+key;t.automated=True;t.replace_existing=True;t.save=True;t.options=ui
    AT.import_asset_tasks([t]);mesh=unreal.load_asset(BASE+'/Models/SM_Craft_'+key);assert mesh,key
    for i,slot in enumerate(mesh.get_editor_property('static_materials')):
        family=str(slot.get_editor_property('material_slot_name')).split('.')[0]
        assert family in materials,family;mesh.set_material(i,materials[family])
    bs=sms.get_lod_build_settings(mesh,0);bs.set_editor_property('recompute_normals',False);sms.set_lod_build_settings(mesh,0,bs)
    A.save_loaded_asset(mesh);readback.append(key)
(DATA/'native-cast-readback.json').write_text(json.dumps({'assets':readback,'material_errors':errors,'art_accepted':False},indent=2))
unreal.log('C16_NATIVE_CAST_READY')
