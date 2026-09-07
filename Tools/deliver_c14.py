from pathlib import Path
import hashlib,json,re,shutil
root=Path(__file__).resolve().parents[1];build=root/'Builds/BrainAdventure-C14-20260907';windows=build/'Windows';evidence=build/'Evidence';evidence.mkdir(exist_ok=True);reports={}
for name,marker in [('smoke','CRAFT_INPUT_REPORT'),('controls','CRAFT_CAMERA_REPORT'),('roam','CRAFT_ROAM_REPORT')]:
    log=root/f'Docs/brain-c14-packaged-{name}.log';match=re.search(marker+r' (\{[^\r\n]+\})',log.read_text(errors='replace'));assert match,str(log);reports[name]=json.loads(match.group(1));assert reports[name]['passed'],reports[name]
assert reports['roam']['visited']==12
capture=(root/'Docs/brain-c14-packaged-capture.log').read_text(errors='replace');assert 'CRAFT_CLOTH_READY' in capture and 'LogExit: Exiting.' in capture
b=(root/'Docs/brain-c14-package.log').read_bytes();package=b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8',errors='replace');assert 'BUILD SUCCESSFUL' in package
for name in ['package','import','import-repair','mantle-import','mantle-author','nest-winding','smoke-r01','gripbaseline-r01','roam-r02','packaged-smoke','packaged-controls','packaged-roam','packaged-capture']:
    src=root/f'Docs/brain-c14-{name}.log'
    if src.exists():shutil.copy2(src,evidence)
screenshots=list((windows/'ThatBodyGame/Saved/Screenshots').glob('Brain-C14-*.png'));assert len(screenshots)>=4
for src in screenshots:shutil.copy2(src,evidence/src.name)
for src in (windows/'ThatBodyGame/Saved').glob('brain-c14-*.json'):shutil.copy2(src,evidence/src.name)
for name in ['BrainCraft.cpp','BrainCraft.h','BrainCraftReview.cpp','BrainCraftExploration.cpp','BrainCraftLayout.inl','BrainCraftRoutes.inl','Animation/AttentionCape.cpp','Animation/AttentionCape.h','Animation/BWBipedGait.cpp','Animation/BWBipedGait.h','Animation/BWGait.h']:
    dest=evidence/'Source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/'Source/ThatBodyGame'/name,dest)
for name in ['portals.json','construction.json','mantle-construction.json','native-readback.json','mantle-native-readback.json','nest-winding.json']:
    dest=evidence/'Construction'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/'Art/BrainCraft/Source/C14'/name,dest)
shutil.copy2(root/'Docs/BRAIN_C14_PLAYABLE.md',evidence)
manifest={'checkpoint':'C14','engine':'5.8','art_accepted':False,'lighting_overhaul_complete':False,'whole_garden_access_complete':False,'twelve_destinations_traversed':True,'packaged_tests':reports,'rendered_cape_initialized':True,'files':[]}
for path in sorted(windows.rglob('*')):
    if path.suffix.lower() in ['.exe','.pak','.ucas','.utoc']:
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
        manifest['files'].append({'path':path.relative_to(build).as_posix(),'bytes':path.stat().st_size,'sha256':h.hexdigest()})
(evidence/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
guide=(root/'Builds/BrainAdventure-C13-20260907/Windows/START HERE.txt').read_text().split('NEW IN C13')[0].replace('checkpoint C13','checkpoint C14')
guide+='''NEW IN C14
The lower gardens and three separate border nests are connected.
New cortical tissue, organic thought nests and rounded paving.
Revised physical handling keeps Attention's hands closer to the thoughts.
Faster movement, cape cloth and the complete thought-care loop are included.

CHECKPOINT SCOPE
The packaged care loop, twelve-destination exploration route and camera
input checks pass. Art and sharp animation transitions still need work.
Physical controller testing remains outstanding. C13 is preserved.
'''
(windows/'START HERE.txt').write_text(guide)
(root/'Play Brain Adventure.bat').write_text('@echo off\nstart "" "%~dp0Builds\\BrainAdventure-C14-20260907\\Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
print(json.dumps({'ready':True,'executable':str(windows/'ThatBodyGame.exe'),'validation':reports},indent=2))
