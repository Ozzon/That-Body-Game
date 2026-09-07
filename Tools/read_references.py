from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from io import BytesIO
import zipfile,json
src=Path(r'C:/Users/Gamescom 2023 #1/Downloads/The body game.jam')
out=Path(__file__).resolve().parents[1]/'Docs'/'References'
out.mkdir(parents=True,exist_ok=True)
z=zipfile.ZipFile(src)
entries=[i for i in z.infolist() if i.filename.startswith('images/') and i.file_size>2000]
index=[]
for start in range(0,len(entries),100):
    sheet=Image.new('RGB',(1800,1400),'#e9e7e2')
    draw=ImageDraw.Draw(sheet)
    for j,info in enumerate(entries[start:start+100]):
        n=start+j
        try:
            im=Image.open(BytesIO(z.read(info))).convert('RGB')
            index.append({'number':n,'entry':info.filename,'width':im.width,'height':im.height})
            im.thumbnail((174,116))
            x=(j%10)*180; y=(j//10)*140
            sheet.paste(im,(x+(180-im.width)//2,y))
            draw.text((x+5,y+119),str(n),fill='black')
        except Exception as e: print(info.filename,str(e))
    sheet.save(out/f'reference-sheet-{start//100+1:02}.jpg',quality=88)
(out/'index.json').write_text(json.dumps(index,indent=2))
(out/'board-thumbnail.png').write_bytes(z.read('thumbnail.png'))
print('REFERENCE_IMAGES',len(entries),'SHEETS',(len(entries)+99)//100)
print(z.read('meta.json').decode())
