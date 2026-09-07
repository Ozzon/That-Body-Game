from pathlib import Path
import hashlib, json, re, shutil

root=Path(__file__).resolve().parents[1]
build=root/'Builds/BrainAdventure-C13-20260907'
windows=build/'Windows'
evidence=build/'Evidence'
evidence.mkdir(exist_ok=True)
reports={}
for name,marker in [('smoke','CRAFT_INPUT_REPORT'),('controls','CRAFT_CAMERA_REPORT')]:
    log=root/f'Docs/brain-c13-packaged-{name}.log'
    match=re.search(marker+r' (\{[^\r\n]+\})',log.read_text(errors='replace'))
    assert match,str(log)
    reports[name]=json.loads(match.group(1))
    assert reports[name]['passed'],reports[name]
capture=(root/'Docs/brain-c13-packaged-capture.log').read_text(errors='replace')
assert 'CRAFT_CLOTH_READY' in capture and 'LogExit: Exiting.' in capture
package_bytes=(root/'Docs/brain-c13-package.log').read_bytes()
package_text=package_bytes.decode('utf-16' if package_bytes.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
assert 'BUILD SUCCESSFUL' in package_text
roam_log=root/'Docs/brain-c13-packaged-roam.log'
roam_match=re.search(r'CRAFT_ROAM_REPORT (\{[^\r\n]+\})',roam_log.read_text(errors='replace')) if roam_log.exists() else None
reports['exploration_playthrough']=json.loads(roam_match.group(1)) if roam_match else {'passed':False,'status':'not fully verified; northern bank traversal stalled in editor check'}
for name in ['package','collision-import','smoke-r03','roam-r03','capture-r03','packaged-smoke','packaged-controls','packaged-roam','packaged-capture']:
    src=root/f'Docs/brain-c13-{name}.log'
    if src.exists():shutil.copy2(src,evidence)
for src in (windows/'ThatBodyGame/Saved/Screenshots').glob('*.png'):
    shutil.copy2(src,evidence/src.name)
for src in (windows/'ThatBodyGame/Saved').glob('brain-c13-*.json'):
    shutil.copy2(src,evidence/src.name)
source_names=['BrainCraft.cpp','BrainCraft.h','BrainCraftReview.cpp','BrainCraftExploration.cpp','BrainCraftLayout.inl','BrainCraftRoutes.inl','Animation/AttentionCape.cpp','Animation/AttentionCape.h','Animation/BWBipedGait.cpp','Animation/BWBipedGait.h','Animation/BWGait.h']
for name in source_names:
    dest=evidence/'Source'/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(root/'Source/ThatBodyGame'/name,dest)
shutil.copy2(root/'Docs/BRAIN_C13_PLAYABLE.md',evidence)
manifest={'checkpoint':'C13','engine':'5.8','art_accepted':False,'lighting_overhaul_complete':False,'whole_garden_access_complete':reports['exploration_playthrough'].get('passed',False),'packaged_tests':reports,'rendered_cape_initialized':True,'headless_tests_do_not_exercise_cape_render_data':True,'new_fitted_cortex_included':False,'files':[]}
for path in sorted(windows.rglob('*')):
    if path.suffix.lower() in ['.exe','.pak','.ucas','.utoc']:
        digest=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024*1024),b''):digest.update(chunk)
        manifest['files'].append({'path':path.relative_to(build).as_posix(),'bytes':path.stat().st_size,'sha256':digest.hexdigest()})
(evidence/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
guide=(root/'Builds/BrainAdventure-C12-20260907/Windows/START HERE.txt').read_text()
guide=guide[:guide.index('CHECKPOINT SCOPE')].replace('checkpoint C12','checkpoint C13')
guide+='''NEW IN C13
Rebuilt terrain with shaped banks, smaller planting and individual paving.
Revised surface materials, movable sunlight, skylight and local lighting.
Two terrain sections repaired to prevent falling through their surfaces.
Faster movement, cape cloth and the complete thought-care loop retained.

CHECKPOINT SCOPE
Packaged core interactions and camera-input checks pass. The rendered
package starts successfully and initializes cape cloth. This is a gameplay
checkpoint; final art quality is still unfinished. Complete traversal of
all lower gardens is not verified: an automated route stalls at a northern
bank. The new fitted brain envelope is not included yet. C12 is preserved.
'''
(windows/'START HERE.txt').write_text(guide)
(root/'Play Brain Adventure.bat').write_text('@echo off\nstart "" "%~dp0Builds\\BrainAdventure-C13-20260907\\Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
print(json.dumps({'ready':True,'executable':str(windows/'ThatBodyGame.exe'),'validation':reports},indent=2))
