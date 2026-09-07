"""Composed branching silhouettes and clustered garden planting, C11 revision 4.

Tree control points describe a leader, five unequal boughs and secondary forks.
Every leaf is a curved mesh; no alpha planes or foliage sphere placeholders.
"""
import bpy,bmesh,numpy as np,math,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,merge,sweep,leaf
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C11'
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'))
manifest=json.loads((DATA/'asset-manifest.json').read_text());changed=[]
coll=bpy.data.collections['C11 | Trees and ecology'];M={m.name:m for m in bpy.data.materials};rng=np.random.default_rng(11471)

def remove(key):
    o=bpy.data.objects.get('SM_Craft_'+key)
    if o:bpy.data.objects.remove(o,do_unlink=True)

def export(o,key,tags):
    o.name='SM_Craft_'+key
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    if not o.data.uv_layers:
        uv=o.data.uv_layers.new(name='CraftUV')
        for i,loop in enumerate(o.data.loops):p=o.data.vertices[loop.vertex_index].co;uv.data[i].uv=(p.x/200,p.y/200)
    manifest[:]=[e for e in manifest if e['key']!=key];manifest.append(dict(name=o.name,key=key,spawn=True,tags=tags,materials=[m.name for m in o.data.materials]));changed.append(key)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(ART/'ExportC11'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')

# Fixed unequal branch arcs retain a clear trunk and airy, layered silhouette.
boughs=[
 ([(0,0,0),(32,-12,160),(-26,12,350),(28,20,590),(107,38,820),(60,45,1000)],[100,88,67,46,19,2]),
 ([(3,0,250),(-160,-45,370),(-370,-105,425),(-555,-110,580),(-670,-85,675)],[63,49,32,15,2]),
 ([(4,5,420),(162,57,495),(335,150,563),(505,160,690),(590,130,865)],[53,43,28,14,1.5]),
 ([(0,0,330),(58,-130,390),(170,-280,450),(340,-415,610),(390,-420,715)],[51,39,26,13,1.5]),
 ([(22,18,510),(-80,195,635),(-210,370,765),(-170,460,905),(-185,505,1050)],[39,30,20,9,1]),
 ([(-25,10,370),(-150,112,475),(-360,285,600),(-390,395,775)],[41,32,18,1])]

def tree(key,origin,scale,angle,leafmat,basecolor):
    remove(key+'Wood');remove(key+'Leaves');origin=np.array(origin,float);a=angle
    R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    def point(p):return origin+R@np.array(p)*scale
    wood=[];twigs=[];leaves=[];crowns=[]
    bark=(.145,.080,.036)
    for k in range(7):
        aa=k*2.399+.4;rad=240+40*math.sin(k*2.1)
        pts=[(math.cos(aa)*rad,math.sin(aa)*rad,3),(math.cos(aa)*155,math.sin(aa)*130,19),(math.cos(aa)*70,math.sin(aa)*65,85),(20,-5,160)]
        wood.append(sweep('Fluted root flare',[point(p) for p in pts],[1.6*scale,24*scale,43*scale,45*scale],bark,coll,M['C11_BarkWood'],24,10,.045))
    for k,(pts,radii) in enumerate(boughs):
        wood.append(sweep('Curved structural bough',[point(p) for p in pts],np.array(radii)*scale,bark,coll,M['C11_BarkWood'],28,12,.025))
        end=np.array(pts[-1]);crowns.append((end+np.array((0,0,20)),np.array((155,140,105))))
        for j,t in enumerate([.55,.74,.89]):
            f=t*(len(pts)-1);i=int(f);u=f-i;start=np.array(pts[i])*(1-u)+np.array(pts[min(i+1,len(pts)-1)])*u
            tangent=end-start;tangent[2]*=.25;tangent/=max(np.linalg.norm(tangent),1)
            side=np.array((-tangent[1],tangent[0],0))*(-1 if (j+k)%2 else 1)
            tip=start+tangent*(70+j*22)+side*(110+j*35)+np.array((0,0,95+j*17))
            mid=start+(tip-start)*.47+np.array((0,0,-32))
            twigs.append(sweep('Unequal rising lateral',[point(start),point(mid),point(tip)],[15*scale,8*scale,.8*scale],bark,coll,M['C11_BarkWood'],14,10,.03))
            crowns.append((tip,np.array((120+22*j,103+18*j,74+12*j))))
            for side0 in [-1,1]:
                t2=tip+side*side0*55+tangent*35+np.array((0,0,29))
                twigs.append(sweep('Fine terminal fork',[point(mid+(tip-mid)*.55),point(tip),point(t2)],[4.5*scale,2.8*scale,.25*scale],bark,coll,M['C11_BarkWood'],10,6,0))
    # Merge and smooth only structural wood. Small twigs retain their thickness.
    o=merge(wood,'Joined root and branch sculpture');bpy.context.view_layer.objects.active=o
    o.data.remesh_voxel_size=5.5*scale;o.data.remesh_voxel_adaptivity=0;bpy.ops.object.voxel_remesh()
    sm=o.modifiers.new('Soft bark unions','SMOOTH');sm.factor=.6;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
    if not o.data.color_attributes.get('HeartColor'):o.data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='POINT')
    vc=o.data.color_attributes['HeartColor'];vals=[]
    for v in o.data.vertices:
        p=(np.array(v.co)-origin)/scale;n=.9+.08*math.sin(p[2]*.019+p[0]*.037)+.04*math.cos(p[1]*.05)
        vals.extend((*np.array(bark)*n,1))
    vc.data.foreach_set('color',vals)
    for p in o.data.polygons:p.use_smooth=True
    export(merge([o]+twigs,'Natural wood assembly'),key+'Wood',['Interactive'])
    # Curved leaf clusters follow crown volumes with an upward canopy normal.
    # Unequal pockets and gaps reveal branch structure without terminal fans.
    for ci,(center,radii) in enumerate(crowns):
        count=110 if scale>.9 else 76
        for j in range(count):
            n=rng.normal(size=3);n/=np.linalg.norm(n);n[2]=abs(n[2])*.85-.2
            rad=rng.uniform(.55,1.05);p=center+n*radii*rad
            aa=rng.uniform(0,math.tau);direction=np.array((math.cos(aa),math.sin(aa),rng.uniform(-.18,.55)))
            length=rng.uniform(27,48)*scale;width=length*rng.uniform(.38,.52)
            tone=rng.uniform(.8,1.13);c=np.array(basecolor)*tone
            c*=np.array((.84,.98,.80)) if (ci+j)%6==0 else 1
            leaves.append(leaf('Folded crown leaf',point(p),R@direction,length,width,c,coll,M['C11_'+leafmat],rng.uniform(.1,.24)))
    crown=merge(leaves,'Layered airy crown');crown.data.update()
    # Foliage normals describe the crown envelope, not random folded sheet edges.
    normals=[]
    for v in crown.data.vertices:
        local=(v.co-Vector(origin)).normalized();normals.append(tuple((v.normal*.30+Vector((local.x*.18,local.y*.18,.85))).normalized()))
    crown.data.normals_split_custom_set_from_vertices(normals)
    export(crown,key+'Leaves',['Occluder','Foliage','Canopy']+(['TreeLight'] if key=='Tree' else []))
    print('C11_BRANCHING_TREE',key,flush=True)

tree('Tree',(0,90,520),1.03,.18,'LeafGold',(.42,.38,.055))
tree('SpringCherry',(-1990,1890,1100),.48,1.9,'PetalPink',(.47,.16,.25))
tree('MemoryWillow',(1480,1980,950),.46,2.6,'LeafGreen',(.09,.23,.075))
tree('ArrivalCherry',(-2200,-1650,290),.32,-1.1,'PetalPink',(.50,.22,.29))
tree('PoolWillow',(2130,-1830,330),.35,.85,'LeafGreen',(.09,.24,.095))

# Thin the meadow into communities. Remove regular isolated flower rosettes;
# concentrate blossoms beside the water and in the shelter's protected beds.
for key in ['GardenGrass0','GardenGrass1','GardenGrass2','GardenGrass3']:
    o=bpy.data.objects['SM_Craft_'+key];bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();removev=[]
    for start in range(0,len(bm.verts),180):
        group=list(bm.verts[start:start+180]);p=group[0].co
        habitat=math.sin(p.x/185)+math.cos(p.y/210)+.5*math.sin((p.x+p.y)/112)
        if habitat<.25:removev.extend(group)
        else:
            root=min(v.co.z for v in group)
            for v in group:v.co.z=root+(v.co.z-root)*.68
    bmesh.ops.delete(bm,geom=removev,context='VERTS');bm.to_mesh(o.data);bm.free();export(o,key,['GroundCover'])
for key in ['GardenPocketLeaves','GardenPocketFlowers','UnderstoryLeaves','UnderstoryFlowers']:
    o=bpy.data.objects['SM_Craft_'+key];bm=bmesh.new();bm.from_mesh(o.data)
    # Connected islands are individual modeled leaves. Group by spatial habitat,
    # using smooth fields so complete colonies survive in coherent pockets.
    unseen=set(bm.verts);discard=[]
    while unseen:
        v=unseen.pop();island=[v];stack=[v]
        while stack:
            u=stack.pop()
            for edge in u.link_edges:
                w=edge.other_vert(u)
                if w in unseen:unseen.remove(w);island.append(w);stack.append(w)
        p=sum((v.co for v in island),Vector())/len(island)
        habitat=math.sin(p.x/240+.7)*math.cos(p.y/260)+.5*math.sin((p.x-p.y)/155)
        if habitat<(.32 if 'Flowers' in key else -.12):discard.extend(island)
    bmesh.ops.delete(bm,geom=discard,context='VERTS');bm.to_mesh(o.data);bm.free();export(o,key,['Foliage'])

(DATA/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(DATA/'contact-patch.json').write_text(json.dumps(changed));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));print('C11_COMPOSED_BOTANY_READY',changed,flush=True)
