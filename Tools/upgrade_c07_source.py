from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'Tools/author_brain_craft.py';s=p.read_text()
a=s.index('# Attention: a fitted hood');b=s.index("print('CRAFT_GEOMETRY_READY'",a)
s=s[:a]+"# The tailored hero is authored independently from environment geometry.\nexec(compile((ROOT/'Tools/craft_attention.py').read_text(),str(ROOT/'Tools/craft_attention.py'),'exec'))\n\n"+s[b:]
# Noise relief in the old material bake was many times too strong at this scale.
s=s.replace("bn.inputs['Strength'].default_value=.28;bn.inputs['Distance'].default_value=bump", "bn.inputs['Strength'].default_value=.17;bn.inputs['Distance'].default_value=bump*.018")
pos=s.index('\ndef uv_project')
atlas="""
# Purpose-made painted material atlas. UV remapping stays in material nodes;
# the generated source bitmap is preserved without raster editing.
atlas_image=bpy.data.images.load(str(TEX/'T_C07_Painted_Atlas.png'))
for key,offset in [('Cortex',(0,.5,0)),('Stone',(.5,.5,0)),('Bark',(0,0,0)),('Sage',(.5,0,0))]:
    m=M[key];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');coord=n.new('ShaderNodeTexCoord');fract=n.new('ShaderNodeVectorMath');fract.operation='FRACTION';l.new(coord.outputs['UV'],fract.inputs[0]);scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.49;l.new(fract.outputs[0],scale.inputs[0]);addv=n.new('ShaderNodeVectorMath');addv.operation='ADD';addv.inputs[1].default_value=tuple(x+.005 if i<2 else x for i,x in enumerate(offset));l.new(scale.outputs[0],addv.inputs[0]);im=n.new('ShaderNodeTexImage');im.image=atlas_image;l.new(addv.outputs[0],im.inputs['Vector']);l.new(im.outputs['Color'],p.inputs['Base Color'])
    if key=='Sage':
        tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.52,.80,.84,1);l.new(im.outputs['Color'],tint.inputs[1]);l.new(tint.outputs[0],p.inputs['Base Color'])
    p.inputs['Roughness'].default_value={'Cortex':.62,'Stone':.78,'Bark':.67,'Sage':.89}[key]
"""
s=s[:pos]+atlas+s[pos:];p.write_text(s)
p=root/'Tools/craft_routes.py';s=p.read_text().replace('(-790,975)','(-1010,1380)').replace('C06','C07');p.write_text(s)
p=root/'Source/ThatBodyGame/BrainCraftReview.cpp';s=p.read_text().replace('Brain-C06-','Brain-C07-').replace('brain-c06-input-report','brain-c07-input-report').replace('FVector(0,100,420)','FVector(0,100,730)').replace('FVector(0,0,760)','FVector(0,0,890)').replace('FVector(1550,1510,760)','FVector(-1450,1430,1240)').replace('FVector(-340,-460,445)','FVector(-340,-460,624)').replace('FVector(1480,1230,745)','FVector(-1010,1280,1204)').replace('{9100,2500,3100,2600}','{10800,2100,2700,3300}');p.write_text(s)
