"""The detailed brain level, drawn around a central awareness tree.
Sources: FigJam images 358, 384 and 307. Coordinates are local centimeters.
"""
import numpy as np
from organ_math import curve,distance
RX,RY=2350,2720
TERRAIN_LIFT=150
GARDEN_EDGE=[(-1790,0),(-1640,-730),(-1160,-1520),(-280,-1860),(650,-1790),(1250,-1320),(1580,-630),(1750,0),(1640,760),(1140,1460),(390,1840),(-440,1790),(-1190,1370),(-1630,720)]
TREE=(0,0)
POOL=[(590,-210),(940,-470),(1390,-380),(1650,-20),(1390,480),(940,560),(600,260)]
STREAM=[(1080,120),(800,-400),(150,-820),(-650,-950),(-1000,-720),(-1590,-260),(-2230,0)]
BRIDGES=[dict(name='Arrival bridge',points=[(-2250,0),(-1990,50),(-1630,35)],width=410),
 dict(name='Memory bridge',points=[(-1060,-600),(-920,-850),(-640,-1090)],width=400),
 dict(name='Synapse bridge',points=[(1450,-620),(1490,-80),(1330,630)],width=400)]
# One continuous loop, one arrival axis and one court connection. The three
# destinations are the reading garden, reflection pool and focus terrace.
PATHS=[dict(points=[(-2180,0),(-1650,30),(-1080,0),(-650,0)],width=420),
 dict(points=[(-1080,0),(-1060,-600),(-920,-850),(-640,-1090),(-200,-1250),(790,-1130),(1450,-620),(1490,-80),(1330,630),(850,1030),(130,1150),(-550,1120),(-1050,700),(-1080,0)],width=370),
 dict(points=[(0,650),(45,890),(130,1150)],width=360)]
ZONES=[dict(key='Meadow',center=[-1440,-220],radii=[340,520],color=[.27,.35,.10]),
 dict(key='Library',center=[-650,-1460],radii=[450,390],color=[.35,.26,.16]),
 dict(key='Idea',center=[750,-1260],radii=[560,490],color=[.27,.36,.105]),
 dict(key='Focus',center=[780,1320],radii=[520,420],color=[.43,.32,.16]),
 dict(key='Worry',center=[-450,1450],radii=[490,400],color=[.22,.105,.29])]
THOUGHTS=[[-800,1300],[-440,1730],[-70,1510],[-410,1120]]
MEMORIES=[[-580,-1260],[720,-1430],[1110,950]]
CARE=[-540,0]
FOCUS=[840,1360]

def ellipse(x,y,c,r):return np.sqrt(((x-c[0])/r[0])**2+((y-c[1])/r[1])**2)
def blend(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def height(x,y):
    h=58+205*blend((1.15-ellipse(x,y,(720,-1240),(560,520)))/.65)
    h+=265*blend((1.15-ellipse(x,y,(800,1300),(550,450)))/.65)
    h+=140*blend((1.10-ellipse(x,y,(-650,-1420),(510,420)))/.65)
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
    walk&=ellipse(x,y,(0,0),(370,350))>1
    # The purple cerebellar overlook is a raised tissue landmark, not a shortcut.
    walk&=ellipse(x,y,(-1460,1370),(450,500))>1
    walk&=~((np.abs(x+700)<510)&(np.abs(y+1655)<110))
    walk&=~((np.abs(x+800)<160)&(np.abs(y+1340)<130))
    walk&=ellipse(x,y,FOCUS,(190,190))>1
    h=np.where(bd<0,bh,height(x,y))+5+TERRAIN_LIFT
    return walk,h
