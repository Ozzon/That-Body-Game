"""Editable C13 landscape and botanical meshes. Does not modify delivered builds."""
import bpy,bmesh,numpy as np,math,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,collection
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C13';EXPORT=ART/'ExportC13';EXPORT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C12.blend'))
manifest=json.loads((ART/'Source/C12/asset-manifest.json').read_text());changed=[]
remove={'Ground','Understory','Paving','CrossingBeds','GardenAccess','GardenAccessEdges','RetainingWalls','TerraceCoping','GardenPocketLeaves','GardenPocketFlowers','UnderstoryLeaves','UnderstoryFlowers'}
remove.update('GardenGrass'+str(i) for i in range(4))
for o in list(bpy.data.objects):
    if o.name.removeprefix('SM_Craft_') in remove:bpy.data.objects.remove(o,do_unlink=True)
manifest=[e for e in manifest if e['key'] not in remove]
coll=collection('C13 | Continuous land and crafted garden surfaces');M={}
for key,rough in [('Turf',.85),('Stone',.63),('Earth',.94),('Grass',.69),('Fern',.56),('Clover',.61),('Iris',.51)]:
    m=bpy.data.materials.get('C13_'+key) or bpy.data.materials.new('C13_'+key);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
    vc=m.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='HeartColor';m.node_tree.links.new(vc.outputs['Color'],p.inputs['Base Color']);M[key]=m

def export(o,key,tags,normals=None):
    o.name='SM_Craft_'+key;o.data.update()
    # Normal directions are explicit for the terrain and blade volumes. Recalc
    # face winding on everything, then restore those authored corner normals.
    if not key.startswith('Terrain'):
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    if normals is not None:o.data.normals_split_custom_set_from_vertices(normals)
    if not o.data.uv_layers:
        uv=o.data.uv_layers.new(name='CraftUV')
        for i,loop in enumerate(o.data.loops):p=o.data.vertices[loop.vertex_index].co;uv.data[i].uv=(p.x/100,p.y/100)
    manifest.append(dict(name=o.name,key=key,spawn=True,tags=tags,materials=[m.name for m in o.data.materials]));changed.append(key)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')

for key in json.loads((DATA/'construction.json').read_text())['terrain_pieces']:
    d=np.load(DATA/(key+'.npz'));o=mesh(key,d['v'],d['f'],d['c'],coll,M['Turf']);o.data.materials.append(M['Earth'])
    top=int(d['topfaces'])
    for f in o.data.polygons:
        if f.index>=top:f.material_index=1
    export(o,key,['Ground'],d['n'].tolist())
print('C13_TERRAIN_EXPORTED',flush=True)

# Five rings roll a stone's edge into a shallow, uneven crown. Separate normal
# groups keep the top readable, while the bevel catches real moving highlights.
buckets={}
for stone in json.loads((DATA/'paving.json').read_text()):
    xy=np.array(stone['xy']);z=np.array(stone['z']);ct=xy.mean(0);n=len(xy);key=(int((ct[0]+3300)//1100),int((ct[1]+3500)//1100))
    V,F,C=buckets.setdefault(key,([],[],[]));start=len(V);seed=stone['seed'];tone=stone['tone']
    base=np.array((.235,.265,.242))*tone
    if seed%9==0:base*=np.array((1.04,.95,.89))
    for k,(inset,lift) in enumerate([(0,-10),(0,-2),(.025,1.7),(.08,4.2),(.38,5.3)]):
        q=ct+(xy-ct)*(1-inset)
        # Low, broad wear avoids the previous cut-glass polygon shading.
        zz=z+lift+.55*np.sin(q[:,0]/29+seed)*np.cos(q[:,1]/31+seed*.7)
        for p,h in zip(q,zz):V.append((*p,h));C.append(base*(.93 if k<2 else 1))
    for layer in range(4):
        for i in range(n):j=(i+1)%n;F.append([start+layer*n+i,start+layer*n+j,start+(layer+1)*n+j,start+(layer+1)*n+i])
    F.append([start+4*n+i for i in range(n)]);F.append([start+i for i in reversed(range(n))])
for (x,y),(V,F,C) in buckets.items():export(mesh('Worn laid stones',V,F,C,coll,M['Stone']),f'Paving{x}_{y}',[])
print('C13_PAVING_EXPORTED',len(buckets),flush=True)

# Botanical geometry is authored at the character's scale: grasses 20–45 cm,
# clover 10–17 cm, fern fronds 45–72 cm, occasional iris accents 45–65 cm.
plants=np.load(DATA/'planting.npz');buckets={};rng=np.random.default_rng(13101)
def leaf(buff,p,a,length,width,rise,col,curl=.22):
    V,F,C,N,UV=buff;start=len(V);axis=np.array([math.cos(a),math.sin(a),0]);side=np.array([-axis[1],axis[0],0]);up=np.array([0,0,1]);p=np.array(p)
    for row in range(7):
        t=row/6;w=width*math.sin(math.pi*t)**.65
        center=p+axis*length*t+up*(rise*t+length*curl*math.sin(math.pi*t))
        for k in [-1,0,1]:
            v=center+side*w*k-up*(abs(k)*w*.19);V.append(v);C.append(np.array(col)*(.77+.23*t+.045*(k==0)))
            n=up*.8-axis*.23+side*k*.20;n/=np.linalg.norm(n);N.append(n);UV.append([k*.5+.5,t])
            if row and k>-1:q=start+(row-1)*3+k;F.append([q,q+1,q+4,q+3])

for idx,(p,kind,s,a) in enumerate(zip(plants['p'],plants['kind'],plants['scale'],plants['angle'])):
    kind=int(kind);ma=['Grass','Clover','Fern','Iris'][kind];key=(ma,int((p[0]+3300)//1100),int((p[1]+3500)//1100));buff=buckets.setdefault(key,([],[],[],[],[]))
    if kind==0:
        for j in range(9):
            ang=a+j*2.399;ln=rng.uniform(16,34)*s;rise=rng.uniform(14,32)*s
            leaf(buff,p+np.array([math.cos(ang)*3,math.sin(ang)*3,0]),ang,ln,1.5*s,rise,(.074,.19,.060),.06)
    elif kind==1:
        for j in range(3):
            base=p+np.array([math.cos(a+j*2.1)*8,math.sin(a+j*2.1)*8,5])*s
            for k in range(3):leaf(buff,base,a+j*.6+k*math.tau/3,12*s,5.8*s,2*s,(.072,.16,.082),.16)
    elif kind==2:
        for j in range(5):
            ang=a+j*2.399;axis=np.array([math.cos(ang),math.sin(ang),0]);ln=rng.uniform(48,72)*s
            # Main midrib and paired, tapering pinnae form one recognizable fern.
            leaf(buff,p,ang,ln,.65*s,17*s,(.055,.135,.052),.24)
            for k in range(1,10):
                t=k/11;at=p+axis*ln*t+np.array([0,0,17*s*t+ln*.24*math.sin(math.pi*t)])
                for sign in [-1,1]:leaf(buff,at,ang+sign*1.05,16*s*math.sin(math.pi*t)**.65,2.3*s,2*s,(.065,.172,.075),.15)
    else:
        for j in range(5):leaf(buff,p,a+j*1.9,20*s,2.8*s,35*s,(.060,.148,.118),.1)
        top=p+np.array([0,0,46*s])
        for j in range(6):leaf(buff,top,a+j*math.tau/6,13*s,6*s,(-2 if j%2 else 10)*s,(.36,.28,.49),.24)
for (ma,x,y),(V,F,C,N,UV) in buckets.items():
    o=mesh('Botanical '+ma,V,F,C,coll,M[ma]);uv=o.data.uv_layers.new(name='CraftUV');weights=o.data.uv_layers.new(name='RootWeight')
    for i,loop in enumerate(o.data.loops):uv.data[i].uv=UV[loop.vertex_index];weights.data[i].uv=UV[loop.vertex_index]
    export(o,f'Botany{ma}{x}_{y}',['GroundCover','Foliage'],[tuple(n) for n in N])
print('C13_BOTANY_EXPORTED',len(buckets),flush=True)
(DATA/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(DATA/'patch.json').write_text(json.dumps(dict(changed=changed,remove=sorted(remove)),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C13.blend'));print('C13_AUTHORED_GARDEN_READY',flush=True)
