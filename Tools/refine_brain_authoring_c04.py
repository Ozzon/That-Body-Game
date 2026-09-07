"""One-time migration retained alongside the previous authoring evidence."""
from pathlib import Path
p=Path(__file__).with_name('author_brain_garden.py');s=p.read_text()
start=s.index('# Hand-shaped radial stonework');end=s.index('# Pools and the narrow flowing',start)
s=s[:start]+'''# Fitted 3D polygon masonry follows every terrace and shares one route mask.
stone=(.42,.285,.15)
d=np.load(ART/'Source/garden_masonry.npz')
add(mesh('SM_BrainGarden_FittedMasonry',d['vertices'].tolist(),d['faces'].tolist(),d['colors'],garden,surface),'Paths')
'''+s[end:]
s=s.replace("add(merge(parts,'SM_BrainGarden_TreeTrunk'),'TreeTrunk',['Interactive'])",'''o=merge(parts,'SM_BrainGarden_TreeTrunk')
# Voxel union produces actual continuous branch junctions and integrated roots.
bpy.context.view_layer.objects.active=o
modifier=o.modifiers.new('Fused root and branch sculpture','REMESH');modifier.mode='VOXEL';modifier.voxel_size=12;modifier.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=modifier.name)
modifier=o.modifiers.new('Hand-softened junctions','SMOOTH');modifier.factor=.64;modifier.iterations=5;bpy.ops.object.modifier_apply(modifier=modifier.name)
for a in list(o.data.color_attributes):o.data.color_attributes.remove(a)
v=np.array([list(v.co) for v in o.data.vertices]);a=np.arctan2(v[:,1],v[:,0]);rib=(.5+.5*np.cos(a*9-v[:,2]/75))**5
cc=np.array([.41,.205,.063])[None,:]*(.86+.29*rib[:,None]+.10*np.clip(v[:,2,None]/1300,0,1))
col=o.data.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='POINT');col.data.foreach_set('color',np.column_stack([cc,np.ones(len(v))]).ravel())
add(o,'TreeTrunk',['Interactive'])''')
start=s.index('# Carved light channels');end=s.index('rng=random.Random',start)
s=s[:start]+'''# Warm spiral channels and buds, seated on the bark rather than floating through it.
parts=[]
for j in range(3):
    pts=[]
    for t in np.linspace(0,1,24):
        z=220+t*600;a=math.pi+j*math.tau/3+.45*math.sin(t*4);r=147-52*t
        center=np.array([-40+95*t if t<.74 else 40,12*t,z])
        pts.append(tuple(center+np.array([math.cos(a)*r,math.sin(a)*r,0])))
    parts.append(sweep('Carved amber channel',pts,[5.4,4.1,2.5],(.94,.40,.055),tree,glow,12,2,.01))
for j in range(13):
    t=(j+.3)/13;z=240+t*680;a=math.pi+1.7*math.sin(j*2.3);r=143-48*t
    x=math.cos(a)*r+20*math.sin(t*5);y=math.sin(a)*r
    parts.append(leaf('Amber bark bud',(x,y,z),(0,0,1),27+j%3*6,9,(.98,.51,.09),tree,glow,.12))
add(merge(parts,'SM_BrainGarden_BarkInlay'),'TreeGlow',['Interactive'],'Glow')

'''+s[end:]
s=s.replace('for i in range(19):','for i in range(33):')
s=s.replace("(.045,.34,.39)","(.035,.27,.33)")
s=s.replace("(.07,.47,.50)","(.045,.37,.44)")
# The full-level angle remains repeatable; add a close source camera for craft review.
s=s.replace("scene.cycles.samples=48","scene.cycles.samples=64")
s=s.replace("camera_data.ortho_scale=6400","camera_data.ortho_scale=6400")
s=s.replace("print('BRAIN_GARDEN_RENDERED',flush=True)","""print('BRAIN_GARDEN_RENDERED',flush=True)
camera.location=(-3050,-2050,2590);target=Vector((-120,-200,660));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=3150
scene.render.filepath=str(ART/'Brain-tree-craft.png');bpy.ops.render.render(write_still=True);print('BRAIN_TREE_CRAFT_RENDERED',flush=True)""")
p.write_text(s)
print('C04_AUTHORING_UPDATED')
