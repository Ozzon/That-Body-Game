"""Keep authored scale, navigation, interactions and review cameras in one coordinate system."""
from pathlib import Path
import re
from brain_garden_layout import *
root=Path(__file__).resolve().parents[1]
def vec(p):return f'FVector({WORLD_X+p[0]*LEVEL_SCALE:.3f},{p[1]*LEVEL_SCALE:.3f},0)'
def change(rel,fn):
    p=root/rel;s=p.read_text();p.write_text(fn(s))
change('Tools/adventure_layout.py',lambda s:s.replace("center=[8050,0,220]","center=[9250,0,220]").replace("(5160,0,0),(5500,0,160),(5800,0,370),(6240,0,370),(6500,0,370)","(5160,0,0),(5380,0,150),(5600,0,355),(5760,0,370)").replace('position=[7510,0,283]',f'position=[{WORLD_X+CARE[0]*LEVEL_SCALE},0,433]').replace('from brain_garden_layout import THOUGHTS as GARDEN_THOUGHTS','from brain_garden_layout import THOUGHTS as GARDEN_THOUGHTS, LEVEL_SCALE, WORLD_X').replace('THOUGHTS=[[8050+x,y,283] for x,y in GARDEN_THOUGHTS]','THOUGHTS=[[WORLD_X+x*LEVEL_SCALE,y*LEVEL_SCALE,433] for x,y in GARDEN_THOUGHTS]'))
change('Tools/sculpt_adventure.py',lambda s:s.replace('12421','13621'))
def native(s):
    s=s.replace('FVector(7510,0,433)',vec(CARE)).replace('FVector(8050,0,300)','FVector(9250,0,440)')
    s=re.sub(r'GardenStarPlaces=\{.*?\};','GardenStarPlaces={'+','.join(map(vec,MEMORIES))+'};',s)
    s=re.sub(r'const FVector ThoughtPlaces\[\]=\{.*?\};','const FVector ThoughtPlaces[]={'+','.join(map(vec,THOUGHTS))+'};',s)
    s=s.replace('FVector(8890,1360,0)',vec(FOCUS))
    s=s.replace('const FVector A(7700,-520,0),B(7600,-1280,0),D=B-A;',f'const FVector A={vec(ROOT_START)},B={vec(ROOT_END)},D=B-A;')
    s=s.replace('>145)return false','>225)return false')
    s=s.replace('FVector(8050,0,220+FMath','FVector(9250,0,220+FMath')
    s=s.replace('FVector(8050+840*(1-XY),1360*(1-XY),220+Base*(1-Z))',f'FVector(9250+{FOCUS[0]*LEVEL_SCALE}*(1-XY),{FOCUS[1]*LEVEL_SCALE}*(1-XY),220+Base*(1-Z))')
    return s
change('Source/ThatBodyGame/BodyAdventure.cpp',native)
change('Source/ThatBodyGame/BodyPlay.cpp',lambda s:s.replace('FVector Spawn(6440,30,0);',f'FVector Spawn={vec((-1630,30))};'))
change('Tools/import_brain_garden.py',lambda s:s.replace('unreal.Vector(8050,0,220)','unreal.Vector(9250,0,220)'))
change('Source/ThatBodyGame/BodyAdventureHUD.cpp',lambda s:s.replace('FVector(8050,0,700)','FVector(9250,0,700)'))
def capture(s):
    s=re.sub(r'const FVector Places\[\]=\{.*?\};','const FVector Places[]={'+','.join(vec(p) for p in [(-1250,0),CARE,(-250,1270),(-700,650)])+'};',s,1)
    s=re.sub(r'const FVector Targets\[\]=\{.*?\};','const FVector Targets[]={FVector(9250,0,650),FVector(9100,-100,750),FVector(9550,2010,690),FVector(8260,1050,560)};',s,1)
    s=s.replace('const float Widths[]={6500,3000,2600,2850}','const float Widths[]={9700,4300,4300,3500}').replace('BrainGarden-C04','BrainGarden-C05')
    return s
change('Source/ThatBodyGame/BodyAdventureReview.cpp',capture)
change('Tools/export_carry_thought.py',lambda s:s.replace('MEMORIES,height,TERRAIN_LIFT','MEMORIES,height,TERRAIN_LIFT,LEVEL_SCALE').replace('origin=Vector((x,y,','origin=Vector((x*LEVEL_SCALE,y*LEVEL_SCALE,'))
change('Tools/garden_input_routes.py',lambda s:s.replace('from scipy.ndimage import distance_transform_edt','from scipy.ndimage import distance_transform_edt\nfrom brain_garden_layout import MEMORIES,CARE,FOCUS,THOUGHTS,ROOT_START,ROOT_END,LEVEL_SCALE,WORLD_X').replace("destinations=[[7470,-1260],[7510,0],[8770,-1430],[7510,0],[9160,950],[7510,0],[8720,1160],[7250,1300],[7610,1730],[7980,1510],[7640,1120],[7700,-520]]","wp=lambda p:[WORLD_X+p[0]*LEVEL_SCALE,p[1]*LEVEL_SCALE]\ndestinations=[wp(p) for p in [MEMORIES[0],CARE,MEMORIES[1],CARE,MEMORIES[2],CARE,[FOCUS[0]-140,FOCUS[1]-100],*THOUGHTS,ROOT_START]]").replace('last=[6440,30]','last=wp([-1630,30])').replace('routes.append([[7700,-520,430],[7675,-710,480],[7650,-900,510],[7625,-1090,500],[7600,-1280,480]])','routes.append([wp(np.array(ROOT_START)*(1-t)+np.array(ROOT_END)*t)+[500] for t in np.linspace(0,1,8)])'))
change('Source/ThatBodyGame/BrainGardenReview.cpp',lambda s:s.replace('FVector(7600,-1280,0)',vec(ROOT_END)))
print('C05_COORDINATES_CONNECTED',WORLD_X,LEVEL_SCALE,'care',vec(CARE),'focus',vec(FOCUS))
