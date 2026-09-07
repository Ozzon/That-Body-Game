# C11: whole-location corrective rebuild

The requested target remains Breath of the Wild quality across the art departments. C11 is a candidate under construction. Neither shader compilation nor a gameplay smoke test establishes that target. C10 remains preserved at `Builds/BrainGameplay-C10-20260907`.

## Playable checkpoint delivered 7 September, 15:58

`Builds/BrainAdventure-C11-20260907/Windows/ThatBodyGame.exe` is the packaged Windows Development build. The owner asked to prioritize a playable level with Attention, thoughts, pushing, pulling and care interactions. The package is a gameplay checkpoint; the overall visual-quality goal remains active.

The packaged keyboard route passed all 13 legs: three stars delivered, lotus focus, physical heavy-cloud carry and release, wisp brushing, persistent-thought pushing, unlocked root bridge and return to arrival. It used CharacterMovement and Chaos through actual PlayerController input, with four physical grabs and zero fall recoveries. Packaged camera input passed orbit, tilt, pan, zoom, overview, reset and controller-axis injection. A physical controller was not tested. The default packaged map also rendered four review views and exited cleanly.

Evidence, binary hashes, source snapshots, screenshots and reports are beside the Windows folder in `Evidence`. The earlier C10 package remains unchanged.

## Remaining work after the playable request

The native collision audit still reports inaccessible samples in the lower planted gardens and part of the spring terrace. New ramps are modeled, but that is not proof of complete access. The core interaction route passes around the spring pools; every garden area is not yet verified. Investigate ramp floor hits and long carrier side faces rather than loosening the audit thresholds. Final art remains unaccepted: terrace walls, paving composition, organic nest fidelity, ground cover, anatomical mantle detail and animation polish still need work. The generated limestone and botanical moss images are real imported surface assets, not proof of final art quality.

Recent fixes: gates share border coordinates with encounters; ordinary CharacterMovement push amplification is disabled while physical thought interaction remains; route paths avoid the actual modeled pool banks; the mantle includes the root-return corridor; correct mouse events and explicit sensitivity are used; a persistent thought deferred before lotus focus returns after 30 seconds. That return branch is implemented but has not yet received a dedicated input test.

## Reference and route logic

Compare the native whole-location and traversal-camera captures with `Docs/References/ref-384.png` and `Art/BrainCraft/Concept/Brain-Location-Key-Art.png`. The important relationships are a substantial living brain envelope, designed planted terraces, fitted paving, elevated water garden, a readable central awareness tree, distinct thought encounters and a lower release garden. Three portals in different destinations override the generated concept's row of three portals.

The scene uses five connected garden districts at 1.4, 3.3, 5.2, 9.5 and 11 metres. Portal locations come from `Art/BrainCraft/Source/C11/portals.json`, with each complete assembly transformed once. Native bounds are recorded after import. Character handling lanes retain the broader collision carrier while stone paths indicate the intended traversal line. Heights are sampled from that carrier for the paving. Bridges have continuous support beneath their fitted stones.

## Implemented source changes awaiting native review

- Replace environment geometry with a complete C11 scene: fitted closed paving, retaining courses and coping, garden-wide evergreen substrate, rooted grasses, leaf rosettes, flowering plant groups, separate gateways, terraced spring basins, waterfall sheets, raked sand, five branching garden trees, a curved shelter and broad root crossing.
- Remove the internal tissue wedges and duplicate arrival gateway. The new cortical mantle is confined to the outside envelope. Its fidelity still requires visual judgement.
- Replace four thought bodies and their faces. Materials distinguish tissue, masonry, worn stone, sand, wood, foliage, water, wool, linen, leather and luminous thought bodies.
- Reduce unshadowed fill lighting, retain a single dominant warm key, introduce cooler ambient fill and local source lighting. Use physically lit shading, two-sided foliage transmission, tissue subsurface response, roughness variation and surface normals. The cel treatment organizes light values without replacing physical shading.
- Disable automatic orthographic plane shifting, which must be checked against the cropped overview from C10.

## BOTWRECKED reuse

The owner explicitly authorized reuse of item handling and animation mechanics. Read-only source: `C:/Users/Gamescom 2023 #1/Documents/BOTWRECKED/Source/Botwrecked/Core/BWGait.h`, `BWBipedGait.h/.cpp`, `Robot/BWRobotPawn.cpp`, and `Robot/BWRobotMining.cpp`.

The distance-based gait math, contact-driven stepper and two-segment limb solver are copied under `Source/ThatBodyGame/Animation`. The stepper's floor trace is adapted to this game's dedicated ground channel. It preserves a planted contact through turns, retargets early swing, eases lift and plant, and derives torso rhythm from actual steps. The robot project itself is unchanged. Body lean responds to acceleration, turn rate and load. The heavy thought uses lower acceleration and a low physical hold; hand targets follow the actual thought surface.

This is procedural animation adapted from the powered robot system. It is not a claim that a finished skeletal animation library was imported, or that visual animation quality is accepted.

## Research used

Nintendo describes Breath of the Wild's image as layers of foreground, middle distance, background, time and space, with art and rendering developed together. The session materials are not public, so this is art-direction evidence, not access to Nintendo's exact shader. [Nintendo presenters at CEDEC 2017](https://cedec.cesa.or.jp/2017/session/VA/s58eed7182c81b.html).

Epic's documentation distinguishes physical material response from style and describes physically based materials as useful for non-photorealistic work. [Physically based materials](https://dev.epicgames.com/documentation/en-us/unreal-engine/physically-based-materials-in-unreal-engine). Two-sided foliage transmits light through thin leaves and avoids the black undersides produced by ordinary opaque shading. [UE 5.8 shading models](https://dev.epicgames.com/documentation/unreal-engine/shading-models-in-unreal-engine?lang=en-US).

## Required evidence before handoff

Native material compilation and portal bounds; fixed whole-location and close captures; traversal footage with visible pickup/carry/push/pull/plant contacts; complete keyboard gameplay loop including the root return; camera and occlusion checks; packaged launch. Physical controller testing remains separate. Any failed visual comparison keeps art acceptance false. Overall Zelda quality remains unproven until every art department meets the requested standard in the actual game.
