import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'Art/HeartBaseline'
bpy.ops.wm.open_mainfile(filepath=str(ART/'Heart_Baseline.blend'))
bpy.context.scene.camera.data.clip_end=30000
bpy.context.scene.camera.data.clip_start=1
bpy.context.scene.render.filepath=str(ART/'Heart-source-review.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Heart_Baseline.blend'))
bpy.ops.render.render(write_still=True)
