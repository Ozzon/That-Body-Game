"""Enlarge navigable land, keep props at human scale, simplify to three places."""
from pathlib import Path
p=Path(__file__).with_name('author_brain_garden.py');s=p.read_text()
# Remove competing mini-districts. The location has one main route and three places.
for start,end in [('# Thought library:','# Focus terrace:'),('# Folded cerebellum','# Planting comes'),('# Two small blossom trees','# Five squat lanterns')]:
    a=s.index(start);b=s.index(end,a);s=s[:a]+s[b:]
s=s.replace("for zone in [z for z in ZONES if z['key'] in ['Library','Focus']]+[dict(key='Pool',center=[1070,55],radii=[580,530])]:","for zone in [dict(key='Pool',center=[1070,55],radii=[580,530])]:")
s=s.replace('fx,fy=840,1360','fx,fy=FOCUS')
s=s.replace('beds=[(-1440,-450,230,250),(-200,-1790,240,120),(830,-1650,300,140),(1100,1660,200,120),(-200,1850,270,120)]','beds=[(-1570,-560,280,160),(400,-1570,340,140),(-320,1820,350,140)]')
s=s.replace('[(-1710,220),(-720,-740),(1170,-700),(1140,760),(-860,850)]','[(-1770,290),(780,-1190),(1060,1410)]')
s=s.replace('start=np.array([-350.,-520.]);end=np.array([-450.,-1280.])','start=np.array(ROOT_START,dtype=float);end=np.array(ROOT_END,dtype=float)')
needle="    if e['key']!='Cortex':\n        for v in o.data.vertices:v.co.z+=TERRAIN_LIFT"
replace="""    # Landscapes grow wider; the tree, lotus and thoughts retain human-scale proportions.
    key=e['key']
    for v in o.data.vertices:
        if key in ['TreeTrunk','TreeGlow','Canopy']:
            v.co.x*=.68;v.co.y*=.68;v.co.z=85+(v.co.z-85)*.68
        elif key in ['Focus','FocusPetals']:
            v.co.x+=FOCUS[0]*(LEVEL_SCALE-1);v.co.y+=FOCUS[1]*(LEVEL_SCALE-1)
        elif key.startswith('BrightThought'):
            k=int(key[-1]);v.co.x+=MEMORIES[k][0]*(LEVEL_SCALE-1);v.co.y+=MEMORIES[k][1]*(LEVEL_SCALE-1)
        else:
            v.co.x*=LEVEL_SCALE;v.co.y*=LEVEL_SCALE
        if key!='Cortex':v.co.z+=TERRAIN_LIFT"""
assert needle in s;s=s.replace(needle,replace)
s=s.replace('camera.location=(-6300,-360,5400)','camera.location=(-9500,-550,8100)')
s=s.replace('camera_data.ortho_scale=6400','camera_data.ortho_scale=9650')
s=s.replace("area('Large soft morning key',(-2700,-2200,4800),170000000,2900","area('Large soft morning key',(-3800,-3600,6500),270000000,4400")
s=s.replace("area('Lavender fill',(1500,3100,3000),100000000,2800","area('Lavender fill',(2100,4100,4700),180000000,4100")
s=s.replace("area('Golden rim',(2200,-1500,3000),140000000,1800","area('Golden rim',(3400,-2500,4900),200000000,2800")
s=s.replace("camera.location=(-3050,-2050,2590)","camera.location=(-3350,-2350,2700)")
s=s.replace("camera_data.ortho_scale=3150","camera_data.ortho_scale=3850")
# A matching Attention proxy in the source scene makes the real navigation scale visible.
needle="manifest=[]"
proxy="""# Source review includes Attention at native character scale, outside the export manifest.
px,py=-1330*LEVEL_SCALE,0;pz=float(height(-1330,0))+TERRAIN_LIFT+12
review_parts=[]
for name,pos,size,col in [('Sage cloak',(px,py,pz+82),(37,44,50),(.19,.32,.21)),('Soft hood',(px,py,pz+139),(49,53,52),(.28,.44,.29)),('Warm face',(px-39,py,pz+140),(20,35,33),(.94,.64,.22))]:review_parts.append(ellipsoid(name,pos,size,col,stage,surface))
for side in [-1,1]:
    review_parts.append(ellipsoid('Tiny boot',(px-11,py+side*20,pz+21),(24,17,22),(.09,.11,.08),stage,surface))
    review_parts.append(ellipsoid('Little arm',(px-3,py+side*47,pz+79),(15,15,30),(.22,.35,.20),stage,surface))
    review_parts.append(ellipsoid('Attention eye',(px-59,py+side*13,pz+147),(3,4,6),(.025,.045,.04),stage,surface))
merge(review_parts,'Attention | native scale for review')

manifest=[]"""
s=s.replace(needle,proxy)
p.write_text(s)
print('BRAIN_C05_THREE_PLACE_LAYOUT_READY')
