import heapq,json,numpy as np
from pathlib import Path
from brain_craft_layout import *
ROOT=Path(__file__).resolve().parents[1];d=np.load(ROOT/'Art/BrainCraft/Source/C11/navigation.npz');xs=d['x'];ys=d['y'];mask=d['walk'];h=d['h'];step=40
def nearest(p):
    ids=np.argwhere(mask);delta=(xs[ids[:,0]]-p[0])**2+(ys[ids[:,1]]-p[1])**2;i=np.argmin(delta);return tuple(ids[i])
def route(start,end):
    a=nearest(start);b=nearest(end);q=[(0,a)];g={a:0};prev={}
    while q:
        _,u=heapq.heappop(q)
        if u==b:break
        for di,dj in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            v=(u[0]+di,u[1]+dj)
            if not(0<=v[0]<len(xs) and 0<=v[1]<len(ys)) or not mask[v]:continue
            if di and dj and (not mask[u[0]+di,u[1]] or not mask[u[0],u[1]+dj]):continue
            cost=np.hypot(di,dj)+abs(h[v]-h[u])/80
            gg=g[u]+cost
            if gg<g.get(v,1e15):g[v]=gg;prev[v]=u;heapq.heappush(q,(gg+np.hypot(v[0]-b[0],v[1]-b[1]),v))
    if b not in g:raise RuntimeError('Disconnected route')
    path=[b]
    while path[-1]!=a:path.append(prev[path[-1]])
    path=path[::-1];picked=[path[0]]
    for i in range(1,len(path)-1):
        if i%3==0:picked.append(path[i])
    picked.append(path[-1]);return [(int(xs[i]),int(ys[j]),int(h[i,j])) for i,j in picked]
encounters=json.loads((ROOT/'Art/BrainCraft/Source/C11/encounters.json').read_text())['thoughts']
targets=[encounters[0],TREE_CARE,encounters[1],TREE_CARE,encounters[2],TREE_CARE,(1530,-1775),encounters[3],(2040,-925),encounters[4],encounters[5],(1220,-1710),SPAWN]
p=SPAWN;out=['// Generated from the same C07 walkable geography. Real input follows these routes.','namespace CraftRoutes {']
for i,t in enumerate(targets):
    r=route(p,t) if i!=12 else [tuple(map(int,q)) for q in curve(SHORTCUT,9,False)]+[SPAWN]
    out.append('static const FVector R%d[]={%s};'%(i,','.join('FVector(%d,%d,%d)'%q for q in r)));p=t
out.append('static TArray<FVector> Route(int I){switch(I){')
for i in range(len(targets)):out.append('case %d:return TArray<FVector>(R%d,UE_ARRAY_COUNT(R%d));'%(i,i,i))
out.append('default:return {};}}}')
(ROOT/'Source/ThatBodyGame/BrainCraftRoutes.inl').write_text('\n'.join(out));print('CRAFT_ROUTES',len(targets))
