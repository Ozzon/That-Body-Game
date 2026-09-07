# Approved direction and complete body layout

The owner selected `Art/Approved/Heart-owner-approved-2026-09-07.png` on 7 September 2026. It is a render of the editable model `Art/HeartModels/A/Heart_Model_A.blend`. This exact heart is the baseline. The previous dense procedural body remains archived in the BodyGarden map.

Build a connected miniature adventure using open sculpted organ rooms, smooth coral walls, quiet floors, arched passages, one clear care landmark per destination, and mint light bridges. No exposed skeleton, rows of decorative tubes, or dense clusters of props. Each organ receives its own outline and interior drawing.

## Geography

| Region | Destinations | Navigation role |
| --- | --- | --- |
| Chest | Four-chamber heart, three-lobe right lung, two-lobe left lung, diaphragm glade | Main breathing and heartbeat loop, with a second route through the throat |
| Head | Two cerebral gardens and central awareness court | A gently rising neck passage, four thoughts to release |
| Upper abdomen | Liver chambers, J-shaped stomach | Recovery and energy side destinations |
| Lower abdomen | Paired kidney chambers with adrenal stations, intestinal galleries | A second connected loop, reached through a central crossing |
| Pelvis | Bladder sanctuary | The quiet end of the digestive route |
| Context | Thyroid, thymus, spleen, pancreas, gallbladder, complete body outline | Restrained supporting forms below or outside the walkable routes |

The head points along +X. Anatomical right is -Y. Organ sizes are adapted to the character and are not a medical scale model. The approved heart remains approximately 30 by 30 meters in gameplay coordinates. The 1.8-meter hooded character occupies a small part of each chamber. Bridges are 4.7–5.4 meters wide; shared glades are approximately 10–12 meters across. Doorways preserve at least a three-character width where the drawings permit it. Collision and floor height come from the same drawings as the meshes.

Light bridges represent travel for attention; they do not claim to reproduce vascular routing. Six organ systems have care interactions. Kidneys, intestines and bladder are explorable context rather than additional management games. Arm and leg silhouettes establish the full body; the playable route follows the organs.

## Anatomy references

Organ arrangement is checked against [SEER body cavities](https://training.seer.cancer.gov/anatomy/body/terminology.html), [NIH respiratory anatomy](https://www.nhlbi.nih.gov/health/lungs/respiratory-system), and [Cleveland Clinic organ anatomy](https://my.clevelandclinic.org/health/articles/organs-in-the-body). The right lung has three lobes and the left two. The diaphragm separates chest from abdomen. The liver and stomach occupy opposite sides below it. The kidney/adrenal regions flank the intestinal district.

The authoritative editable placements, sizes, room shapes, doors and bridge centerlines are in `Tools/adventure_layout.py`. Each room must be connected in the generated navigation grid, followed by a native keyboard-input traversal check. Compilation and route checks establish technical behavior; screenshots and owner review establish art acceptance.
