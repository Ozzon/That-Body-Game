"""Attention leg segments, root-weight channels and sculptural effect meshes."""
import bpy,bmesh,numpy as np,math,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,merge,sweep,ellipsoid,leaf
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C11';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));manifest=json.loads((DATA/'asset-manifest.json').read_text());changed=[];coll=bpy.data.collections['C11 | Thought creatures'];M={m.name:m for m in bpy.data.materials}
def export(o,key,spawn=False,tags=None):
    o.name='SM_Craft_'+key
    if not o.data.uv_layers:
        uv=o.data.uv_layers.new(name='CraftUV')
        for p in o.data.polygons:
            for i in p.loop_indices:
                v=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v.x/100,v.z/100)
    manifest[:]=[e for e in manifest if e['key']!=key];manifest.append(dict(name=o.name,key=key,spawn=spawn,tags=tags or [],materials=[m.name for m in o.data.materials]));changed.append(key)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'ExportC11'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
for side in ['L','R']:
    for part,length,widths in [('Thigh',34,[13,15,14,12,11]),('Shin',34,[11,12,11,10,10])]:
        V=[];F=[]
        for i,w in enumerate(widths):
            z=-length*i/(len(widths)-1)
            for j in range(40):
                a=j*math.tau/40;r=w*(1+.023*math.cos(a*7+i*.5));V.append((r*math.cos(a),r*math.sin(a),z))
                if i:q=(i-1)*40+j;n=(i-1)*40+(j+1)%40;F.append((q,q+40,n+40,n))
        F.extend([tuple(reversed(range(40))),tuple((len(widths)-1)*40+j for j in range(40))]);o=mesh('Soft articulated trouser',V,F,(1,1,1),coll,M['Sage']);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();export(o,'Attention'+part+side)
# Correct explicit UV1 channel: UV0 is conventional surface coordinates.
for i in range(4):
    o=bpy.data.objects['SM_Craft_GardenGrass'+str(i)];first=o.data.uv_layers[0];first.name='CraftUV';second=o.data.uv_layers.new(name='RootWeight')
    for li,loop in enumerate(o.data.loops):
        v=o.data.vertices[loop.vertex_index].co;first.data[li].uv=(v.x/200,v.y/200);second.data[li].uv=(0,(loop.vertex_index%15)//3/4)
    export(o,'GardenGrass'+str(i),True,['GroundCover'])
# Ripple rings have a real curved profile and no opaque rectangular sprite.
V=[];F=[]
for i in range(128):
    a=i*math.tau/128
    for j in range(8):
        b=j*math.tau/8;r=100+1.4*math.cos(b);V.append((r*math.cos(a),r*math.sin(a),.45*math.sin(b)))
        F.append((i*8+j,((i+1)%128)*8+j,((i+1)%128)*8+(j+1)%8,i*8+(j+1)%8))
export(mesh('Fine expanding water ring',V,F,(.32,.65,.61),coll,M['C11_WaterFoam']),'FXRipple')
o=leaf('Fluttering cherry petal',(0,0,0),(1,0,.06),20,9,(.55,.16,.32),coll,M['C11_PetalPink'],.28);export(o,'FXPetal')
sparks=[]
for k in range(5):
    a=k*math.tau/5;sparks.append(leaf('Small luminous seed',(0,0,0),(math.cos(a),math.sin(a),.35),11,4,(.93,.56,.1),coll,M['C11_ThoughtGold'],.1))
export(merge(sparks,'Awareness pollen'),'FXPollen')
(DATA/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(DATA/'contact-patch.json').write_text(json.dumps(changed));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));print('C11_CONTACT_PATCH_READY',changed,flush=True)
