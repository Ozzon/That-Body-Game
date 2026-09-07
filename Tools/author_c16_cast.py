"""Editable thought models and expression parts, based on FigJam ref-275."""
import bpy, bmesh, math, json, sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Tools'))
from garden_model import mesh, merge, sweep, collection, material
ART = ROOT/'Art/BrainCraft'; DATA = ART/'Source/C16'; EXPORT = ART/'ExportC16'
EXPORT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=.01
cast = collection('C16 | Thought cast and expression rig')
palette = {'Gold':(.92,.47,.038), 'Cloud':(.047,.027,.13), 'Wisp':(.10,.027,.22),
           'Amber':(.59,.135,.021), 'Ink':(.009,.008,.02), 'Eye':(.61,.16,.95),
           'Glint':(1,.83,.40), 'Filament':(.28,.08,.61), 'Cheek':(.96,.22,.08)}
M = {k:material('C16_'+k, .4 if k in ['Eye','Glint','Filament'] else 0, .36 if k=='Gold' else .58) for k in palette}
manifest=[]

def finish(o,key):
    o.name='SM_Craft_'+key
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    o.data.update()
    uv=o.data.uv_layers.new(name='CraftUV')
    for face in o.data.polygons:
        for li in face.loop_indices:
            p=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(p.y/100,p.z/100)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    manifest.append({'key':key,'materials':[m.name for m in o.data.materials], 'vertices':len(o.data.vertices),'spawn':False})
    return o

def orb(name,center,radii,family):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=center)
    o=bpy.context.object;o.name=name;o.scale=radii
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for old in list(o.users_collection):old.objects.unlink(o)
    cast.objects.link(o);o.data.materials.append(M[family])
    attr=o.data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='POINT')
    for c in attr.data:c.color=(*palette[family],1)
    for face in o.data.polygons:face.use_smooth=True
    return o

# One inflated star with continuous curved side walls and a five-point silhouette.
v=[];f=[];colors=[];rows=64;cols=240
for i in range(rows+1):
    p=math.pi*i/rows
    for j in range(cols):
        a=j*math.tau/cols
        r=(39+14*math.cos(5*a))*math.sin(p)
        v.append((24*math.cos(p),r*math.sin(a),r*math.cos(a)))
        colors.append(np.array(palette['Gold'])*(.94+.06*math.cos(a)))
        if i:q=(i-1)*cols+j;n=(i-1)*cols+(j+1)%cols;f.append((q,n,n+cols,q+cols))
finish(mesh('Bright thought inflated star',v,f,colors,cast,M['Gold']),'C16ThoughtStar')
for kind in ['Cloud','Wisp']:
    d=np.load(DATA/f'Thought{kind}.npz');v=d['v'];col=np.tile(palette[kind],(len(v),1))
    col*= (.91+.09*np.clip((v[:,2]+70)/140,0,1))[:,None]
    finish(mesh(kind+' authored soft lobes',v,d['f'],col,cast,M[kind]),'C16Thought'+kind)

# The persistent thought is overlapping curled petals, not one thick spiral pipe.
petals=[orb('Amber rosette heart',(0,0,0),(17,30,30),'Amber')]
for ring,count,radius,start in [(0,7,38,0),(1,5,20,.42)]:
    for k in range(count):
        V=[];F=[];C=[];nr=44;nc=20
        base=k*math.tau/count+start
        for i in range(nr):
            t=i/(nr-1);angle=base+t*1.68
            rad=radius*(.58+.54*t)
            width=(9 if ring==0 else 6.8)*(math.sin(math.pi*t)**.50+.10)
            for j in range(nc):
                a=j*math.tau/nc
                V.append(((10 if ring==0 else 22)+math.sin(t*math.pi)*3+width*.33*math.cos(a),
                          (rad+width*math.sin(a))*math.sin(angle),
                          (rad+width*math.sin(a))*math.cos(angle)))
                C.append(np.array(palette['Amber'])*(1+.12*math.cos(a)) + np.array((.09,.04,.006))*math.sin(t*math.pi))
                if i:q=(i-1)*nc+j;n=(i-1)*nc+(j+1)%nc;F.append((q,n,n+nc,q+nc))
        F.extend([tuple(reversed(range(nc))),tuple((nr-1)*nc+j for j in range(nc))])
        petals.append(mesh('Curled rosette petal',V,F,C,cast,M['Amber']))
finish(merge(petals,'Layered persistent rosette'),'C16ThoughtKnot')

# Eyes are separate meshes with centred pivots so blinks do not squash mouths.
for kind,width,height in [('Bright',5.6,8.4),('Cloud',7.8,5.7),('Wisp',4.3,5.0)]:
    parts=[orb('Eye socket',(0,0,0),(2.3,width+1.1,height+1.0),'Ink')]
    if kind=='Bright':
        parts += [orb('Polished dark iris',(1.3,0,0),(1.8,width,height),'Ink'),
                  orb('Large warm catchlight',(2.8,-1.5,2.8),(.65,1.8,2.3),'Glint'),
                  orb('Small catchlight',(2.9,1.3,-2.5),(.4,.7,.9),'Glint')]
    else:
        eye=orb('Violet almond',(1.3,0,0),(1.6,width,height),'Eye')
        for vert in eye.data.vertices:
            p=vert.co; p.z+=p.y*.32
        parts+=[eye,orb('Soft eye highlight',(2.6,-1.4,1.8),(.45,width*.19,height*.24),'Glint')]
    finish(merge(parts,kind+' expression eye'),'C16Eye'+kind)
mouths=[]
mouths.append(sweep('Small warm smile',[(25.2,y,-10-2.8*math.cos(y/6*math.pi/2)) for y in np.linspace(-6,6,24)],[.8,.95,.8],palette['Ink'],cast,M['Ink'],10,2,0))
for side in [-1,1]:mouths.append(orb('Subtle warm cheek',(20.8,side*22,-7),(1,4.2,2),'Cheek'))
finish(merge(mouths,'Star cheeks and smile'),'C16FaceBright')
finish(sweep('Heavy thought downturned mouth',[(47,y,-12+1.6*math.cos(y/6*math.pi/2)) for y in np.linspace(-6,6,24)],[.9,1.1,.9],palette['Ink'],cast,M['Ink'],10,2,0),'C16FaceCloud')
finish(orb('Small wisp mouth',(20,0,-7),(1,1.9,1.3),'Ink'),'C16FaceWisp')
V=[(34,0,11),(34,9,0),(34,0,-11),(34,-9,0),(39,0,0),(32,0,0)]
F=[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(1,0,5),(2,1,5),(3,2,5),(0,3,5)]
finish(mesh('Persistent glowing diamond',V,F,palette['Glint'],cast,M['Glint']),'C16FaceKnot')
for k in range(3):
    points=[]
    for t in np.linspace(0,math.tau,120):
        r=33+3*math.sin(t*3+k)
        points.append((-4+12*math.sin(t*2+k),r*math.cos(t),r*math.sin(t)))
    finish(sweep('Fine restless filament',points,[.75,.95,.75],palette['Filament'],cast,M['Filament'],8,2,0),'C16WispThread'+str(k))

# Measure frontal body surface for each eye socket, retaining contact data.
anchors={}
for kind,bodykey,y,z in [('Bright','Star',13,3),('Cloud','Cloud',19,1),('Wisp','Wisp',9,1)]:
    body=bpy.data.objects['SM_Craft_C16Thought'+bodykey]
    tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    pts=[]
    for side in [-1,1]:
        hit=tree.ray_cast(Vector((200,side*y,z)),Vector((-1,0,0)),400)
        assert hit[0] is not None
        pts.append([float(hit[0].x+1),side*y,z])
    anchors[kind]=pts
(DATA/'cast-patch.json').write_text(json.dumps({'assets':manifest,'eye_anchors':anchors},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Thought_Cast_C16.blend'))
print('C16_EDITABLE_CAST_READY',json.dumps(anchors),flush=True)
