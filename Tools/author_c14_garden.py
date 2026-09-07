"""C14 editable garden: continuous slopes, worn paving and living border nests."""
import bpy,numpy as np,math,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Intermediate/BlenderDeps'))
from scipy.ndimage import map_coordinates
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,collection
from brain_craft_layout import OUTLINE,curve
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C14';OLD=ART/'Source/C13';EXPORT=ART/'ExportC14';EXPORT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C13.blend'))
coll=collection('C14 | Connected garden and living gates');terrain=np.load(DATA/'terrain.npz');H=terrain['h'];D=terrain['delta'];xs=terrain['x'];ys=terrain['y'];step=xs[1]-xs[0];gates=json.loads((DATA/'portals.json').read_text());changed=[]
def sample(h,p):p=np.asarray(p);return map_coordinates(h,[(p[...,0]-xs[0])/step,(p[...,1]-ys[0])/step],order=1,mode='nearest')
def remove(key):
    o=bpy.data.objects.get('SM_Craft_'+key)
    if o:bpy.data.objects.remove(o,do_unlink=True)
def export(o,key):
    o.name='SM_Craft_'+key;o.data.update()
    if not o.data.uv_layers:
        uv=o.data.uv_layers.new(name='CraftUV')
        for f in o.data.polygons:
            axis=max(range(3),key=lambda k:abs(f.normal[k]));ab=[k for k in range(3) if k!=axis]
            for i in f.loop_indices:p=o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(p[ab[0]]/100,p[ab[1]]/100)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    changed.append(key)
for key in json.loads((DATA/'construction.json').read_text())['changed_terrain']:
    remove(key);a=np.load(DATA/(key+'.npz'));n=a['n'].copy();n[np.abs(n[:,2])<.001]*=-1
    o=mesh('SM_Craft_'+key,a['v'],a['f'],a['c'],coll,bpy.data.materials['C13_Turf'],n.tolist());o.data.materials.append(bpy.data.materials['C13_Earth']);top=int(a['topfaces'])
    for f in o.data.polygons:
        if f.index>=top:f.material_index=1
    assert min(f.normal.z for f in o.data.polygons[:top])>0,key
    export(o,key)
print('C14_CONNECTED_TERRAIN_EXPORTED',flush=True)
# Round each stone's plan silhouette; crown planes fit the local slope rather
# than folding a polygon across several different heightfield samples.
stones=json.loads((OLD/'paving.json').read_text());rng=np.random.default_rng(14073)
for e in gates:
    p=np.array(e['p'][:2]);a=np.array(e['approach_start'][:2]);v=p-a;ln=np.linalg.norm(v);v/=ln;side=np.array([-v[1],v[0]])
    for t in np.arange(60,ln+1,88):
        for k in [-1,0,1]:
            ct=a+v*t+side*k*83;q=[ct+side*u+v*w for u,w in [(-38,-40),(38,-40),(38,40),(-38,40)]]
            stones.append(dict(xy=np.array(q).tolist(),tone=float(rng.uniform(.92,1.06)),seed=len(stones)))
buckets={};gx,gy=np.gradient(H,step)
for s in stones:
    poly=Polygon(s['xy']);poly=poly.buffer(-7,join_style=1).buffer(7,quad_segs=3)
    if poly.is_empty or poly.area<400:continue
    if poly.geom_type=='MultiPolygon':poly=max(poly.geoms,key=lambda g:g.area)
    # Shapely's buffer exterior is clockwise; explicit top face winding matters.
    from shapely.geometry.polygon import orient
    xy=np.array(orient(poly,1).exterior.coords[:-1]);ct=xy.mean(0);n=len(xy);key=(int((ct[0]+3300)//1100),int((ct[1]+3500)//1100));V,F,C=buckets.setdefault(key,([],[],[]));start=len(V)
    hc=float(sample(H,ct[None,:])[0]);grad=np.array([sample(gx,ct[None,:])[0],sample(gy,ct[None,:])[0]])
    base=np.array([.27,.245,.205])*s['tone']
    for inset,lift in [(0,-9),(0,-1),(.025,1.5),(.085,3.3),(.33,4.2)]:
        q=ct+(xy-ct)*(1-inset);z=hc+(q-ct)@grad+lift
        V.extend(np.column_stack([q,z]).tolist());C.extend([base.tolist()]*n)
    for layer in range(4):
        for i in range(n):j=(i+1)%n;F.append([start+layer*n+i,start+layer*n+j,start+(layer+1)*n+j,start+(layer+1)*n+i])
    F.append([start+4*n+i for i in range(n)]);F.append([start+i for i in reversed(range(n))])
for (x,y),(V,F,C) in buckets.items():
    key=f'Paving{x}_{y}';remove(key);o=mesh('SM_Craft_'+key,V,F,C,coll,bpy.data.materials['C13_Stone']);export(o,key)
print('C14_ROUNDED_PAVING_EXPORTED',len(buckets),flush=True)
access=unary_union([LineString([e['approach_start'][:2],e['p'][:2]]).buffer(180) for e in gates])
for o in list(bpy.data.objects):
    if not o.name.startswith('SM_Craft_Botany'):continue
    key=o.name.removeprefix('SM_Craft_');verts=np.array([v.co[:] for v in o.data.vertices]);z=sample(D,verts[:,:2]);verts[:,2]+=z
    for v,p in zip(o.data.vertices,verts):v.co=p
    # Clear only the new gate paths, keeping small plants at their edges.
    if any(access.intersects(Point(*p[:2])) for p in verts[::60]):
        import bmesh
        bm=bmesh.new();bm.from_mesh(o.data);kill=[]
        for f in bm.faces:
            c=f.calc_center_median()
            if access.contains(Point(c.x,c.y)):kill.append(f)
        bmesh.ops.delete(bm,geom=kill,context='FACES');bm.to_mesh(o.data);bm.free()
    o.data.update();norm=np.zeros((len(o.data.vertices),3))
    for f in o.data.polygons:
        n=np.array(f.normal);n*=1 if n[2]>=0 else -1
        for i in f.vertices:norm[i]+=n
    norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],.001);norm=norm*.86+np.array([0,0,.14]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],.001);o.data.normals_split_custom_set_from_vertices(norm.tolist());export(o,key)
print('C14_ROOTED_BOTANY_EXPORTED',flush=True)
# Shift the cortical root with the actual ground, then cut a real tunnel for
# each nest. Boolean cutters are construction tools, not visible placeholders.
outline=curve(OUTLINE,30);aa=np.mod(np.arctan2(outline[:,1],outline[:,0]),math.tau);rr=np.linalg.norm(outline,axis=1);order=np.argsort(aa);aa=aa[order];rr=rr[order]
cutters=[]
for e in gates:
    p=np.array(e['p']);out=np.array([*e['outward'],0]);side=np.array([-out[1],out[0],0]);V=[];F=[];count=96
    for depth in [-350,1100]:
        for j in range(count):t=j*math.tau/count;V.append((p+side*205*math.cos(t)+out*depth+np.array([0,0,205+235*math.sin(t)])).tolist())
    for j in range(count):k=(j+1)%count;F.append([j,k,k+count,j+count])
    F.append(list(reversed(range(count))));F.append(list(range(count,count*2)))
    cutter=mesh('Gate construction cutter',V,F,[.5,.5,.5],coll,bpy.data.materials['C13_Tissue']);cutters.append(cutter)
for key in json.loads((OLD/'cortex-construction.json').read_text())['keys']:
    o=bpy.data.objects['SM_Craft_'+key];v=np.array([p.co[:] for p in o.data.vertices]);angle=np.mod(np.arctan2(v[:,1],v[:,0]),math.tau);r=np.interp(angle,np.r_[aa-math.tau,aa,aa+math.tau],np.tile(rr,3))-18;inner=np.column_stack([r*np.cos(angle),r*np.sin(angle)]);v[:,2]+=sample(D,inner)
    for p,q in zip(o.data.vertices,v):p.co=q
    for cutter in cutters:
        mod=o.modifiers.new('Carved nest passage','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    export(o,key)
for c in cutters:bpy.data.objects.remove(c,do_unlink=True)
print('C14_CORTEX_PASSAGES_CARVED',flush=True)
for idx,e in enumerate(gates):
    p=np.array(e['p']);out=np.array([*e['outward'],0]);side=np.array([-out[1],out[0],0]);up=np.array([0,0,1]);n=192;m=64;V=[];F=[];C=[]
    for i in range(n):
        a=math.tau*i/n;ca=math.cos(a);sa=math.sin(a);thick=91+10*math.sin(a*3+.6)
        for j in range(m):
            t=math.tau*j/m;wave=7*math.cos(a*25+math.sin(t*2)*1.4)+3*math.cos(a*11-t*3);r=thick+wave
            q=p+side*((239+r*math.cos(t))*ca)+out*(90+156*math.sin(t))+up*(205+(252+r*math.cos(t))*sa)
            V.append(q.tolist());violet=(1-math.cos(t))*.5;col=np.array([.43,.165,.235])*(1-violet*.6)+np.array([.25,.085,.36])*(violet*.6);C.append(col.tolist())
    for i in range(n):
        for j in range(m):a=i*m+j;b=((i+1)%n)*m+j;c=((i+1)%n)*m+(j+1)%m;d=i*m+(j+1)%m;F.append([a,b,c,d])
    key='Nest'+str(idx);remove(key);o=mesh('SM_Craft_'+key,V,F,C,coll,bpy.data.materials['C13_Tissue']);o['GatePose']=json.dumps(e);export(o,key)
    # Recessed living surface, UV coordinates follow the mouth rather than world
    # axes. Existing animated neural shader remains the interactive focal point.
    V=[(p+out*255+up*205).tolist()];F=[];C=[];uvs=[[.5,.5]]
    for ring in range(1,17):
        r=ring/16
        for j in range(128):
            a=j*math.tau/128;V.append((p+side*(180*r*math.cos(a))+up*(205+208*r*math.sin(a))+out*(255-110*r*r)).tolist());uvs.append([.5+.5*r*math.cos(a),.5+.5*r*math.sin(a)])
    for j in range(128):F.append([0,1+j,1+(j+1)%128])
    for ring in range(15):
        for j in range(128):a=1+ring*128+j;b=1+ring*128+(j+1)%128;F.append([a,a+128,b+128,b])
    key='NestGlow'+str(idx);remove(key);ma=bpy.data.materials['C11_Portal'+e['color']];col={'Dawn':[.78,.38,.075],'Spring':[.06,.54,.54],'Memory':[.34,.13,.56]}[e['color']];o=mesh('SM_Craft_'+key,V,[f[::-1] for f in F],col,coll,ma);uv=o.data.uv_layers.new(name='CraftUV')
    for i,l in enumerate(o.data.loops):uv.data[i].uv=uvs[l.vertex_index]
    export(o,key)
(DATA/'patch.json').write_text(json.dumps(dict(changed=list(dict.fromkeys(changed)),new_paving=[f'Paving{x}_{y}' for x,y in buckets]),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C14.blend'));print('C14_AUTHORED_GARDEN_READY',flush=True)
