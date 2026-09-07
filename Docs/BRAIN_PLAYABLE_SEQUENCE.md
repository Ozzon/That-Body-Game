# Brain garden: movement and encounter construction

The initial C06 paved layout was rejected. The replacement must be judged from a moving character camera, with no overview teleportation used as gameplay evidence. Generated key art is a visual target, not proof of build quality.

## Opening

Attention enters through a recognizable arched threshold. A bright thought floats three meters ahead in a quiet meadow. The open foreground route leads directly into the tree court; the player does not have to circle the entire organ while learning the first verb. The first approach is broad, gently graded and visible from the arrival. A separate longer promenade invites exploration toward the spring.

E physically gathers the star. Its face remains visible above the arms; hand targets, capsule clearance and collision filtering must agree. The character slows, raises both hands, and the star retains a little spring lag. The court has turning space around the tree and a distinct delivery position at the front roots. A delivery produces a root-to-crown glow response.

## The two invitations

From the tree, the blue spring is one branch; the violet nest glade is the other. The spring has a water crossing and the second bright thought. The glade presents three behavior silhouettes: a nimble light wisp, a dense heavy cloud, and a coiled amber knot. The third bright thought is within the glade. Most ground is moss, garden beds and soft earth; masonry is limited to crossings, stepping slabs and small interaction plinths.

The wisp teaches one directed swat. It moves under a physical impulse and dissipates. The knot recoils and drifts back until three readable pushes loosen it. The heavy cloud is physically dragged along the broad east garden route. The lotus first calms the current: holding E causes a timed petal response and visibly slows drift. A carried object can still be dropped at the lotus; focus cannot trap the player into holding an object forever.

## Return and care response

Three bright deliveries, the focus action, and the three thought behaviors restore the garden. A newly visible root crossing cuts across the front of the location from the release garden to arrival. It must have real collision and an unobstructed path, including at both landings. The morning completes only after returning home. A test that merely sets the completion flags is invalid.

## Movement-specific checks

- Native CharacterMovement capsule uses the visible floor triangles, slopes and steps; no position-only walking.
- Care paths are at least 5.1 meters wide before vegetation, with a 68 cm character capsule. Planted beds do not intrude into the central 3.6 m walking ribbon.
- Test carrying through the first crossing, circling the tree, approaching the spring thought and dragging the cloud through the east turn.
- Test physically displaced thoughts near water, walls and player contact; retain a recovery location for accidental falls.
- Camera orbit and zoom must preserve Attention's visibility. Fade scenery using the actual camera ray, retain interactive objects, and never hide the floor.
- Run all actions through keyboard input and collision. Then inspect recorded real play for readability, pacing, contact quality and visual response.

## Actual implementation status

Native character, rigid-body thoughts, physical handle, action poses, camera controls, event particles, scene-lighting setup, care states and an automated input route are written. They require successful import, runtime validation and visual review. The whole brain level is not finished or art approved. The first C06 source render did not meet the required fidelity or garden composition and is archived as rejected.
