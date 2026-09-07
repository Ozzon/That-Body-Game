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
