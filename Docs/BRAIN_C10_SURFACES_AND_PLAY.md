# Brain C10: material, layout and interaction overhaul

Status: implementation candidate, not art accepted. The requested Zelda quality baseline remains a review target, not an achieved claim. C01–C09 are preserved studies; the old green texture and broad blurred path overlay are superseded.

## Surface construction

The garden now uses a continuous, geometrically displaced soil substrate. The separately overlaid EarthPath mesh is removed from the map. Shallow soil variation is baked into the mesh at a 14 cm grid; moss cushions reach approximately 20 cm of relief. Collision uses those same triangles. This is actual mesh displacement, not a promise of collision from a shader.

Grass is modeled as curved tapered blades, grouped into 3,535 placed clumps. Damp margins receive broad-leaf moss rosettes. Four geometry groups provide camera-stable cover, rooted lighting and a vertex-weighted wind/attention bend. Portal fronts, travel centers, lotus turning space and the sand pocket are excluded from placement.

New dedicated material assets use a generated painted atlas for soil, sandstone, moss and sand. The old Moss and Earth material assets are retained only for historical source compatibility. The new ground uses mirrored world projection, detailed painted grain, geometric normals and local surface-gradient relief. No broad grass-to-soil color blur remains. The sand pocket has modeled concentric rake grooves and three grouped contemplation stones.

Texture source: `Art/BrainCraft/Textures/T_C10_Garden_Atlas.png`, generated with the built-in image tool. Exact prompt: `Art/BrainCraft/Concept/C10-Garden-Atlas-Prompt.txt`. The atlas is an input asset; it is not a rendered game screenshot.

## Portal and encounter layout

| Stop | Authored location, cm | Purpose |
|---|---|---|
| Dawn alcove | -2130, -2020, 140; turned east | First star and persistent knot, near the arrival lesson |
| Spring of ideas | -1040, 1760, 1100 | A second star and light wisp, beside the terraced water garden |
| Memory shelter | 2050, 1700, 950; angled toward its approach | A third star and the heavy cloud, on the upper memory terrace |

The former row of three portals is removed. Their complete modeled assemblies move together, and the navigation mask excludes their solid backs and feet. Their thought spawn locations and visible currents move with the destinations. A small curved-roof rest shelter occupies part of the vacated court. Its roof fades separately for player visibility.

## Character and loop

Attention has tailored upper arms, forearms and mittens. A two-segment solve follows the thought's actual physical surface. Carry contact blends in; a heavy thought permits both pushing and backward dragging. Foot placement follows the real displaced collision. Cape spring motion, landing compression, breathing, blinks and swat anticipation remain procedural. This is a modular procedural character, not a completed skeletal animation library.

Keyboard and mouse controls remain WASD/arrows, Shift, E, Space, RMB orbit, wheel zoom, MMB pan, Tab overview, Home camera reset, H help, Escape pause, R restart. Controller support adds movement/camera sticks, triggers for zoom, X for care, A for brush/hop and left shoulder for hurry. Physical controller verification remains outstanding until explicitly recorded.

The complete care loop is three stars to the tree, focus at the lotus, heavy-cloud release, wisp brushing, three knot pushes, then the opened root bridge back to arrival. C09 completed all of these through injected PlayerController keyboard input, CharacterMovement and Chaos: 4 physical grabs, 0 recoveries, all 3 stars and 3 releases. C10 changes the layout and arm behavior, so that older result is not a C10 pass.

## Research applied

Nintendo's official development-series page identifies exploration, scale, music, combat and character behavior as parts of the open-air concept. The application here is to evaluate materials and small actions in a traversable location, with distinct destinations and route choices. The videos were linked by the page; a full viewing is not claimed. [Nintendo development series](https://www.nintendo.com/en-gb/News/2017/March/Go-behind-the-scenes-with-the-making-of-The-Legend-of-Zelda-Breath-of-the-Wild-1206592.html).

Adam Robinson-Yu describes triplanar cliff projection and selecting the strongest terrain paint channel for cleaner boundaries in A Short Hike. C10 adopts the principle of deliberate boundaries; the implemented technique is a continuous soil surface plus explicit geometric vegetation, rather than that game's exact shader. [Developer's shader notes](https://threadreaderapp.com/thread/1113100182655262721.html).

Epic distinguishes continuous surfaces from aggregate geometry such as grass, for which Nanite's simplification and occlusion benefits need measurement. Its displacement documentation also notes that changing geometry does not automatically generate matching shading normals. C10 therefore uses baked collision-matched displacement and independent surface normals, with conventional grass geometry. No unmeasured Nanite performance benefit is claimed. [UE 5.8 Nanite content guidance](https://dev.epicgames.com/documentation/unreal-engine/working-with-naniteenabled-content?lang=en-US).

## Required review

Fresh C10 imports, native captures and a complete input-driven loop must be checked after the final geometry and code changes. Screenshot poses are composition evidence only. Shader compilation, navigation masks and C++ builds are technical evidence, not visual or player acceptance. The approved heart is unchanged; lungs and the rest of the body remain earlier, unaccepted work.
