from pathlib import Path
import re,json,heapq
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'Source/ThatBodyGame/HeartStudyNav.inl').read_text()
rows=re.findall(r'"([01]+)"',src);grid=np.array([[c=='1' for c in r] for r in rows])
ox=int(re.search(r'HeartNavOriginX=(-?\d+)',src).group(1));oy=int(re.search(r'HeartNavOriginY=(-?\d+)',src).group(1))
points=[[-1700,181],[-1140,270],[-645,230],[-645,-550],[485,-565],[485,395],[-196,565],[-715,355],[-1120,265],[-1680,181]]
def index(p):return (round((p[0]-ox)/10),round((p[1]-oy)/10))
def legal(p):return 0<=p[0]<grid.shape[0] and 0<=p[1]<grid.shape[1] and grid[p]
report=[]
for a,b in zip(points,points[1:]):
    ia,ib=index(a),index(b);q=[(0,ia)];dist={ia:0};seen=set()
    while q:
        _,p=heapq.heappop(q)
        if p in seen:continue
        seen.add(p)
        if p==ib:break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            np_=p[0]+dx,p[1]+dy
            if not legal(np_) or not legal((p[0]+dx,p[1])) or not legal((p[0],p[1]+dy)):continue
            nd=dist[p]+(1.414 if dx and dy else 1)
            if nd<dist.get(np_,1e9):
                dist[np_]=nd;heapq.heappush(q,(nd+np.hypot(np_[0]-ib[0],np_[1]-ib[1]),np_))
    checks=[legal(index(np.array(a)*(1-t)+np.array(b)*t)) for t in np.linspace(0,1,200)]
    report.append({'from':a,'to':b,'start_valid':bool(legal(ia)),'end_valid':bool(legal(ib)),'connected':ib in seen,'straight_route_clear':bool(all(checks))})
print(json.dumps(report,indent=2))
(ROOT/'Art/HeartBaseline/Source/route-layout-check.json').write_text(json.dumps(report,indent=2))
