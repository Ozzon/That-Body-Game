import bpy,sys,math,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from adventure_layout import PATHS
from organ_math import curve
from garden_model import collection,material,mesh
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=.01
c=collection('Connected light paths');m=material('Light paths',1)
V=[];F=[];C=[]
for path in PATHS:
    pts=curve(path['points'],14,False);start=len(V)
    for i,p in enumerate(pts):
        d=pts[min(len(pts)-1,i+1)]-pts[max(0,i-1)];side=np.array([-d[1],d[0],0]);side/=np.linalg.norm(side)
        for f in [-1,-.82,.82,1]:q=p+side*path['width']/2*f;q[2]+=60;V.append(q.tolist());C.append((.40,.63,.46) if abs(f)<.9 else (.26,.44,.34))
        if i:
            for j in range(3):a=start+(i-1)*4+j;F.append((a,a+4,a+5,a+1))
o=mesh('SM_Adventure_LightBridges',V,F,C,c,m);o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(ROOT/'Art/BodyAdventure/Export/SM_Adventure_LightBridges.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',colors_type='LINEAR')
print('LIGHT_BRIDGES_UPDATED',len(PATHS))
