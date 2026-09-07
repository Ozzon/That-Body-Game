from pathlib import Path
import hashlib,json,re,shutil
root=Path(__file__).resolve().parents[1];build=root/'Builds/BrainAdventure-C15-20260907';windows=build/'Windows';evidence=build/'Evidence';evidence.mkdir(exist_ok=True)
reports={}
for name,marker in [('smoke','CRAFT_INPUT_REPORT'),('controls','CRAFT_CAMERA_REPORT'),('roam','CRAFT_ROAM_REPORT')]:
    log=root/f'Docs/brain-c15-packaged-{name}.log'
    match=re.search(marker+r' (\{[^\r\n]+\})',log.read_text(errors='replace'));assert match,str(log)
    reports[name]=json.loads(match.group(1));assert reports[name]['passed'],reports[name]
assert reports['roam']['visited']==12 and reports['roam']['fall_recoveries']==0
capture=(root/'Docs/brain-c15-packaged-capture.log').read_text(errors='replace')
assert 'CRAFT_CLOTH_READY' in capture and 'LogExit: Exiting.' in capture
raw=(root/'Docs/brain-c15-package.log').read_bytes();log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace');assert 'BUILD SUCCESSFUL' in log
screens=list((windows/'ThatBodyGame/Saved/Screenshots').glob('Brain-C15-*.png'));assert len(screens)==4
for src in screens:shutil.copy2(src,evidence/src.name)
for src in (root/'Docs').glob('brain-c15-*.log'):shutil.copy2(src,evidence/src.name)
for src in (windows/'ThatBodyGame/Saved').glob('brain-c15-*.json'):shutil.copy2(src,evidence/src.name)
for src in (root/'Art/BrainCraft/Source/C15').glob('*.json'):
    dest=evidence/'Construction'/src.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(src,dest)
for src in (root/'Source/ThatBodyGame').glob('BrainCraft*'):
    dest=evidence/'Source'/src.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(src,dest)
for src in (root/'Source/ThatBodyGame/Animation').glob('*'):
    if src.is_file():
        dest=evidence/'Source/Animation'/src.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(src,dest)
for src in (root/'Tools').glob('*c15*'):
    if src.is_file():
        dest=evidence/'Tools'/src.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(src,dest)
shutil.copy2(root/'Docs/BRAIN_C15_WORK.md',evidence)
manifest=dict(checkpoint='C15',engine='5.8',art_accepted=False,goal_complete=False,whole_garden_access_complete=False,twelve_destinations_traversed=True,packaged_tests=reports,files=[])
timing=re.search(r'CRAFT_VIEW_TIMING samples=(\d+) median_ms=([\d.]+) p95_ms=([\d.]+)',capture)
if timing:manifest['offscreen_timing']={'samples':int(timing[1]),'median_ms':float(timing[2]),'p95_ms':float(timing[3]),'representative_player_performance':False}
for path in sorted(windows.rglob('*')):
    if path.suffix.lower() in ['.exe','.pak','.ucas','.utoc']:
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
        manifest['files'].append(dict(path=path.relative_to(build).as_posix(),bytes=path.stat().st_size,sha256=h.hexdigest()))
(evidence/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
guide=(root/'Builds/BrainAdventure-C14-20260907/Windows/START HERE.txt').read_text().split('NEW IN C14')[0].replace('checkpoint C14','checkpoint C15')
guide+='''NEW IN C15
Rounded brain folds without the previous pinched geometry.
Continuous spring water and a lotus moat with graded banks.
More readable shadows and physical water highlights.
The orange thought's glowing core is clear of its spiral body.

CHECKPOINT SCOPE
The packaged care loop, twelve-destination route and camera checks pass.
Art, landmark detail and animation polish are still in progress.
This is not the final Zelda-quality art target. C14 is preserved.
'''
(windows/'START HERE.txt').write_text(guide)
(root/'Play Brain Adventure.bat').write_text('@echo off\nstart "" "%~dp0Builds\\BrainAdventure-C15-20260907\\Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
print(json.dumps(dict(ready=True,executable=str(windows/'ThatBodyGame.exe'),packaged_tests=reports),indent=2))
