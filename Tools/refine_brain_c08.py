import bpy,bmesh,numpy as np,math,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,merge,leaf,sweep
from brain_craft_layout import *
ART=ROOT/'Art/BrainCraft';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft.blend'))
M={m.name:m for m in bpy.data.materials};env=bpy.data.collections['01 | Sculpted hemisphere topology'];props=bpy.data.collections['04 | Thought ecology'];changed=[]

def uv_project(o,size):
    uv=o.data.uv_layers.new(name='CraftUV')
    for poly in o.data.polygons:
        axis=max(range(3),key=lambda i:abs(poly.normal[i]));ab=[i for i in range(3) if i!=axis]
        for loop in poly.loop_indices:
            p=o.data.vertices[o.data.loops[loop].vertex_index].co;uv.data[loop].uv=(p[ab[0]]/size,p[ab[1]]/size)

for file in (ART/'Source/C08').glob('Cortex*.npz'):
    name='SM_Craft_'+file.stem;o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
    d=np.load(file);o=mesh(name,d['v'],d['f'],(1,1,1),env,M['Cortex'],-d['n']);uv_project(o,1100);changed.append(o)

# Quiet grass margins narrow the visual path without narrowing its collision.
o=bpy.data.objects['SM_Craft_EarthPath'];v=np.array([p.co[:] for p in o.data.vertices]);dd=np.full(len(v),1e6)
for route in ROUTES:dd=np.minimum(dd,distance(v[:,0],v[:,1],curve(route['points'],12,False),False))
dd=np.minimum(dd,np.abs(np.hypot(v[:,0],v[:,1])-780));blend=np.clip((172-dd)/105,0,1);blend=blend*blend*(3-2*blend);o.data.color_attributes['HeartColor'].data.foreach_set('color',np.column_stack([blend,blend,blend,np.ones(len(v))]).ravel());changed.append(o)

# Retain the fitted water crossings and interaction courts. Remove isolated
# coin-like stepping slabs that read as arbitrary repeated markers.
o=bpy.data.objects['SM_Craft_Paving'];bm=bmesh.new();bm.from_mesh(o.data);seen=set();remove=[]
for vert in bm.verts:
    if vert in seen:continue
    stack=[vert];group=[];seen.add(vert)
    while stack:
        vv=stack.pop();group.append(vv)
        for edge in vv.link_edges:
            other=edge.other_vert(vv)
            if other not in seen:seen.add(other);stack.append(other)
    center=sum((vv.co for vv in group),Vector())/len(group);x,y=center.x,center.y
    if water(x,y)>155 and not(415<math.hypot(x,y-90)<540) and math.hypot(x-LOTUS[0],y-LOTUS[1])>345:remove.extend(group)
bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free();changed.append(o)

# A living braided crossing has a curved deck with thickness and correctly
# offset roots, not two rails translated along the length of a flat plank.
for key in ['RootBridge','RootBridgeEdges']:
    o=bpy.data.objects.get('SM_Craft_'+key)
    if o:bpy.data.objects.remove(o,do_unlink=True)
points=curve(SHORTCUT,24,False);v=[];f=[];normals=[]
for i,p in enumerate(points):
    tangent=points[min(i+1,len(points)-1)]-points[max(i-1,0)];side=np.array((-tangent[1],tangent[0],0));side/=np.linalg.norm(side);normals.append(side)
    for j in range(9):
        t=(j/8-.5)*2;q=p+side*t*250;q[2]+=22*(1-t*t)*math.sin(math.pi*i/(len(points)-1));v.append(q)
        if i and j:a=(i-1)*9+j-1;f.append((a,a+1,a+10,a+9))
o=mesh('SM_Craft_RootBridge',v,f,(1,1,1),props,M['Bark']);sol=o.modifiers.new('Solid living root deck','SOLIDIFY');sol.thickness=34;uv_project(o,360);changed.append(o)
pieces=[]
for side in [-1,1]:
    pp=points+np.array(normals)*side*224;pp[:,2]+=18
    pieces.append(sweep('Braided crossing edge',pp[::3],[22,36,26,18],(1,1,1),props,M['Bark'],18,4,.045))
o=merge(pieces,'SM_Craft_RootBridgeEdges');uv_project(o,360);changed.append(o)

green=[];flowers=[]
for rid,route in enumerate(ROUTES):
    points=curve(route['points'],24,False);cum=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points[:,:2],axis=0),axis=1))]
    for i,dist in enumerate(np.arange(180,cum[-1]-150,190)):
        ix=np.searchsorted(cum,dist);p=points[ix];t=points[min(ix+1,len(points)-1)]-points[max(0,ix-1)];a=math.atan2(t[1],t[0]);side=1 if rid%2 else -1
        x=p[0]-math.sin(a)*side*(route['width']/2-10);y=p[1]+math.cos(a)*side*(route['width']/2-10);d,z,rd=fields(x,y)
        if d>-28 or water(x,y)<110 or math.hypot(x,y-90)<440:continue
        for k in range(3):
            xx=x+math.cos(a)*(k-1)*36;yy=y+math.sin(a)*(k-1)*36
            for j in range(7):
                aa=j*2.399+i*.9;green.append(leaf('Composed pathside leaves',(xx,yy,float(z)+4),(math.cos(aa),math.sin(aa),.8),45+(i%4)*9,13+(j%2)*5,(1,1,1),props,M['Fern'],.3))
            if i%4==0:
                for j in range(5):
                    aa=j*math.tau/5;flowers.append(leaf('Small pathside blossom',(xx,yy,float(z)+51),(math.cos(aa),math.sin(aa),.4),17,10,(1,1,1),props,M['Blossom'],.3))
for parts,key in [(green,'PathsidePlanting'),(flowers,'PathsideBlossoms')]:
    if parts:o=merge(parts,'SM_Craft_'+key);uv_project(o,120);changed.append(o)

manifest=json.loads((ART/'asset-manifest.json').read_text());keys={e['name'] for e in manifest}
for o in changed:
    if o.name not in keys:manifest.append(dict(name=o.name,key=o.name.replace('SM_Craft_',''),spawn=True,tags=[],materials=[m.name for m in o.data.materials]));keys.add(o.name)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'Export'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
(ART/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(ART/'Source/C08/changed-assets.json').write_text(json.dumps([o.name for o in changed]))
scene=bpy.context.scene;scene.cycles.samples=40;scene.render.filepath=str(ART/'Brain-C08-Actual-Model.png');bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C08.blend'));print('C08_SAVED',flush=True);bpy.ops.render.render(write_still=True)
camera=scene.camera;camera.location=(-1850,-3400,3200);target=Vector((-150,150,990));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=3600;scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.filepath=str(ART/'Brain-C08-Tree-Garden.png');bpy.ops.render.render(write_still=True);print('C08_DONE',flush=True)
