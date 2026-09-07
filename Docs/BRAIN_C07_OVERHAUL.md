# Brain C07: terrain and asset overhaul

The owner rejected C06's flat terrain, primitive surface treatment, small-looking
spaces and mismatch to the Figma garden. C06 is preserved in
`Art/BrainCraft/Reviews/C06-Flat-Garden-Rejected`. C07 is work in progress and has
no visual acceptance. A generated picture is never a gameplay screenshot.

## Reference correspondence

- refs 358 and 384: embedded garden terraces and level changes within recognizably
  brain-shaped tissue. Arrival 1.4 m, tree court 5.2 m, thought glade 9.5 m and
  spring court 11 m. The spring basins rise to 12.2 m and 14.1 m. Heights are
  designed gameplay dimensions, not anatomical measurements.
- Brain Location Key Art: spring at upper left, thought nests at upper right,
  golden awareness tree in the center, lower arrival and release garden, with a
  restored root crossing providing the final return route.
- ref 307: fused twisting tree roots and boughs, smaller individual pointed leaves,
  light traveling through root channels, contained planting around the court.
- ref 379: Attention has a closed peaked hood, fitted glowing face opening, layered
  scarf, botanical cape embroidery, A-line tunic, cuffs, mittens and wrapped boots.
- ref 275: different silhouettes and physical responses for the star, heavy cloud,
  light wisp and persistent knot. Carry, drag, brush and repeated push remain
  distinct actions. The focus lotus slows the drift.

## Construction changes

The old straight tissue extrusion is replaced by a closed rounded volume. Surface
folds extend down the walls. Garden courts have explicit elevations and graded
approaches. Stepped spring basins have retaining masonry, spill openings, curved
waterfall meshes and foam contacts. A cherry tree frames the spring; fitted stone
arches and roots frame the thought nests. Planting and stones occupy chosen outer
margins, leaving movement centers clear.

A purpose-made painted atlas supplies tissue, sandstone, wood and cloth. Normal
relief is reduced substantially; world projection removes per-polygon color seams
on the tissue and terrain. Lighting uses a daylight ambient cube, broad colored
fill and warm local tree illumination. Canopy and fine midrib geometry no longer
cast the solid black shadow that hid Attention in C06. This requires actual Unreal
comparison; source material and lighting setup alone do not establish quality.

The character uses separate authored meshes driven by a procedural pivot rig,
ground-aware feet, cape spring motion, carry/drag poses and a timed swat impact.
It is not a finished skinned animation library. Thoughts use real rigid-body
collision and a physics handle, with controlled hover forces, reactions and faces.
Event particles are instanced meshes, not authored Niagara systems.

## Verification and remaining work

Geometry-derived C07 route grid: 1,297.76 square meters, one connected component,
39-degree maximum allowed sampled slope. This is a design audit, not a complete
collision or play test. The new source and materials must be imported and the
entire input-driven care sequence must complete, including the root crossing.

C06 input validation carried and delivered two stars without a fall recovery,
then stalled while chasing the third star. The chase timer is corrected in C07;
successful C07 validation has not yet been recorded. Character ground queries and
thought spawn heights now use the visible walkable geometry, including terraces.

Approved Heart Model A is unchanged. Lungs and the remaining organ locations do
not yet have this replacement level of modeled detail. C01-C06 are not candidates
for visual approval or packaging.
