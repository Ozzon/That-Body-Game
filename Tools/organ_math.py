import numpy as np

def curve(points,sub=10,closed=True):
    p=np.array(points,dtype=np.float32);out=[]
    def at(i):return p[i%len(p)] if closed else p[max(0,min(len(p)-1,i))]
    for i in range(len(p) if closed else len(p)-1):
        a,b,c,d=[at(k) for k in [i-1,i,i+1,i+2]]
        for t in np.linspace(0,1,sub,endpoint=False):out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    if not closed:out.append(p[-1])
    return np.array(out)

def distance(x,y,points,closed=True):
    x,y=np.asarray(x),np.asarray(y)
    d=np.full(np.broadcast_shapes(x.shape,y.shape),1e12,dtype=np.float32);inside=np.zeros_like(d,dtype=bool)
    ends=np.roll(points,-1,axis=0) if closed else points[1:];starts=points if closed else points[:-1]
    for a,b in zip(starts,ends):
        vx,vy=b[:2]-a[:2];wx=x-a[0];wy=y-a[1];t=np.clip((wx*vx+wy*vy)/(vx*vx+vy*vy+1e-10),0,1)
        d=np.minimum(d,(wx-t*vx)**2+(wy-t*vy)**2)
        if closed:inside^=((a[1]>y)!=(b[1]>y))&(x<vx*(y-a[1])/(vy+1e-8)+a[0])
    return np.sqrt(d)*np.where(inside,-1,1)

def box(x,y,c,r):
    dx=np.abs(x-c[0])-r[0];dy=np.abs(y-c[1])-r[1]
    return np.hypot(np.maximum(dx,0),np.maximum(dy,0))+np.minimum(np.maximum(dx,dy),0)

def smoothmax(a,b,k=32):
    h=np.maximum(k-np.abs(a-b),0)/k
    return np.maximum(a,b)+h*h*k*.25

def room_fields(spec,x,y):
    outer=distance(x,y,curve(spec['outline']))
    raw=[distance(x,y,curve(r['points'])) if 'points' in r else distance(x,y,curve(r['channel'],closed=False),False)-r['width']/2 for r in spec['rooms']]
    fields=[]
    for i,d in enumerate(raw):
        if len(raw)>1:
            other=np.minimum.reduce([s for j,s in enumerate(raw) if j!=i])
            d=np.maximum(d-50,(d-other+115)*.5)
        fields.append(np.maximum(d,outer+125))
    return outer,fields

PALETTES={
 'coral':[(.28,.035,.032),(.52,.10,.058),(.72,.205,.105),(.60,.18,.10)],
 'mint':[(.10,.20,.21),(.24,.43,.36),(.49,.66,.48),(.32,.53,.43)],
 'lavender':[(.12,.065,.22),(.32,.20,.43),(.57,.38,.59),(.40,.30,.48)],
 'ochre':[(.24,.055,.047),(.45,.14,.085),(.65,.31,.16),(.51,.24,.12)],
 'peach':[(.28,.10,.075),(.59,.25,.17),(.76,.43,.27),(.67,.36,.22)],
 'water':[(.09,.15,.23),(.22,.34,.43),(.39,.57,.62),(.25,.43,.47)],
 'honey':[(.23,.12,.07),(.49,.31,.14),(.71,.49,.24),(.60,.40,.19)]}
