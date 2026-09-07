# Corrective art direction after C10 rejection

Owner feedback on 7 September 2026: the garden remains too brown, flat, poorly shaded, and detached from the concept. C10 is a gameplay test checkpoint, not an accepted art baseline. Do not label the sparse-grass screenshots or the dense-grass source pass as meeting Zelda quality.

## Compare actual geometry against the images

Primary location: `Art/BrainCraft/Concept/Brain-Location-Key-Art.png`. Original FigJam garden: `Docs/References/ref-384.png`. These are visual references, not evidence of implemented geometry.

| Concept feature | C10 shortfall | Required physical construction |
|---|---|---|
| Garden terraces have depth, exposed banks and stepped water | Ground reads as paths laid across one continuous brown surface | Build coherent planted terraces, retaining foundations and actual height transitions |
| Planting is a designed bed around landmarks and in sheltered pockets | Repeated grass clumps are an isolated surface treatment | Compose complete beds, ground cover, shrubs and trees at three scales, with clear unplanted approaches |
| Brain tissue frames the garden with deep, rounded gyri | Large smooth internal wedges compete with the garden | Keep a recognizable hemispheric envelope; model nested folds and prevent them from occupying play courts |
| Water belongs to basins with visible lips, channels, spillways and crossing landings | Grid edges, repeated circular bowls and disconnected stone tops | Fit each basin and bridge to a clear hydraulic and architectural sequence |
| Paving is fitted and worn, with bevels that catch light | Incorrect slab winding hid many top faces in Unreal | Seal each slab and verify outward normals in the native render before approving the material |
| The awareness tree has an airy, sculptural crown and distinct wood response | Repeated leaves and a uniformly orange trunk | Vary crown masses, preserve negative space, author bark relief and separate waxy leaf response from rough wood |
| Character, thoughts, shade and local light form one image | Inputs work, but modular poses and flat surfaces break that coherence | Judge moving footage at the actual gameplay camera, with visible hand and foot contacts |

The owner requested that the portals be separated. This supersedes the generated concept's group of three mouths. Preserve separate arrival, spring and memory encounters; build each into an appropriate garden alcove.

## Shader and lighting direction

PBR response must be visibly distinct: matte soil, damp dark margins, worn stone with light-catching bevels, rough fibrous bark, waxy leaves, softly translucent tissue and reflective water. A generic roughness value or a texture sample is not completion. Preserve the painted colors through a controlled light/shadow treatment. Assess highlights and contact shade on curved models, not only a top-down screenshot.

Nintendo's official CEDEC 2017 session abstract describes the Breath of the Wild image as layered foreground, middle distance, background, time and space, and explicitly connects art direction with rendering implementation. This supports a complete scene composition rather than treating cel shading as a single filter. The actual session materials are marked non-public; no exact Nintendo shader implementation is claimed. [CEDEC: painting the world of Breath of the Wild in layers](https://cedec.cesa.or.jp/2017/session/VA/s58eed7182c81b.html).

Nintendo's Tears of the Kingdom interview describes making interactions visibly understandable and adjusting individual item combinations to match player expectations. For this game, visible hand contact, weight, a readable destination and an intentional release animation belong in the same review as appearance. [Nintendo developer interview, part 4](https://www.nintendo.com/us/whatsnew/ask-the-developer-vol-9-the-legend-of-zelda-tears-of-the-kingdom-part-4/).

## Protected playable checkpoint

Finish and verify `Builds/BrainGameplay-C10-20260907` before importing the next visual candidate. Keep the packaged gameplay checkpoint unchanged while the art construction continues. The approved heart remains untouched.
