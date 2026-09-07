from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil
root=Path(__file__).resolve().parents[1]
build=root/'Builds/BrainAdventure-C16-20260907';windows=build/'Windows';evidence=build/'Evidence'
def read(path):
    raw=path.read_bytes();return raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def report(log,marker):
    value=read(log);match=re.search(marker+r' (\{[^\r\n]+\})',value);assert match,log
    result=json.loads(match.group(1));assert result['passed'],result
    assert 'LogExit: Exiting.' in value,log
    return result
assert 'BUILD SUCCESSFUL' in read(root/'Docs/brain-c16-package.log')
checks={}
for key,marker in [('smoke','CRAFT_INPUT_REPORT'),('controls','CRAFT_CAMERA_REPORT'),('roam','CRAFT_ROAM_REPORT')]:
    checks[key]=report(root/f'Docs/brain-c16-packaged-{key}.log',marker)
assert checks['smoke']['complete'] and checks['smoke']['physical_grabs']>=4
assert checks['roam']['visited']==12 and checks['roam']['fall_recoveries']==0
rendered=report(root/'Docs/brain-c16-rendered-r03.log','CRAFT_INPUT_REPORT')
film=report(root/'Docs/brain-c16-film-r03.log','CRAFT_INPUT_REPORT')
cape={}
for key,path in [('packaged',root/'Docs/brain-c16-packaged-smoke.log'),('rendered',root/'Docs/brain-c16-rendered-r03.log'),('recorded',root/'Docs/brain-c16-film-r03.log')]:
    m=re.search(r'CRAFT_CAPE_REPORT stretch=([\d.]+) travel_cm=([\d.]+) resets=(\d+)',read(path));assert m,path
    cape[key]={'max_stretch_ratio':float(m[1]),'max_travel_cm':float(m[2]),'resets':int(m[3])}
    assert float(m[1])<1.25,cape[key]
capture=read(root/'Docs/brain-c16-packaged-capture.log')
assert 'CRAFT_CLOTH_READY' in capture and 'LogExit: Exiting.' in capture
screens=sorted((windows/'ThatBodyGame/Saved/Screenshots').glob('Brain-C16-*.png'));assert len(screens)==4
evidence.mkdir(exist_ok=True)
for p in screens:shutil.copy2(p,evidence/p.name)
for p in (root/'Saved/Screenshots').glob('Cast-C16-*.png'):shutil.copy2(p,evidence/p.name)
for p in (root/'Docs').glob('brain-c16-*'):
    if p.is_file():shutil.copy2(p,evidence/p.name)
shutil.copy2(root/'Docs/BRAIN_C16_WORK.md',evidence)
shutil.copytree(root/'Source',evidence/'Source',dirs_exist_ok=True)
shutil.copytree(root/'Art/BrainCraft/Source/C16',evidence/'Construction',dirs_exist_ok=True)
shutil.copytree(root/'Art/BrainCraft/Reviews/C16-Motion',evidence/'Motion',dirs_exist_ok=True)
for p in (root/'Tools').glob('*c16*'):
    if p.is_file():
        dest=evidence/'Tools'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest)
manifest={'checkpoint':'C16','engine':'5.8','created_utc':datetime.now(timezone.utc).isoformat(),
          'art_accepted':False,'goal_complete':False,'whole_garden_exploration_accepted':False,
          'packaged_tests':checks,'rendered_care_test':rendered,'fixed_simulation_recording':film,
          'cape':cape,'files':[],'source_files':[]}
for p in sorted(windows.rglob('*')):
    if p.suffix.lower() in ('.exe','.pak','.ucas','.utoc'):
        manifest['files'].append({'path':p.relative_to(build).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
for p in sorted((evidence/'Source').rglob('*')):
    if p.is_file():manifest['source_files'].append({'path':p.relative_to(evidence).as_posix(),'sha256':sha(p)})
(evidence/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
guide=(root/'Builds/BrainAdventure-C15-R2-20260907/Windows/START HERE.txt').read_text().split('ABOUT THIS BUILD')[0].replace('checkpoint C15-R2 /','checkpoint C16 /')
guide+='''NEW IN C16
Rebuilt bright stars, heavy clouds, restless wisps and amber rosettes.
Separate expressive eyes, readable faces and animated wisp filaments.
Smoother carrying turns and hand release transitions.
Hands follow the completed physics update. The cape keeps its intended shape
while responding to motion, wind and the held thought.

The care loop, camera checks and twelve-destination route passed in this package.
Art quality, wider environment composition and full animation polish remain
unfinished. This is not the final Breath of the Wild quality target.
'''
(windows/'START HERE.txt').write_text(guide)
(build/'Play.bat').write_text('@echo off\nstart "" "%~dp0Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
(root/'Play Brain Adventure.bat').write_text('@echo off\nstart "" "%~dp0Builds\\BrainAdventure-C16-20260907\\Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
print(json.dumps({'ready':True,'launcher':str(build/'Play.bat'),'checks':checks,'cape':cape},indent=2))
