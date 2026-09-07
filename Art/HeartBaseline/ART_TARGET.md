# Heart baseline: fixed reference

The owner approved `Concept/Heart-direction-study.png` for its quality and layout, then explicitly requested precise modeling of that image: clear, authored, stylized. This is the art target for the heart and the foundation for the body's later organs. Approval of the generated image is not approval of the actual 3D model.

The initial full-body procedural cutaway was rejected for flat organs, random tubes, clutter, and insufficient authored quality. It is preserved in Git and review captures. The active review is now one organ, the heart.

## Required correspondence

- One substantial continuous cutaway heart volume, with two rear chambers and two larger front chambers.
- Thick rounded coral walls that enclose real interiors. Complete arched connections between rooms, and an arched entrance at the apex.
- A single short great-vessel form rooted behind the heart. No freestanding network of decorative tubes.
- Quiet, continuous walkable floors with carved surface detail. No separate plates used as rooms.
- One raised pacing station and a luminous heart token in the rear right chamber.
- A gentle entrance bridge; a small hooded attention figure for scale.
- Warm coral and peach, restrained gold light, dark blue setting. Fine surface treatment remains subordinate to chamber shapes and the route.

## Editable source

`Heart_Baseline.blend` contains the complete watertight sculpt, surface pieces for camera occlusion, the great vessel, pacing valve and pulse seed. The pieces share the same sculpture and matched boundary normals. The complete sculpture remains in the source collection, hidden during rendering to prevent overlapping surfaces.

`Source/heart-layout.json` records the silhouette, individual chamber drawings and arched openings in centimeters. `Tools/sculpt_heart.py` converts those authored drawings into the solid sculpt and derives the navigation mask from the same room and door shapes. `Tools/author_heart_blender.py` assembles and exports the editable asset. These are not measurements recovered from the single concept image; the image's visible proportions and layout are the comparison target.

The Unreal map is `/Game/Maps/HeartStudy`. Source mesh pieces are placed in the map as editable Static Mesh Actors. Exported FBX Y coordinates are mirrored on these actors to match the Unreal gameplay drawing coordinates. The map should be reviewed in Play for the final lighting, character, camera, fading and pacing interaction.

## Review standard

Compare the actual Unreal full-model screenshot against the fixed image, then inspect the ventricles, pacing chamber and arches close up. Do not describe a compilation, navigation or packaging pass as visual acceptance. Remaining visible deviations must be stated and corrected before claiming an exact match.

## Concept provenance

The fixed image was generated with the built-in image-generation tool. Supplied FigJam references 19 and 99 guided its chamber architecture and layout. It is a design study, not an Unreal screenshot. The reference archive and generated study are used as visual guidance; the deliverable is independently constructed 3D geometry.
