import bpy, numpy as np, math, json, sys
from mathutils import Vector
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VARIANT=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'A'
ART=ROOT/'Art/HeartModels'/VARIANT
SPEC=json.loads((ART/'Source/heart-layout.json').read_text())
EXPORT=ART/'Export';EXPORT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01

def collection(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
sculpt_collection=collection('01 | Continuous sculpted heart')
vessel_collection=collection('02 | Great vessels')
care_collection=collection('03 | Pacing valve')
stage_collection=collection('04 | Review lighting and cameras')

def material(name,color,emission=0,vertex=False):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    nodes=m.node_tree.nodes;p=nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.65
    p.inputs['Subsurface Weight'].default_value=.06
    if vertex:
        a=nodes.new('ShaderNodeVertexColor');a.layer_name='HeartColor'
        m.node_tree.links.new(a.outputs['Color'],p.inputs['Base Color'])
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    return m

sculpt_mat=material('Heart | painted coral muscle',(.7,.2,.16),vertex=True)
coral=material('Artery | warm coral',(.52,.10,.058))
inner=material('Vessel | inner membrane',(.45,.10,.10))
blue=material('Vein | muted periwinkle',(.18,.28,.35))
peach=material('Valve | soft peach',(.79,.27,.15))
gold=material('Pulse | honey light',(1,.5,.10),1.3)
dark=material('Stage | midnight teal',(.022,.04,.065))

def mesh_object(name,verts,faces,coll,mat,colors=None,normals=None):
    me=bpy.data.meshes.new(name+' Geometry');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);coll.objects.link(ob);me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    if colors is not None:
        a=me.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='POINT')
        rgba=np.concatenate((colors,np.ones((len(colors),1))),axis=1).ravel()
        a.data.foreach_set('color',rgba)
    if normals is not None:me.normals_split_custom_set_from_vertices(normals)
    return ob

data=np.load(ART/'Source/heart_sculpt.npz')
V,F,N,C=[data[n] for n in ['vertices','faces','normals','colors']]
centers=V[F].mean(axis=1)
# Keep one complete editable sculpt; matched surface pieces let Unreal fade only the foreground wall.
master=mesh_object('Heart | master watertight sculpt',V.tolist(),F.tolist(),sculpt_collection,sculpt_mat,C,N.tolist())
master.hide_render=True;master.hide_set(True)
master['source']='Four individually drawn chambers, five arched portals, asymmetrical muscular shell.'
master['units']='Unreal centimeters'
exports=[]
partition=np.where(centers[:,2]<110,0,1+(centers[:,0]>60).astype(int)*2+(centers[:,1]>0).astype(int))
names=['SM_Heart_Foundation','SM_Heart_WallFrontRight','SM_Heart_WallFrontLeft','SM_Heart_WallBackRight','SM_Heart_WallBackLeft']
for i,name in enumerate(names):
    faces=F[partition==i];ids,inv=np.unique(faces.ravel(),return_inverse=True)
    ob=mesh_object(name,V[ids].tolist(),inv.reshape((-1,3)).tolist(),sculpt_collection,sculpt_mat,C[ids],N[ids].tolist());exports.append(ob)

def spline(points,steps=12):
    p=[Vector(x) for x in points];out=[]
    for i in range(len(p)-1):
        a=p[max(0,i-1)];b=p[i];c=p[i+1];d=p[min(len(p)-1,i+2)]
        for k in range(steps):
            t=k/steps;out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    out.append(p[-1]);return out

def vessel(name,points,radii,mat):
    points=spline(points,12);verts=[];faces=[];count=len(points);sides=48
    for shell in range(2):
        for i,p in enumerate(points):
            t=i/(count-1);r=float(np.interp(t,np.linspace(0,1,len(radii)),radii))-shell*24
            tangent=(points[min(count-1,i+1)]-points[max(0,i-1)]).normalized()
            u=tangent.cross(Vector((0,0,1))).normalized()
            if u.length<.1:u=Vector((1,0,0))
            v=tangent.cross(u).normalized()
            for j in range(sides):
                a=j*math.tau/sides;rr=r*(1+.015*math.cos(a*3+t*5))
                verts.append(tuple(p+rr*(u*math.cos(a)+v*math.sin(a))))
        base=shell*count*sides
        for i in range(count-1):
            for j in range(sides):
                q=base+i*sides+j;qn=base+i*sides+(j+1)%sides
                face=(q,qn,qn+sides,q+sides);faces.append(face if shell==0 else face[::-1])
    for end in [0,count-1]:
        for j in range(sides):
            a=end*sides+j;b=end*sides+(j+1)%sides
            faces.append((a,b,b+count*sides,a+count*sides) if end else (b,a,a+count*sides,b+count*sides))
    ob=mesh_object(name,verts,faces,vessel_collection,mat)
    # A small bevel rolls the open lip into the lumen.
    mod=ob.modifiers.new('Soft membrane lip','BEVEL');mod.width=5;mod.segments=3
    exports.append(ob);return ob

vessel('SM_Heart_Aorta',SPEC['aorta'],[155,148,118,95],coral)

def rounded_mesh(name,location,scale,mat,coll=care_collection):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=location)
    ob=bpy.context.object;ob.name=name;ob.scale=scale
    for c in list(ob.users_collection):c.objects.unlink(ob)
    coll.objects.link(ob);ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=True
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    # Export world coordinates with one consistent origin.
    bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
    return ob

sx,sy=SPEC['station'];base=105*max(0,min(1,(sx-150)/650)) if SPEC['floor']=='terraced' else 0
station=[]
station.append(rounded_mesh('Valve lower step',(sx,sy,base+76),(205,194,27),coral))
station.append(rounded_mesh('Valve upper step',(sx,sy,base+108),(170,160,22),peach))
station.append(rounded_mesh('Valve central disc',(sx,sy,base+128),(129,123,13),coral))
bpy.ops.object.select_all(action='DESELECT')
for ob in station:ob.select_set(True)
bpy.context.view_layer.objects.active=station[0];bpy.ops.object.join()
valve=bpy.context.object;valve.name='SM_Heart_PacingValve';exports.append(valve)

# A single heart-shaped resource, with a soft sculpted profile and rounded thickness.
verts=[];faces=[];rows=32;cols=96
for r in range(rows+1):
    lat=-math.pi/2+math.pi*r/rows;rad=math.cos(lat)
    for j in range(cols):
        t=j*math.tau/cols
        x=16*math.sin(t)**3
        z=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        verts.append((sx+math.sin(lat)*48,sy+x*5*rad,base+267+z*5*rad))
        if r<rows:
            a=r*cols+j;b=r*cols+(j+1)%cols;faces.append((a,b,b+cols,a+cols))
seed=mesh_object('SM_Heart_PulseSeed',verts,faces,care_collection,gold);exports.append(seed)

for ob in exports:
    if not ob.data.color_attributes.get('HeartColor'):
        attr=ob.data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='CORNER')
        for poly in ob.data.polygons:
            color=ob.data.materials[poly.material_index].diffuse_color
            for loop in poly.loop_indices:attr.data[loop].color=color
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',bake_space_transform=False,mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')

# Lighting for reviewing the authored source. Unreal screenshots are captured separately.
ground=rounded_mesh('Review plinth',(0,0,-250),(5000,5000,20),dark,stage_collection)
def area(name,pos,energy,size,color):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);stage_collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,100))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large warm key',(-1800,-1800,3800),110000000,2200,(1,.81,.66))
area('Soft peach fill',(-300,2000,2200),44000000,2200,(1,.70,.59))
area('Cool upper rim',(2200,0,2600),90000000,1900,(.57,.72,1))
scene.world.color=(.22,.22,.22)
camd=bpy.data.cameras.new('Heart three quarter');cam=bpy.data.objects.new('Heart three quarter',camd);stage_collection.objects.link(cam)
cam.location=(-3700,200,2950);target=Vector((-100,0,130));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=3800;camd.clip_end=30000;camd.clip_start=1;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ART/'Heart-source-review.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/('Heart_Model_'+VARIANT+'.blend')))
(ART/'Export/asset-manifest.json').write_text(json.dumps({'assets':[o.name for o in exports],'unit':'cm','source':'Heart_Baseline.blend','style_target':'Concept/Heart-direction-study.png'},indent=2))
print('HEART_AUTHORING_SAVED',flush=True)
bpy.ops.render.render(write_still=True)
print('HEART_SOURCE_RENDERED',flush=True)
