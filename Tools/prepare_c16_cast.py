"""Intentional cloud silhouettes for the FigJam thought cast, in centimetres."""
from pathlib import Path
import json
import numpy as np
from skimage.measure import marching_cubes
from scipy.ndimage import gaussian_filter

root = Path(__file__).resolve().parents[1]
out = root / 'Art/BrainCraft/Source/C16'
out.mkdir(parents=True, exist_ok=True)
report = {}
for name, scale in [('Cloud', 1.0), ('Wisp', .43)]:
    axis = np.arange(-84, 85, 1.5)
    x, y, z = np.meshgrid(axis, axis, axis, indexing='ij')
    field = np.full(x.shape, 1000., np.float32)
    # Large crown, unequal shoulders and a broad weighted lower silhouette.
    # These lobes have a readable composition rather than a uniform ball grid.
    lobes = [(0, 0, -3, 44), (-3, 0, 39, 26), (0, -29, 29, 25),
             (-3, 31, 25, 27), (1, -48, 2, 22), (-2, 47, -2, 25),
             (2, -32, -32, 23), (-1, 31, -34, 23), (4, 0, -43, 22),
             (-31, -27, 10, 26), (-32, 28, 3, 28), (-37, 0, -24, 27),
             (24, -26, 18, 20), (25, 28, 14, 21), (29, -22, -20, 20),
             (28, 21, -24, 22)]
    for cx, cy, cz, r in lobes:
        d = np.sqrt(((x-cx)*1.1)**2 + (y-cy)**2 + ((z-cz)*1.04)**2)-r
        blend = np.clip(.5+.5*(d-field)/7, 0, 1)
        field = d*(1-blend)+field*blend-7*blend*(1-blend)
    field = gaussian_filter(field, .4)
    v, f, n, _ = marching_cubes(field, 0, spacing=(1.5,)*3)
    v = (v+axis[0])*scale
    tri = v[f]
    volume = np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1],tri[:, 2])).sum()/6
    if volume < 0:
        f = f[:, ::-1]
    np.savez_compressed(out / f'Thought{name}.npz', v=v, f=f)
    report[name] = {'vertices': len(v), 'triangles': len(f), 'volume_cm3': abs(float(volume)), 'lobes': len(lobes)}
(out / 'cast-construction.json').write_text(json.dumps(report, indent=2))
print('C16_CAST_VOLUMES_READY', report)
