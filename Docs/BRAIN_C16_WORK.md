# C16 — thought cast and physical character presentation

The full Breath of the Wild quality objective remains active and unachieved.
C15-R2 is preserved. This revision develops the thought characters and player
presentation; it does not complete the garden environment overhaul.

## Reference and implementation

Compared native C15-R2 gameplay recordings with FigJam `ref-275.png` (four
thought types), `ref-379.png` (Attention costume), and the brain location key art.
Read the current BOTWRECKED `BWRobotPawn.cpp` carry centre / local grip anchors and
`BWBipedGait.cpp` contact stepper. The existing Attention gait is already adapted
from that title; this revision does not import unrelated robot or vehicle assets.

- Authored new closed star and cloud volumes, a small wisp with three independently
  animated filaments, and an amber rosette with curved overlapping petals.
- Added separate eye meshes and pivots: blinks leave mouths and cheeks intact.
  Upward face presentation makes expressions readable at the gameplay camera.
  Proximity, holding, calm and pushing affect expression and motion.
- Preserved the physical gameplay roles: carry stars, hold/push/drag the cloud,
  brush away the wisp, repeatedly push the persistent knot. Existing focus,
  delivery and return-bridge progression remain in the actual garden.
- Limited turning during carrying, compensated torso position for the load,
  and added a body-relative release transition for both hands.
- Added a post-physics presentation component. Hands and cloth now use the
  completed physical thought position, rather than the previous physics frame.
  The handle target update explicitly follows the character's movement tick.
- Corrected variable-step Verlet velocity, transported the cape simulation with
  the character, added bounded cloth tethers and increased constraint iterations.
  Relative wind and acceleration continue to drive physical motion.

Editable source: `Art/BrainCraft/Thought_Cast_C16.blend`.
Individual FBX expression/body parts: `Art/BrainCraft/ExportC16`.
Native imports use new C16 asset names; the original cast is preserved and is
selectable with `-CraftCastBaseline` for diagnostic comparison.

## Rejected revisions and meaningful checks

The C15-R2 rendered film completed the loop, but showed speckled deforming cloth
and up to 134.61 cm of clamped wrist-target error during screenshot stalls.
That contradicts using its headless 0.40 cm mean error as visual acceptance.

C16 r01 improved face readability, but its rosette resembled separate beads.
The first cloth patch still reached 11.83 times rest length in the recording.
The r01 recording failed the handle-lag limit despite completing all care actions.
These images, logs and the first editable cast are retained in the review folders.

C16 r02 flattened/extended the rosette petals and reduced excessive star/eye
emission. The cloth's headless worst stretch fell to 1.0831 with zero resets.
The r02 recording was deliberately stopped after identifying a harness problem:
screenshot readback could skip the entire 0.2-second E press window. R03 issues
that discrete input at least once. The interrupted recording remains preserved.

R03 adds post-physics presentation. Its headless care run completed with four
physical grabs, no fall recoveries, maximum cloth stretch 1.0710 and zero resets.
Read the separate real-time rendered and packaged logs for their results; this
document is not a substitute for those runs.

The final real-time rendered care run also passed: four grabs, three stars,
three released worries, an open crossing and a completed morning. Maximum
wrist-target clamp error was 15.91 cm, mean 2.04 cm; this is not perfect visual
hand contact. Cape maximum stretch was 1.0730, with one reset. The fixed-time
front-view recording passed too (1.0805 stretch, zero resets).

The C16 Windows package passed the care loop, camera checks and all 990 route
waypoints / twelve destinations, with zero fall recoveries. Its cloth ratio
was 1.0743 with one reset; wrist-target error was 17.85 cm peak and 2.29 cm mean.
Seven separately labelled native motion clips accompany the build. The first
two packaged close views were inspected. None of these results accepts the art.

Motion recordings use fixed simulation time to avoid screenshot readback changing
the movement being filmed. A separate rendered care run without screenshots uses
normal frame timing. Recordings are animation-review evidence, not performance
benchmarks. Camera and twelve-destination traversal tests remain distinct from
physical-controller testing and unrestricted exploration acceptance.

## Remaining full-goal work

- The environment is still far below the requested art target: tree canopy/bark,
  ground and paving, terrace construction, planting, border tissue and gate
  interiors need substantial authored work. The reference composition is not met.
- Thought characters are more readable, but reference fidelity, expression range,
  motion transitions and VFX still require further visual iteration.
- Character costume surfaces, silhouette, contact on sharp direction changes,
  full locomotion quality and placement animations are not accepted.
- Cape scenery/self collision are not implemented. This is a local body/thought
  cloth solver, not a claim that every scene element is physically simulated.
- Twelve tested destinations do not prove every intended part of the garden can
  be explored. Physical controller and complete occlusion testing remain open.

## Technical references checked

[Epic physics sub-stepping](https://dev.epicgames.com/documentation/en-us/unreal-engine/physics-sub-stepping-in-unreal-engine)
explains the variable-frame / physics-step distinction. The installed UE 5.8
MovementComponent and PhysicsHandleComponent source established actual tick order.
No global physics settings were changed merely to hide capture stalls.

[Nintendo GDC session](https://www.gdcvault.com/play/1024562/Change-and-Constant-Breaking-Conventions)
was located as a primary art/design reference. Its listing was inspected; this is
not a claim that the full video was watched or its visual quality reproduced.
