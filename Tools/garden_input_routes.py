"""Input traversal fixtures generated through the actual global walk mask."""
from pathlib import Path
import numpy as np,heapq,json
from scipy.ndimage import distance_transform_edt
from brain_garden_layout import MEMORIES,CARE,FOCUS,THOUGHTS,ROOT_START,ROOT_END,LEVEL_SCALE,WORLD_X
root=Path(__file__).resolve().parents[1];d=np.load(root/'Art/BodyAdventure/navigation.npz');walk=d['walk'];xs=d['xs'];ys=d['ys'];height=d['height'];clearance=distance_transform_edt(walk)
def snap(p):
    a=(round((p[0]-xs[0])/30),round((p[1]-ys[0])/30))
    if walk[a]:return a
    q=np.argwhere(walk);dist=np.sum((q-a)**2,axis=1);idx=dist.argmin()
    if dist[idx]>64:raise ValueError('Point outside walkable floor '+str(p))
    return tuple(q[idx])
def route(a,b):
    a,b=snap(a),snap(b);cost={a:0};prev={};done=set();queue=[(0,a)]
    while queue:
        _,p=heapq.heappop(queue)
        if p in done:continue
        done.add(p)
        if p==b:break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            q=(p[0]+dx,p[1]+dy)
            if not (0<=q[0]<len(xs) and 0<=q[1]<len(ys)) or not walk[q] or not walk[p[0]+dx,p[1]] or not walk[p[0],p[1]+dy]:continue
            c=cost[p]+(1.414 if dx and dy else 1)+2/max(1,clearance[q])
            if c<cost.get(q,1e10):cost[q]=c;prev[q]=p;heapq.heappush(queue,(c+np.hypot(q[0]-b[0],q[1]-b[1]),q))
    path=[b]
    while path[-1]!=a:path.append(prev[path[-1]])
    path=path[::-1];result=[];i=0
    while i<len(path)-1:
        j=i+1;dr=np.subtract(path[j],path[i])
        while j<len(path)-1 and j-i<30 and np.all(np.subtract(path[j+1],path[j])==dr):j+=1
        q=path[j];result.append([int(xs[q[0]]),int(ys[q[1]]),int(height[q])]);i=j
    return result
wp=lambda p:[WORLD_X+p[0]*LEVEL_SCALE,p[1]*LEVEL_SCALE]
destinations=[wp(p) for p in [MEMORIES[0],CARE,MEMORIES[1],CARE,MEMORIES[2],CARE,[FOCUS[0]-140,FOCUS[1]-100],*THOUGHTS,ROOT_START]]
routes=[];last=wp([-1630,30])
for dest in destinations:routes.append(route(last,dest));last=dest
routes.append([wp(np.array(ROOT_START)*(1-t)+np.array(ROOT_END)*t)+[500] for t in np.linspace(0,1,8)])
header='// Generated walk routes; final route checks the unlocked root bridge.\nnamespace BrainGardenRoutes {\n'
for i,r in enumerate(routes):header+='static const FVector Route'+str(i)+'[]={'+','.join('FVector('+','.join(map(str,p))+')' for p in r)+'};\n'
header+='}\n';(root/'Source/ThatBodyGame/BrainGardenRoutes.inl').write_text(header)
(root/'Art/BrainGarden/Source/input-route-audit.json').write_text(json.dumps(dict(legs=len(routes),waypoints=[len(r) for r in routes],actions=['pickup','deliver','pickup','deliver','pickup','deliver','focus','release','release','release','release','approach bridge','cross unlocked bridge']),indent=2))
print('GARDEN_INPUT_ROUTES_READY',len(routes),[len(r) for r in routes],flush=True)
