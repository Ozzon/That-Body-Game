import bpy,json,numpy as np,math
from pathlib import Path
ART=Path(__file__).resolve().parents[1]/'Art/BrainCraft';DATA=ART/'Source/C11';bpy.ops.wm.open_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));moves=json.loads((DATA/'gate-move.json').read_text());changed=json.loads((DATA/'contact-patch.json').read_text())
for i,(old,new) in enumerate(zip(moves['old'],moves['new'])):
    for key in ['Nest'+str(i),'NestGlow'+str(i)]:
        o=bpy.data.objects['SM_Craft_'+key];prior=json.loads(o.get('GatePose',json.dumps(old)));oldp=np.array(prior['p']);newp=np.array(new['p']);a=math.radians(new['yaw']-prior['yaw']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
        for vert in o.data.vertices:vert.co=R@(np.array(vert.co)-oldp)+newp
        o['GatePose']=json.dumps(new);o.data.update();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(ART/'ExportC11'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,colors_type='LINEAR');changed.append(key)
(DATA/'contact-patch.json').write_text(json.dumps(list(dict.fromkeys(changed))));bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Brain_Craft_C11.blend'));print('C11_BORDER_GATES_AUTHORED',flush=True)
