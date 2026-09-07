from pathlib import Path
import hashlib, json, re, shutil

root=Path(__file__).resolve().parents[1]
build=root/'Builds/BrainAdventure-C12-20260907'
windows=build/'Windows'
evidence=build/'Evidence'
evidence.mkdir(exist_ok=True)
reports={}
for name,marker in [('smoke','CRAFT_INPUT_REPORT'),('controls','CRAFT_CAMERA_REPORT')]:
    log=root/f'Docs/brain-c12-packaged-{name}.log'
    match=re.search(marker+r' (\{[^\r\n]+\})',log.read_text(errors='replace'))
    assert match, str(log)
    reports[name]=json.loads(match.group(1))
    assert reports[name]['passed']
capture=(root/'Docs/brain-c12-packaged-capture.log').read_text(errors='replace')
assert 'CRAFT_CLOTH_READY' in capture and 'LogExit: Exiting.' in capture
package_bytes=(root/'Docs/brain-c12-package.log').read_bytes()
package_text=package_bytes.decode('utf-16' if package_bytes.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
assert 'BUILD SUCCESSFUL' in package_text
for name in ['package','build-prep','smoke','film','packaged-smoke','packaged-controls','packaged-capture']:
    shutil.copy2(root/f'Docs/brain-c12-{name}.log',evidence)
for src in (windows/'ThatBodyGame/Saved/Screenshots').glob('*.png'):
    shutil.copy2(src,evidence/('C12-'+src.name))
source_names=['BrainCraft.cpp','BrainCraft.h','BrainCraftReview.cpp','BrainCraftLayout.inl','BrainCraftRoutes.inl','Animation/AttentionCape.cpp','Animation/AttentionCape.h','Animation/BWBipedGait.cpp','Animation/BWBipedGait.h','Animation/BWGait.h']
for name in source_names:
    dest=evidence/'Source'/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(root/'Source/ThatBodyGame'/name,dest)
shutil.copy2(root/'Docs/BRAIN_C12_PLAYABLE.md',evidence)
manifest={'checkpoint':'C12','engine':'5.8','art_accepted':False,'lighting_overhaul_complete':False,'whole_garden_access_complete':False,'packaged_tests':reports,'rendered_cape_initialized':True,'headless_tests_do_not_exercise_cape_render_data':True,'files':[]}
for path in sorted(windows.rglob('*')):
    if path.suffix.lower() in ['.exe','.pak','.ucas','.utoc']:
        digest=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024*1024),b''):digest.update(chunk)
        manifest['files'].append({'path':path.relative_to(build).as_posix(),'bytes':path.stat().st_size,'sha256':digest.hexdigest()})
(evidence/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
guide=(root/'Builds/BrainAdventure-C11-20260907/Windows/START HERE.txt').read_text()
guide=guide.replace('checkpoint C11','checkpoint C12').replace('The previous C10 build is preserved.','The previous C11 build is preserved.\n\nNEW IN C12\nMovement is faster: 560 cm/s walking and 800 cm/s hurrying, with faster\ncarrying and pushing / pulling. Stepping cadence and camera follow were\nretuned. The cape now uses cloth simulation with body and thought\nclearance. The new lighting and shading overhaul is still in progress.')
(windows/'START HERE.txt').write_text(guide)
(root/'Play Brain Adventure.bat').write_text('@echo off\nstart "" "%~dp0Builds\\BrainAdventure-C12-20260907\\Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
print(json.dumps({'ready':True,'executable':str(windows/'ThatBodyGame.exe'),'validation':reports},indent=2))
