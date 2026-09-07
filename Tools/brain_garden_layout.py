"""The detailed brain level, drawn around a central awareness tree.
Sources: FigJam images 358, 384 and 307. Coordinates are local centimeters.
"""
import numpy as np
from organ_math import curve,distance
RX,RY=2350,2720
LEVEL_SCALE=1.55
WORLD_X=9250
TERRAIN_LIFT=150
GARDEN_EDGE=[(-1790,0),(-1640,-730),(-1160,-1520),(-280,-1860),(650,-1790),(1250,-1320),(1580,-630),(1750,0),(1640,760),(1140,1460),(390,1840),(-440,1790),(-1190,1370),(-1630,720)]
TREE=(0,0)
GARDEN_EDGE=[(x*1.16,y*1.16) for x,y in GARDEN_EDGE]
POOL=[(590,-210),(940,-470),(1390,-380),(1650,-20),(1390,480),(940,560),(600,260)]
STREAM=[(1080,120),(500,540),(-220,770),(-850,450),(-1510,480),(-2280,750)]
BRIDGES=[dict(name='Arrival bridge',points=[(-2250,0),(-1990,50),(-1630,35)],width=410),
 dict(name='Quiet garden bridge',points=[(1420,-550),(1510,15),(1350,650)],width=380)]
# One continuous loop, one arrival axis and one court connection. The three
# destinations are the reading garden, reflection pool and focus terrace.
PATHS=[dict(points=[(-2180,0),(-1450,0),(-800,0),(-550,-290),(-210,-610),(600,-850),(1180,-720),(1420,-550)],width=300),
 dict(points=[(1350,650),(1070,990),(450,1270),(-350,1400),(-650,1120)],width=300)]
ZONES=[dict(key='Meadow',center=[-1330,0],radii=[660,720],color=[.24,.34,.12]),
 dict(key='TreeCourt',center=[0,0],radii=[690,780],color=[.28,.31,.115]),
 dict(key='Worry',center=[-230,1320],radii=[730,510],color=[.255,.16,.29])]
THOUGHTS=[[-800,1300],[-440,1730],[-70,1510],[-410,1120]]
MEMORIES=[[-1300,210],[720,-1100],[450,1340]]
CARE=[-225,0]
FOCUS=[850,1310]
ROOT_START=[-600,1060]
ROOT_END=[-810,210]

def ellipse(x,y,c,r):return np.sqrt(((x-c[0])/r[0])**2+((y-c[1])/r[1])**2)
def blend(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def height(x,y):
    h=58+115*blend((1.15-ellipse(x,y,(530,1290),(970,580)))/.65)
    return h
def waters(x,y):return np.minimum(distance(x,y,curve(POOL)),distance(x,y,curve(STREAM,closed=False),False)-92)
def inner_distance(x,y):
    return distance(x,y,curve(GARDEN_EDGE,8))
def floor_height(x,y):return height(x,y)-92*blend(-waters(x,y)/100)
def bridge_values(x,y):
    dist=np.full(np.broadcast_shapes(np.shape(x),np.shape(y)),1e9);h=np.array(height(x,y),copy=True)
    for b in BRIDGES:
        p=curve(b['points'],14,False);total=np.linalg.norm(np.diff(p,axis=0),axis=1).sum();run=0
        for a,c in zip(p,p[1:]):
            v=c-a;l=np.linalg.norm(v);t=np.clip(((x-a[0])*v[0]+(y-a[1])*v[1])/(l*l),0,1);d=np.hypot(x-a[0]-t*v[0],y-a[1]-t*v[1])-b['width']/2
            u=(run+t*l)/total;z0=float(height(*p[0]));z1=float(height(*p[-1]));z=z0+(z1-z0)*u+np.sin(u*np.pi)*85+12
            m=d<dist;h=np.where(m,z,h);dist=np.minimum(dist,d);run+=l
    return dist,h
def navigation(x,y):
    water=waters(x,y);bd,bh=bridge_values(x,y)
    walk=(inner_distance(x,y)<-95)&(water>65)
    walk|=(bd<-65)&(inner_distance(x,y)<200)
    walk&=ellipse(x,y,(0,0),(250/LEVEL_SCALE,250/LEVEL_SCALE))>1
    walk&=ellipse(x,y,FOCUS,(190/LEVEL_SCALE,190/LEVEL_SCALE))>1
    h=np.where(bd<0,bh,height(x,y))+5+TERRAIN_LIFT
    return walk,h
