"""C06 geography. Centimeters; explicit districts and walkable connections.

Independent replacement, not an in-place mutation of any rejected model.
"""
import numpy as np
from organ_math import curve, distance

DISTRICTS = [
    dict(key='Arrival', p=(-1700,-2200,140), r=(680,680)),
    dict(key='Awareness', p=(0,0,520), r=(1050,1080)),
    dict(key='Spring', p=(-1500,1400,1100), r=(770,790)),
    dict(key='Nests', p=(1500,1400,950), r=(850,850)),
    dict(key='Release', p=(1580,-1390,330), r=(760,730)),
]
ROUTES = [
    dict(key='FirstThoughtCrossing', width=540, points=[(-1700,-2200,140),(-1410,-1650,225),(-1080,-1030,295),(-640,-480,340),(0,0,340)]),
    dict(key='ArrivalPromenade', width=520, points=[(-1700,-2200,140),(-2170,-1480,290),(-2230,-270,580),(-2200,1150,990),(-2000,2070,1100),(-1340,2070,1100),(-1020,1400,1100)]),
    dict(key='SpringBridge', width=540, points=[(-1020,1400,1100),(-1120,650,1000),(-1200,210,780),(-780,-120,520),(0,0,520)]),
    dict(key='MemoryWalk', width=510, points=[(-1020,1400,1100),(-1450,2310,1180),(-600,2450,1300),(650,2430,1250),(1500,1400,950)]),
    dict(key='NestApproach', width=560, points=[(0,0,520),(1000,-150,520),(1550,100,710),(1770,510,920),(1500,1400,950)]),
    dict(key='ReleaseWalk', width=530, points=[(1500,1400,630),(2400,450,450),(2400,-600,340),(1580,-1390,330)]),
    dict(key='LotusBridge', width=520, points=[(1580,-1390,330),(760,-1240,340),(440,-650,340),(0,0,340)]),
]
SHORTCUT=[(1220,-1780,330),(380,-2210,290),(-470,-2440,210),(-1300,-2310,140)]
SPAWN=(-1810,-2470,140)
TREE=(0,90,520)
TREE_CARE=(0,-365,520)
LOTUS=(1580,-1390,330)
RELEASE=(2070,-1150,330)
NESTS=[(1170,1970,950),(1730,1960,950),(2170,1420,950)]
THOUGHTS=[(980,1380,950),(1710,1050,950),(1640,1490,950),(1830,1610,950)]
OUTLINE=[(-150,-3100),(-1380,-3310),(-2470,-2700),(-3000,-1300),(-3020,800),(-2460,2570),(-1410,3180),(-180,3050),
         (0,2730),(190,3050),(1590,3210),(2760,2300),(3140,600),(2940,-1480),(2440,-2680),(1280,-3310),(160,-3060),(0,-2640)]

def ellipse(x,y,p,r):return (np.sqrt(((x-p[0])/r[0])**2+((y-p[1])/r[1])**2)-1)*min(r)

def route_profile(r):
    p=curve(r['points'],20,False);s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p[:,:2],axis=0),axis=1))];z=np.full(len(p),np.nan)
    for d in DISTRICTS:
        norm=np.sqrt(((p[:,0]-d['p'][0])/d['r'][0])**2+((p[:,1]-d['p'][1])/d['r'][1])**2)
        z[norm<.80]=d['p'][2]
    valid=~np.isnan(z)
    if valid.any():p[:,2]=np.interp(s,s[valid],z[valid])
    if r['key']=='MemoryWalk':p[:,2]+=180*np.sin(np.pi*s/max(s[-1],1))
    return p

def fields(x,y):
    shape=np.broadcast_shapes(np.shape(x),np.shape(y)); nearest=np.full(shape,1e9); h=np.full(shape,340.)
    for d in DISTRICTS:
        v=ellipse(x,y,d['p'],d['r']);m=v<nearest;h=np.where(m,d['p'][2],h);nearest=np.minimum(nearest,v)
    road=np.full(shape,1e9);center_dist=np.full(shape,1e9);graded=np.full(shape,520.)
    for r in ROUTES:
        p=route_profile(r)
        for a,b in zip(p,p[1:]):
            v=b-a;t=np.clip(((x-a[0])*v[0]+(y-a[1])*v[1])/(v[0]**2+v[1]**2+1e-9),0,1)
            dd=np.hypot(x-a[0]-t*v[0],y-a[1]-t*v[1])-r['width']/2
            dc=dd+r['width']/2;m=dc<center_dist;graded=np.where(m,a[2]+t*v[2],graded);center_dist=np.minimum(center_dist,dc)
            m=dd<nearest;h=np.where(m,a[2]+t*v[2],h);nearest=np.minimum(nearest,dd);road=np.minimum(road,dd)
    # Court stone rings and purposeful open landings.
    road=np.minimum(road,np.abs(np.hypot(x,y)-805)-240)
    for k in [0,3]:
        d=DISTRICTS[k];road=np.minimum(road,ellipse(x,y,d['p'],(d['r'][0]-110,d['r'][1]-130)))
    road=np.minimum(road,ellipse(x,y,LOTUS,(470,440)))
    # Flat inhabited terraces have explicit elevations. Curved graded approaches
    # interpolate between their inner landings, not arbitrary global Y height.
    h=graded
    for d in DISTRICTS:
        n=np.sqrt(((x-d['p'][0])/d['r'][0])**2+((y-d['p'][1])/d['r'][1])**2)
        t=np.clip((1.08-n)/.30,0,1);t=t*t*(3-2*t);h=h*(1-t)+d['p'][2]*t
    return nearest,h,road

def water(x,y):
    # The spring is a terraced water garden beside, not across, its main path.
    a=ellipse(x,y,(-1600,1430),(400,490))
    b=distance(x,y,curve([(-1630,1510),(-1930,900),(-1700,380),(-1210,-50),(-970,-630)],12,False),False)-100
    c=np.maximum(ellipse(x,y,LOTUS,(670,650)),-ellipse(x,y,LOTUS,(480,460)))
    return np.minimum.reduce([a,b,c])

def walk(x,y):
    d,h,road=fields(x,y);w=water(x,y)
    ok=(d < -48) & ((w>38)|(road < -55)) & (np.hypot(x-TREE[0],y-TREE[1])>300) & (np.hypot(x-LOTUS[0],y-LOTUS[1])>342) & (distance(x,y,curve(OUTLINE,10)) < -48)
    return ok,h
