import bpy,numpy as np,json,sys,math,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,collection
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C14';OUT=ART/'ExportC14Mantle';OUT.mkdir(exist_ok=True);review=ART/'Reviews/C14-r01';review.mkdir(parents=True,exist_ok=True)
if not (review/'Brain_Craft_C14.blend').exists():shutil.copy2(ART/'Brain_Craft_C14.blend',review/'Brain_Craft_C14.blend')
bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C14.blend'));coll=collection('C14 | Deep gyri and carved living nests');gates=json.loads((DATA/'portals.json').read_text());cutters=[];changed=[]
def export(o,key):
    if not o.data.uv_layers:
        uv=o.data.uv_layers.new(name='CraftUV')
        for i,l in enumerate(o.data.loops):p=o.data.vertices[l.vertex_index].co;uv.data[i].uv=(p.x/180,p.z/180)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR');changed.append(key)
for e in gates:
    p=np.array(e['p']);out=np.array([*e['outward'],0]);side=np.array([-out[1],out[0],0]);V=[];F=[];count=96
    for depth in [-350,1550]:
        for j in range(count):a=j*math.tau/count;V.append((p+side*205*math.cos(a)+out*depth+np.array([0,0,207+240*math.sin(a)])).tolist())
    for j in range(count):k=(j+1)%count;F.append([j,k,k+count,j+count])
    F.append(list(reversed(range(count))));F.append(list(range(count,count*2)));cutters.append(mesh('Nest cavity construction cutter',V,F,[.4,.1,.2],coll,bpy.data.materials['C13_Tissue']))
for key in json.loads((DATA/'mantle-construction.json').read_text())['keys']:
    old=bpy.data.objects.get('SM_Craft_'+key)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    a=np.load(DATA/(key+'.npz'));o=mesh('SM_Craft_'+key,a['v'],a['f'],a['c'],coll,bpy.data.materials['C13_Tissue'],a['n'].tolist())
    for c in cutters:
        mod=o.modifiers.new('Sculpted passage','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    export(o,key)
for c in cutters:bpy.data.objects.remove(c,do_unlink=True)
for idx,e in enumerate(gates):
    p=np.array(e['p']);out=np.array([*e['outward'],0]);side=np.array([-out[1],out[0],0]);basis=np.stack([side,out,[0,0,1]],axis=1);key='Nest'+str(idx);old=bpy.data.objects.get('SM_Craft_'+key)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    a=np.load(DATA/(key+'.npz'));v=a['v']@basis.T+p;n=a['n']@basis.T;faces=a['f'][:,::-1] if np.linalg.det(basis)<0 else a['f'];o=mesh('SM_Craft_'+key,v,faces,a['c'],coll,bpy.data.materials['C13_Tissue'],n.tolist());export(o,key)
    key='NestGlow'+str(idx);o=bpy.data.objects['SM_Craft_'+key]
    if not o.get('C14ShallowAperture',False):
        for v in o.data.vertices:v.co-=125*__import__('mathutils').Vector(out)
        o['C14ShallowAperture']=True
    export(o,key)
(DATA/'mantle-patch.json').write_text(json.dumps(changed,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C14.blend'));print('C14_DEEP_LIVING_ENVELOPE_READY',flush=True)
