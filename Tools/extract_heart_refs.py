from pathlib import Path
import json, zipfile
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'Docs/References/index.json').read_text())
with zipfile.ZipFile(r'C:/Users/Gamescom 2023 #1/Downloads/The body game.jam') as z:
    for n in [13,61,86,99,379]:
        item=next(i for i in items if i['number']==n)
        (root/f'Docs/References/ref-{n}.png').write_bytes(z.read(item['entry']))
