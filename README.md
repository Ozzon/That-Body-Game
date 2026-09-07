# That Body Game

An Unreal Engine **5.8** organ-care adventure prototype, with editable Blender
sources, imported game assets, authoring tools, concepts and iteration evidence.

## Current checkpoint

The working project includes the unfinished **C17 brain garden** revision.
Its editable scene is `Art/BrainCraft/Brain_Craft_C17.blend`; the native level is
`Content/Maps/BrainCraft.umap`. Work is stopped at this checkpoint. The overall
art, animation and gameplay quality goals remain unfinished.

C17 R03 editor checks passed the care loop, camera controls and all 12 scripted
exploration destinations. The final capture-framing and material-diagnostic
edits compiled afterward but were not rerun. C17 has **not** been packaged.
See `Docs/BRAIN_C17_WORK.md` and `Docs/brain-c17-*-r03.log` for scope and evidence.

The last delivered Windows build is **C16-R2**, locally located under
`Builds/BrainAdventure-C16-R2-20260907`. Packaged builds are excluded from Git.
The root `Play Brain Adventure.bat` launcher requires that local build folder;
it cannot launch directly from a fresh clone.

## Getting the project

Install Git LFS before cloning so binary assets are downloaded correctly:

```sh
git lfs install
git clone https://github.com/Ozzon/That-Body-Game.git
cd That-Body-Game
git lfs pull
```

Open `ThatBodyGame.uproject` with Unreal Engine 5.8 and a compatible Windows C++
toolchain. Let Unreal generate and compile the project files. Blender sources
were authored using Blender 5.1. Some authoring and packaging scripts contain
workstation-specific paths and need adjustment on another machine.

## Repository contents

- `Source`, `Config`, `Content`: native game code, configuration and Unreal assets.
- `Art`: editable models, exports, textures, concepts and preserved iterations.
- `Tools`: authoring, import, review and packaging scripts.
- `Docs`, `Presentations`: design references, work notes and validation evidence.
- `Build`: project build resources, distinct from generated `Builds` packages.

Generated binaries, packaged builds, engine caches and Python caches are
excluded. The downloaded Figma session HTML and the local Android file-server
security token are also excluded; extracted design references are retained.
