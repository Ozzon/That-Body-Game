"""Editable world and organ drawings. World units are centimeters; +X points to the head.

The owner approved HeartModels/A on 2026-09-07. Its geometry remains unchanged.
Negative Y is anatomical right. The diagrammatic cavity layout enlarges playable spaces.
"""
from heart_model_layouts import get_layout

def door(x,y,rx=390,ry=235,axis=0):return dict(center=[x,y],radii=[rx,ry],axis=axis)
def room(points):return dict(points=points)
def channel(points,width):return dict(channel=points,width=width)
def organ(key,name,center,outline,rooms,doors,palette,**kw):
    return dict(key=key,name=name,center=center,outline=outline,rooms=rooms,doors=doors,palette=palette,**kw)

LUNG_R=organ('LungRight','RIGHT LUNG',[2300,-3050,0],
 [(-1530,-600),(-1400,-1000),(-700,-1200),(350,-1100),(1260,-650),(1610,-110),(1360,320),(480,660),(-550,1040),(-1360,970)],
 [room([(-1240,-700),(-720,-1000),(-430,-840),(-430,640),(-1140,790)]),
  room([(-140,-800),(270,-830),(590,-500),(460,370),(-100,670)]),
  room([(770,-390),(1270,-340),(1410,-60),(1140,230),(680,330)])],
 [door(-1470,0),door(-330,0,340,265),door(565,0,315,255),door(1470,0,370,230)],'mint',kind='lung',lobes=3)
LUNG_L=organ('LungLeft','LEFT LUNG',[2300,3050,0],
 [(-1500,580),(-1390,1010),(-620,1140),(410,1010),(1290,580),(1570,90),(1350,-320),(660,-540),(80,-690),(-300,-420),(-770,-780),(-1290,-850)],
 [room([(-1220,580),(-700,890),(-260,740),(-100,220),(-280,-270),(-710,-520),(-1190,-570)]),
  room([(195,670),(770,670),(1290,270),(1330,20),(810,-330),(250,-450)])],
 [door(-1450,0),door(30,100,370,300),door(1450,0,360,230)],'mint',kind='lung',lobes=2)
BRAIN=organ('Brain','BRAIN',[9250,0,220],
 [(-1720,0),(-1510,-850),(-910,-1510),(-180,-1740),(540,-1640),(1280,-1190),(1580,-510),(1420,0),(1580,510),(1280,1190),(540,1640),(-180,1740),(-910,1510),(-1510,850)],
 [room([(-1160,-600),(-650,-1220),(130,-1430),(1010,-1110),(1190,-650),(610,-480),(-180,-440)]),
  room([(-1160,600),(-650,1220),(130,1430),(1010,1110),(1190,650),(610,480),(-180,440)]),
  room([(-1350,-210),(-440,-270),(710,-235),(950,0),(710,235),(-440,270),(-1350,210)])],
 [door(-1550,0,500,250),door(-450,-415,300,400,1),door(-450,415,300,400,1)],'lavender',kind='brain',custom='BrainGarden')
LIVER=organ('Liver','LIVER',[-2900,-2050,0],
 [(1320,-600),(1000,-1350),(280,-1690),(-530,-1580),(-1180,-1010),(-1410,-160),(-1040,890),(-350,1490),(440,1240),(1070,540)],
 [room([(910,-690),(570,-1300),(-120,-1420),(-720,-1080),(-1080,-340),(-680,-20),(110,-80),(830,-210)]),
  room([(-830,300),(-880,800),(-340,1160),(310,920),(700,500),(390,210),(-220,170)])],
 [door(1140,0,460,270),door(-190,90,290,370,1),door(-1220,450,510,270)],'ochre',kind='liver')
STOMACH=organ('Stomach','STOMACH',[-2900,2250,0],
 [(1460,-340),(1190,120),(800,410),(580,990),(-40,1190),(-800,900),(-1340,340),(-1160,-470),(-680,-810),(-230,-300),(440,-130),(990,-610)],
 [room([(1080,-310),(980,30),(580,300),(390,690),(-80,920),(-670,650),(-1010,190),(-920,-330),(-720,-440),(-330,-100),(230,90),(650,-140)])],
 [door(1260,-315,420,225),door(-1110,-330,450,250)],'peach',kind='stomach')

def kidney(side):
    # The inward hilum distinguishes each kidney from an oval dish.
    s=1 if side=='Right' else -1
    outline=[(1050,-210),(850,-640),(100,-830),(-680,-650),(-1090,-100),(-800,570),(-190,780),(240,490),(20,160),(530,210)]
    interior=[(760,-210),(570,-470),(50,-600),(-520,-440),(-810,-60),(-610,400),(-210,540),(-40,310),(-130,20),(410,0)]
    return organ('Kidney'+side,side.upper()+' KIDNEY',[-5850,-3400 if side=='Right' else 3400,0],
      [(x,y*s) for x,y in outline],[room([(x,y*s) for x,y in interior])],
      [door(940,-190*s,440,230),door(-925,-40*s,420,230)],'water',kind='kidney')
GUT=organ('Intestine','INTESTINES',[-7700,0,0],
 [(1650,0),(1570,-1510),(1060,-2120),(220,-2370),(-930,-2210),(-1530,-1510),(-1580,-350),(-1450,850),(-1290,1810),(-520,2190),(810,2120),(1410,1320)],
 [channel([(-1030,-1470),(220,-1750),(1010,-1130),(1120,0),(940,1310),(50,1720),(-870,1370),(-1120,850)],490),
  channel([(-900,-700),(-420,-1060),(140,-750),(420,-200),(120,550),(-560,650),(-1000,190),(-600,-270)],470)],
 [door(1400,0,500,270),door(400,-2040,280,530,1),door(400,1950,280,530,1),door(-1490,860,480,250),door(-820,-1070,290,480,1)],'honey',kind='intestine')
BLADDER=organ('Bladder','BLADDER',[-10700,0,0],
 [(800,0),(590,-540),(-40,-730),(-610,-440),(-780,0),(-610,440),(-40,730),(590,540)],
 [room([(550,0),(370,-370),(-50,-475),(-380,-290),(-490,0),(-380,290),(-50,475),(370,370)])],
 [door(710,0,390,220)],'water',kind='bladder')
ORGANS=[LUNG_R,LUNG_L,BRAIN,LIVER,STOMACH,kidney('Right'),kidney('Left'),GUT,BLADDER]
HEART={**get_layout('A'),'key':'Heart','name':'HEART','center':[1400,0,0],'source':'HeartModels/A'}
# Shared places are intentionally small in number. They make route choices readable.
HUBS=[dict(key='Diaphragm',name='BREATHING GLADE',center=[-1000,0,0],radius=610,palette='mint'),
      dict(key='Throat',name='THROAT PASS',center=[4960,0,0],radius=610,palette='mint'),
      dict(key='DigestiveCrossing',name='DIGESTIVE CROSSING',center=[-4790,0,0],radius=510,palette='honey')]

def path(name,points,width=470):return dict(name=name,points=[list(p) if len(p)==3 else [p[0],p[1],0] for p in points],width=width)
PATHS=[
 path('Heart entrance',[(-1080,0),(-690,120),(-160,210)]),
 path('Right breath bridge',[(-1050,-300),(-920,-1330),(-420,-2580),(830,-3050)],510),
 path('Left breath bridge',[(-1050,300),(-920,1330),(-420,2580),(850,3050)],510),
 path('Right lung to throat',[(3770,-3050),(4380,-2520),(4840,-980),(4960,-200)]),
 path('Left lung to throat',[(3750,3050),(4380,2520),(4840,980),(4960,200)]),
 path('Heart to throat',[(2590,-790),(3230,-870),(3990,-350),(4960,0)]),
 path('Crown ascent',[(5160,0,0),(5380,0,150),(5600,0,355),(5760,0,370)],540),
 path('Liver approach',[(-1170,-290),(-1570,-1160),(-1810,-2050)],510),
 path('Stomach approach',[(-1170,290),(-1530,1130),(-1640,1935)],510),
 path('Solar descent',[(-1440,0),(-2880,0),(-4200,0),(-4790,0)],500),
 path('Liver lower arch',[(-4120,-1600),(-4470,-1010),(-4790,0)]),
 path('Stomach outlet',[(-4010,1920),(-4500,1080),(-4790,0)]),
 path('Right recovery path',[(-4450,-1020),(-4550,-2340),(-4910,-3590)]),
 path('Left recovery path',[(-4480,1090),(-4550,2340),(-4910,3590)]),
 path('Digestive entry',[(-4790,0),(-5470,0),(-6300,0)],520),
 path('Right kidney return',[(-6775,-3440),(-7240,-2860),(-7300,-2040)]),
 path('Left kidney return',[(-6775,3440),(-7240,2860),(-7300,1950)]),
 path('Pelvic passage',[(-9190,860),(-9600,500),(-9990,0)],500),
]

STATIONS=[
 dict(name='LUNGS',title='Breathing glade',position=[-1000,0,63],kind='breath',palette='mint'),
 dict(name='HEART',title='Pacing chamber',position=[2050,750,63],kind='heart',palette='coral'),
 dict(name='BRAIN',title='Awareness garden',position=[8901.25,0,433],kind='brain',palette='lavender'),
 dict(name='STOMACH',title='Digestion hearth',position=[-3200,2500,63],kind='glucose',palette='honey'),
 dict(name='LIVER',title='Recovery pool',position=[-2860,-2850,63],kind='filter',palette='ochre'),
 dict(name='ADRENALS',title='Calm spring',position=[-4930,-3560,63],kind='calm',palette='mint'),
 dict(name='ADRENALS',title='Energy spring',position=[-4930,3560,63],kind='energy',palette='peach'),
]
from brain_garden_layout import THOUGHTS as GARDEN_THOUGHTS, LEVEL_SCALE, WORLD_X
THOUGHTS=[[WORLD_X+x*LEVEL_SCALE,y*LEVEL_SCALE,433] for x,y in GARDEN_THOUGHTS]
# Context silhouettes sit beneath play surfaces, keeping routes free.
CONTEXT=[dict(key='Spleen',center=[-2950,3760,-30],scale=[620,300,190],palette='lavender'),
         dict(key='Pancreas',center=[-4600,880,-170],scale=[220,690,105],palette='honey'),
         dict(key='Gallbladder',center=[-3920,-2310,-30],scale=[310,180,200],palette='mint'),
         dict(key='Thymus',center=[3400,450,-70],scale=[310,240,110],palette='peach'),
         dict(key='ThyroidRight',center=[5430,-550,-40],scale=[290,210,110],palette='peach'),
         dict(key='ThyroidLeft',center=[5430,550,-40],scale=[290,210,110],palette='peach')]
BODY_HALF=[(10050,0),(9820,1440),(9070,2280),(7840,2430),(6710,1780),(5950,860),(5160,970),(4450,3440),(3580,4680),(2330,5080),(470,5490),(-1600,6030),(-4170,6420),(-6160,6200),(-6810,5710),(-6160,5230),(-4000,5050),(-2240,4540),(-4780,4640),(-7200,4270),(-9590,3590),(-11070,2960),(-13900,2670),(-15800,2470),(-16500,1890),(-16040,1270),(-14360,1270),(-12480,1140),(-11280,0)]
