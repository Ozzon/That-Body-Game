"""Build the editable organ collection, world layout and native FBX assets."""
import bpy,numpy as np,math,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from organ_math import curve,PALETTES
from adventure_layout import ORGANS,HEART,HUBS,PATHS,STATIONS,CONTEXT,BODY_HALF
ART=ROOT/'Art/BodyAdventure';EXPORT=ART/'Export';EXPORT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
manifest=[]

def collection(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
def mat(name,color,vertex=False,emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.65
    if vertex:
        v=m.node_tree.nodes.new('ShaderNodeVertexColor');v.layer_name='HeartColor';m.node_tree.links.new(v.outputs['Color'],p.inputs['Base Color'])
    if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    return m
surface=mat('Authored organ palette',(1,1,1),True)
light=mat('Bridges of light',(.35,.67,.51),True,.38)
glow=mat('Warm care light',(1,.57,.17),False,1)
dark=mat('Midnight background',(.025,.037,.059))

def mesh(name,V,F,coll,C=None,N=None,material=surface):
    data=bpy.data.meshes.new(name);data.from_pydata(V,[],F);data.update();o=bpy.data.objects.new(name,data);coll.objects.link(o);data.materials.append(material)
    for p in data.polygons:p.use_smooth=True
    if C is None:C=np.tile(material.diffuse_color[:3],(len(V),1))
    a=data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='POINT');a.data.foreach_set('color',np.column_stack([C,np.ones(len(V))]).ravel())
    if N is not None:data.normals_split_custom_set_from_vertices(N)
    return o
def export(o,key,position=(0,0,0),tags=()):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    manifest.append(dict(name=o.name,key=key,position=list(position),tags=list(tags),material='Light' if o.data.materials[0]==light else 'Glow' if o.data.materials[0]==glow else 'Surface'))
    o.location=position

for s in ORGANS:
    coll=collection(s['name']+' | authored interior');d=np.load(ART/s['key']/'Source/sculpt.npz');V,F,N,C=[d[n] for n in ['vertices','faces','normals','colors']]
    mid=V[F].mean(axis=1);parts=np.where(mid[:,2]<110,0,1+(mid[:,0]>0).astype(int)*2+(mid[:,1]>0).astype(int))
    for i,label in enumerate(['Floor','FrontRight','FrontLeft','BackRight','BackLeft']):
        faces=F[parts==i];ids,inv=np.unique(faces.ravel(),return_inverse=True)
        o=mesh('SM_'+s['key']+'_'+label,V[ids].tolist(),inv.reshape(-1,3).tolist(),coll,C[ids],N[ids].tolist());export(o,s['key'],s['center'])
    print('EXPORTED_ORGAN',s['key'],flush=True)

# Append the actual approved heart, keeping its mesh and local layout intact.
with bpy.data.libraries.load(str(ROOT/'Art/HeartModels/A/Heart_Model_A.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('SM_Heart_')]
hc=collection('HEART | owner-approved model A')
for o in dst.objects:
    hc.objects.link(o);o.location=(1400,0,0)
    manifest.append(dict(name=o.name,key='Heart',position=[1400,0,0],tags=['Interactive'] if 'PulseSeed' in o.name or 'PacingValve' in o.name else [],existing='/Game/HeartModels/A/'+o.name,material='Glow' if 'PulseSeed' in o.name else 'Surface'))

world=collection('WORLD | light bridges and quiet tissue');landmarks=collection('LANDMARKS | care and organ identity')
def ellipsoid(name,pos,scale,color,coll=landmarks):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,location=pos);o=bpy.context.object;o.name=name;o.scale=scale
    for c in list(o.users_collection):c.objects.unlink(o)
    coll.objects.link(o);bpy.ops.object.transform_apply(location=True,rotation=False,scale=True)
    V=np.array([v.co[:] for v in o.data.vertices]);F=[p.vertices[:] for p in o.data.polygons]
    bpy.data.objects.remove(o,do_unlink=True)
    return mesh(name,V.tolist(),F,coll,np.tile(color,(len(V),1)))
def merge(objects,name,coll):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
def sweep(points,radius,color,name,coll=landmarks):
    pts=curve(points,sub=10,closed=False);V=[];F=[];sides=16
    for i,p in enumerate(pts):
        t=Vector(pts[min(len(pts)-1,i+1)]-pts[max(0,i-1)]).normalized();u=t.cross(Vector((0,0,1))).normalized()
        if u.length<.1:u=Vector((1,0,0))
        v=t.cross(u).normalized();r=radius*(1-i/(len(pts)-1)*.5)
        for j in range(sides):V.append(tuple(Vector(p)+r*(math.cos(j*math.tau/sides)*u+math.sin(j*math.tau/sides)*v)))
        if i:
            for j in range(sides):a=(i-1)*sides+j;b=(i-1)*sides+(j+1)%sides;F.append((a,b,b+sides,a+sides))
    return mesh(name,V,F,coll,np.tile(color,(len(V),1)))

# Tapered slabs of light: no rails, vessel spaghetti or clutter underfoot.
V=[];F=[];C=[]
for path in PATHS:
    pts=curve(path['points'],14,False);start=len(V)
    for i,p in enumerate(pts):
        d=pts[min(len(pts)-1,i+1)]-pts[max(0,i-1)];side=np.array([-d[1],d[0],0]);side/=np.linalg.norm(side);w=path['width']/2
        for f in [-1,-.82,.82,1]:
            q=p+side*w*f;q[2]+=60;V.append(q.tolist());C.append((.40,.63,.46) if abs(f)<.9 else (.26,.44,.34))
        if i:
            for j in range(3):a=start+(i-1)*4+j;F.append((a,a+4,a+5,a+1))
o=mesh('SM_Adventure_LightBridges',V,F,world,np.array(C),material=light);export(o,'Bridges',tags=['LightBridge'])
for h in HUBS:
    x,y,z=h['center'];base,wall,edge,floor=PALETTES[h['palette']]
    o=ellipsoid('SM_Hub_'+h['key'],(x,y,z+15),(h['radius'],h['radius'],48),floor,world);export(o,h['key'],tags=['LightBridge'])

# A full soft body outline establishes place without adding bones or high enclosing ribs.
points=BODY_HALF+[(x,-y) for x,y in BODY_HALF[-2:0:-1]];pts=curve(points,8)
# Concave polygon triangulation through Blender's tessellator preserves arm/leg gaps.
from mathutils.geometry import tessellate_polygon
poly=[Vector((x,y,-340)) for x,y in pts];tris=tessellate_polygon([poly]);lookup={tuple(p):i for i,p in enumerate(poly)}
V=[tuple(p) for p in poly];F=[tuple(p if isinstance(p,int) else lookup[tuple(p)] for p in tri) for tri in tris];C=[(.075,.055,.075)]*len(V)
offset=len(V)
for x,y in pts:V.append((x,y,-520));C.append((.04,.035,.055))
for i in range(len(pts)):j=(i+1)%len(pts);F.append((i,j,j+offset,i+offset))
o=mesh('SM_Adventure_Body',V,F,world,np.array(C));export(o,'Body',tags=['BodyOutline'])
rim=sweep([(x,y,-325) for x,y in list(pts)+[pts[0]]],80,(.19,.10,.115),'SM_Adventure_BodyRim',world);export(rim,'Body',tags=['BodyOutline'])

for c in CONTEXT:
    o=ellipsoid('SM_Context_'+c['key'],c['center'],c['scale'],PALETTES[c['palette']][1],world);export(o,c['key'])

# Wind petals are a single sculpted landmark in each lung, not repeated decoration.
for key,y in [('Right',-3050),('Left',3050)]:
    x=1200;parts=[]
    parts.append(ellipsoid('Wind seat',(x,y,77),(160,155,28),(.40,.59,.43)))
    for j in range(3):
        a=j*math.tau/3;dx,dy=math.cos(a),math.sin(a)
        parts.append(sweep([(x+dx*125,y+dy*125,90),(x+dx*165,y+dy*165,220),(x+dx*75,y+dy*75,345)],25,(.52,.65,.43),'Wind petal'))
    o=merge(parts,'SM_Lung'+key+'_WindPetals',landmarks);export(o,'Wind'+key,tags=['Interactive'])

# A small, sculpted awareness tree makes the brain a destination.
cx,cy,cz=7720,0,283;parts=[]
parts.append(ellipsoid('Awareness bed',(cx,cy,cz+12),(205,220,35),(.38,.30,.48)))
parts.append(sweep([(cx,cy,cz+20),(cx+15,cy,cz+170),(cx-30,cy+20,cz+370)],32,(.61,.43,.29),'Awareness trunk'))
for j,(dx,dy,dz) in enumerate([(-70,-125,230),(55,130,265),(-30,20,390)]):
    parts.append(sweep([(cx,cy,cz+110),(cx+dx*.4,cy+dy*.5,cz+dz*.75),(cx+dx,cy+dy,cz+dz)],18,(.61,.43,.29),'Awareness branch'))
    o=ellipsoid('Awareness leaf',(cx+dx,cy+dy,cz+dz),(90,100,50),(.46,.64,.37));parts.append(o)
o=merge(parts,'SM_Brain_AwarenessTree',landmarks);export(o,'BrainTree',tags=['Interactive'])

# Quiet care pads are integrated low platforms. The native game adds their moving resource.
for i,s in enumerate(STATIONS):
    if i in [1,2]:continue
    x,y,z=s['position'];palette=PALETTES[s['palette']];r=185 if i<5 else 135
    parts=[ellipsoid('Care base',(x,y,z-2),(r,r,24),palette[1]),ellipsoid('Care inset',(x,y,z+15),(r*.77,r*.77,15),palette[2])]
    if i in [5,6]:
        parts.append(ellipsoid('Adrenal cap',(x+115,y,z+90),(130,170,95),(.64,.49,.24)))
    o=merge(parts,'SM_Care_'+str(i),landmarks);export(o,'Care'+str(i),tags=['Interactive'])

(ART/'asset-manifest.json').write_text(json.dumps(manifest,indent=2))
print('ADVENTURE_EXPORTS_READY',len(manifest),flush=True)

# The editable world opens with named organ collections and a close heart camera.
stage=collection('REVIEW | cameras and lighting')
def area(name,pos,energy,size,color):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
area('Soft key',(-5000,-9000,17000),2500000000,12000,(1,.86,.74));area('Cool fill',(6500,6000,10000),1600000000,10000,(.66,.80,1))
scene.world.color=(.20,.20,.20)
camd=bpy.data.cameras.new('Body atlas');cam=bpy.data.objects.new('Body atlas',camd);stage.objects.link(cam);cam.location=(-3500,100,30000);target=Vector((-3300,0,-100));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=29400;camd.clip_end=100000;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=2200;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ART/'Body-source-review.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Body_Adventure.blend'));print('BODY_EDITABLE_WORLD_SAVED',flush=True)
bpy.ops.render.render(write_still=True);print('BODY_SOURCE_RENDERED',flush=True)
