from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil

root = Path(__file__).resolve().parents[1]
build = root / 'Builds/BrainAdventure-C15-R2-20260907'
windows = build / 'Windows'
evidence = build / 'Evidence'

def read_log(path):
    raw = path.read_bytes()
    return raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8', errors='replace')

def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()

assert (root / 'Docs/brain-c15-r2-package-exit.txt').read_text(encoding='utf-8-sig').strip() == '0'
assert 'BUILD SUCCESSFUL' in read_log(root / 'Docs/brain-c15-r2-package.log')
reports = {}
for name, marker in [('smoke', 'CRAFT_INPUT_REPORT'), ('controls', 'CRAFT_CAMERA_REPORT'), ('roam', 'CRAFT_ROAM_REPORT')]:
    text = read_log(root / f'Docs/brain-c15-r2-packaged-{name}.log')
    match = re.search(marker + r' (\{[^\r\n]+\})', text)
    assert match, name
    reports[name] = json.loads(match.group(1))
    assert reports[name]['passed'], reports[name]
    assert 'LogExit: Exiting.' in text, name
assert reports['smoke']['complete'] and reports['smoke']['physical_grabs'] >= 4
assert reports['roam']['visited'] == 12 and reports['roam']['fall_recoveries'] == 0
capture = read_log(root / 'Docs/brain-c15-r2-packaged-capture.log')
assert 'CRAFT_CLOTH_READY' in capture and 'LogExit: Exiting.' in capture
screens = sorted((windows / 'ThatBodyGame/Saved/Screenshots').glob('Brain-C15-*.png'))
assert len(screens) == 4

# Verify this really is the requested fresh package of the delivered gameplay.
previous = root / 'Builds/BrainAdventure-C15-20260907/Evidence/Source'
for source in previous.rglob('*'):
    if source.is_file():
        assert digest(source) == digest(root / 'Source/ThatBodyGame' / source.relative_to(previous)), source

evidence.mkdir(exist_ok=True)
for source in screens:
    shutil.copy2(source, evidence / source.name)
for source in (root / 'Docs').glob('brain-c15-r2-*'):
    if source.is_file():
        shutil.copy2(source, evidence / source.name)
shutil.copytree(root / 'Source', evidence / 'Source', dirs_exist_ok=True)
shutil.copy2(root / 'ThatBodyGame.uproject', evidence)
for name in ['rebuild_c15.ps1', 'check_c15_rebuild.ps1', 'deliver_c15_rebuild.py']:
    target = evidence / 'Tools' / name
    target.parent.mkdir(exist_ok=True)
    shutil.copy2(root / 'Tools' / name, target)

manifest = {
    'checkpoint': 'C15-R2',
    'engine': '5.8',
    'packaged_utc': datetime.now(timezone.utc).isoformat(),
    'purpose': 'Fresh Windows package of current C15 gameplay at user request.',
    'gameplay_changed_since_c15': False,
    'art_changed_since_c15': False,
    'art_accepted': False,
    'goal_complete': False,
    'packaged_tests': reports,
    'files': [],
}
for source in sorted(windows.rglob('*')):
    if source.suffix.lower() in ('.exe', '.pak', '.ucas', '.utoc'):
        manifest['files'].append({'path': source.relative_to(build).as_posix(), 'bytes': source.stat().st_size, 'sha256': digest(source)})
(evidence / 'build-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

guide = (root / 'Builds/BrainAdventure-C15-20260907/Windows/START HERE.txt').read_text().split('NEW IN C15')[0].replace('checkpoint C15 /', 'checkpoint C15-R2 /')
guide += '''ABOUT THIS BUILD
Freshly packaged from the current C15 game, with a new packaged verification run.
Gameplay and art content are unchanged from C15.
Carrying, pushing, pulling, focusing, releasing worries and the return bridge
are included. The prior C15 build remains available.
The larger art and animation overhaul remains unfinished.
'''
(windows / 'START HERE.txt').write_text(guide, encoding='utf-8')
(build / 'Play.bat').write_text('@echo off\nstart "" "%~dp0Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
# Only switch the user's play shortcut after every packaged check has passed.
(root / 'Play Brain Adventure.bat').write_text('@echo off\nstart "" "%~dp0Builds\\BrainAdventure-C15-R2-20260907\\Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
print(json.dumps({'ready': True, 'launcher': str(build / 'Play.bat'), 'packaged_tests': reports}, indent=2))
