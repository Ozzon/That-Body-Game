# That Body Game — A Living Adventure

Prepared for the owner and the game's art, level and gameplay implementation. 7 September 2026. Native Unreal Engine 5.8. Research and proposed production direction, with explicit distinctions between reference art, existing models and unbuilt designs.

## The decision

Build the body as a connected world of complete locations. An organ is recognizable through its silhouette and internal structure, memorable through a major landmark, and playable through a short journey that changes the place. The same tactile care vocabulary works everywhere. Anatomy supplies the organizing structure; fantasy turns it into welcoming terrain, architecture and characters.

The owner's latest instruction expands the earlier six-station design into full locations for the visible body. Preserve the accepted heart model. Treat the current brain and lung studies as rejected evidence. A successful mesh export or connected navigation mask does not make those studies visually complete. The next review must show an actual modeled player journey against the relevant Figma image, including the organ's changed state after care.

## What the references actually require

The FigJam package contains several visual families. Selecting isolated attractive props from all of them produces the present incoherence. Establish a hierarchy: the accepted heart is the material and sculptural baseline; brain images 358 and 384 establish folded tissue and terraced garden geography; images 275 and 307 establish thought habitats and the central awareness tree; image 354 establishes lung branching and alveolar gardens. Image 330 contributes wind-travel ideas. Architectural heart image 309 supplies small mechanical and planted details, while the approved heart shell remains authoritative. These are observations from the owner's local package, not external medical claims. [F1, F2]

In the brain, broad cortex folds must continue into the edges of the terraced garden. The silhouette needs two substantial cerebral masses, a fissure and a smaller cerebellar region. The current repeated rim around an oval floor is a large-form mismatch. The tree needs a fused root/trunk base, a deliberate crown, textured bark channels and clustered light-bearing foliage. Its roots meet soil and masonry; they do not sit as separate tapered sticks on top of a disc.

In the lungs, the airway hierarchy determines the geography. A large trunk divides into a few major branches that visibly terminate in flowering exchange gardens. Lobe asymmetry, coral outer tissue, pale blue airways, pink membranes and the moving diaphragm form a single composition. Empty mint compartments and scattered tubes do not meet that source.

The reference detail is concentrated at meaningful places: a nest mouth, a valve hinge, a bridge landing, an open book, a flower's center. The clear floor between them provides room to move and makes the detail valuable. Detail also includes the way surfaces join, catch light and move.

## What the game research changes

Hob's lead designer describes exploration routes that unlock shorter returns, with shared visual cues for recurring interactions. This supports a two-part structure here: first discover an organ's districts, then use its restored express route during daily events. [G1, G2]

Cocoon's creators tie terrain to the movement mechanic: bridge-making belongs in a landscape with gaps and height. Its art director describes structures that appear grown from their surrounding material. For this project, lung wind routes should require shelter, branching and elevation; heart valve movement should structure chambers; brain thought currents should shape crossings and overlooks. A shared material treatment keeps these places in one body. [G4, G5]

Cocoon's arrival framing puts useful information in view immediately. Keep the user's full orbit camera, but author a default view that already shows Attention, the immediate route, the organ landmark and the first care opportunity. Rotation should reveal optional discoveries. [G6]

Nintendo's Link's Awakening art director explicitly balances rich diorama craftsmanship against the imagined small character's scale. Tunic's designer likewise describes a boundary between unfinished and excessive detail. Our practical rule is to review the walking surface and landmark hierarchy at the actual player camera, not at a close modeling zoom. There is no sourced universal asset-count or detail-percentage rule. [G17, G9]

Double Fine derives level dimensions from character movement and distinguishes pretty art tests from locations integrating movement, quests, audio, art and effects. The organ review therefore requires a continuous player journey and a visible care consequence. Mesh count, triangle count and import success remain technical evidence only. [G14, G15]

Death's Door's forest spirits show how a few specific idle reactions can make a place feel inhabited. Its action feedback coordinates weight, timing, sound and visuals. Give an air keeper a small inflation gag, a blood courier a polite queue reaction and a heavy thought a struggling walk; do not fill the body with constant particles. The Last Campfire supports care itself as an adventure action that opens new places. [G10, G11, G12]

## Whole-body geography

Use five connected regions. The crown contains the brain and cerebellar gardens. The resonance pass contains throat and nearby tempo lanterns. The chest contains the heart between two lung conservatories and a sheltered thymus cloister. The digestive crossing links stomach, liver, pancreatic gallery, gallbladder and spleen. The lower region contains twin kidney springs, signal observatories, intestinal neighborhoods, colon promenade and the quiet bladder reservoir.

Keep four anatomical flow systems separate: air runs through throat and branching lungs; blood travels body to right heart to lungs to left heart to body; food travels through esophagus, stomach and intestines; urine travels from kidneys through paired ureters to the bladder. Attention's light bridges form a fifth, explicitly fictional walking network. Their job is player navigation, and they may follow or cross real structures without pretending to be biological corridors. [A2, A3, A5, A9, A10, A14]

The first connected adventure is diaphragm → lung grove → heart → brain tree → liver recovery → return to heart. Each location has a self-contained exploration circuit. After its first restoration, a short return path keeps the daily care loop practical. The atlas shows organ silhouettes and major Attention connections; it suppresses local props, particles and minor flow branches. The local camera presents the full environment and its inhabitants.

## A consistent journey, different in each place

Every location has seven authored beats: arrival reveal; a visible need; a choice between an obvious route and a curiosity; one signature traversal; a tactile care action; a physical change; and a return shortcut. This is a design synthesis from the cited games, not a claim that every source follows the same seven-step formula.

Do not give every organ a unique control scheme or a disconnected minigame. Reuse move, tap, hold, pull, carry, place and release. The organ changes the situation: pulling a diaphragm fills air gardens; holding a lotus slows thought currents; placing a burden at the liver starts a visible processing sequence. The player learns the body by reading these differences.

First exploration should support curiosity without punishment. Repeat events use the restored routes and already learned interactions. An optional lift or timing challenge has a stable walking alternative. Stress can change wind, pacing and carrying weight while preserving readable routes and recoverable mistakes.

## Space and camera targets

The current Attention figure is roughly 1 m wide and 1.5 m tall in the game's enlarged architecture. Use proposed primary path widths of 3.6–4.5 m, bridge widths of at least 3.6 m, and care courts 7–10 m across. These are design targets derived from the current character, not anatomical measurements or established industry standards. Verify turn space while carrying, two-way passage with an NPC, bridge landings and every doorway in the actual model.

Use a local orthographic view showing about 30–42 m across at normal play, with adjustable pitch, full orbit, zoom and pan. Frame each arrival individually. Inspect at least entrance, active care and return views, then rotate to the reverse angle. The complete organ overview is a separate composition from the player view. The whole-body atlas is a navigation view rather than a quality proof for tiny organ details.

Fade only scenery that blocks the player: foreground cortex, canopy sections and high decorative structures. Keep care targets, gates and interactive creatures visible. Build the scene so fading is occasional. Low railings, deliberate sightline gaps and correctly scaled canopies solve many occlusion problems before a shader is involved.

## Modeling and surface treatment

For each organ, make a silhouette model first: organ mass, two or three major landforms, hero landmark and player. Match this to its Figma reference at the same view. Then construct the connected floors, retaining walls, gates and bridges. Model their joins before adding small decorations. A bridge needs a continuous deck, abutments that meet the bank and a navigable landing; a terrace needs a real retaining edge and an intentional ramp.

Use primary, secondary and tertiary forms. Primary forms establish the organ and district. Secondary forms include large folds, roots, lobe seams and significant masonry. Tertiary forms include bark grooves, restrained paving joints, leaf veins and tiny tissue grain. Tertiary detail should never be used to disguise a primary-form mismatch.

The material family is soft, tactile and welcoming. Tissue has broad painted color and a mild wet sheen. Dry paths and soil are matte. Bark has directional ridges and darker recesses. Membranes and water carry localized reflection. Light is concentrated in useful resources and restored landmarks. The body should retain rich pink, violet, teal, amber and sage color families without every surface becoming equally bright. Stylization can deliberately depart from literal physical material values. [G18, G19]

Make the major meshes editable and individually meaningful: cortex masses, terrain districts, tree trunk, canopy sections, bridges, gates, water and care landmarks. Preserve source geometry and the accepted heart. Use textures and vertex paint to support forms, not to draw missing architecture onto flat geometry. Add moving joints and deformation only after their rest shapes and attachment points are correct.

## Attention and the inhabitants

Keep the sage hood, warm face and short cape from reference 379. Attention feels attentive through anticipation and response: a short lean before hurrying, arms reaching toward a bright thought, a compressed landing, an oversized parcel that changes the gait, and a hood that catches a lung gust. Wacky movement must remain predictable at the feet.

The motion sequence for care is anticipation → contact → response → recovery. A pull visibly tensions the diaphragm before it descends. A valve rebounds after a tap. A tree receives a thought through its roots before light reaches the leaves. Each action has a clear sound onset and an unmistakable completion pose. These timing choices are proposed implementation rules informed by the cited action-feedback practice. [G10]

Use a small cast with distinct roles: blood couriers, air keepers, thought creatures, digestive helpers, filter keepers and guardian trainees. Each has one signature idle behavior, one reaction to Attention and one care response. They occupy designed courts or alcoves; they do not wander into every bridge or obscure the next destination. [G11]

## Anatomy, metaphor and uncertainty

The design deliberately enlarges microscopic structures into architecture. Brain folds, lung branching, heart chambers, stomach curvature and kidney shape remain recognizable. Garden soil, reading furniture, leaf lifts, light bridges and carried heartbeat tokens are fiction. Preserve that distinction in design language.

Some claims in design v11 are not supported as literal physiology: adrenal glands do not manufacture a vagal hormone, cortisol clouds are not a universal waste item, and theta waves do not establish a guaranteed mechanism for permanently dissolving thoughts. Preserve the intended play with calm signals, stress mist and clarity ripples. These terminology corrections do not require a warning-heavy game interface. [A11, A15]

The research supports organ topology and functions, not exact room dimensions, prop density, camera pitch or puzzle timing. Those remain hypotheses to test. Detailed anatomical plates are still needed when producing renal pyramids, laryngeal structures and the spleen's internal landmarks. Sources with unavailable full pages or abstract-only access are identified in the ledger.

## Production order and honest status

The approved heart shell is retained. Current brain C01–C03 and the first full-body lung models are below the reference bar. Their construction and navigation experiments can inform later work, but they are not final art. The location designs in this atlas are proposals; most are not built yet.

First finish the brain's actual reference-matched landforms, tree, three strong destinations, thought behavior and a physically changing shortcut. Review the arrival and close care views before expanding. Next build the lung conservatories around one proven branch–grove–wind interaction. Then populate the approved heart with its chamber-specific flow and valve journey. Connect those three into a complete playable care circuit. Extend the same construction and review standard through the digestive and recovery locations.

A location reaches the art baseline only when its silhouette, layout, hero asset, material distinction, lighting and prop placement correspond to the chosen Figma image at player scale. It reaches a playable checkpoint only after real input traverses its route, performs the care actions, demonstrates the state change and returns through the shortcut. Art acceptance belongs to the owner; technical validation cannot substitute for it.

## Research completion

The two independent research lanes completed discovery and targeted follow-up. The coordinator inspected the high-resolution local package and spot-checked the most consequential developer and anatomical claims. Evidence converges on the same correction: build distinctive spatial journeys, connect their parts carefully, and concentrate craftsmanship at the places the player reads and touches. Further broad inspiration searches are unlikely to alter that conclusion. The remaining uncertainty is in the models and play experience and must be resolved there.


# Complete location designs

## Brain — The Awareness Garden

Enter a living, folded landscape where thoughts have homes and the great golden tree grows through everything you care for.

**Size:** Proposed 48 × 55 m shell; 34 × 37 m usable garden; 3.6–4.2 m paths.

**Anatomy:** Two folded hemispheres, a readable central fissure and a smaller cerebellar district. The garden occupies terraced cuts within those volumes. A thin decorated ring around an oval floor fails the silhouette.

**Arrival:** The crown landing frames Attention low in the foreground, a stream crossing in the middle, and the tree beyond. One nearby sleepy thought demonstrates the first action. A distant glowing nest introduces a later destination.

**Care:** Tap small thoughts, catch bright thoughts, carry bright thoughts to the tree, and drag heavy thoughts to the release edge. Hold the focus lotus to slow a local current. A recurring thought becomes a short root-tracing puzzle after the garden settles. These are variations of the shared care verbs.

**Change:** Three visible stages: dim bark with curled leaves; warm channels spreading up the trunk; branches opening, nearby flowers turning toward the tree, and a root bridge completing the return route. The whole tree remains the same authored asset across states.

**Shortcut:** A 3.8 m root crossing links the focus terrace to the tree court after care. The crown-to-tree delivery route remains available throughout. Exploration is rewarded without making urgent deliveries repeat the entire circuit.

**Material:** Rose cortex, cool violet recesses, moss green gardens, amber stone and luminous gold foliage. Soft tissue sheen differs from matte soil, rough bark and reflective water. Ground stays quieter than the tree and interactive thoughts.

**Life:** A thought peeks out of a nest, notices Attention and retreats. Bright thoughts bob toward the open palm. Heavy thoughts drag their feet; the cape pulls backward while carrying them.

**Must Fix:** Current C03 still has repeated rim folds, a dominant paving circle, weak terrace construction, unfinished paving joins and insufficient material distinction. It is a study, not reference-matched final art.

**Journey:**
1. Crown landing and memory meadow: meet a drifting bright thought beside the first bridge.
2. Reading garden: follow its trail past an open-book lectern and embedded shelf niches; find the first thought nest.
3. Synapse pools: cross a real arched bridge and redirect a gentle thought current through two visible gates.
4. Focus terrace: hold the lotus until its petals settle; the current slows and reveals a root crossing.
5. Worry hollow and release edge: a heavy thought requires a deliberate short carry to the rim.
6. Return to the central tree; its roots unfurl a direct garden shortcut.

**Modeled assets:**
- Two asymmetrical cortical masses with broad primary folds and smaller branching sulci; exposed tissue turns into retaining walls.
- One mature tree: fused trunk/root junction, six designed major limbs, dense but readable leaf clusters, bark grooves and luminous inlays.
- Three distinct thought nests recessed into cortex, each with a mouth, curled rim, and current outlet.
- Three tiered gardens, one reflective pool, a continuous stream, fitted bridge abutments and paving thresholds.
- Reading furniture, a sculpted focus lotus and a cerebellar overlook, each built as a destination rather than a floating marker.

Sources: A1, G1, G4, G6, G14

## Heart — The Pulse House

A warm four-room workshop that beats around you. Small blood couriers queue at valves, the floors gently pulse, and your care brings the whole house into rhythm.

**Size:** Keep the approved Model A shell and four-room proportions. Target at least 3.5 m clear crossing routes and 6 m turning courts around care objects.

**Anatomy:** Four chambers, four directional valves, two circulation loops, a muscular septum and a strong aortic exit. Preserve the accepted model's existing arches and silhouette. A central Attention gallery is a deliberate fantasy connection; blood circulation remains separate.

**Arrival:** The first arch reveals a courier channel leading toward the pulse dais. The dais, doorway and player are visible together. The aortic arch is a landmark seen above the rear wall.

**Care:** Deliver breath to settle the rhythm. Tap the pacing valve with a clear anticipation, contact and rebound. Catch the produced heartbeat. Blood courier gates respond to the rhythm while the player always has a stable dry route.

**Change:** Racing double beats become an even pulse. Valve leaflets synchronize; couriers stop bunching at gates; warm light travels around the chamber walls. Restoration opens a short return arch to the central gallery.

**Shortcut:** Central gallery links the four rooms for repeat care. The first journey follows the chamber sequence; subsequent breath delivery reaches the dais directly. The main path never requires waiting for a narrow timed valve.

**Material:** Terracotta muscle, cream valve edges, burgundy channels and gold care light. Oxygen-rich and oxygen-poor couriers use two shades of red plus different light accents; blue is an optional diagram cue, not literal blood color.

**Life:** Couriers politely shuffle forward, wobble when the beat surges and wave when their queue clears. The room breathes through small coordinated motion rather than shaking the camera.

**Must Fix:** The accepted shell is the baseline, not a finished adventure. Its rooms still need distinct functions, valve assemblies, flow channels and a tested continuous journey.

**Journey:**
1. Receiving court: watch tired couriers arrive in a cool crimson channel.
2. Right pump room: open a valve using a gentle rhythmic tap and release the outgoing queue toward the lungs.
3. Return court: oxygen-carrying couriers arrive with warm lantern packs; place a breath at the pacing station.
4. Power chamber: keep a short comfortable rhythm, catch a heartbeat and operate the aortic departure lift.
5. A side recovery alcove introduces carrying a heavy stress cloud to the liver.

**Modeled assets:**
- Approved four-room shell, untouched as the accepted source.
- Valve assemblies with modeled flexible leaflets, an anchoring ring, hinge folds and distinct opening silhouettes.
- Low blood channels with continuous banks and bridges where the player crosses.
- A pacing flower integrated into its dais, a modest aortic lift and a recessed recovery alcove.
- Three blood-courier silhouettes with expressive squash and backpacks; sparse queues, no field of decorative red beads.

Sources: A2, G1, G10, G14

## Lungs — The Breathwood Conservatories

Explore two warm pink conservatories where branching blue airways feed flowering air gardens. Wind becomes a playful means of travel, and a deep breath visibly opens the landscape.

**Size:** Proposed 34 × 25 m per lung, with three right-lung districts and two left-lung districts; 4 m main routes, 7–10 m grove courts.

**Anatomy:** The right lung has three lobes; the smaller left lung has two and a cardiac indentation. One airway hierarchy splits into bronchi, smaller branches and terminal alveolar clusters. The diaphragm is the moving foundation below both lungs.

**Arrival:** From the diaphragm terrace, see the two lung entrances and one clear airway fork. A hanging leaf bends toward the active route. The first alveolar grove is visible beyond a broad bridge.

**Care:** Hold and release the diaphragm; turn a sail with a tap; hold a closed flower until its motion follows the breath; carry the produced breath to the heart or brain. A heartbeat deposited at the receiver strengthens the next two garden breaths.

**Change:** Airway illumination advances from trunk to branch to flower. Alveolar cups swell, leaf sails turn, a lift rises, and the sound opens from muffled air to a soft chord. No random wind particles obscure the walking surface.

**Shortcut:** Restoring the upper grove deploys a broad light bridge back to the diaphragm. Repeat breath collection is close to the hub; optional grove routes remain full places to explore.

**Material:** Coral tissue, translucent-looking pink air cups, cool blue airway interiors, sage leaves and warm ivory paths. Keep shininess concentrated on membranes and water-like breath light.

**Life:** An air keeper briefly inflates into a balloon and squeaks back down. Alveolar flowers lean in sequence with the gust. Attention's hood catches the breeze before a lift rises.

**Must Fix:** The current mint compartment meshes do not correspond to the lung references. Replace their internal geography and hero assets; recoloring or adding scattered tubes is insufficient.

**Journey:**
1. Diaphragm terrace: pull the soft handle; the lung canopy expands and the first breath forms.
2. Lower exchange grove: help a closed alveolar flower open and meet its tiny air keeper.
3. Bronchial fork: turn a leaf sail to route a gust into one branch.
4. Upper wind gallery: ride a short rising leaf platform to an overlook; a stable ramp remains available.
5. Sheltered grove: catch a breath, then open a return bridge to the diaphragm.
6. The opposite lung varies the lesson with two larger groves and an alternating cross-breeze.

**Modeled assets:**
- Asymmetric coral lung shells with readable lobe seams and spacious dry interiors.
- One purposeful branched airway sculpture per lung, with resolved junctions and occasional cartilage bands.
- Five distinct alveolar groves: hollow, soft air-cup clusters on branching stalks; varied large/medium/small forms, not uniform grapes.
- A diaphragm platform with a deforming membrane, rooted pull handle and visible perimeter attachment.
- Wind sails, one short lift per lung, fitted bridges and planted sheltered ledges.

Sources: A3, A4, G4, G5, G6

## Stomach — The Supper Cavern

A cozy mixing cavern with folded walls, soft rolling machinery and comically overstuffed food parcels. Dinner arrives with a little procession.

**Size:** Proposed 34 × 27 m; a 5 m dry rim route surrounds a lower moving basin; three 8 m work bays.

**Anatomy:** An asymmetric curved sac, broad fundus/body, inner folds and a narrowing pyloric outlet. Food continues into the small intestine. Glucose pickup at this location is a gameplay shorthand for the digestive system.

**Arrival:** Enter on an upper balcony as a parcel slides down the esophageal chute. The warm mixing bowl below, dry rim route and distant outlet are immediately legible.

**Care:** Carry and place food parcels, hold a kneading pad to assist mixing, and tap the outlet when the parcel is ready. A heartbeat temporarily helps the fictional preparation machinery. No additional combat or crafting inventory.

**Change:** The basin's motion settles, prepared parcels become compact warm bundles, and the outlet unfolds. The walls stretch subtly with fullness; the stable walking shelf stays stable.

**Shortcut:** Opening the outlet creates a direct lower-body connection. A fold arch returns to the meal receiving point in a few seconds.

**Material:** Warm peach tissue, toasted amber ridges, cream dry paths and a restrained glossy basin. Bright food colors occupy a small part of the image.

**Life:** A parcel hiccups, rolls back a little and gets caught by a patient helper. Attention uses both arms and leans backward when carrying something oversized.

**Must Fix:** Build rugae, working basin and outlet as connected architecture. An empty stomach-shaped floor with a glucose orb does not establish this location.

**Journey:**
1. Arrival balcony: receive a lumpy food parcel.
2. Preparation bay: set it down for gentle mixing; a soft floor wave advances the cargo.
3. Rugae promenade: follow a winding raised fold to a tasting nook and optional bright memory.
4. Pyloric gate: time one release to send prepared cargo into the intestinal route.
5. Return through a fold arch beside the arrival balcony.

**Modeled assets:**
- A custom curved shell with layered rugae continuing from wall into ledges.
- One low mixing basin, three molded preparation bays and a soft iris-like pyloric gate.
- Food parcels with changing shapes and a distinct ready state.
- A chute mouth, one small observation alcove and carefully fitted rim paving.

Sources: A5, A6, G5, G12

## Small intestine — The Ribbon Markets

A winding nutrient market where velvety villus gardens collect useful parcels. Each bend reveals another little working neighborhood.

**Size:** Proposed 45 × 39 m folded footprint; a continuous cargo channel with 3.8–4.5 m paths and three neighborhood courts.

**Anatomy:** A continuous sequence through duodenum, jejunum and ileum, with a folded absorptive surface. The enlarged villi become garden architecture; their relative microscopic scale is deliberately transformed.

**Arrival:** The stomach outlet opens onto a visible cargo stream. A single oversized villus cluster establishes the texture and scale before the route bends out of sight.

**Care:** Carry, place and hold a sorting flap; keep useful cargo moving toward its receiver. A gentle contraction provides a predictable moving walkway on an optional route.

**Change:** Villus gardens rise from a slumped posture, their tips light in sequence, and an outgoing energy stream becomes visible. The final fold bridge opens a repeat-delivery shortcut.

**Shortcut:** Two overpasses connect adjacent bends for Attention. Their distinct light material prevents them from being mistaken for the food route.

**Material:** Honey and peach tissue, soft velvet villi, ivory walking ledges and small golden cargo accents. The main route remains broad and low in visual noise.

**Life:** A villus helper stretches to reach a passing parcel, misses, then politely passes it to its neighbor. Attention surfs a gentle contraction with arms out.

**Must Fix:** Replace the generic winding trench with distinct arrival, sorting, absorption and departure neighborhoods. The continuous food direction must remain visible at every crossing.

**Journey:**
1. Duodenal junction: combine a prepared food parcel with the arriving digestive supplies.
2. Absorption gardens: direct useful parcels toward welcoming villus alcoves.
3. Ribbon bend: walk over a fold bridge while cargo follows the longer continuous channel below.
4. Dispatch court: send a warm energy token toward the liver's storage orchard.
5. Ileal gate: continue toward the wider, slower colon promenade.

**Modeled assets:**
- One continuous folded interior with three authored bends and clear upstream/downstream thresholds.
- Villus clusters with a designed growth direction and graduated size; no dense uniform spike field.
- Sorting alcoves, cargo flaps, warm dispatch pods and two bridge abutments.
- Subtle peristaltic deformation zones with stable landing shelves.

Sources: A5, A7, G1, G3

## Colon — The Reservoir Promenade

A slow, reassuring promenade through soft pouch-like rooms, where water is recovered and the bustle of digestion settles.

**Size:** Proposed broad outer digestive loop with 5 m paths and four distinct 8–10 m pocket plazas.

**Anatomy:** Wider segmented pouches distinguish the colon from the small intestine. It recovers water and electrolytes and has no villus carpet.

**Arrival:** The narrow intestinal route opens into a visibly broader chamber. Slow ripples and deep rounded wall pockets communicate the change in tempo.

**Care:** Turn a simple recovery flap, place a signal and hold the exit latch. The task is sorting and pacing, with a relaxed timing window.

**Change:** Water level lowers to a comfortable band, side channels brighten and a dry return shelf becomes available.

**Shortcut:** Outer promenade connects pocket plazas without forcing the player through every cargo gate.

**Material:** Muted warm terracotta, cream shelves, slate-blue water and amber recesses. Softer motion and fewer bright accents than the nutrient market.

**Life:** A sleepy helper opens one eye when cargo arrives and slowly shuffles a lever into place.

**Must Fix:** Give the colon its own width, pouch silhouette and slow rhythm; do not reuse small-intestine villi or the same narrow trench.

**Journey:**
1. Receiving pocket: observe the slower procession.
2. Water recovery terrace: direct useful water back toward a return stream.
3. Quiet crossing: traverse broad dry stepping shelves above the remaining cargo.
4. Departure court: coordinate a soft opening and return through the outer promenade.

**Modeled assets:**
- A wider segmented shell with four asymmetrical pouch chambers.
- Two recovery terraces, a stable upper promenade and a broad closing gate.
- Rounded cargo bundles, water return mouths and wall niches with a quiet sequence of landmarks.

Sources: A7, G4, G12

## Liver — The Amber Works

An amber processing orchard: parcels arrive, move through clear stages, and emerge as useful reserves or a lighter load. The place hums patiently even while Attention is elsewhere.

**Size:** Proposed 34 × 34 m lobed interior; three large districts around a 5 m loop; reserve courtyard about 10 m across.

**Anatomy:** A broad lobed mass under the right diaphragm. Lobular organization and sinusoidal flow inspire radial work gardens; storage and redistribution matter as much as processing. Bile and blood routes remain distinct.

**Arrival:** Two small incoming channels converge beside a receiving court. The reserve tree and its hanging golden pods are visible beyond the sorting terraces.

**Care:** Carry burdens here, place them at the receiving bay and hold to assist processing. Directly observe the parcel change; collect useful reserves instead of simply watching a percentage rise.

**Change:** Dark curled leaves relax, channels run clearly and storage pods gain warm cores. The receiving bay gains capacity through an unfolding terrace rather than more floating counters.

**Shortcut:** A lower service arch returns to the digestive crossing. The receiving bay stays near the heart-facing entrance for urgent cleanup.

**Material:** Burgundy exterior, amber interior terraces, warm gold storage pods and restrained jade bile accents. Rough work surfaces contrast with flowing channels.

**Life:** Patient liver helpers roll up their sleeves when a large parcel arrives. A reserve pod warms and drops gently into Attention's hands.

**Must Fix:** The current two-room bowl needs a full processing journey and an unmistakable reserve landmark. Decorative gold dots will not supply those roles.

**Journey:**
1. Receiving court: place the heavy stress parcel from the heart.
2. Processing terrace: hold a kneading surface to help a visible three-stage process.
3. Reserve orchard: collect a warm energy pod when a reserve release becomes available.
4. Dispatch well: send energy back toward the heart or brain.
5. Gallbladder side garden: discover the separate bile reservoir and return through the lower arch.

**Modeled assets:**
- A lobed shell with three raised lobular gardens, avoiding a uniform honeycomb carpet.
- A receiving basin, visible processing sequence, reserve tree and radial dispatch well.
- Thin, clearly connected channels with fitted banks and generous crossings.
- Separate bile-side doorway and small reservoir pavilion.

Sources: A5, A8, G1, G12

## Kidneys — The Twin Springs

Two bean-shaped water gardens where the pleasure comes from returning the useful things. Clear water trickles through sculpted terraces and small filtering groves.

**Size:** Proposed 24 × 20 m per kidney; 4 m circulation path; 7–9 m filter and collection courts.

**Anatomy:** Paired bean silhouettes, an inward hilum, filter units, return channels and a collecting outlet. Blood returns through veins; urine leaves through ureters toward the bladder.

**Arrival:** Enter the inner curve of the bean. A filter fountain is visible ahead, while two distinct channels leave it in different directions.

**Care:** Carry and place droplets, turn a recovery flap and hold the release lever. The second kidney reverses the route's emphasis while preserving the same control vocabulary.

**Change:** Filter petals uncurl, the returning-water channel brightens, and the collection stream clears. Sorting preserves something valuable instead of deleting everything labeled dirty.

**Shortcut:** A crescent gallery joins the entry and collection court. It also gives a quick connection to the signal observatory above.

**Material:** Muted plum tissue, blue-green water, pale mineral terraces and warm light at useful-return points. Fine water ripples carry detail; dry paths stay quiet.

**Life:** A tiny filter keeper inspects a droplet, polishes it and sends it home with a satisfied nod.

**Must Fix:** Replace the plain bean bowls with filter, recovery and collection landmarks; verify that all three paths are distinguishable in the default camera.

**Journey:**
1. Hilum court: watch a mixed parcel enter the filter garden.
2. Filter grove: separate a useful bright droplet from excess cargo.
3. Return terrace: guide the useful droplet back toward circulation.
4. Collection court: open the remaining route toward the bladder.
5. Upper overlook: climb to the nearby signal observatory and descend by a short slide.

**Modeled assets:**
- Two individually shaped bean shells with different interior layouts and inward hila.
- Sculpted radial renal terraces, one filter fountain and a loop of returning water per kidney.
- Separate collecting outlet and bridge thresholds; two color families of droplet cargo.
- A stable crescent gallery and an upper adrenal approach.

Sources: A9, G4, G5

## Adrenals — The Signal Watch

Two lively observatories that prepare the signals needed elsewhere. Their watchkeepers anticipate changes in the whole body.

**Size:** Proposed 12 × 12 m each, with nested terraces and a 4 m approach. Compact complete locations above the kidneys.

**Anatomy:** Small glands above the kidneys, with an outer cortex and inner medulla. Adrenaline dispatch fits the inner chamber; a calm-signal waystation is explicitly Attention's fantasy mechanism rather than an adrenal hormone factory.

**Arrival:** A short kidney ramp reveals a cap-like silhouette and a warm signal lantern visible from the lower-body crossing.

**Care:** Hold to prepare, carry to store, pick up to use. Keep the four signal appearances distinct by shape and motion as well as color.

**Change:** The observatory's lantern fills, the dispatch petals lift and the watchkeeper straightens. The nearby calm waystation softens its light and motion.

**Shortcut:** A short safe slide returns to the kidney's entry court; every stored signal remains reachable from the arrival terrace.

**Material:** Warm ochre caps, copper mechanisms, pale gold light and sage calm accents. The architecture shares the kidneys' rounded joints.

**Life:** A watchkeeper overinflates a bellows, sits on it to settle it, and presents the finished signal with both hands.

**Must Fix:** The current small caps and glowing orbs need an arrival, preparation action, storage place and return route to feel like a location.

**Journey:**
1. Outer terrace: gather a ready signal.
2. Inner dispatch room: hold the bellows until the lantern fills.
3. Reserve balcony: place a signal in one of three visible nests.
4. Release balcony: send a signal toward the body and open the quick slide back to the kidney.

**Modeled assets:**
- Capped outer shell with a distinct nested inner chamber.
- Bellows, a three-nest reserve balcony and one strong lantern silhouette.
- A soft slide/ramp and two clearly differentiated signal dispensers.

Sources: A11, G10, G12

## Throat — The Resonance Pass

A resonant passage where air, voice and food share a neighborhood but follow distinct routes. Crossing it feels like stepping through a softly sounding instrument.

**Size:** Proposed 25 × 16 m vertical transition; 4.5 m main Attention route, separate air and food structures.

**Anatomy:** Separate tracheal and esophageal paths, with a coordinated swallowing junction and a voice region. The esophagus continues behind the airway toward the stomach.

**Arrival:** From the heart, see a cool airway gallery ascending toward the lungs' fork and a warmer food chute descending toward the stomach.

**Care:** Hold a resonant fold, carry a parcel and place it at the correct junction. An optional short timing challenge enriches the pass without blocking urgent organ care.

**Change:** The tense passage opens, the sound broadens and the main light bridge stops quivering. Food and air animations remain clearly separated.

**Shortcut:** The principal Attention ascent always connects heart, lung fork and brain. Optional voice and thyroid loops reconnect to that spine.

**Material:** Cool teal airway, warm peach food passage, cream connective tissue and a restrained gold voice accent.

**Life:** Attention's hood vibrates with a low note; a tiny echo comes back a beat late and makes the character look over their shoulder.

**Must Fix:** The current hub and connector need a recognizable pass with purposeful air/food separation. Do not fill this gap with miscellaneous tubes.

**Journey:**
1. Resonance court: touch a chime-like fold and hear the passage respond.
2. Voice bridge: hold a soft note to steady a trembling span.
3. Swallow junction: wait for one clear gate cycle and deliver a parcel to the food route.
4. Crown ascent: continue to the brain while the return bridge remains in view.

**Modeled assets:**
- Two distinct passage structures with a readable shared junction.
- A sculpted pair of vocal folds, cartilage-like supports and a swallowing gate.
- One broad light bridge, one sheltered resonance alcove and integrated crown threshold.

Sources: A14, G5, G6

## Thyroid — The Tempo Lanterns

A paired lantern conservatory that gives the body's daily rhythm a visible home.

**Size:** Proposed 14 × 10 m paired galleries with a 3.5 m isthmus crossing.

**Anatomy:** Two thyroid lobes beside the trachea connected by an isthmus; follicular structures inspire the small lantern chambers.

**Arrival:** Two unequal warm silhouettes flank the cool throat route, with the connecting gallery plainly visible.

**Care:** A short carry-and-place sequence balances two fictional signal lanterns. Reuse the same input language as the main organs.

**Change:** Alternating lantern pulses settle into a common tempo; the central gallery gently unfurls.

**Shortcut:** An outer ledge returns directly to the throat pass after the first visit.

**Material:** Rose tissue, warm cream paths and peach-gold signal light. Its slower pulse differentiates it from the adrenal dispatch mechanism.

**Life:** Two keepers accidentally nod out of time, notice each other and try again.

**Must Fix:** A contextual butterfly-shaped prop is insufficient under the expanded full-location brief. The paired galleries need usable interiors.

**Journey:**
1. First lobe: meet a sleepy signal keeper.
2. Isthmus crossing: carry a warm token across the narrow gallery.
3. Second lobe: place it in the matching receiving lantern.
4. Upper window: see the throat open below and return by the outer ledge.

**Modeled assets:**
- Two lobe volumes joined by a narrow but usable isthmus.
- Large follicle-inspired receiving lanterns, small wall niches and one exterior viewing ledge.

Sources: A12, G4, G12

## Thymus — The Guardian Cloister

A small school for earnest, slightly clumsy guardian cells. The humor comes from practice and recognition.

**Size:** Proposed 16 × 12 m, with two training courts and a 4 m connecting cloister.

**Anatomy:** A two-lobed chest structure associated with T-cell maturation. Its depiction is age-dependent; the game's enlarged navigable version is a deliberate scale translation.

**Arrival:** A calm side arch above the heart reveals a practice court where a guardian is trying to recognize two different parcel shapes.

**Care:** Carry, place and briefly hold attention near a nervous trainee. No separate combat system or new equipment screen.

**Change:** The trainee gains a small leaf badge, the departure gate opens and a few graduates move into the body's ambient population.

**Shortcut:** A balcony returns to the heart-facing arch; the training courts are optional during timed care events.

**Material:** Warm parchment tissue, pale coral arches, sage cloth and tiny gold badges. A bright but gentle chest-side refuge.

**Life:** A guardian salutes so enthusiastically that its helmet slips over its eyes, then carefully straightens it.

**Must Fix:** Replace the contextual oval with a designed training courtyard only when its full route and interactions can be built to the same standard.

**Journey:**
1. Welcome court: watch one demonstration.
2. Recognition room: bring the matching practice parcel.
3. Escort cloister: lead a newly ready guardian to the departure gate.
4. Return balcony: look across the heart before rejoining the main route.

**Modeled assets:**
- Two soft lobes forming sheltered courtyards.
- A recognition table with large readable parcel silhouettes, training arches and a departure balcony.
- Three guardian poses: curious, uncertain and ready.

Sources: A13, G11, G12

## Bladder — The Quiet Reservoir

A peaceful pelvic reservoir that expands gently around its stable walkway. It is the calm ending to the lower-body journey.

**Size:** Proposed 20 × 18 m reservoir, a 4.5 m upper promenade and two clear incoming channels.

**Anatomy:** A hollow muscular reservoir receiving two ureters, with a lower controlled outlet. The storage and release relationship must be visible from the arrival view.

**Arrival:** The upper promenade reveals both incoming streams and the single lower outlet; the waterline is easy to read without a number.

**Care:** Hold to settle a gate and release at a clearly signaled moment. Treat the sequence warmly and avoid gross-out presentation.

**Change:** The waterline eases, the shell relaxes and reflected light stops flickering. A lower viewing shelf becomes reachable.

**Shortcut:** The upper promenade remains stable and continuously connects the two kidney returns.

**Material:** Warm pale tissue, blue-green water and soft gold reflections. Broad calm surfaces dominate.

**Life:** A droplet keeper floats past on a leaf and sleepily nudges a gate with one foot.

**Must Fix:** The current small bowl needs visible inflows, changing water level and an actual upper route.

**Journey:**
1. Upper arrival: follow a returning droplet from a kidney.
2. Twin inlet terraces: settle a fluttering flow gate.
3. Reservoir overlook: see the body gently expand with the waterline.
4. Release court: coordinate a comfortable outlet opening.
5. Return via the now quiet upper ring.

**Modeled assets:**
- A soft reservoir shell, stable inner promenade and clearly attached inlet mouths.
- One lower outlet, two small flow gates and a gently deforming water surface.

Sources: A10, G5, G12

## Pancreas & gallbladder — The Digestive Side Gardens

Two small but complete working locations: a long preparation mill and a green supply reservoir that support the larger digestive adventure.

**Size:** Proposed pancreas 20 × 8 m; gallbladder 12 × 9 m. Each has an arrival, a working interior and a return connection.

**Anatomy:** The pancreas supplies digestive secretions and has hormone functions. The gallbladder stores bile and connects into the digestive system. Neither is a passage through which food travels.

**Arrival:** A side path from the stomach reveals the pancreas as a long, gently folded mill. A separate jade doorway beneath the liver leads to the gallbladder reservoir.

**Care:** Carry a request, hold a preparation handle and place the resulting supply parcel. The reservoir uses the same hold/release rhythm already learned elsewhere.

**Change:** The preparation gallery warms in sequence, the supply route lights, and the small reservoir relaxes after dispatch.

**Shortcut:** Both side gardens reconnect to the digestive crossing. They enrich exploration without becoming compulsory stops on every meal delivery.

**Material:** Soft butter-gold pancreas, jade gallbladder, cream paths and restrained warm supply glows. Share the digestive district's rounded joinery.

**Life:** A meticulous mill keeper measures a parcel, finds it too fluffy, and gently pats it into the correct shape.

**Must Fix:** These are presently contextual silhouettes. The expanded brief requires complete small interiors, not simply enlarging those props.

**Journey:**
1. Pancreatic receiving nook: bring a request from the stomach.
2. Preparation gallery: help a supply parcel progress through two visible stations.
3. Dispatch ledge: send the parcel toward the duodenal junction and return to the digestive crossing.
4. Gallbladder inlet: view the reserve pool; assist a controlled supply release into its own narrow channel.

**Modeled assets:**
- A long lobulated preparation gallery with a readable head and tail.
- Two fitted work alcoves, one dispatch mouth and a stable side walkway.
- A pear-shaped green reservoir with a true interior, upper shelf and distinct outlet.

Sources: A5, A8, G4, G12

## Spleen — The Crimson Repair Garden

A tucked-away working garden where tired courier equipment is inspected and useful material returns to the world.

**Size:** Proposed 18 × 12 m, with a sheltered receiving bay, a repair grove and a return balcony.

**Anatomy:** Preserve the spleen's location beside the stomach and its compact elongated silhouette. Blood and immune roles motivate the theme; the specific repair-yard activities are fiction and require a dedicated anatomical plate before detailed modeling.

**Arrival:** A small shaded bridge beside the stomach reveals an inviting purple grove and a patient queue of returning couriers.

**Care:** Carry, match and place a parcel, then hold a gentle repair action. Keep the task about tending a working place.

**Change:** A dim courtyard becomes warm, repaired bundles leave in a small procession and the waiting couriers straighten up.

**Shortcut:** The side arch joins the stomach's upper promenade after the first visit.

**Material:** Deep plum tissue, pale rose paving, sage repair plants and copper light. A sheltered contrast to the bright stomach cavern.

**Life:** A courier tries to stay awake on the waiting bench, then perks up when Attention returns its parcel.

**Must Fix:** This is a proposed complete location. The current context mesh supplies only placement and cannot be counted as built gameplay or finished art.

**Journey:**
1. Receiving bay: meet an exhausted courier.
2. Inspection grove: carry its parcel to the matching station.
3. Renewal balcony: collect a useful recovered bundle.
4. Return arch: send the bundle toward the circulating routes and rejoin the stomach path.

**Modeled assets:**
- A compact elongated shell with a genuinely sheltered interior.
- Receiving bench, inspection grove, repair surface and a clear return arch.
- Two courier states and a small set of purposeful work props.

Sources: G11, G12

# Claim-to-source ledger

## F1 — The body game.jam
Owner-supplied FigJam package; Provided 7 September 2026. [The body game.jam](https://www.figma.com/board/rFrsYIJ8wyqGDX8OIUzbYo/The-body-game)

Full-resolution reference images extracted from the local package. Numbers are local index identifiers, not original Figma node numbers.

Access: Local archive and images inspected

## F2 — That Body Game — Design v11
Owner-supplied design; Version 11; date not verified. [That Body Game — Design v11](https://docs.google.com/document/d/1oNsGpc6BWey_fFHaC50kpmkionjnVT3Q/edit)

Attention character, eight tactile verbs, inter-organ carried resources, six original active organs, daily events and visible body states.

Access: Local fetched text inspected; user's later full-location brief extends its earlier scope

## G1 — Hob: Designing a Transforming World on PS4
Patrick Blank / Runic Games / PlayStation Blog; 28 April 2016. [Hob: Designing a Transforming World on PS4](https://blog.playstation.com/2016/04/28/hob-designing-a-transforming-world-on-ps4/)

Exploration detours unlock return shortcuts; interactions share recognizable cues; world transformation is both gameplay and story.

Access: Full page inspected by coordinator

## G2 — Save a Mysterious World in Hob
Patrick Blank interview / Runic Games / PlayStation Blog; 25 September 2017. [Save a Mysterious World in Hob](https://blog.playstation.com/2017/09/25/save-a-mysterious-world-in-hob-out-tomorrow-on-ps4/)

Known connections enabled deliberate world flow after randomized level ideas were abandoned.

Access: Research-lane primary interview read

## G3 — Hob project portfolio
Rick Lesley, senior level designer; Project August 2017; page undated. [Hob project portfolio](https://www.ricklesleydesign.com/hob)

Level responsibilities include connectivity, cameras, collision, ambient life and 2–5 minute puzzles.

Access: Research-lane creator portfolio read; timing applies to Hob

## G4 — Cocoon — Art Direction
Erwin Kho, art director; Undated. [Cocoon — Art Direction](https://zerbamine.nl/Cocoon-Art-Direction)

Architecture grows from the surrounding material; shared circular motifs and material handling unify distinct biomes.

Access: Research-lane page read; coordinator corroborated indexed primary text; one direct coordinator open failed

## G5 — The challenges of laying worlds upon worlds in puzzle game COCOON
Carlsen, Kho and Schmid interview / Game Developer; 22 March 2024. [The challenges of laying worlds upon worlds in puzzle game COCOON](https://www.gamedeveloper.com/design/the-challenges-of-laying-worlds-upon-worlds-in-puzzle-game-cocoon)

Bridge ability shaped canyon/spire terrain; other worlds adopt different landforms while retaining shared architecture.

Access: First-person interview, research lane plus coordinator indexed text

## G6 — Mental staircases and paradoxical suitcases: crafting the world-hopping puzzles of Cocoon
Jeppe Carlsen interview / Game Developer; 3 November 2023. [Mental staircases and paradoxical suitcases: crafting the world-hopping puzzles of Cocoon](https://www.gamedeveloper.com/design/mental-staircases-and-paradoxical-suitcases-crafting-the-world-hopping-puzzles-of-cocoon)

Arrival framing supplies useful information; satisfying movement toys matter; failed approaches must communicate clearly.

Access: Research-lane first-person interview read

## G7 — TUNIC: This Was Here the Whole Time
Andrew Shouldice / GDC; 2023. [TUNIC: This Was Here the Whole Time](https://gdcvault.com/play/1029384/-TUNIC-This-Was-Here)

Secrets and unresolved clues stimulate curiosity within a finite world.

Access: Session abstract only; full talk not watched

## G8 — The creation of Tunic's invaluable in-game manual
Andrew Shouldice / PlayStation Blog; 21 September 2022. [The creation of Tunic's invaluable in-game manual](https://blog.playstation.com/?p=370009)

A deliberately crafted manual integrates maps, hints, illustrations and secrets; physical material reference informed its texture.

Access: Research-lane developer-written article read

## G9 — Tracing Threads: The Making Of Tunic
Team interviews / Game Informer; 30 May 2022. [Tracing Threads: The Making Of Tunic](https://gameinformer.com/2022/05/30/tracing-threads-the-making-of-tunic)

Eric Billingsley describes a detail range between unfinished and stylistically excessive; the isometric camera both supports and constrains hidden routes.

Access: Research-lane attributed creator testimony

## G10 — Death's Door spreads its wings on PS4 and PS5
David Fenn / Acid Nerve / PlayStation Blog; 27 October 2021. [Death's Door spreads its wings on PS4 and PS5](https://blog.playstation.com/?p=355699)

Action weight and timing are reinforced by coordinated visual, audio and haptic feedback.

Access: Research-lane developer-written article; haptics platform-specific

## G11 — Xbox Podcast 753 — Death's Door discussion
David Fenn interview / Xbox Wire; 2021; exact day unverified. [Xbox Podcast 753 — Death's Door discussion](https://news.xbox.com/en-us/podcast/753-battlefield-portal-deaths-door-and-more/?ver=3.7.1)

Forest spirits approach idle players, smile and use leaves as clothing or hiding places, supporting ambient life beyond required mechanics.

Access: Research-lane transcript read

## G12 — Navigate the puzzling world of The Last Campfire
Sean Murray / Hello Games / PlayStation Blog; 26 August 2020. [Navigate the puzzling world of The Last Campfire](https://blog.playstation.com/?p=339929)

Helping inhabitants, world manipulation and newly reachable places form an adventure structure.

Access: Research-lane developer-written article read

## G13 — Dev Diary — Colors, windows & path to release
Pounce Light / Tiny Glade; 27 April 2023. [Dev Diary — Colors, windows & path to release](https://steamcommunity.com/games/2198150/announcements/detail/3682298662732600152)

Paths, walls, arches and windows adapt at intersections; seemingly simple craft requires bespoke construction rules.

Access: Research-lane dated Steam feed verified; used as visual construction reference only

## G14 — Episode 2 — Putting the Fun of the Mental into the Fundamentals
Double Fine; Undated page. [Episode 2 — Putting the Fun of the Mental into the Fundamentals](https://www.doublefine.com/games/psychonauts-2/updates/episode-2-putting-the-fun-of-the-mental-into-the-fundamentals)

Movement abilities determine jump distances, ledge and ladder clearance and therefore level geometry.

Access: Coordinator and research-lane full-page reads

## G15 — Episode 5 — First Playable Milestone
Double Fine; Undated page. [Episode 5 — First Playable Milestone](https://www.doublefine.com/games/psychonauts-2/updates/episode-5-first-playable-milestone)

Art tests differ from a complete playable location; asset construction includes concept, model, texture, animation and iterative review.

Access: Coordinator and research-lane full-page reads

## G16 — Chatting With The Doctor
Double Fine; 24 August 2022. [Chatting With The Doctor](https://www.doublefine.com/news/chatting-with-the-doctor)

Level conception considers host, condition, aesthetic, setting and twist; funny metaphors benefit from informed review.

Access: Published summary read; embedded discussion not watched

## G17 — Link's Awakening — visual style with Yoshiki Haruhana
Nintendo; 9 October 2019. [Link's Awakening — visual style with Yoshiki Haruhana](https://www.nintendo.com/en-gb/News/2019/October/Discover-what-graphic-refining-director-Yoshiki-Haruhana-aimed-for-with-the-visual-style-of-The-Legend-of-Zelda-Link-s-Awakening--1656228.html)

Detailed diorama craft is balanced against the imagined small character's scale; interiors also receive deliberate detail.

Access: Coordinator full page read

## G18 — Creating a stylized world with Unreal Engine 4
Epic Games / creator technical article; 2016; exact day not used. [Creating a stylized world with Unreal Engine 4](https://www.unrealengine.com/en-US/tech-blog/creating-a-stylized-world-with-unreal-engine-4)

Stylized environment choices need not reproduce literal real-world material values.

Access: Coordinator full page read; historical art practice, not UE5.8 implementation guidance

## G19 — Artist 02: Light a Scene
Epic Games documentation; UE5.8 documentation; accessed 7 September 2026. [Artist 02: Light a Scene](https://dev.epicgames.com/documentation/en-us/unreal-engine/artist-02-light-a-scene)

Lighting contributes to mood, readability and a consistent visual language for interactive locations.

Access: Coordinator full page read

## A1 — Brain Basics: Know Your Brain
NIH / NINDS; Page date unverified. [Brain Basics: Know Your Brain](https://www.ninds.nih.gov/es/node/8168)

Folded cerebral hemispheres, corpus callosum and distinct cerebellar movement role.

Access: Substantial indexed primary text verified; some full-page opens failed

## A2 — How Blood Flows through the Heart
NIH / NHLBI; 25 June 2025. [How Blood Flows through the Heart](https://www.nhlbi.nih.gov/health/heart/blood-flow)

Four directional valves and the body–right heart–lungs–left heart–body circulation sequence.

Access: Coordinator full page read

## A3 — The Respiratory System
NIH / NHLBI; 24 March 2022. [The Respiratory System](https://www.nhlbi.nih.gov/health/lungs/respiratory-system)

Three right and two left lobes; branching airway hierarchy; terminal alveoli and capillary exchange.

Access: Coordinator full page read

## A4 — What Breathing Does for the Body
NIH / NHLBI; 27 June 2025. [What Breathing Does for the Body](https://www.nhlbi.nih.gov/health/lungs/breathing-benefits)

Diaphragm motion, inhalation/exhalation and gas exchange.

Access: Research-lane primary page read

## A5 — Your Digestive System & How It Works
NIH / NIDDK; Reviewed December 2017. [Your Digestive System & How It Works](https://www.niddk.nih.gov/health-information/digestive-diseases/digestive-system-how-it-works)

Continuous digestive route, coordinated movement, absorption and liver processing/storage.

Access: Coordinator full page read

## A6 — Stomach
NIH / NCI SEER Training; Undated. [Stomach](https://training.seer.cancer.gov/anatomy/digestive/regions/stomach.html)

Stomach regions, asymmetry, curvatures and pyloric outlet.

Access: Research-lane primary page read

## A7 — Small & Large Intestine
NIH / NCI SEER Training; Undated. [Small & Large Intestine](https://training.seer.cancer.gov/anatomy/digestive/regions/intestine.html)

Small-intestinal sequence and absorptive surface; wider colon pouches and water recovery.

Access: Research-lane primary page read

## A8 — Accessory Organs
NIH / NCI SEER Training; Undated. [Accessory Organs](https://training.seer.cancer.gov/anatomy/digestive/regions/accessory.html)

Liver organization and flow, pancreas functions and gallbladder storage.

Access: Research-lane primary page read

## A9 — Your Kidneys & How They Work
NIH / NIDDK; Reviewed June 2018. [Your Kidneys & How They Work](https://www.niddk.nih.gov/health-information/kidney-disease/kidneys-how-they-work)

Filtration, recovery of useful substances and separate blood/urine exits.

Access: Research-lane primary page read

## A10 — The Urinary Tract & How It Works
NIH / NIDDK; Reviewed June 2020. [The Urinary Tract & How It Works](https://www.niddk.nih.gov/health-information/urologic-diseases/urinary-tract-how-it-works)

Two ureters, expanding bladder reservoir and coordinated release.

Access: Research-lane primary page read

## A11 — Adrenal Gland
NIH / NCI SEER Training; Undated. [Adrenal Gland](https://training.seer.cancer.gov/anatomy/endocrine/glands/adrenal.html)

Outer cortex and inner medulla have different hormone functions; adrenal glands do not produce a vagal hormone.

Access: Research-lane primary page read

## A12 — Thyroid & Parathyroid Glands
NIH / NCI SEER Training; Undated. [Thyroid & Parathyroid Glands](https://training.seer.cancer.gov/anatomy/endocrine/glands/thyroid.html)

Two thyroid lobes joined by an isthmus and follicular structure.

Access: Research-lane primary page read

## A13 — Thymus
NIH / NCI SEER Training; Undated. [Thymus](https://training.seer.cancer.gov/anatomy/lymphatic/components/thymus.html)

Two-lobed chest location, immune maturation and age-related change.

Access: Research-lane primary page read

## A14 — Pharynx & Esophagus
NIH / NCI SEER Training; Undated. [Pharynx & Esophagus](https://training.seer.cancer.gov/anatomy/digestive/regions/pharynx.html)

Distinct air and food passageways with a coordinated swallowing junction.

Access: Research-lane primary page read

## A15 — Meditation and Mindfulness: Effectiveness and Safety
NIH / NCCIH; June 2022. [Meditation and Mindfulness: Effectiveness and Safety](https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety)

Brain-activity findings have uncertain practical interpretation; no deterministic theta thought-dissolution mechanism established.

Access: Research-lane primary page read; used only to bound design-document claims
