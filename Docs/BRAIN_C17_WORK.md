# C17 — awareness tree and garden surfaces

The full Breath of the Wild quality objective remains active and unachieved.
The delivered C16-R2 build is preserved. This is a substantial environment
revision within the existing playable brain, not acceptance of the whole art
direction or all animation and gameplay requirements.

## Reference-led changes

The close awareness-tree reference is `Docs/References/ref-307.png`; the whole
location reference is `Art/BrainCraft/Concept/Brain-Location-Key-Art.png`.
They show connected twisting wood, exposed roots, attached pointed golden
leaves, fitted circular paving and distinct planted borders. Those structural
features guide the replacement, rather than adding loose ornaments to the old
tree and grass plane.

- Replaced the awareness tree with a continuous sculpted trunk, integrated
  buttress roots, seven authored primary boughs, tapered forks and petioles.
- Authored 493 folded lanceolate leaves with blade UVs and rooted wind motion.
- Fitted four narrow sap channels to the actual trunk surface. Existing care
  progression drives their glow; the material remains physically lit.
- Rebuilt 1,636 paving pieces, with explicit bevel rings and triangulated tops
  that follow the current C15 terrain heights. Seven circular courses form the
  central clearing. Its clear ring extends from radius 345 to 990 cm around
  the awareness tree; roots remain inside approximately 323 cm.
- Cleared decorative foliage from that expanded walking ring.
- Added bounded modeled relief to the existing 40 continuous terrain pieces
  away from paths. Existing grades, waterways and gate positions remain the
  navigation foundation; these are not claimed to satisfy every exploration need.
- Added a versioned generated moss color texture. R03 blends randomly offset
  samples over a triangular grid at a 420 cm base scale to suppress repetition.
  The shader computes explicit surface gradients using filtered samples instead
  of deriving tiny bump features from adjacent screen pixels. Its illustrated
  shading is not a scanned/calibrated PBR material set.
- Added a physical stone, bark, leaf and sap material family. Leaf canopy casts
  shadows and decorative leaves can fade for visibility.
- Interactive actors are now explicitly excluded from occlusion fading.
  Restart clears the previous carry-release pose state.

Editable source: `Art/BrainCraft/Brain_Craft_C17.blend`.
Exports and native assets use new C17 names. The level before placement is
preserved at `Art/BrainCraft/Source/C17/BrainCraft-before-C17.umap`.
Generated texture and exact built-in image prompt are documented in
`Art/BrainCraft/Source/C17/image-provenance.md`.

## Iteration evidence

The first authoring attempt found repeated projection points in sap channels,
which caused invalid tangent frames. The second removes duplicate samples and
handles nearly parallel frames. Logs are retained.

Geometry inspection then found 76 detached voxel-tip fragments and an inverted
root-bed top. R02 removes the small fragments, retains the main connected wood
surface, reverses the root bed and welds its center. The R01 editable scene is
preserved in the review folder.

The first native import aborted on an empty foliage mesh left after courtyard
clearance. It stopped before replacing level actors. Five empty meshes were
removed from the patch, and the resumed import reuses already imported assets.
Read the separate native logs for final import and play-check results; no visual
acceptance is inferred from import or material compilation alone.

R02 imported and rendered the actual new environment. Care and camera checks
passed. Its exploration run failed after three destinations at the lotus plinth
(waypoint 247): the overlapping step blocks stopped CharacterMovement. The
underlying terrain at that point remains flat at 330 cm, so this was not treated
as a reason to remove the new terrain relief or relax the test. R03 replaces
the physical pedestal with a continuous model: four shallow levels, broad
treads, beveled risers, and matching visible/physical ground. Maximum tread rise
is 18 cm. The original R02 failure is retained.

The R02 native image also showed a burned-out patch on the upper trunk and
excessively dark roots. The old tree point light lay inside the larger new wood
volume. R03 moves it outside the trunk, explicitly uses lumens, softens its
source, and reduces flat ambient fill. `-CraftC16Lighting` retains the old
lighting for diagnostic comparison. This is a lighting iteration, not final
lighting or performance acceptance.

## Outstanding scope

Reference fidelity and composition must be judged in actual native images.
Lighting, the wider garden planting and terrace architecture, cortical detail,
gate interiors, costume surfaces, thought expressions, VFX and animation contact
still need further work. A successful care route does not prove unrestricted
exploration or physical-controller support. No full-goal acceptance is asserted.
