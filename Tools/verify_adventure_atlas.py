from pathlib import Path
import json
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];p=root/'Presentations/That Body Game — A Living Adventure.pdf';out=root/'Docs/Research/AtlasReview';out.mkdir(exist_ok=True)
d=pdfium.PdfDocument(str(p));reader=PdfReader(p);sheet=Image.new('RGB',(1680,((len(d)+3)//4)*320),'#e8e7e0');draw=ImageDraw.Draw(sheet)
for i,page in enumerate(d):
    im=page.render(scale=1).to_pil().convert('RGB');im.save(out/f'page-{i+1:02}.png');im.thumbnail((400,282));x=(i%4)*420;y=(i//4)*320;sheet.paste(im,(x,y));draw.text((x+10,y+290),str(i+1),fill='#263644')
sheet.save(out/'contact.png')
text='\n'.join(page.extract_text() or '' for page in reader.pages)
report=dict(pages=len(d),links=sum(len(page.get('/Annots',[])) for page in reader.pages),all_pages_have_text=all(bool(page.extract_text()) for page in reader.pages),missing_organ_titles=[x['title'] for x in json.loads((root/'Docs/Research/location-design.json').read_text()) if x['title'] not in text],visual_review='all-page contact sheet; full-size samples 1,2,3,4,7,9,21,25,26')
(out/'verification.json').write_text(json.dumps(report,indent=2));print(report)
