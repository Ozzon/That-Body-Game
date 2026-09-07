"""Render the source-grounded location design as an illustrated, linked PDF atlas."""
from pathlib import Path
import json,html,math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'Docs/Research';OUT=ROOT/'Presentations';OUT.mkdir(exist_ok=True)
LOC=json.loads((DATA/'location-design.json').read_text(encoding='utf-8'));SRC={x['id']:x for x in json.loads((DATA/'source-ledger.json').read_text(encoding='utf-8'))}
for n,f in [('Body','segoeui.ttf'),('Strong','seguisb.ttf'),('Bold','segoeuib.ttf')]:pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
W,H=1120,790;PAPER=HexColor('#F6F2E8');INK=HexColor('#263644');MUTED=HexColor('#677581');GREEN=HexColor('#5F897B');GOLD=HexColor('#B48646');LINE=HexColor('#D8D8CE');PDF=OUT/'That Body Game — A Living Adventure.pdf';c=canvas.Canvas(str(PDF),pagesize=(W,H));c.setTitle('That Body Game — A Living Adventure');c.setAuthor('That Body Game / research and location design');page=0;checks=[]

def text(s,x,y,size=11,color=INK,font='Body'):
    c.setFont(font,size);c.setFillColor(color);c.drawString(x,H-y-size*.80,s)
def para(s,x,y,w,size=10.8,leading=14.7,color=INK,font='Body',max_bottom=735):
    st=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=0)
    p=Paragraph(s,st);ww,hh=p.wrap(w,2000)
    if y+hh>max_bottom:raise RuntimeError(f'Page {page} text overflow {y+hh:.1f}: {s[:80]}')
    p.drawOn(c,x,H-y-hh);checks.append((page,x,y,w,hh));return y+hh
def block(title,s,x,y,w,size=10.8):
    text(title.upper(),x,y,8.9,GREEN,'Strong');return para(html.escape(s),x,y+18,w,size,size*1.35)+20
def line(x1,y1,x2,y2,color=LINE,width=1):c.setStrokeColor(color);c.setLineWidth(width);c.line(x1,H-y1,x2,H-y2)
def rect(x,y,w,h,color,r=0):
    c.setFillColor(color)
    if r:c.roundRect(x,H-y-h,w,h,r,stroke=0,fill=1)
    else:c.rect(x,H-y-h,w,h,stroke=0,fill=1)
def picture(p,x,y,w,h):
    im=Image.open(p);iw,ih=im.size;s=min(w/iw,h/ih);ww,hh=iw*s,ih*s
    c.drawImage(ImageReader(im),x+(w-ww)/2,H-y-hh,width=ww,height=hh,mask='auto');return hh
def start(kicker,title,subtitle=''):
    global page
    page+=1;rect(0,0,W,H,PAPER);text('THAT BODY GAME',48,25,10,INK,'Bold');text('A LIVING ADVENTURE',880,25,9,GREEN,'Strong');line(48,48,W-48,48)
    text(kicker.upper(),48,67,9,GREEN,'Strong');text(title,48,88,31,INK,'Strong')
    if subtitle:para(html.escape(subtitle),48,130,W-96,10.5,14.5,MUTED)
def foot():
    line(48,751,W-48,751);text('REFERENCE-LED LOCATION DESIGN  /  7 SEPTEMBER 2026',48,765,8,MUTED);text(f'{page:02}',1047,763,10,INK,'Strong');c.showPage()
def cite(ids,x,y,w):
    parts=[]
    for i in ids:
        s=SRC[i];parts.append(f'<a href="{html.escape(s["url"],quote=True)}" color="#496C76">{html.escape(s["title"])}</a> · {html.escape(s["publisher"])} · {html.escape(s["date"])}')
    return para('Sources: '+'<br/>'.join(parts),x,y,w,7.2,9.5,MUTED)
def diagram(d,x,y,w,h):
    accent=HexColor('#'+d['color']);rect(x,y,w,h,HexColor('#EAECE5'),8);nodes=d['nodes']
    def p(n):return x+w/2+n[0]*(w*.37),y+h/2-n[1]*(h*.34)
    for i,j in d['links']:
        a,b=p(nodes[i]),p(nodes[j]);line(*a,*b,HexColor('#A1B6A9'),5)
    for i,n in enumerate(nodes):
        xx,yy=p(n);c.setFillColor(accent);c.circle(xx,H-yy,11,stroke=0,fill=1);text(str(i+1),xx-3,yy-4.6,9,INK,'Strong')
        label=n[2];tw=pdfmetrics.stringWidth(label,'Strong',8);text(label,xx-tw/2,yy+15,8,INK,'Strong')
    text('ROUTE DIAGRAM · PROPOSED, NOT A MODEL RENDER',x+10,y+h-14,6.5,MUTED)

# The owner rejected the crowded single-diagram approach during implementation.
# This direction takes precedence over earlier candidate dimensions and layouts.
start('Design reset / 7 September 2026','Make each organ a world.','A clear body atlas for orientation. Large, independent organ interiors for play.')
picture(ROOT/'Docs/References/ref-275.png',48,185,655,435)
text('FIGMA VISION · CONCEPT ART, NOT THE CURRENT GAME',48,634,8,MUTED)
y=184
for a,b in [('A different structure','Stop fitting every playable organ into a single visible body diagram. Give each location its own scale, lighting, landmarks and movement.'),('A different camera','Frame Attention, the route and the next landmark. Seeing the entire organ belongs to the atlas, not the normal player view.'),('A different standard','A care action changes a place. A return route makes it familiar. More props, a larger bowl or a successful build do not establish quality.')]:y=block(a,b,751,y,321,12)
rect(751,615,321,82,HexColor('#E5E8DD'),7);para('This reset supersedes the crowded C01–C04 brain layouts. The approved Heart Model A remains protected. The other location briefs are design targets, not finished levels.',765,629,293,10,14)
foot()

start('Brain / spatial reset','Room for a journey.','Three legible places establish the first brain section. Additional brain districts must earn their own space and purpose.')
picture(ROOT/'Art/BrainGarden/Brain-garden-source.png',48,183,645,484)
text('C05 ACTUAL SOURCE MODEL · REJECTED BY OWNER · PRESERVED EVIDENCE',48,681,8,HexColor('#A46555'),'Strong')
y=185
for a,b in [('01 / Arrival meadow','Quiet ground, a readable Attention character, one bright thought and a view toward the tree.'),('02 / Awareness court','A smaller tree within a generous court. Bring thoughts to its roots; the main route continues past the water.'),('03 / Quiet thought garden','Cross the broad bridge, open the lotus and release worries. Restoration grows a root route back toward the arrival.'),('What changed','Landscape coordinates expand by 1.55 in both horizontal axes. The tree is reduced to 0.68 of its former size. Extra displays and competing paved loops are removed.'),('What is still missing','The candidate establishes room and a local care route. It still needs stronger cortical landforms, fitted transitions, richer surfaces and visual review at the player camera.')]:y=block(a,b,751,y,321,11.3)
foot()

# Cover: source art is explicitly distinguished from built work.
start('Research + art direction + full location designs','A whole world inside the body.','Every organ becomes a welcoming adventure location, with its own geography, inhabitants, movement and response to care.')
picture(ROOT/'Docs/References/ref-275.png',48,175,690,460)
text('OWNER’S FIGMA REFERENCE · THOUGHT GARDEN AND AWARENESS TREE',48,646,8,MUTED)
y=182
for title,s in [('One body, distinct places','Folded brain gardens. Wind-filled lung conservatories. A four-room heart that beats around you. Working digestive and recovery districts.'),('Crafted around Attention','Every arrival, bridge, tree, valve and garden has a spatial purpose. The small character remains readable and has room to move.'),('Research becomes a build brief','Fifteen complete location briefs, source-grounded anatomy, explicit modeling targets, camera rules and a production sequence.')]:y=block(title,s,782,y,290,12)
rect(782,600,290,87,HexColor('#E5E8DD'),7);para('The images labeled <b>Figma reference</b> are supplied concept art. The location plans are proposals. Current studies are explicitly identified; this atlas does not claim a finished game.',796,614,263,10,14)
foot()

start('01 / The visual correction','Match the large forms first.','The current models must be judged against a specific reference, at the same viewing scale.')
picture(ROOT/'Docs/References/ref-358.png',48,177,500,290);picture(ROOT/'Art/BrainGarden/Reviews/C03/Brain-garden-source.png',574,177,498,290)
text('FIGMA REFERENCE · EMBEDDED TERRACES, FOLDED CORTEX',48,475,8,GREEN,'Strong');text('CURRENT C03 MODEL STUDY · BELOW THE REFERENCE BAR',574,475,8,HexColor('#A46555'),'Strong')
items=[('Silhouette','Two cerebral masses and a smaller cerebellar district. Replace the repeated rim surrounding an oval floor.'),('Landform','Build gardens into substantial tissue terraces. Give ramps, bridges and retaining walls continuous, fitted joins.'),('Hero asset','The central tree needs a fused root base, deliberate crown, directional bark and luminous leaf clusters.'),('Surface + light','Separate tissue, soil, stone, bark and water. Concentrate brightness on care targets and restored landmarks.')]
for i,(a,b) in enumerate(items):block(a,b,48+(i%2)*526,515+(i//2)*99,490,11)
foot()

start('02 / Research findings','What strong adventure games contribute.','Specific design practices, translated into this project. These games inform construction and play; Figma remains the art authority.')
cards=[('Hob','Discover a route, then earn a short return. Restoration changes geography and keeps repeated care practical.','G1'),('Cocoon','Terrain follows the movement idea. Branching wind routes belong to lungs; valve gates belong to the heart.','G5'),('Link’s Awakening','Rich miniature craft is balanced against character scale. Judge details at the player camera, not only in close-ups.','G17'),('Psychonauts 2','A complete location integrates movement, purpose, art, animation and sound. Attractive scenery alone is an art test.','G15'),('Death’s Door','A few specific creature reactions make a place feel alive. Match action weight with coordinated sound and motion.','G11'),('The Last Campfire','Helping can drive an adventure. Care reveals new routes, restores inhabitants and makes a place worth revisiting.','G12')]
for i,(title,body,source) in enumerate(cards):
    x=48+(i%2)*526;y=180+(i//2)*180;rect(x,y,500,160,HexColor('#EAEBE2'),8);text(title,x+18,y+16,20,INK,'Strong');para(body,x+18,y+48,462,11.5,16);cite([source],x+18,y+107,462)
foot()

start('03 / World geography','Anatomy gives the world its structure.','Attention’s light bridges connect the locations. Air, blood, food and urine retain their own distinct routes.')
coords={'Brain':(365,209),'Throat':(365,292),'Right lung':(188,365),'Heart':(365,383),'Left lung':(542,365),'Liver':(226,474),'Stomach':(491,474),'Kidney R':(169,568),'Intestines':(365,567),'Kidney L':(561,568),'Bladder':(365,675)}
edges=[('Brain','Throat'),('Throat','Heart'),('Throat','Right lung'),('Throat','Left lung'),('Right lung','Heart'),('Left lung','Heart'),('Heart','Liver'),('Heart','Stomach'),('Liver','Intestines'),('Stomach','Intestines'),('Liver','Kidney R'),('Stomach','Kidney L'),('Kidney R','Bladder'),('Kidney L','Bladder'),('Intestines','Bladder')]
for a,b in edges:line(*coords[a],*coords[b],HexColor('#BCD3C0'),6)
for i,(n,(x,y)) in enumerate(coords.items()):
    col=HexColor('#DCCFE9') if n=='Brain' else HexColor('#EEC2B0') if n=='Heart' else HexColor('#B6D9D6') if 'lung' in n else HexColor('#E4D8BD');rect(x-62,y-22,124,44,col,17);tw=pdfmetrics.stringWidth(n,'Strong',12);text(n,x-tw/2,y-5,12,INK,'Strong')
text('SCHEMATIC CONNECTION PLAN · PROPORTIONS ARE NOT ANATOMICAL',48,714,7.5,MUTED)
y=183
for title,s in [('Crown','Brain gardens, the awareness tree and the cerebellar movement district.'),('Chest','Heart between asymmetric lungs; a throat ascent above and the guardian cloister beside it.'),('Digestive crossing','Stomach, liver and intestinal routes, with pancreatic, bile and spleen side gardens.'),('Recovery region','Twin kidney springs, signal observatories, the colon promenade and quiet bladder reservoir.'),('Keep the flows distinct','The luminous walking network is fantasy. Real anatomical connections guide the subordinate air, blood, food and urine systems.')]:y=block(title,s,728,y,344,11)
cite(['A2','A3','A5','A9','A10'],728,650,344);foot()

start('04 / Exploration + daily care','A full location can still be quick to revisit.','First-time discovery opens the world. Restored shortcuts support the faster rhythm of daily events.')
steps=['ARRIVE','NOTICE','CHOOSE','TRAVERSE','CARE','TRANSFORM','RETURN']
for i,label in enumerate(steps):
    x=48+i*148;rect(x,190,133,53,HexColor('#DDE5D9'),7);text(str(i+1),x+12,201,12,GREEN,'Bold');text(label,x+12,221,8.2,INK,'Strong')
    if i<6:line(x+133,217,x+148,217,GREEN,2)
y=287
for title,s in [('The first visit','A destination appears before the fork. A side curiosity gives a short detour. One signature traversal creates a memorable moment. Care changes the space and opens a return.'),('The familiar visit','The receiving station and the express return remain easy to reach. Optional groves, balconies and inhabitants still reward exploration. Repeated care does not demand repeating every puzzle.'),('During a stressful event','The same routes carry changed wind, rhythm or weight. Effects communicate body state while leaving the player a readable, recoverable route.')]:y=block(title,s,48,y,465,12)
y=287
for title,s in [('Shared verbs','Move, tap, hold, pull, carry, place and release. Each organ changes the situation around these actions. Avoid a new control scheme or inventory for every location.'),('Spatial targets to test','Attention is about 1 m wide and 1.5 m tall in the enlarged world. Begin with 3.6–4.5 m paths, broad bridge landings and 7–10 m care courts. These are proposed game dimensions, not anatomical measurements.'),('Camera targets to test','A normal view covers roughly 30–42 m. Author the arrival view individually; retain full orbit, zoom and pan. Fade occasional foreground scenery while keeping interactive targets visible.')]:y=block(title,s,607,y,465,12)
cite(['G1','G14'],48,677,1024);foot()

for index,d in enumerate(LOC):
    start(f'{index+5:02} / Full location design · {d["organ"]}',d['title'],d['promise'])
    x1,x2,x3=48,407,752;w1,w2,w3=325,311,320
    ref=d['refs'][0];p=ROOT/'Docs/References'/f'ref-{ref}.png'
    if d['organ']=='Heart':p=ROOT/'Art/Approved/Heart-owner-approved-2026-09-07.png'
    picture(p,x1,182,w1,180);text('APPROVED HEART MODEL' if d['organ']=='Heart' else 'OWNER’S FIGMA REFERENCE' if ref!=298 else 'FIGMA WHOLE-BODY CONTEXT · DETAIL DESIGN PROPOSED',x1,367,7.0,MUTED)
    y=389;y=block('Recognizable structure',d['anatomy'],x1,y,w1,10.2)
    diagram(d,x1,max(y,502),w1,139)
    para(html.escape(d['size']),x1,max(y,502)+151,w1,9.2,12.5,MUTED)
    y=182;y=block('Arrival view',d['arrival'],x2,y,w2,10.4)
    text('THE JOURNEY',x2,y,8.9,GREEN,'Strong');y+=19
    for j,s in enumerate(d['route']):
        y=para(f'<b>{j+1:02}</b>  '+html.escape(s),x2,y,w2,10.4,14)+10
    y=block('Care interaction',d['care'],x2,y+4,w2,10.4)
    y=182;text('MODELED AS A PLACE',x3,y,8.9,GREEN,'Strong');y+=19
    for s in d['models']:y=para('• '+html.escape(s),x3,y,w3,10.2,13.7)+7
    y=block('Material + color',d['material'],x3,y+7,w3,10.2)
    y=block('Visible response',d['change'],x3,y,w3,10.2)
    y=block('Return shortcut',d['shortcut'],x3,y,w3,10.2)
    # Cite anatomy near its column, with a compact full descriptive source note.
    cite(d['sources'][:1],x2,690,w2)
    text('LOCATION DESIGN PROPOSAL · BUILT STATUS IS SEPARATE',x3,727,7,MUTED)
    foot()

start('20 / Inhabitants + character','Wacky movement. Clear intentions.','Give life to a small cast through specific behavior, readable weight and coordinated care responses.')
picture(ROOT/'Docs/References/ref-379.png',48,180,455,360);text('OWNER’S FIGMA REFERENCE · ATTENTION CHARACTER',48,552,8,MUTED)
y=180
for title,s in [('Attention','Keep the sage hood, warm face and short cape. Anticipate a sprint with a small lean; reach for a bright thought; compress on landing. Oversized parcels change the gait. Feet remain predictable.'),('A small living cast','Blood couriers queue and wave. Air keepers inflate briefly. Thought creatures peek from nests. Filter keepers polish useful droplets. Guardian trainees practice and occasionally fumble.'),('A care action has a readable arc','Anticipation → contact → response → recovery. The diaphragm tensions before moving. A valve rebounds after a tap. The tree receives light through roots before its leaves brighten.'),('Designed places for the inhabitants','Use alcoves, receiving courts and sheltered benches. Keep bridge mouths and camera sightlines open. One memorable reaction is more useful than constant particle motion.')]:y=block(title,s,565,y,507,12)
cite(['G10','G11'],48,620,455);foot()

start('21 / Model construction','Craft the joins. Then craft the details.','A consistent material family and deliberate construction make different organs feel like parts of one living world.')
columns=[('PRIMARY FORMS',[('Organ + landform','Recognizable organ mass, major subdivisions, two or three meaningful terrain changes and one dominant landmark.'),('Player-scale review','Inspect the silhouette with Attention in the scene. Compare the reference angle, default camera and reverse view before decoration.'),('Continuous construction','Floors meet walls. Roots enter soil. Arches meet their supports. Every bridge has a continuous deck, abutments and a clear landing.')]),('SECONDARY FORMS',[('The organ’s character','Cortex folds, lung branches, stomach rugae, heart valve leaflets and renal terraces follow each organ’s structural logic.'),('A few authored assets','Build a tree, a valve or a grove with its own silhouette and material response. Avoid repeating one primitive as a substitute for a whole district.'),('Readable routes','Use path widths, low retaining edges and opening silhouettes to show where Attention can move. A good default view does not depend on constant fading.')]),('TERTIARY FORMS',[('Surface distinction','Mild tissue sheen, matte soil, directional bark, rough stone, membrane highlights and local water reflections.'),('Placed small detail','Paving joints, leaf veins, bark channels and fine tissue grain support the large forms. Keep the walking surface calm.'),('Light + movement','Brightness belongs to useful resources and restored landmarks. Motion travels through connected structures rather than wobbling every prop independently.')])]
for i,(title,rows) in enumerate(columns):
    x=48+i*351;rect(x,186,324,47,HexColor('#DFE6D9'),7);text(title,x+16,203,11,GREEN,'Bold');y=260
    for a,b in rows:y=block(a,b,x,y,324,12)
cite(['G13','G17','G19'],48,650,1024);foot()

start('22 / Acceptance and implementation','Quality is visible in the player’s journey.','A high triangle count, a successful import and a connected route are useful technical checks. They do not establish art acceptance.')
y=183
for a,b in [('Preserve','Keep the approved heart source and the rejected model studies as evidence. Avoid overwriting the chosen baseline with a new generic shell.'),('Finish the brain first','Match cortex massing, embedded terraces and the awareness tree. Build thought habitats, fitted crossings and one physical care-driven return route. Review the actual player views.'),('Then the lungs and heart','Build one complete branch–grove–wind experience before repeating it across lobes. Give the accepted heart distinct chamber functions, valves and courier flow.'),('Extend the complete standard','Take the same arrival, journey, care, transformation and return structure into every digestive, recovery and smaller body location.')]:y=block(a,b,48,y,477,12)
y=183
for a,b in [('Visual review','Reference-corresponding silhouette and layout; strong hero asset; distinct materials; controlled lighting; clear floor; no arbitrary tube or prop scatter.'),('Playable review','Real input completes the route, turns while carrying, reaches every care target, shows a visible response and uses the return route. Check reverse-camera views and occlusion.'),('Current status','The atlas defines fifteen locations. Most are not built. Brain C05 is a larger independent candidate; C01–C04 and the original lungs are rejected. The approved heart is a shell baseline. Neither the atlas nor a technical checkpoint establishes finished art.'),('What remains uncertain','Exact camera framing, clearances, timing and density require modeled views and play. Some organ microstructure needs dedicated anatomical plates before final sculpting.')]:y=block(a,b,592,y,480,12)
cite(['G14','G15'],48,680,1024);foot()

start('23 / Source boundaries','Keep the fantasy intentional.','The body’s recognizable structures support the world. Garden architecture and the actions of Attention are deliberate game metaphors.')
y=184
for a,b in [('Verified source package','The local FigJam package supplied the illustrated references. Design v11 supplies the original care vocabulary and daily-event rhythm. Later owner instructions require full organ locations and a central brain tree.'),('Research coverage','Two independent research lanes examined primary creator accounts and NIH anatomy, followed by focused gap checks. The coordinator checked the most consequential claims and inspected the high-resolution local art.'),('Why broad research stops here','Evidence converges on location identity, purposeful routes, visible restoration and crafted construction. More inspirational titles would not resolve the current geometry and material mismatches. The next evidence must come from models and play.')]:y=block(a,b,48,y,477,12)
y=184
for a,b in [('Anatomy and scale','Air, blood, food and urine keep separate routes. Attention travels on fictional light bridges. Microscopic structures become enlarged architecture; dimensions in this atlas are proposed game-scale targets.'),('Design-document corrections','Use calm signals, stress mist and clarity ripples as fiction. Adrenal glands do not make a vagal hormone, and research does not establish a guaranteed theta-wave mechanism that permanently dissolves thoughts.'),('Access limits','Some brain-anatomy pages were available as indexed text while direct opens failed. The Tunic GDC record was an abstract, not a watched talk. Creator interviews support design practice, not universal room-size or density rules.')]:y=block(a,b,592,y,480,12)
cite(['F1','F2'],48,628,477);cite(['A11','A15'],592,628,480);foot()
c.save();(DATA/'atlas-layout-audit.json').write_text(json.dumps(dict(pages=page,text_blocks=len(checks),overflow_checks='passed',source_images='Figma references and explicitly labeled current/approved model renders',pdf=str(PDF)),indent=2));print('ATLAS_RENDERED',page,'pages',PDF)
