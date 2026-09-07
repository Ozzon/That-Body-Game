# C12 movement checkpoint — 7 September 2026

Requested delivery: a fresh playable Windows build immediately. This checkpoint carries the current movement and cape changes. The broader art, lighting and lower-garden access overhaul remains in progress.

## Changes from C11

- Normal movement: 430 → 560 cm/s. Hurry: 590 → 800 cm/s.
- Bright-thought carrying: 340 → 450 cm/s. Heavy-thought handling: 220 → 300 cm/s.
- Acceleration and braking tuned for the increased speeds; quicker contact-step cadence and camera follow with velocity look-ahead.
- Authored cape and embroidery deform through a 315-particle cloth lattice with stretch, shear and bend constraints, pinned shoulders, gravity, inertia, body clearance and held-thought collision.
- All C11 thought interactions and the core garden route retained.

## Limits

This is an immediate gameplay checkpoint. It does not deliver the requested final art quality or advanced lighting overhaul. Some lower planted areas remain disconnected from the main walking route. The cloth uses a custom local solver; it does not yet collide with arbitrary scenery or itself. Physical controller testing remains outstanding.

The delivered C11 package is preserved. Build-specific validation and source snapshots accompany C12 in its Evidence directory.
