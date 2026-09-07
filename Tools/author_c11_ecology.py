"""Reference-grounded thought cast and composed lower planted gardens."""
import bpy,bmesh,numpy as np,math,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from garden_model import mesh,merge,sweep,ellipsoid,leaf
ART=ROOT/'Art/BrainCraft';DATA=ART/'Source/C11';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));manifest=json.loads((DATA/'asset-manifest.json').read_text());changed=[];env=bpy.data.collections['C11 | Living terraced garden'];cast=bpy.data.collections['C11 | Thought creatures'];M={m.name:m for m in bpy.data.materials}
def remove(key):
    o=bpy.data.objects.get('SM_Craft_'+key)
    if o:bpy.data.objects.remove(o,do_unlink=True)
def export(o,key,tags=None,spawn=True):
    o.name='SM_Craft_'+key;bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    if not o.data.uv_layers:
        uv=o.data.uv_layers.new(name='CraftUV')
        for i,loop in enumerate(o.data.loops):p=o.data.vertices[loop.vertex_index].co;uv.data[i].uv=(p.x/200,p.y/200)
    manifest[:]=[e for e in manifest if e['key']!=key];manifest.append(dict(name=o.name,key=key,spawn=spawn,tags=tags or [],materials=[m.name for m in o.data.materials]));changed.append(key)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'ExportC11'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR')
d=np.load(DATA/'Understory.npz');remove('Understory');v=d['v'];c=np.tile((.095,.18,.058),(len(v),1))*(.86+.14*np.sin(v[:,0]/390)*np.cos(v[:,1]/260))[:,None];o=mesh('Rooted lower garden',v,d['f'],c,env,M['C11_Turf']);export(o,'Understory',['Ground'])
plants=[];flowers=[]
for idx,p in enumerate(np.load(DATA/'understory-plants.npz')['p']):
    a=idx*2.399;size=.7+.6*(.5+.5*math.sin(idx*.9))
    for j in range(9):
        aa=a+j*2.399;plants.append(leaf('Lower garden broad-leaf colony',p+np.array((0,0,12)),(math.cos(aa),math.sin(aa),.4),85*size,34*size,(.09,.25,.061),env,M['C11_LeafGreen'],.35))
    if idx%5==0:
        for j in range(5):
            aa=a+j*math.tau/5;flowers.append(leaf('Damp garden iris',p+np.array((0,0,92)),(math.cos(aa),math.sin(aa),.4),36,17,(.43,.14,.31),env,M['C11_PetalPink'],.4))
remove('UnderstoryLeaves');export(merge(plants,'Lower garden planted communities'),'UnderstoryLeaves',['Foliage'])
remove('UnderstoryFlowers');export(merge(flowers,'Lower garden iris pockets'),'UnderstoryFlowers',['Foliage'])
for key,col in [('ThoughtCloud',(.046,.033,.108)),('ThoughtWisp',(.082,.032,.17))]:
    remove(key);d=np.load(DATA/(key+'.npz'));o=mesh('Soft joined thought cloud',d['v'],d['f'],col,cast,M['C11_ThoughtCloud'],d['n']);export(o,key,[],False)
# Thin restless neural loops distinguish the small negative thought from the
# heavy cloud. They are one model assembly, with its face clear at the front.
o=bpy.data.objects['SM_Craft_ThoughtWisp'];parts=[o]
for k in range(3):
    pts=[]
    for t in np.linspace(0,math.tau,145):
        r=31+4*math.sin(t*3+k);pts.append((math.sin(t*2+k)*14-k*2,r*math.cos(t),r*math.sin(t)))
    parts.append(sweep('Restless neural filament',pts,[1.5,1.5,1.5],(.21,.064,.4),cast,M['C11_PortalMemory'],8,2,.015))
export(merge(parts,'Restless light negative thought'),'ThoughtWisp',[],False)
remove('ThoughtKnot');V=[];F=[];rows=280;cols=16
for i in range(rows):
    t=i/(rows-1);a=t*math.pi*8;r=6+44*t;cx=8*math.sin(a*.5);cy=r*math.cos(a);cz=r*math.sin(a)
    for j in range(cols):
        b=j*math.tau/cols;w=8+2.5*math.sin(t*math.pi);V.append((cx+13*math.cos(b),cy+math.cos(a)*w*math.sin(b),cz+math.sin(a)*w*math.sin(b)))
        if i:q=(i-1)*cols+j;n=(i-1)*cols+(j+1)%cols;F.append((q,n,n+cols,q+cols))
F.extend([tuple(reversed(range(cols))),tuple((rows-1)*cols+j for j in range(cols))]);export(mesh('Persistent curled thought rosette',V,F,(.68,.24,.04),cast,M['C11_ThoughtKnot']),'ThoughtKnot',[],False)
for key,front,eye_y,scale in [('ThoughtFaceCloud',60,18,1.2),('ThoughtFaceWisp',29,10,.74)]:
    remove(key);parts=[]
    for sign in [-1,1]:
        o=ellipsoid('Expressive violet eye',(front,sign*eye_y,2),(2,5*scale,7*scale),(.52,.14,.78),cast,M['C11_PortalMemory'],0,24,18)
        for vert in o.data.vertices:
            delta=vert.co-Vector((front,sign*eye_y,2)) if False else np.array(vert.co)-np.array((front,sign*eye_y,2));yy=delta[1];zz=delta[2];a=sign*.30;vert.co=(front+delta[0],sign*eye_y+yy*math.cos(a)-zz*math.sin(a),2+yy*math.sin(a)+zz*math.cos(a))
        parts.append(o)
    export(merge(parts,'Thought weighted expression'),key,[],False)
remove('ThoughtFaceKnot');parts=[]
for sign in [-1,1]:
    parts.append(sweep('Persistent insight diamond',[(19,0,sign*10),(19,sign*9,0),(19,0,-sign*10)],[1.6,1.6,1.6],(.97,.54,.1),cast,M['C11_ThoughtGold'],10,3))
export(merge(parts,'Persistent thought core glyph'),'ThoughtFaceKnot',[],False)
(DATA/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(DATA/'contact-patch.json').write_text(json.dumps(list(dict.fromkeys(changed))));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));print('C11_ECOLOGY_AND_REFERENCE_THOUGHTS_READY',changed,flush=True)
