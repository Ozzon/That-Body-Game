"""Model continuous welcoming descents, open masonry passages, fix earth sides."""
import bpy,bmesh,numpy as np,math,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,block,merge
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C11';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));manifest=json.loads((DATA/'asset-manifest.json').read_text());changed=[]
coll=bpy.data.collections['C11 | Fitted garden architecture'];routes=json.loads((DATA/'garden-access.json').read_text());M={m.name:m for m in bpy.data.materials}
def export(o,key,tags):
    o.name='SM_Craft_'+key
    if not o.data.uv_layers:
        uv=o.data.uv_layers.new(name='CraftUV')
        for i,loop in enumerate(o.data.loops):p=o.data.vertices[loop.vertex_index].co;uv.data[i].uv=(p.x/180,p.y/180)
    manifest[:]=[e for e in manifest if e['key']!=key];manifest.append(dict(name=o.name,key=key,spawn=True,tags=tags,materials=[m.name for m in o.data.materials]));changed.append(key)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'ExportC11'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
def distance(p,points):
    a=points[:-1];delta=points[1:]-a;t=np.clip(np.sum((p[:2]-a[:,:2])*delta[:,:2],axis=1)/np.maximum(np.sum(delta[:,:2]**2,axis=1),.01),0,1);q=a+delta*t[:,None];idx=np.argmin(np.linalg.norm(q[:,:2]-p[:2],axis=1));return np.linalg.norm(q[idx,:2]-p[:2]),q[idx,2]
V=[];F=[];C=[];edging=[]
for ri,r in enumerate(routes):
    p=np.array(r['points']);w=r['width'];start=len(V)
    for i,q in enumerate(p):
        tangent=p[min(i+1,len(p)-1)]-p[max(0,i-1)];side=np.array((-tangent[1],tangent[0],0));side/=np.linalg.norm(side)
        for j in range(9):
            u=(j/8-.5)*w;V.append(q+side*u+np.array((0,0,3*math.cos(u/w*math.pi*2))));C.append((.38,.36,.28))
            if i and j:a=start+(i-1)*9+j-1;F.append((a,a+9,a+10,a+1))
        if i%4==0:
            for sign in [-1,1]:
                pos=q+side*sign*(w/2+16);edging.append(block('Short garden kerb',pos,(65,38,22),(.42,.40,.31),coll,M['C11_Coping'],math.atan2(tangent[1],tangent[0]),6,i+ri))
for key in ['GardenAccess','GardenAccessEdges']:
    old=bpy.data.objects.get('SM_Craft_'+key)
    if old:bpy.data.objects.remove(old,do_unlink=True)
o=mesh('Garden ramp walkways',V,F,C,coll,M['C11_Paving']);solid=o.modifiers.new('Continuous ramp support','SOLIDIFY');solid.thickness=28;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=solid.name);export(o,'GardenAccess',['Ground']);export(merge(edging,'Ramp edge stones'),'GardenAccessEdges',[])
# Carve whole bricks from descents. Never leave half blocks or overlapping
# rail fragments in an opening. The old ground side faces receive the same cut.
for key in ['RetainingWalls','TerraceCoping','Ground','CrossingBeds']:
    o=bpy.data.objects['SM_Craft_'+key];bm=bmesh.new();bm.from_mesh(o.data)
    if key in ['Ground','CrossingBeds']:
        discard=[]
        for f in bm.faces:
            if f.normal.z>.45:continue
            p=np.array(f.calc_center_median())
            for r in routes:
                dist,z=distance(p,np.array(r['points']))
                if dist<r['width']/2+24 and max(v.co.z for v in f.verts)>z-110:discard.append(f);break
        bmesh.ops.delete(bm,geom=discard,context='FACES')
    else:
        unseen=set(bm.verts);discard=[]
        while unseen:
            v=unseen.pop();island=[v];stack=[v]
            while stack:
                u=stack.pop()
                for edge in u.link_edges:
                    w=edge.other_vert(u)
                    if w in unseen:unseen.remove(w);island.append(w);stack.append(w)
            p=np.array(sum((v.co for v in island),Vector())/len(island))
            for r in routes:
                dist,z=distance(p,np.array(r['points']))
                if dist<r['width']/2+65 and p[2]>z-130:discard.extend(island);break
        bmesh.ops.delete(bm,geom=discard,context='VERTS')
    bm.to_mesh(o.data);bm.free()
    if key=='Ground':
        # The former shared green vertex color made exposed earth walls read
        # as vertical grass smears. Give side faces their own mineral pigment.
        old=o.data.color_attributes.get('HeartColor');domain=old.domain;col=[tuple(c.color) for c in old.data];o.data.color_attributes.remove(old);new=o.data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='CORNER')
        for f in o.data.polygons:
            for li in f.loop_indices:new.data[li].color=(.24,.23,.185,1) if f.normal.z<.45 else col[li if domain=='CORNER' else o.data.loops[li].vertex_index]
    tags=next(e['tags'] for e in manifest if e['key']==key);export(o,key,tags)
(DATA/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(DATA/'contact-patch.json').write_text(json.dumps(changed));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));print('C11_GARDEN_DESCENTS_READY',flush=True)
