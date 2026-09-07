# C15 — cortical geometry, water integration and readable lighting

C14 remains an immutable playable checkpoint. C15 is work toward the original
brain-adventure goal. The Breath of the Wild art target is not achieved.

## Authoritative comparison

Compared the packaged C14 views with `Art/BrainCraft/Concept/Brain-Location-Key-Art.png`
and FigJam images `Docs/References/ref-384.png` and `ref-275.png`.

C14 had pinched cortical surfaces, discontinuous water, almost black tree shadows,
and insufficient material/landmark detail. The concept calls for rounded tissue,
clearly constructed terraces, coherent watercourses, planted borders and readable
thought characters. A pass on movement does not satisfy those art requirements.

## Implemented

- Replaced normal-displaced cortical geometry with radial cross-sections that
  remain in their own angular plane. Positive radii and monotone cross-section
  angle are checked during construction. Carved the same three border openings.
- Rebuilt the spring stream with a shared descending water/physical-bed profile,
  laid stones at the channel margins and reconstructed the lotus moat. Existing
  path decks remain traversable crossings. Bank deformation fades toward paths.
- Increased cool fill and sky illumination, reduced excessive contact occlusion,
  and softened the sun. Kept physical material response and the restrained light
  banding pass. `-CraftLightingBaseline` retains C14 lighting for comparison.
- Added physical water normals and restrained moving surface variation. The first
  shader exposed legacy unbounded UVs; the corrected R2 shader clamps its edge
  input before exponentiation.
- Inspected the native-source thought cast with ray tests. Cloud and wisp eye
  geometry clears their bodies. The knot glyph had 23 sampled vertices hidden
  behind its spiral (minimum clearance -2.89 cm); moved that glyph forward 4 cm.
- Added settled-view frame-time reporting to the capture run. These are offscreen
  diagnostic samples, not representative frame-rate or player acceptance claims.

## Revisions and evidence

C15 r01 completed the care loop and camera checks. Actual exploration failed at
the lotus bank after 5 of 12 destinations. The failing log and native pictures
are preserved. R2 widens the bank and blends its deformation into path edges.
R2 then exposed a second channel lip. R3 limits the actual editable ground grade
and samples floor continuity between navigation nodes. A separate import bug
matched the category tag `Water` when removing the old mesh of that name, removing
the spring surfaces and cascades too. The importer now identifies removal targets
by mesh asset name and restores those four existing water pieces.

R3's care loop and camera checks pass; its exploration route reached the lower
gardens, then collided with a thought at its home position. R4 keeps the navigation
route outside each physical thought's home footprint. Final results must be read
from the r04 exploration and packaged logs; this document does not substitute for
those results. The two failed terrain routes and their screenshots are retained.

The corrected R4 native run traversed all 990 waypoints and visited all twelve
destinations with zero fall recoveries. C15 packaging follows that pass; packaged
results are stored separately in `Builds/BrainAdventure-C15-20260907/Evidence`.

The final source ray test confirms the knot glyph's minimum clearance is now
+1.11 cm, with no sampled glyph vertices behind the spiral body. This proves the
geometric clearance correction, not final thought-character art acceptance.

## Outstanding against the full objective

- Art: not accepted. Tree canopy/bark, planting composition, ground material,
  paving construction, terraced landmarks and gate interiors still need work.
  Rounded cortex repairs remove defects but do not establish concept fidelity.
- Thought models: source geometry inspected; actual close-up gameplay expression,
  movement and behavior presentation still need a dedicated rendered review.
- Player animation: C14 gait and physical handling retained. Sharp grip transitions
  and body/hand contact require filmed validation and further tuning.
- Cape: local body/thought collision only; scenery and self collision unfinished.
- Gameplay: core loop exists; final geometry needs repeated native traversal.
  Twelve test destinations do not prove every intended accessible area.
- Camera: mouse/keyboard and injected controller checks exist. Physical-controller
  testing and foreground occlusion with the complete art set remain outstanding.

## Primary lighting sources checked

- [Epic: Sky Lights](https://dev.epicgames.com/documentation/unreal-engine/sky-lights-in-unreal-engine?lang=en-US)
- [Epic: physical lighting units](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-physical-lighting-units-in-unreal-engine)
- [Nintendo CEDEC 2017 art session](https://cedec.cesa.or.jp/2017/session/VA/s58eed7182c81b.html)

Used Epic's sky-light controls together with the installed UE 5.8 component
definitions. The lighting balance is an art decision tested against native
captures; these sources do not establish visual equivalence to Zelda.
