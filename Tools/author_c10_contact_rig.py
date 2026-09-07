"""Segmented tailored arms for actual two-bone hand contact, plus rooted grass UVs."""
import bpy,numpy as np,math,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,merge,sweep,ellipsoid
ART=ROOT/'Art/BrainCraft';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C10.blend'));M={m.name:m for m in bpy.data.materials};cast=bpy.data.collections['05 | Attention and thoughts'];manifest=json.loads((ART/'asset-manifest.json').read_text());changed=json.loads((ART/'Source/C10/changed-assets.json').read_text())
def sleeve(name,length,widths,mat):
    V=[];F=[]
    for j,w in enumerate(widths):
        z=-length*j/(len(widths)-1)
        for k in range(48):
            a=k*math.tau/48;r=w*(1+.025*math.cos(a*7));V.append((r*math.cos(a),r*math.sin(a),z))
            if j:q=(j-1)*48+k;n=(j-1)*48+(k+1)%48;F.append((q,q+48,n+48,n))
    return mesh(name,V,F,(1,1,1),cast,M[mat])
def save(o,key):
    o.name='SM_Craft_'+key
    uv=o.data.uv_layers.new(name='CraftUV')
    for p in o.data.polygons:
        for k in p.loop_indices:
            v=o.data.vertices[o.data.loops[k].vertex_index].co;uv.data[k].uv=(math.atan2(v.y,v.x)/math.tau,v.z/60)
    manifest[:]=[e for e in manifest if e['key']!=key];manifest.append(dict(name=o.name,key=key,spawn=False,tags=[],materials=[m.name for m in o.data.materials]));changed.append(o.name);export(o)
def export(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'Export'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
for sign in [-1,1]:
    tag='L' if sign<0 else 'R';old=bpy.data.objects.get('SM_Craft_AttentionArm'+tag)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    top=[sleeve('Soft upper sleeve',31,[12,15,14,12,11],'Sage'),ellipsoid('Rounded sleeve shoulder',(0,0,-4),(12,12,9),(1,1,1),cast,M['Sage'],0,24,16)];save(merge(top,'Upper sleeve'),'AttentionArm'+tag)
    fore=[sleeve('Bent cuffed forearm',32,[11,11.6,13,14,14],'Sage')]
    for z in [-27,-31]:fore.append(sweep('Cuff welt',[(14*math.cos(a),14*math.sin(a),z) for a in np.linspace(0,math.tau,49)],[1.9,1.9],(1,1,1),cast,M['Linen'],10,2))
    save(merge(fore,'Forearm'),'AttentionForearm'+tag)
    hand=[ellipsoid('Soft mitten palm',(0,0,-5),(11,10,13),(1,1,1),cast,M['Linen'],0,28,18),ellipsoid('Mitten thumb',(6,-sign*8,-1),(6,5,8),(1,1,1),cast,M['Linen'],0,24,16)]
    for j in range(3):hand.append(sweep('Mitten stitched fingers',[(8,j*4-4,-8),(8,j*4-4,-14)],[.55,.55],(1,1,1),cast,M['Trim'],6,2))
    save(merge(hand,'Soft mitten'),'AttentionHand'+tag)
for i in range(4):
    o=bpy.data.objects['SM_Craft_GardenGrass'+str(i)];u=o.data.uv_layers.new(name='RootToTip')
    for p in o.data.polygons:
        for loop in p.loop_indices:
            vi=o.data.loops[loop].vertex_index;u.data[loop].uv=((vi%3)/2,((vi%18)//3)/5)
    export(o)
(ART/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(ART/'Source/C10/changed-assets.json').write_text(json.dumps(list(dict.fromkeys(changed))));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C10.blend'));print('C10_CONTACT_RIG_SAVED')
