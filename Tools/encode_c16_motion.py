"""Encode unaltered native frames as separate, explicitly labelled motion clips."""
from pathlib import Path
import csv,json,subprocess,shutil,html
root=Path(__file__).resolve().parents[1]
src=root/'Saved/BrainFilm/C16-Front';out=root/'Art/BrainCraft/Reviews/C16-Motion'
out.mkdir(exist_ok=True)
rows=[(int(r[0]),float(r[1]),int(r[2])) for r in csv.reader((src/'frames.csv').open())]
groups=[]
for row in rows:
    if not groups or row[2]!=groups[-1][-1][2] or row[1]-groups[-1][-1][1]>.12:groups.append([])
    groups[-1].append(row)
names={1:'Reaching and picking up',2:'Carrying a bright thought',13:'Finding calm',16:'Handling the heavy thought',19:'Brushing away a wisp',21:'Loosening the amber knot',24:'Walking the return crossing'}
clips=[]
ffmpeg=shutil.which('ffmpeg');assert ffmpeg
for idx,group in enumerate(groups):
    if len(group)<3:continue
    lines=[]
    for j,(frame,time,stage) in enumerate(group):
        path=src/f'Frame{frame:05d}.png';assert path.exists(),path
        duration=group[j+1][1]-time if j+1<len(group) else .05
        escaped=path.as_posix().replace("'", "'\\''")
        lines.extend([f"file '{escaped}'",f'duration {duration:.5f}'])
    listing=out/f'clip-{idx:02d}.txt';listing.write_text('\n'.join(lines))
    video=out/f'clip-{idx:02d}.mp4'
    subprocess.run([ffmpeg,'-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-an','-vf','fps=20','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    clips.append({'title':names.get(group[0][2],'Native interaction'),'file':video.name,'frames':len(group),'stage':group[0][2]})
page='''<!doctype html><meta charset="utf-8"><title>C16 native motion study</title>
<style>body{background:#18242d;color:#eee6d6;font:17px system-ui;margin:40px auto;max-width:1120px}h1{font-size:30px}p{line-height:1.6;color:#c5cdcc}video{width:100%;border-radius:12px;background:#0b1218}section{margin:40px 0}small{color:#b7c8c5}</style>
<h1>Attention &amp; thoughts — C16</h1><p>Unaltered native Unreal frames from the actual garden care route. These are separate interaction clips, recorded at fixed simulation timing. They show animation and contact; they are not frame-rate benchmarks or final art acceptance.</p>'''
for clip in clips:page+=f'<section><h2>{html.escape(clip["title"])}</h2><video controls loop muted preload="metadata" src="{clip["file"]}"></video></section>'
(out/'index.html').write_text(page,encoding='utf-8');(out/'clips.json').write_text(json.dumps(clips,indent=2))
print(json.dumps({'clips':len(clips),'review':str(out/'index.html')},indent=2))
