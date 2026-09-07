"""C17: continuous awareness tree, fitted paving and modeled garden relief."""
import bpy, bmesh, math, json, sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'Tools'),str(ROOT/'Intermediate/BlenderDeps')]
from scipy.ndimage import map_coordinates, distance_transform_edt
from shapely.geometry import Polygon, Point
from shapely.geometry.polygon import orient
from shapely.ops import triangulate
from garden_model import mesh, collection, merge
from organ_math import curve

ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C17';OUT=ART/'ExportC17'
DATA.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C15.blend'))
coll=collection('C17 | Awareness tree and fitted garden');manifest=[];removed=[]
rng=np.random.default_rng(17091);M={}
for name,col,rough in [('Bark',(.24,.105,.035),.61),('Leaf',(.65,.36,.047),.40),('Glow',(.93,.48,.06),.34),('Stone',(.24,.18,.12),.66),('Moss',(.095,.16,.038),.85)]:
    mat=bpy.data.materials.new('C17_'+name);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough
    vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='HeartColor';mat.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
    if name=='Glow':mat.node_tree.links.new(vc.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1.4
    M[name]=mat

def erase(key):
    old=bpy.data.objects.get('SM_Craft_'+key)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    removed.append(key)

def export(obj,key,tags,collision=False):
    obj.name='SM_Craft_C17_'+key
    obj.data.update()
    if not obj.data.uv_layers:
        uv=obj.data.uv_layers.new(name='CraftUV')
        for i,l in enumerate(obj.data.loops):
            p=obj.data.vertices[l.vertex_index].co;uv.data[i].uv=(p.x/250,p.y/250)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(OUT/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    manifest.append(dict(key=key,name=obj.name,tags=tags,collision=collision,materials=[m.name for m in obj.data.materials],vertices=len(obj.data.vertices),triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)))

origin=np.array([0.,90.,520.]);wood=[]
def branch(points,radii,name='Growing wood',rib=.06,sides=24,sub=10):
    pts=curve(points,sub,False);pts=pts[np.r_[True,np.linalg.norm(np.diff(pts,axis=0),axis=1)>1e-4]]
    assert len(pts)>1,name
    rads=np.interp(np.linspace(0,1,len(pts)),np.linspace(0,1,len(radii)),radii);V=[];F=[];C=[]
    last_u=None
    for i,(p,r) in enumerate(zip(pts,rads)):
        axis=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)];axis/=np.linalg.norm(axis)
        if last_u is None:
            helper=np.array([0.,1.,0.]) if abs(axis[1])<.85 else np.array([1.,0.,0.]);u=np.cross(axis,helper)
        else:u=last_u-axis*np.dot(last_u,axis)
        if np.linalg.norm(u)<1e-4:u=np.cross(axis,[0,1,0] if abs(axis[1])<.85 else [1,0,0])
        u/=np.linalg.norm(u);v=np.cross(axis,u);last_u=u;t=i/(len(pts)-1)
        for j in range(sides):
            a=j*math.tau/sides;rr=r*(1+rib*math.cos(a*5-t*6)+rib*.45*math.cos(a*9-t*4))
            V.append(p+(u*math.cos(a)+v*math.sin(a))*rr);C.append(np.array([.24,.115,.037])*(.95+.05*math.cos(a*5-t*6)))
            if i:q=(i-1)*sides+j;k=(i-1)*sides+(j+1)%sides;F.append([q,k,k+sides,q+sides])
    F.append(list(range(sides-1,-1,-1)));F.append(list(range((len(pts)-1)*sides,len(pts)*sides)))
    return mesh(name,V,F,C,coll,M['Bark'])

trunk=np.array([(0,0,-25),(-25,4,150),(38,9,320),(-32,25,510),(30,32,700),(-5,52,870),(45,24,1030)])
tradii=[135,97,76,61,43,22,.5]
wood.append(branch(trunk+origin,tradii,'Continuous fluted trunk',rib=.15,sides=48,sub=15))
# Root flares share the trunk's helical flow. Every root meets the planted bed.
for k,a in enumerate([-.48,.30,1.05,1.82,2.65,3.43,4.25,5.03]):
    pts=[]
    for r,z,turn in [(300+16*math.sin(k),-5,0),(225,16,.10),(145,60,.23),(88,145,.43),(48,280,.82)]:
        pts.append(origin+np.array([math.cos(a+turn)*r,math.sin(a+turn)*r,z]))
    wood.append(branch(pts,[1,19,39,43,37],'Integrated buttress root',rib=.08,sides=28,sub=10))
    if k%2==0:
        p=np.array(pts[1]);wood.append(branch([p,origin+np.array([math.cos(a-.21)*270,math.sin(a-.21)*270,7]),origin+np.array([math.cos(a-.26)*323,math.sin(a-.26)*323,-2])],[13,7,.3],'Root finger',sides=12))
branches=[
    ([(7,0,365),(-136,-22,505),(-330,-45,565),(-475,-65,722),(-570,-22,860)],[67,54,34,14,.6]),
    ([(0,18,435),(150,28,565),(323,90,623),(450,130,805),(565,85,925)],[61,47,30,15,.5]),
    ([(12,27,620),(-105,165,735),(-240,317,825),(-310,440,1030)],[43,31,18,.4]),
    ([(14,37,692),(148,202,775),(276,368,942),(402,459,1088)],[36,29,14,.3]),
    ([(-2,4,470),(-105,-130,535),(-295,-220,594),(-422,-285,775)],[43,31,20,.4]),
    ([(18,11,544),(145,-109,593),(260,-195,707),(375,-250,858)],[39,28,16,.4]),
    ([(-1,39,813),(-107,94,952),(-171,88,1085),(-246,117,1170)],[25,18,8,.3]),
]
sprigs=[]
for b,(points,radii) in enumerate(branches):
    pts=np.array(points,float)+origin;wood.append(branch(pts,radii,'Grafted primary bough',rib=.08,sides=32,sub=13))
    for j,t in enumerate([.48,.69,.88]):
        dense=curve(pts,18,False);idx=int(t*(len(dense)-1));start=dense[idx]
        tangent=dense[min(idx+1,len(dense)-1)]-dense[max(idx-1,0)];tangent/=np.linalg.norm(tangent)
        sign=(-1)**j;d=np.array([-tangent[1]*sign,tangent[0]*sign,.65]);d/=np.linalg.norm(d)
        tip=start+d*(130+(b+j)%3*24)+np.array([0,0,40]);fork=[start,start+d*70+np.array([0,0,-6]),tip]
        wood.append(branch(fork,[max(7,13-j*3),6,.35],'Tapered leaf-bearing fork',rib=.035,sides=14,sub=10))
        sprigs.append((np.array(fork),b*3+j))
    sprigs.append((pts[-2:],100+b))
sprigs.append((trunk[-2:]+origin,200))
tree=merge(wood,'Connected tree sculpt')
rem=tree.modifiers.new('Fuse grown branch junctions','REMESH');rem.mode='VOXEL';rem.voxel_size=3.5;rem.use_smooth_shade=True
bpy.context.view_layer.objects.active=tree;bpy.ops.object.modifier_apply(modifier=rem.name)
smooth=tree.modifiers.new('Soften junction transitions','SMOOTH');smooth.factor=.7;smooth.iterations=5;bpy.ops.object.modifier_apply(modifier=smooth.name)
bm=bmesh.new();bm.from_mesh(tree.data);seen=set();islands=[]
for v in bm.verts:
    if v in seen:continue
    stack=[v];seen.add(v);island=[]
    while stack:
        a=stack.pop();island.append(a)
        for e in a.link_edges:
            b=e.other_vert(a)
            if b not in seen:seen.add(b);stack.append(b)
    islands.append(island)
largest=max(islands,key=len);loose=[v for island in islands if island is not largest for v in island]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(tree.data);bm.free()
if tree.data.color_attributes.get('HeartColor'):tree.data.color_attributes.remove(tree.data.color_attributes['HeartColor'])
coords=np.array([v.co[:] for v in tree.data.vertices]);z=(coords[:,2]-520)/1150
col=np.column_stack([.20+.075*z,.078+.057*z,.022+.025*z])
col*=np.clip(.94+.06*np.sin(coords[:,0]/63+coords[:,2]/117),.82,1.1)[:,None]
ca=tree.data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',np.column_stack([col,np.ones(len(col))]).ravel())
for f in tree.data.polygons:f.use_smooth=True
erase('TreeWood');export(tree,'TreeWood',['Interactive'],True)
print('C17_CONTINUOUS_TREE_READY',len(tree.data.vertices),flush=True)

# Leaves are folded lanceolate blades, each attached to a twig. Their UVs run
# across the blade and root-to-tip, supporting stable veins and rooted wind.
V=[];F=[];C=[];UV=[];leaf_count=0
def leaf(p,d,length,width,roll,tone):
    global leaf_count
    axis=np.array(d,float);axis/=np.linalg.norm(axis);side=np.cross(axis,[0,0,1.])
    if np.linalg.norm(side)<.1:side=np.array([1.,0,0])
    side/=np.linalg.norm(side);up=np.cross(side,axis);side=side*math.cos(roll)+up*math.sin(roll);up=np.cross(side,axis)
    start=len(V);rows=10;cols=5
    for i in range(rows+1):
        t=i/rows;span=width*math.sin(math.pi*t)**.88
        center=p+axis*length*t+up*(length*.14*math.sin(math.pi*t)-length*.17*t*t)
        for j in range(cols):
            w=(j/(cols-1)*2-1);q=center+side*span*w+up*(span*.24*(1-abs(w)))
            V.append(q);C.append(np.array([.64,.33,.038])*tone*(.82+.18*t+.14*(1-abs(w))));UV.append([j/(cols-1),t])
            if i and j:a=start+(i-1)*cols+j-1;F.append([a,a+1,a+cols+1,a+cols])
    leaf_count+=1
twigs=[]
for points,seed in sprigs:
    dense=curve(points,12,False)
    for node,t in enumerate([.24,.46,.68,.87,1.]):
        index=int((len(dense)-1)*t);base=dense[index]
        tangent=dense[min(index+1,len(dense)-1)]-dense[max(0,index-1)];tangent/=np.linalg.norm(tangent)
        a=math.atan2(tangent[1],tangent[0]);long=35+(seed+node)%4*6
        for j in range(5 if node==4 else 3):
            theta=a+(j-1)*1.6+node*.62
            direction=np.array([math.cos(theta),math.sin(theta),.22+.18*((j+seed)%3)])
            stalktip=base+direction*9
            twigs.append(branch([base,stalktip],[1.2,.45],'Leaf petiole',sides=6,sub=2,rib=0))
            leaf(stalktip,direction,long*(.82+.10*j),long*.26,math.sin(seed+node+j)*.35,.86+.07*((seed+j)%5))
if twigs:export(merge(twigs,'Connected terminal petioles'),'TreeTwigs',[],False)
leaves=mesh('Lanceolate golden leaves',V,F,C,coll,M['Leaf']);uv=leaves.data.uv_layers.new(name='LeafUV')
for i,l in enumerate(leaves.data.loops):uv.data[i].uv=UV[l.vertex_index]
erase('TreeLeaves');export(leaves,'TreeLeaves',['Foliage','Canopy','Occluder'])

# A few fine living channels are fitted onto the actual sculpted trunk.
bvh=BVHTree.FromObject(tree,bpy.context.evaluated_depsgraph_get());lines=[]
for k in range(4):
    pts=[]
    for t in np.linspace(.07,.83,100):
        dense=curve(trunk+origin,20,False);ct=dense[int(t*(len(dense)-1))];r=np.interp(t,np.linspace(0,1,len(tradii)),tradii)
        a=k*math.tau/4+t*4.7+.45*math.sin(t*8);test=ct+np.array([math.cos(a)*r*1.18,math.sin(a)*r*1.18,0])
        at,n,_,dist=bvh.find_nearest(Vector(test))
        if at is not None:pts.append(np.array(at)+np.array(n)*1.5)
    o=branch(pts,[.7,2.0,1.6,.2],'Living sap inlay',rib=0,sides=8,sub=1);o.data.materials.clear();o.data.materials.append(M['Glow'])
    ca=o.data.color_attributes['HeartColor'];ca.data.foreach_set('color',np.tile([.94,.49,.055,1],len(o.data.vertices)))
    lines.append(o)
export(merge(lines,'Tree care glow channels'),'TreeChannels',['Interactive','TreeLight'])

terrain=np.load(ART/'Source/C15/terrain.npz');H=terrain['h'];xs=terrain['x'];ys=terrain['y'];step=xs[1]-xs[0]
distance=distance_transform_edt(~terrain['path'])*step
def sample(p,field=H):
    p=np.atleast_2d(p);return map_coordinates(field,[(p[:,0]-xs[0])/step,(p[:,1]-ys[0])/step],order=1,mode='nearest')
def relief(p):
    p=np.asarray(p);d=sample(p,distance);r=np.hypot(p[:,0],p[:,1]-90);fade=np.clip((d-25)/90,0,1)*np.clip((r-990)/100,0,1)
    return fade*(2.6*np.sin(p[:,0]/26+np.sin(p[:,1]/47))+2.2*np.sin(p[:,1]/39+p[:,0]/97))

# The existing continuous graded terrain remains the navigation datum. Bake
# fine moss cushions into the mesh away from routes; max added relief is 4.8cm.
terrain_count=0
for obj in list(bpy.data.objects):
    key=obj.name.removeprefix('SM_Craft_')
    if obj.type!='MESH' or not key.startswith('Terrain'):continue
    points=np.array([v.co[:] for v in obj.data.vertices]);top=sample(points[:,:2]);mask=abs(points[:,2]-top)<1.2
    delta=relief(points[:,:2]);points[mask,2]+=delta[mask]
    obj.data.vertices.foreach_set('co',points.ravel())
    for i,mat in enumerate(obj.data.materials):
        if mat and mat.name=='C13_Turf':obj.data.materials[i]=M['Moss']
    # Heightfield normals use neighboring samples, shared at chunk boundaries.
    shift=np.array([2.,0]);dzx=(sample(points[:,:2]+shift)+relief(points[:,:2]+shift)-sample(points[:,:2]-shift)-relief(points[:,:2]-shift))/4
    shift=np.array([0.,2.]);dzy=(sample(points[:,:2]+shift)+relief(points[:,:2]+shift)-sample(points[:,:2]-shift)-relief(points[:,:2]-shift))/4
    norms=np.array([v.normal[:] for v in obj.data.vertices]);norms[mask]=np.column_stack([-dzx[mask],-dzy[mask],np.ones(mask.sum())]);norms/=np.maximum(np.linalg.norm(norms,axis=1)[:,None],1e-5)
    obj.data.normals_split_custom_set_from_vertices(norms.tolist());removed.append(key);export(obj,key,['Ground'],True);terrain_count+=1
print('C17_SCULPTED_TERRAIN_READY',terrain_count,flush=True)

# Every stone has explicit bevel rings and triangulated non-planar tops. The
# central court replaces the old fragmented paving with circular laid courses.
for obj in list(bpy.data.objects):
    if obj.name.startswith('SM_Craft_Paving'):erase(obj.name.removeprefix('SM_Craft_'))
erase('TreePlanter')
buckets={};stone_count=0
def paving(poly,seed,collar=False):
    global stone_count
    if poly.is_empty or poly.area<220:return
    if poly.geom_type!='Polygon':
        for p in getattr(poly,'geoms',[]):paving(p,seed,collar)
        return
    poly=orient(poly,sign=1);xy=np.array(poly.exterior.coords[:-1]);ct=np.array(poly.centroid.coords[0]);n=len(xy)
    if n<3:return
    bucket=(int((ct[0]+3300)//1100),int((ct[1]+3500)//1100));V,F,C=buckets.setdefault(bucket,([],[],[]));base=len(V)
    tone=.86+.055*(seed%6);color=np.array([.235,.164,.108])*tone
    if seed%11==0:color*=np.array([.90,1.02,1.13])
    size=max(np.linalg.norm(xy-ct,axis=1).mean(),10);zbase=sample(xy)-2
    if collar:zbase[:]=535
    # Modest physical relief follows the correct current terrain; no floating
    # old-height stones across the spring or later carved bank.
    for k,(inset,lift) in enumerate([(0,-12),(0,-1),(min(.065,2.8/size),1.2),(min(.15,5.2/size),3.2)]):
        ring=ct+(xy-ct)*(1-inset)
        zz=sample(ring)-2 if not collar else np.full(n,535.)
        for p,z in zip(ring,zz):
            V.append([*p,z+lift+.35*math.sin(p[0]/34+seed)*math.cos(p[1]/41)]);C.append(color*(.83 if k<2 else 1.0))
    for k in range(3):
        for i in range(n):j=(i+1)%n;F.append([base+k*n+i,base+k*n+j,base+(k+1)*n+j,base+(k+1)*n+i])
    topxy=np.array([V[base+3*n+i][:2] for i in range(n)]);toppoly=Polygon(topxy)
    for tri in triangulate(toppoly):
        if not toppoly.covers(tri.representative_point()):continue
        ids=[int(np.argmin(np.linalg.norm(topxy-np.array(p),axis=1))) for p in list(orient(tri,sign=1).exterior.coords)[:-1]]
        F.append([base+3*n+i for i in ids])
    F.append([base+i for i in reversed(range(n))]);stone_count+=1

court=Point(0,90).buffer(990,resolution=160)
for stone in json.loads((ART/'Source/C13/paving.json').read_text()):
    p=Polygon(stone['xy']).difference(court)
    paving(p,stone['seed'])
# Seven broad radial stone courses. All joints are 3 cm; no ornamental bars
# or plants cross the player route. Root bed inside 345 cm is non-walkable.
for course,(ra,rb) in enumerate(zip([345,410,485,570,665,770,880],[410,485,570,665,770,880,990])):
    count=round(math.tau*((ra+rb)/2)/100)
    for j in range(count):
        aa=(j+course*.37)*math.tau/count;bb=(j+1+course*.37)*math.tau/count
        angles=np.linspace(aa,bb,6)
        xy=[[r*math.cos(a),90+r*math.sin(a)] for r,seq in [(ra,angles[::-1]),(rb,angles)] for a in seq]
        paving(Polygon(xy).buffer(-1.5,join_style=2),10000+course*70+j)
for j in range(25):
    aa=j*math.tau/25;bb=(j+1)*math.tau/25;angles=np.linspace(aa,bb,5)
    xy=[[r*math.cos(a),90+r*math.sin(a)] for r,seq in [(303,angles[::-1]),(342,angles)] for a in seq]
    paving(Polygon(xy).buffer(-1.5,join_style=2),15000+j,True)
for (x,y),(V,F,C) in buckets.items():
    obj=mesh('Fitted sandstone',V,F,C,coll,M['Stone']);export(obj,f'Paving{x}_{y}',[],False)
print('C17_FITTED_PAVING_READY',stone_count,flush=True)

# A real moss-covered root bed: shallow domes rather than flat green paint.
V=[];F=[];C=[];nr=32;na=128
for i in range(nr+1):
    r=306*i/nr
    for j in range(na):
        a=j*math.tau/na;x=r*math.cos(a);y=90+r*math.sin(a)
        z=521+12*(1-(r/306)**2)+3*math.sin(x/31)*math.cos(y/35)
        V.append([x,y,z]);C.append([.092,.16,.045])
        if i:q=(i-1)*na+j;k=(i-1)*na+(j+1)%na;F.append([q,q+na,k+na,k])
export(mesh('Rooted moss cushions',V,F,C,coll,M['Moss']),'RootBed',[],False)

# Remove ornamental foliage from the expanded walking court. Connected leaf
# islands are kept whole; outside the court the established beds are retained.
for obj in list(bpy.data.objects):
    key=obj.name.removeprefix('SM_Craft_')
    if obj.type!='MESH' or not key.startswith('Botany'):continue
    bm=bmesh.new();bm.from_mesh(obj.data);remove=[]
    seen=set()
    for v in bm.verts:
        if v in seen:continue
        stack=[v];island=[];seen.add(v)
        while stack:
            a=stack.pop();island.append(a)
            for e in a.link_edges:
                b=e.other_vert(a)
                if b not in seen:seen.add(b);stack.append(b)
        if any(325<math.hypot(v.co.x,v.co.y-90)<1040 for v in island):remove.extend(island)
    if remove:
        bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(obj.data);removed.append(key)
        if obj.data.vertices:export(obj,key,['Foliage','GroundCover'])
        else:bpy.data.objects.remove(obj,do_unlink=True)
    bm.free()

(DATA/'patch.json').write_text(json.dumps(dict(changed=manifest,remove=sorted(set(removed))),indent=2))
(DATA/'construction.json').write_text(json.dumps(dict(tree_vertices=len(tree.data.vertices),leaves=leaf_count,stones=stone_count,terrain_chunks=terrain_count,root_radius_cm=323,clear_walking_ring_cm=[345,990],tree_care_position=[0,-365,520],max_ground_relief_cm=4.8,art_accepted=False),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C17.blend'))
print('C17_EDITABLE_GARDEN_READY',flush=True)
