"""Fixed garden compositions: a spring blossom tree and crafted nest thresholds."""
# An asymmetric cherry tree grows from the damp spring bank. Branches are chosen
# to frame the water and remain above the walking envelope.
tx,ty=-2040,1880;_,tz,_=fields(tx,ty);tz=float(tz)
wood=[];petals=[];smallleaves=[]
paths=[([(0,0,0),(-25,9,155),(25,17,330),(15,32,530)],[35,29,20,5]),
       ([(8,10,240),(-75,-10,315),(-178,-17,368),(-243,-7,442)],[21,17,9,2]),
       ([(10,20,290),(111,29,365),(183,71,430),(207,120,505)],[20,14,8,2]),
       ([(5,18,380),(-49,87,447),(-81,140,554),(-126,177,610)],[17,11,7,2]),
       ([(10,25,429),(52,-43,492),(110,-111,568),(160,-120,634)],[16,11,6,2])]
tips=[]
for points,radii in paths:
    p=[(tx+x,ty+y,tz+z) for x,y,z in points];wood.append(tube('Spring tree gesture',p,radii,'Bark',props,18,10,.03));tips.append(np.array(p[-1]))
for i in range(6):
    a=i*math.tau/6;wood.append(tube('Spring tree mossy root',[(tx,ty,tz+60),(tx+49*math.cos(a),ty+49*math.sin(a),tz+13),(tx+87*math.cos(a),ty+87*math.sin(a),tz+3)],[22,15,2],'Bark',props,14,7))
add(merge(wood,'Spring cherry wood'),'SpringTreeWood',tags=['Interactive'])
for i,tip in enumerate(tips):
    for j in range(72):
        a=j*2.399;rr=math.sqrt(j/72)*137;p=tip+np.array((rr*math.cos(a),rr*math.sin(a),(j%7-3)*11))
        for k in range(5):
            b=a+k*math.tau/5;petals.append(leaf('Cherry blossom petal',p,(math.cos(b),math.sin(b),.3),22,14,(1,1,1),props,M['Blossom'],.29))
        if j%3==0:smallleaves.append(leaf('Young spring leaf',p,(math.cos(a),math.sin(a),.6),38,13,(1,1,1),props,M['Fern'],.25))
add(merge(petals+smallleaves,'Sculpted cherry canopy'),'SpringBlossomCanopy',tags=['Occluder','Foliage'])

# Three distinct nest mouths sit in built, rooted alcoves. The surrounding arch
# has large readable stones and a few engraved current marks, not loose clutter.
for i,(x,y,z) in enumerate(NESTS):
    frame=[];sill=[];r=228
    for j in range(19):
        a=j*math.pi/18
        frame.append(block('Nest arch voussoir',(x+r*math.cos(a),y-24,z+150+r*math.sin(a)),(82,119,77),(1,1,1),props,M['Stone'],a+math.pi/2,12,j+i))
    for sign in [-1,1]:
        for j in range(2):frame.append(block('Nest arch foot',(x+sign*r,y-24,z+49+j*73),(85,125,76),(1,1,1),props,M['Stone'],0,12,j))
    for j in range(5):sill.append(block('Nest fitted threshold',(x+(j-2)*89,y-109,z+10),(87,141,38),(1,1,1),props,M['Trim'],0,10,j))
    add(merge(frame+sill,'Nest sculpted surround'),f'NestSurround{i}',tags=['Interactive'])
    # Small roots grip the sill but keep the front approach empty.
    roots=[]
    for sign in [-1,1]:
        roots.append(tube('Nest root',[(x+sign*270,y+20,z+205),(x+sign*288,y-63,z+50),(x+sign*327,y-164,z+5)],[22,18,2],'Violet',props,14,8,.05))
    add(merge(roots,'Nest roots'),f'NestRoots{i}')

# A restrained row of rounded tissue stones and low ferns edges each destination.
# Only planted outer margins receive these details; the movement center stays open.
for district in DISTRICTS:
    if district['key']=='Spring':continue
    cx,cy,z=district['p'];rx,ry=district['r'];rocks=[];leaves=[]
    for i in range(18):
        a=i*2.399;x=cx+rx*.83*math.cos(a);y=cy+ry*.83*math.sin(a);dd,zz,rd=fields(x,y)
        if rd<110 or water(x,y)<100:continue
        rocks.append(orb('Layered garden bank stone',(x,y,float(zz)+17),(49+(i%3)*13,39,28),'Stone',props,20))
        for j in range(7):
            b=j*2.399;leaves.append(leaf('Bank clover fan',(x+35*math.cos(b),y+35*math.sin(b),float(zz)+27),(math.cos(b),math.sin(b),.55),35,15,(1,1,1),props,M['Fern'],.33))
    if rocks:add(merge(rocks,'Planted margin stones'),district['key']+'BankStones')
    if leaves:add(merge(leaves,'Planted margin leaves'),district['key']+'BankLeaves')
