"""Author sculpted organ interiors and a complete connected navigation drawing."""
from pathlib import Path
import sys,json,heapq
import numpy as np
from scipy.ndimage import label,distance_transform_edt
from skimage.measure import marching_cubes
from PIL import Image
import trimesh
from adventure_layout import ORGANS,HEART,HUBS,PATHS,STATIONS,THOUGHTS,CONTEXT,BODY_HALF
from organ_math import curve,distance,box,smoothmax,room_fields,PALETTES

ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/BodyAdventure';ART.mkdir(exist_ok=True)

def save_sculpt(spec):
    out=ART/spec['key']/'Source';out.mkdir(parents=True,exist_ok=True)
    bounds=np.array(spec['outline']);step=14
    xs=np.arange(bounds[:,0].min()-150,bounds[:,0].max()+151,step,dtype=np.float32)
    ys=np.arange(bounds[:,1].min()-150,bounds[:,1].max()+151,step,dtype=np.float32)
    zs=np.arange(-294,661,step,dtype=np.float32);X,Y=np.meshgrid(xs,ys,indexing='ij');Z=zs[None,None,:]
    outer,fields=room_fields(spec,X,Y)
    tops=415+np.clip(X/1600,-1,1)*65
    kind=spec['kind']
    if kind in ['brain','lung','intestine']:
        t=np.clip((-outer-160)/260,0,1);t=t*t*(3-2*t)
        height=280 if kind=='brain' else 220 if kind=='intestine' else 320
        tops=tops*(1-t)+height*t
    if kind=='brain':
        # Broad, shallow gyri are carved into the surrounding tissue, not piled on top.
        tops+=15*np.sin(X/135+np.sin(Y/210))*np.sin(Y/140)
    field=smoothmax(outer[:,:,None]+np.maximum(-Z,0)**2/1150,Z-tops[:,:,None],55)
    field=smoothmax(field,-205-Z,65)
    for D in fields:
        cavity=smoothmax(D[:,:,None]-(Z-65)*.04,58-Z,42)
        field=smoothmax(field,-cavity,30)
    for d in spec['doors']:
        C,R,axis=d['center'],d['radii'],d['axis'];D=box(X,Y,C,R)
        across=(Y-C[1])/R[1] if axis==0 else (X-C[0])/R[0]
        ceiling=245+130*np.sqrt(np.maximum(1-np.clip(across,-1,1)**2,0))
        cavity=smoothmax(D[:,:,None],58-Z,25);cavity=smoothmax(cavity,Z-ceiling[:,:,None],20)
        field=smoothmax(field,-cavity,28)
    field+=2.0*np.sin(X[:,:,None]/105+Z/95)*np.sin(Y[:,:,None]/150-Z/110)*np.clip((Z-115)/160,0,1)
    v,f,_,_=marching_cubes(field,0,spacing=(step,step,step),allow_degenerate=False);v+=np.array([xs[0],ys[0],zs[0]])
    mesh=trimesh.Trimesh(v,f,process=True);trimesh.repair.fix_normals(mesh);trimesh.smoothing.filter_taubin(mesh,lamb=.38,nu=.4,iterations=5)
    v=np.array(mesh.vertices,dtype=np.float32);f=np.array(mesh.faces,dtype=np.int32);n=np.array(mesh.vertex_normals,dtype=np.float32)
    base,wall,edge,floor=np.array(PALETTES[spec['palette']]);low=np.clip((v[:,2]+120)/230,0,1)[:,None]
    c=base*(1-low)+wall*low
    flat=(np.clip((n[:,2]-.55)/.4,0,1)*np.clip((150-v[:,2])/70,0,1))[:,None];c=c*(1-flat)+floor*flat
    rim=(np.clip((n[:,2]-.05)/.95,0,1)*np.clip((v[:,2]-160)/130,0,1))[:,None];c=c*(1-rim*.45)+edge*rim*.45
    # Soft tissue grain, deliberately subordinate to the large color regions.
    u=v[:,0]/130+.10*np.sin(v[:,1]/210);w=v[:,2]/175+.13*np.sin(v[:,1]/340)
    crease=np.exp(-(np.sin(u+w*.4)/.13)**2)*np.exp(-(np.sin(w)/.30)**2)
    c*=1-crease[:,None]*.11*np.clip((.8-n[:,2])/.6,0,1)[:,None]
    c*=1+.022*(np.sin(v[:,0]/220)*np.cos(v[:,1]/170))[:,None]
    # Floor inlays describe lobes and channels while leaving most floor quiet.
    _,floor_fields=room_fields(spec,v[:,0],v[:,1]);nearest=np.argmin(np.array(floor_fields),axis=0)
    for i,r in enumerate(spec['rooms']):
        pts=np.array(r.get('points',r.get('channel')));center=pts.mean(axis=0)
        rad=np.hypot(v[:,0]-center[0],v[:,1]-center[1]);ring=np.exp(-(np.sin(rad/115*np.pi)/.18)**2)
        if 'channel' not in r:c*=1-ring[:,None]*flat*.075*(nearest==i)[:,None]
    np.savez_compressed(out/'sculpt.npz',vertices=v,faces=f,normals=n,colors=np.clip(c,0,1))
    report={**spec,'vertices':len(v),'triangles':len(f),'watertight':bool(mesh.is_watertight),'units':'cm'}
    (out/'model.json').write_text(json.dumps(report,indent=2));print('ORGAN_SCULPT_READY',spec['key'],len(f),mesh.is_watertight,flush=True)

def navigation():
    step=30;xs=np.arange(-11400,13621,step);ys=np.arange(-6550,6551,step);X,Y=np.meshgrid(xs,ys,indexing='ij')
    walk=np.zeros(X.shape,bool);blocked=np.zeros(X.shape,bool);height=np.full(X.shape,63,dtype=np.int16);regions=np.zeros(X.shape,np.uint8)
    for i,s in enumerate(ORGANS):
        if s.get('custom')=='BrainGarden':
            import brain_garden_layout as brain
            xx,yy=(X-s['center'][0])/brain.LEVEL_SCALE,(Y-s['center'][1])/brain.LEVEL_SCALE;m,h=brain.navigation(xx,yy)
            walk|=m;height[m]=np.rint(h[m]+s['center'][2]).astype(np.int16);regions[m]=i+1
            blocked|=(brain.inner_distance(xx,yy)<200)&~m
            continue
        xx,yy=X-s['center'][0],Y-s['center'][1];outer,fields=room_fields(s,xx,yy);space=np.minimum.reduce(fields)
        for d in s['doors']:space=np.minimum(space,box(xx,yy,d['center'],d['radii']))
        m=(space<-80)&(outer<-45);walk|=m;height[m]=63+s['center'][2];regions[m]=i+1
        blocked|=(outer<-45)&(space>=-80)
    # Use the approved heart's exact local navigation image, including its arches.
    a=np.array(Image.open(ROOT/'Art/HeartModels/A/Source/walkable-clearance.png'))[::-1,:].T>0
    ix=np.rint((X-1400+2220)/10).astype(int);iy=np.rint((Y+1740)/10).astype(int)
    valid=(ix>=0)&(iy>=0)&(ix<a.shape[0])&(iy<a.shape[1]);m=valid&a[np.clip(ix,0,a.shape[0]-1),np.clip(iy,0,a.shape[1]-1)];walk|=m;regions[m]=10
    blocked|=(distance(X-1400,Y,curve(HEART['outline']))<-45)&~m
    for h in HUBS:
        m=np.hypot(X-h['center'][0],Y-h['center'][1])<h['radius']-80;walk|=m
    # Bridges are identical sampled curves in the authored meshes and nav mask.
    for p in PATHS:
        pts=curve(p['points'],sub=14,closed=False)
        best=np.full(X.shape,1e12);z=np.zeros(X.shape)
        for a,b in zip(pts,pts[1:]):
            d=b-a;t=np.clip(((X-a[0])*d[0]+(Y-a[1])*d[1])/(d[0]**2+d[1]**2+1e-8),0,1)
            dd=(X-a[0]-t*d[0])**2+(Y-a[1]-t*d[1])**2;near=dd<best;z[near]=(a[2]+t*d[2])[near];best=np.minimum(best,dd)
        m=best<(p['width']/2-70)**2;walk|=m;hm=m&(regions!=3);height[hm]=np.rint(z[hm]+63).astype(np.int16)
    bridge_wall_overlap=int(np.sum(walk&blocked));walk&=~blocked
    components,ncomp=label(walk);points=np.argwhere(walk);clearance=distance_transform_edt(walk)*step
    def idx(p):return int(round((p[0]-xs[0])/step)),int(round((p[1]-ys[0])/step))
    def snap(p):
        q=idx(p)
        if 0<=q[0]<walk.shape[0] and 0<=q[1]<walk.shape[1] and walk[q]:return q
        ds=np.sum((points-np.array(q))**2,axis=1);k=points[np.argmin(ds)]
        if np.sqrt(ds.min())*step>230:raise RuntimeError('Station far outside walkable floor '+str(p))
        return tuple(k)
    def legal(p):return 0<=p[0]<walk.shape[0] and 0<=p[1]<walk.shape[1] and walk[p]
    def clear(a,b):
        return all(legal((round(a[0]*(1-t)+b[0]*t),round(a[1]*(1-t)+b[1]*t))) and clearance[round(a[0]*(1-t)+b[0]*t),round(a[1]*(1-t)+b[1]*t)]>=45 for t in np.linspace(0,1,int(np.hypot(b[0]-a[0],b[1]-a[1])*2)+2))
    def route(aa,bb):
        a,b=snap(aa),snap(bb)
        if components[a]!=components[b]:raise RuntimeError(f'Disconnected route {aa} -> {bb} components {components[a]} / {components[b]}')
        q=[(0,a)];cost={a:0};prev={};seen=set()
        while q:
            _,p=heapq.heappop(q)
            if p in seen:continue
            seen.add(p)
            if p==b:break
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                n=(p[0]+dx,p[1]+dy)
                if not legal(n) or not legal((p[0]+dx,p[1])) or not legal((p[0],p[1]+dy)):continue
                d=cost[p]+(1.414 if dx and dy else 1)+2/max(1,clearance[n]/step)
                if d<cost.get(n,1e9):cost[n]=d;prev[n]=p;heapq.heappush(q,(d+np.hypot(n[0]-b[0],n[1]-b[1]),n))
        path=[b]
        while path[-1]!=a:path.append(prev[path[-1]])
        path=path[::-1];simple=[];i=0
        while i<len(path)-1:
            # Keyboard steering has eight headings. Preserve those headings instead
            # of replacing curved routes with arbitrary-angle line-of-sight chords.
            j=i+1;direction=(path[j][0]-path[i][0],path[j][1]-path[i][1])
            while j<len(path)-1 and j-i<50 and (path[j+1][0]-path[j][0],path[j+1][1]-path[j][1])==direction:j+=1
            i=j;k=path[i];simple.append([int(xs[k[0]]),int(ys[k[1]]),int(height[k])])
        return simple
    # Visit every organ and the heart's four chambers, then perform the care loop.
    targets=[[-1000,0],[-900,-3000],[1100,-3050],[2550,-3050],[3450,-3050],[4900,0],[3430,3050],[1530,3050],[-1000,0],
      [600,-740],[1965,-765],[2050,750],[550,725],[-1000,0],[-2860,-2850],[-4930,-3560],[-6100,-3750],[-7400,-1750],[-10000,0],[-10700,0],[-7300,1750],[-6100,3750],[-4930,3560],[-3200,2500],[-4790,0],[-1000,0]]
    # Remove a route-only drawing helper outside the lung; never silently move a care station.
    targets=[p for p in targets if p!=[-900,-3000]]
    for p in [s['position'] for s in STATIONS]+THOUGHTS: snap(p)
    travel=[];last=targets[0]
    for p in targets[1:]:travel+=route(last,p);last=p
    legs=[]
    for dest in [STATIONS[1]['position'],STATIONS[2]['position'],*THOUGHTS]:
        legs.append(route(last,dest));last=dest
    extras=[]
    for dest in [[650,-730,63],STATIONS[4]['position'],STATIONS[3]['position'],STATIONS[2]['position'],STATIONS[5]['position'],STATIONS[6]['position']]:
        extras.append(route(last,dest));last=dest
    basecomp=components[snap(targets[0])];unreachable=[]
    for i,s in enumerate(ORGANS):
        area=(regions==i+1)&walk
        if np.any(area&(components!=basecomp)):unreachable.append(s['key'])
    report=dict(navigation_components=int(ncomp),unreachable_organ_regions=unreachable,travel_waypoints=len(travel),care_route_waypoints=[len(r) for r in legs],bridges=len(PATHS),organs=len(ORGANS)+1,character_width=100,bridge_width_min=min(p['width'] for p in PATHS),grid_step=step)
    (ART/'navigation-report.json').write_text(json.dumps(report,indent=2))
    Image.fromarray(np.uint8(walk.T[::-1])*255).save(ART/'walkable-route.png')
    np.savez_compressed(ART/'navigation.npz',walk=walk,height=height,regions=regions,xs=xs,ys=ys)
    if unreachable:raise RuntimeError('Disconnected organ floors '+str(unreachable))
    header='// Generated from the same authored rooms and bridges as the visible model.\nnamespace BodyAdventureNav {\n'
    header+=f'static constexpr int NX={len(xs)}, NY={len(ys)}, X0={xs[0]}, Y0={ys[0]}, Step={step};\n'
    header+='static constexpr char Walk[NX][NY+1]={\n'+ '\n'.join('"'+''.join('1' if v else '0' for v in row)+'",' for row in walk)+'};\n'
    header+='static constexpr int16 Height[NX][NY]={\n'+'\n'.join('{'+','.join(str(z) for z in row)+'},' for row in height)+'};\n'
    for key,pts in [('Travel',travel)]+[(f'Care{i}',r) for i,r in enumerate(legs)]+[(f'Extra{i}',r) for i,r in enumerate(extras)]:header+='static const FVector '+key+'[]={'+','.join('FVector('+','.join(map(str,p))+')' for p in pts)+'};\n'
    header+='}\n';(ROOT/'Source/ThatBodyGame/BodyAdventureNav.inl').write_text(header)
    (ART/'world-layout.json').write_text(json.dumps(dict(organs=ORGANS,heart=HEART,hubs=HUBS,paths=PATHS,stations=STATIONS,thoughts=THOUGHTS,context=CONTEXT,body_half=BODY_HALF),indent=2))
    print('ADVENTURE_NAV_READY',json.dumps(report),flush=True)

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'all'
    if mode in ['all','nav']:navigation()
    if mode!='nav':
        for spec in ORGANS:
            if not spec.get('custom') and (mode=='all' or spec['key']==mode):save_sculpt(spec)
