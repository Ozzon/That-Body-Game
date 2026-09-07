# C14 connected brain garden — 7 September 2026

Native Unreal Engine 5.8 Windows checkpoint. C13 is preserved. This packages the current art and interaction work for playtesting; it does not claim the requested final Breath of the Wild quality.

## Changes

- Reshaped the northern meadow approach to approximately 22 degrees. Refit paving and small plants to the ground.
- Moved the three thought nests to separate positions 110 cm inside the authored brain boundary. Added clear, graded approaches and carved openings in the cortical volume.
- Replaced the detached thin rim with deeper cortical geometry and replaced the masonry gate frames with fused, sculpted tissue nests. The nests retain animated neural apertures.
- Rounded the paving silhouettes and gave their crowns coherent local slopes. Reworked small foliage normals to follow the leaves.
- Removed duplicate smoothing in the physical carrying target, revised the drive response, and kept hands attached to the moving thought's contact targets. Faster movement and cape cloth are retained.
- Expanded the exploration check from nine destinations to twelve, including all three nest approaches. The tree's raised root bed is treated as an obstacle with a clearance margin.

## Evidence and limits

The same native scripted care route completed with both grip implementations. At a fixed 60 Hz, measured mean wrist-to-contact error fell from 17.14 cm to 0.40 cm. The revised implementation still had a 29.07 cm peak on that run; sharp transitions need more work. These measurements exclude the first 0.6 seconds of each pickup and are not visual animation acceptance.

Before the final tissue import, the input-driven exploration run visited all twelve destinations with zero fall recoveries. Final packaged results are recorded in the adjacent build manifest. Collision-graph analysis and actual input-driven traversal are separate checks; neither certifies every square centimeter of scenery as walkable.

Art quality remains unfinished, particularly foliage, surface treatment, waterfall integration and landmark detail. Physical gamepad use and representative frame-rate testing remain outstanding. The cape has local body and thought collision, not arbitrary scenery or self collision. The separate heart and lung locations are outside this brain checkpoint.

The Evidence directory contains package checks, native screenshots, source snapshots and executable/container hashes.
