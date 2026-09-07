from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1];source=root/'Source/ThatBodyGame';gates=json.loads((root/'Art/BrainCraft/Source/C14/portals.json').read_text())
header=source/'BrainCraftLayout.inl';old=header.read_text();thoughts=re.search(r'static const FVector Thoughts\[\]=[^;]+;',old).group(0)
portals=[];approaches=[]
for e in gates:
    p=e['p'];v=e['outward'];portals.append(p);approaches.append([p[0]-v[0]*330,p[1]-v[1]*330,p[2]])
def array(name,points):return 'static const FVector '+name+'[]={'+','.join('FVector(%.2f,%.2f,%.2f)'%tuple(p) for p in points)+'};'
header.write_text('// Generated from the C14 tissue-nest boundary layout.\nnamespace CraftLayout {\n'+array('Portals',portals)+'\n'+array('PortalApproaches',approaches)+'\n'+thoughts+'\n}\n')
for name in ['BrainCraftReview.cpp','BrainCraftExploration.cpp']:
    p=source/name;t=p.read_text().replace('brain-c13-','brain-c14-').replace('Brain-C13-','Brain-C14-').replace('BrainFilm/C13/','BrainFilm/C14/')
    if name=='BrainCraftReview.cpp':
        t=t.replace('RoamVisited==9&&Recoveries==0','RoamVisited==RoamCheckpoints.Num()&&RoamVisited>0&&Recoveries==0').replace('\\\"expected\\\":9','\\\"expected\\\":%d').replace('RoamVisited,RoamWaypoint,RoamRoute.Num()','RoamVisited,RoamCheckpoints.Num(),RoamWaypoint,RoamRoute.Num()')
    p.write_text(t)
print('C14_NATIVE_LAYOUT_READY')
