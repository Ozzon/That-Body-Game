"""C15 editable cortical envelope, stream bed, banks and water geometry."""
import bpy, numpy as np, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'));sys.path.insert(0,str(ROOT/'Intermediate/BlenderDeps'))
from scipy.ndimage import map_coordinates
from garden_model import mesh, collection, ellipsoid, merge
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C15';OUT=ART/'ExportC15';OUT.mkdir(exist_ok=True)
surface_only='--surfaces-only' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(ART/('Brain_Craft_C15.blend' if surface_only else 'Brain_Craft_C14.blend')))
coll=collection('C15 | Rounded cortex and continuous spring');changed=[]
water_mat=bpy.data.materials.get('C13_WaterBlue') or bpy.data.materials['C11_WaterBlue']
terrain=np.load(DATA/'terrain.npz');H=terrain['h'];xs=terrain['x'];ys=terrain['y'];step=xs[1]-xs[0]
def sample(p):
    p=np.asarray(p);scalar=p.ndim==1;p=np.atleast_2d(p)
    result=map_coordinates(H,[(p[...,0]-xs[0])/step,(p[...,1]-ys[0])/step],order=1,mode='nearest')
    return result[0] if scalar else result
def remove(key):
    o=bpy.data.objects.get('SM_Craft_'+key)
    if o:bpy.data.objects.remove(o,do_unlink=True)
def export(o,key,tags,material,spawn=True):
    previous=bpy.data.objects.get('SM_Craft_'+key)
    if previous and previous!=o:bpy.data.objects.remove(previous,do_unlink=True)
    o.name='SM_Craft_'+key;o.data.update()
    if not o.data.uv_layers:
        uv=o.data.uv_layers.new(name='CraftUV')
        for i,l in enumerate(o.data.loops):p=o.data.vertices[l.vertex_index].co;uv.data[i].uv=(p.x/180,p.y/180)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
    changed.append(dict(key=key,tags=tags,material=material,spawn=spawn))
gates=json.loads((ART/'Source/C14/portals.json').read_text());cutters=[]
for e in ([] if surface_only else gates):
    p=np.array(e['p']);out=np.array([*e['outward'],0]);side=np.array([-out[1],out[0],0]);V=[];F=[];count=96
    for depth in [-350,1550]:
        for j in range(count):a=j*math.tau/count;V.append((p+side*205*math.cos(a)+out*depth+np.array([0,0,207+240*math.sin(a)])).tolist())
    for j in range(count):k=(j+1)%count;F.append([j,k,k+count,j+count])
    F.append(list(reversed(range(count))));F.append(list(range(count,count*2)))
    cutters.append(mesh('Passage construction',V,F,[.4,.1,.2],coll,bpy.data.materials['C13_Tissue']))
for key in ([] if surface_only else json.loads((DATA/'cortex-construction.json').read_text())['keys']):
    remove(key);a=np.load(DATA/(key+'.npz'));o=mesh('SM_Craft_'+key,a['v'],a['f'],a['c'],coll,bpy.data.materials['C13_Tissue'],a['n'].tolist())
    for c in cutters:
        mod=o.modifiers.new('Carved nest opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    export(o,key,['Occluder'],'Tissue')
for c in cutters:bpy.data.objects.remove(c,do_unlink=True)
print('C15_ROUNDED_CORTEX_EXPORTED',flush=True)
for key in json.loads((DATA/'water-construction.json').read_text())['terrain']:
    remove(key);a=np.load(DATA/(key+'.npz'));n=a['n'].copy();n[np.abs(n[:,2])<.001]*=-1
    o=mesh('SM_Craft_'+key,a['v'],a['f'],a['c'],coll,bpy.data.materials['C13_Turf'],n.tolist());o.data.materials.append(bpy.data.materials['C13_Earth'])
    for f in o.data.polygons:
        if f.index>=int(a['topfaces']):f.material_index=1
    export(o,key,['Ground'],'Terrain')
# Remove the old terrain-independent surface; cascades and basins are retained.
remove('Water')
d=np.load(DATA/'watercourse.npz');xy=d['xy'];level=d['level'];width=d['width'];side=d['side'];along=d['along'];V=[];F=[];C=[];UV=[];rows=len(xy);cols=17
for i in range(rows):
    for j in range(cols):
        u=j/(cols-1);p=xy[i]+side[i]*width[i]*(u*2-1)
        V.append([*p,level[i]]);C.append([.025,.19,.205]);UV.append([u,along[i]/170])
        if i and j:a=(i-1)*cols+j-1;F.append([a,a+1,a+cols+1,a+cols])
# The local side basis and curve tangent determine winding, never assume it.
vv=np.array(V)
if np.cross(vv[F[0][1]]-vv[F[0][0]],vv[F[0][2]]-vv[F[0][0]])[2]<0:F=[f[::-1] for f in F]
o=mesh('Stream',V,F,C,coll,water_mat);uv=o.data.uv_layers.new(name='CraftUV')
for i,l in enumerate(o.data.loops):uv.data[i].uv=UV[l.vertex_index]
export(o,'SpringCurrent',['Water'],'Water')
# Small damp stones follow the water edge at fixed spacing. They are outside
# path decks and never scatter over the player's walking line.
stones=[]
for target in np.arange(30,along[-1],88):
    i=int(np.argmin(abs(along-target)))
    for sign in [-1,1]:
        p=xy[i]+side[i]*(width[i]+25)*sign
        path=map_coordinates(terrain['path'].astype(float),[[(p[0]-xs[0])/step],[(p[1]-ys[0])/step]],order=0,mode='nearest')[0]
        if path>.5:continue
        z=max(float(sample(p)),level[i]-8)
        o=ellipsoid('Damp stream stone',(p[0],p[1],z-11),(47,34,24),(.19,.23,.20),coll,bpy.data.materials['C13_Stone'],seed=i+sign,segments=16,rings=8)
        stones.append(o)
if stones:export(merge(stones,'Rooted watercourse stones'),'SpringBankStones',[],'Stone')
V=[];F=[];UV=[];rows=256;cols=9
for i in range(rows):
    a=math.tau*i/rows
    for j in range(cols):
        r=515+j/(cols-1)*110;V.append([1580+1.02*r*math.cos(a),-1390+r*math.sin(a),315]);UV.append([j/(cols-1),i/24])
for i in range(rows):
    for j in range(cols-1):a=i*cols+j;b=((i+1)%rows)*cols+j;F.append([a,a+1,b+1,b])
o=mesh('Lotus water garden',V,F,[.025,.19,.205],coll,water_mat);uv=o.data.uv_layers.new(name='CraftUV')
for i,l in enumerate(o.data.loops):uv.data[i].uv=UV[l.vertex_index]
export(o,'LotusMoat',['Water'],'Water')
# Keep the persistent thought's luminous core in front of its spiral body.
# Measured C14 minimum clearance was -2.89 cm, hiding part of the symbol.
o=bpy.data.objects['SM_Craft_ThoughtFaceKnot']
if not o.get('C15CoreClearance',False):
    for v in o.data.vertices:v.co.x+=4
    o['C15CoreClearance']=True
export(o,'ThoughtFaceKnot',[],'ThoughtGold',False)
if surface_only:
    prior=json.loads((DATA/'patch.json').read_text())
    changed=[e for e in prior['changed'] if e['key'] not in {e['key'] for e in changed}]+changed
(DATA/'patch.json').write_text(json.dumps(dict(changed=changed,remove=['Water']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C15.blend'));print('C15_EDITABLE_GARDEN_READY',flush=True)
