from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
r=Path(__file__).resolve().parents[1];d=np.load(r/'Art/BrainCraft/Source/C13/terrain.npz');h=d['h'];xs=d['x'];ys=d['y'];step=xs[1]-xs[0]
gx,gy=np.gradient(h,step);s=np.hypot(gx,gy)
for x,y in [(-240,800),(-220,840),(-220,860),(-240,880),(-240,900),(-240,920),(-240,960),(0,1600),(0,1640),(0,2000),(0,2250)]:
    ix=int(round((x-xs[0])/step));iy=int(round((y-ys[0])/step));print(x,y,'height',round(h[ix,iy],2),'slope',round(s[ix,iy],2),'degrees',round(float(np.degrees(np.arctan(s[ix,iy]))),2))
v=(xs[:,None]>-420)&(xs[:,None]<180)&(ys[None,:]>720)&(ys[None,:]<1500)
print('bank max',s[v].max(),'99p',np.quantile(s[v],.99))
