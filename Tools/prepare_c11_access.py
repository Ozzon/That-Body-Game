"""Four explicit garden descents and a clear eastern spring promenade."""
import numpy as np,json
from pathlib import Path
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import map_coordinates
from organ_math import curve
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'Art/BrainCraft/Source/C11'
d=np.load(DATA/'Understory.npz');lower=LinearNDInterpolator(d['v'][:,:2],d['v'][:,2]);t=np.load(DATA/'terrain.npz')
def upper(x,y):return float(map_coordinates(t['h'],[[(x-t['x'][0])/14],[(y-t['y'][0])/14]],order=1)[0])
routes=[
 ('Front fern walk',[(-1510,-2110),(-1370,-1910),(-1160,-1750),(-930,-1800)],280),
 ('Western moss walk',[(-2150,-730),(-1940,-670),(-1760,-630),(-1570,-650)],290),
 ('Northern quiet walk',[(260,2440),(260,2160),(120,1880),(0,1640)],330),
 ('Eastern iris walk',[(1380,-1230),(1370,-1030),(1230,-810),(1100,-650)],290),
 ('Spring promenade',[(-1040,650),(-980,1100),(-1080,1500),(-1060,1880),(-1420,2180)],360)]
out=[]
for key,xy,width in routes:
    points=curve(xy,16,False);s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))];t0=s/s[-1]
    if key=='Spring promenade':z=np.array([upper(*p)+18 for p in points])
    else:
        z0=upper(*points[0])+12;z1=float(lower(*points[-1]))+8
        # Flat ends for planted foot contact; all ramps are below 30 degrees.
        f=t0*t0*(3-2*t0);z=z0+(z1-z0)*f
        z=np.maximum(z,np.array([float(lower(*p))+6 for p in points]))
    z=np.max(z[None,:]-.55*np.abs(s[:,None]-s[None,:]),axis=1)
    p=np.column_stack([points,z]);slope=np.max(np.abs(np.diff(z))/np.linalg.norm(np.diff(points,axis=0),axis=1));assert slope<.65,(key,slope)
    out.append(dict(name=key,points=p.tolist(),width=width,max_slope_degrees=float(np.degrees(np.arctan(slope)))))
(DATA/'garden-access.json').write_text(json.dumps(out,indent=2));print([(r['name'],round(r['max_slope_degrees'],1)) for r in out])
