from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil

root = Path(__file__).resolve().parents[1]
build = root / 'Builds/BrainAdventure-C16-R2-20260907'
windows = build / 'Windows'
evidence = build / 'Evidence'


def read(path):
    raw = path.read_bytes()
    return raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8', errors='replace')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def report(kind, marker):
    path = root / f'Docs/brain-c16-r2-packaged-{kind}.log'
    log = read(path)
    match = re.search(marker + r' (\{[^\r\n]+\})', log)
    assert match, path
    result = json.loads(match.group(1))
    assert result['passed'], result
    assert 'LogExit: Exiting.' in log, path
    return result


assert read(root / 'Docs/brain-c16-r2-package-exit.txt').strip() == '0'
assert 'BUILD SUCCESSFUL' in read(root / 'Docs/brain-c16-r2-package.log')
checks = {
    'care': report('smoke', 'CRAFT_INPUT_REPORT'),
    'camera': report('controls', 'CRAFT_CAMERA_REPORT'),
    'traversal': report('roam', 'CRAFT_ROAM_REPORT'),
}
assert checks['care']['complete'] and checks['care']['physical_grabs'] >= 4
assert checks['traversal']['visited'] == 12 and checks['traversal']['fall_recoveries'] == 0
capture = read(root / 'Docs/brain-c16-r2-packaged-capture.log')
assert 'CRAFT_CLOTH_READY' in capture and 'LogExit: Exiting.' in capture
screens = sorted((windows / 'ThatBodyGame/Saved/Screenshots').glob('Brain-C16-*.png'))
assert len(screens) == 4, screens
cape_match = re.search(r'CRAFT_CAPE_REPORT stretch=([\d.]+) travel_cm=([\d.]+) resets=(\d+)', read(root / 'Docs/brain-c16-r2-packaged-smoke.log'))
assert cape_match
cape = {'max_stretch_ratio': float(cape_match[1]), 'max_travel_cm': float(cape_match[2]), 'resets': int(cape_match[3])}
assert cape['max_stretch_ratio'] < 1.25
previous = json.loads((root / 'Builds/BrainAdventure-C16-20260907/Evidence/build-manifest.json').read_text())
source_changes = [item['path'] for item in previous['source_files'] if sha(root / item['path']) != item['sha256']]
assert not source_changes, source_changes

evidence.mkdir(exist_ok=True)
for path in screens:
    shutil.copy2(path, evidence / path.name)
for path in (root / 'Docs').glob('brain-c16-r2-*'):
    if path.is_file():
        shutil.copy2(path, evidence / path.name)
shutil.copy2(root / 'Docs/BRAIN_C16_WORK.md', evidence)
shutil.copytree(root / 'Source', evidence / 'Source', dirs_exist_ok=True)
for name in ('rebuild_c16.ps1', 'check_c16_rebuild.ps1', 'deliver_c16_rebuild.py'):
    (evidence / 'Tools').mkdir(exist_ok=True)
    shutil.copy2(root / 'Tools' / name, evidence / 'Tools' / name)

manifest = {
    'checkpoint': 'C16-R2',
    'engine': '5.8',
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Fresh build/cook/package of C16; no gameplay or art changes.',
    'art_accepted': False,
    'goal_complete': False,
    'physical_controller_tested': False,
    'whole_garden_exploration_accepted': False,
    'source_changes_since_c16': source_changes,
    'packaged_tests': checks,
    'cape': cape,
    'files': [],
    'source_files': [],
    'native_assets': [],
}
for path in sorted(windows.rglob('*')):
    if path.suffix.lower() in ('.exe', '.pak', '.ucas', '.utoc'):
        manifest['files'].append({'path': path.relative_to(build).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)})
for path in sorted((evidence / 'Source').rglob('*')):
    if path.is_file():
        manifest['source_files'].append({'path': path.relative_to(evidence).as_posix(), 'sha256': sha(path)})
assets = sorted((root / 'Content/BrainCraft').rglob('*.uasset')) + [root / 'Content/Maps/BrainCraft.umap']
for path in assets:
    manifest['native_assets'].append({'path': path.relative_to(root).as_posix(), 'sha256': sha(path)})
(evidence / 'build-manifest.json').write_text(json.dumps(manifest, indent=2))
guide = (root / 'Builds/BrainAdventure-C16-20260907/Windows/START HERE.txt').read_text().replace('checkpoint C16 /', 'checkpoint C16-R2 /')
guide = guide.split('NEW IN C16')[0] + '''ABOUT THIS BUILD
Fresh Windows build of the current C16 project, packaged on 7 September 2026.
Includes C16 thought characters, carrying transitions and cape physics.
No additional gameplay or art changes since C16. The garden art overhaul is
still unfinished and is not represented as complete in this package.

The packaged care loop, camera controls and twelve-destination route passed.
Physical controller testing and unrestricted exploration acceptance remain open.
'''
(windows / 'START HERE.txt').write_text(guide)
(build / 'Play.bat').write_text('@echo off\nstart "" "%~dp0Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
(root / 'Play Brain Adventure.bat').write_text('@echo off\nstart "" "%~dp0Builds\\BrainAdventure-C16-R2-20260907\\Windows\\ThatBodyGame.exe" -windowed -ResX=1600 -ResY=1000\n')
print(json.dumps({'ready': True, 'launcher': str(build / 'Play.bat'), 'checks': checks, 'cape': cape}, indent=2))
