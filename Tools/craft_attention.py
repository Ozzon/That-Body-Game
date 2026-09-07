"""Attention's tailored costume, modeled from Figma ref-379.

Separate pivot meshes preserve the existing playable animation rig.
"""
def garment(name,rings,material,coll=cast,open_angle=0):
    v=[];f=[];sides=80
    for j,(z,rx,ry,cx) in enumerate(rings):
        for k in range(sides+1):
            a=open_angle+(math.tau-open_angle*2)*k/sides
            fold=1+.025*math.cos(a*9)*max(0,1-j/len(rings))
            v.append((cx+rx*math.cos(a)*fold,ry*math.sin(a)*fold,z))
            if j and k:q=(j-1)*(sides+1)+k-1;f.append((q,q+1,q+sides+2,q+sides+1))
    o=raw(name,v,f,material,coll);s=o.modifiers.new('Tailored fabric thickness','SOLIDIFY');s.thickness=1.5;return o

# Hood silhouette has a soft peak, a closed rear and a fitted rounded triangle
# around the face. The front is a real opening with a rolled fabric lining.
v=[];f=[];rows=24;sides=96
def hood_edge(a,scale=1):
    return (scale*42*math.sin(a)*(1-.16*math.cos(a)),135+scale*47*math.cos(a))
for j in range(rows):
    t=j/(rows-1);rr=max(.005,math.sin(t*math.pi/2)**.58);xx=-48+84*t
    for k in range(sides):
        a=k*math.tau/sides;y,z=hood_edge(a,rr);z+=7*(1-t)*max(0,math.cos(a));xx1=xx-5*(1-t)*max(0,math.cos(a))
        v.append((xx1,y,z))
        if j:q=(j-1)*sides+k;n=(j-1)*sides+(k+1)%sides;f.append((q,n,n+sides,q+sides))
head=[raw('Sculpted closed hood',v,f,'Sage',cast)]
rim=[(36,*hood_edge(a)) for a in np.linspace(0,math.tau,97)]
head.append(tube('Rolled hood lining',rim,[3.7,3.7,3.7],'Linen',cast,12,2))
v=[];f=[]
for row in range(17):
    t=max(.005,row/16)
    for k in range(96):
        a=k*math.tau/96;y,z=hood_edge(a,t*.88);v.append((42-14*t*t,y,z))
        if row:q=(row-1)*96+k;n=(row-1)*96+(k+1)%96;f.append((q,n,n+96,q+96))
head.append(raw('Warm rounded attention face',v,f,'Face',cast))
for i in range(34):
    a=.10+i*(math.tau-.20)/34;y,z=hood_edge(a,1.10)
    head.append(tube('Hood embroidery stitch',[(32,y,z),(32,*hood_edge(a+.028,1.10))],[.66,.66],'Trim',cast,5,2))
    if i%3==0:
        y2,z2=hood_edge(a+.035,1.18);head.append(tube('Hood leaf motif',[(32,y,z),(30,y2,z2),(32,*hood_edge(a+.08,1.10))],[.55,.9,.45],'Trim',cast,6,3))
add(merge(head,'Attention tailored hood'),'AttentionHead',False)
eyes=[orb('Warm face eye',(43,side*12,134),(1.4,3.1,5.6),'Ink',cast,20) for side in [-1,1]]
add(merge(eyes,'Attention expressive eyes'),'AttentionEyes',False)

cape=[garment('Flowing shoulder cape',[(38,51,48,-3),(43,50,47,-3),(61,45,43,-2),(83,37,35,-1),(104,29,29,0),(111,27,27,0)],'Sage',open_angle=.66)]
hem=[(-3+51*math.cos(a),48*math.sin(a),40) for a in np.linspace(.66,math.tau-.66,96)]
cape.append(tube('Cream cloak hem',hem,[2.9,2.9,2.9],'Linen',cast,10,2))
for i in range(46):
    a=.69+i*(math.tau-1.38)/46;cape.append(tube('Cloak hem running stitch',[(-3+49*math.cos(a),46*math.sin(a),47),(-3+49*math.cos(a+.044),46*math.sin(a+.044),47)],[.6,.6],'Trim',cast,5,2))
# A single botanical embroidery motif belongs on the back, not scattered symbols.
cape.append(tube('Cloak awareness stem',[(-51,0,48),(-48,0,62),(-43,0,78),(-39,0,88)],[.9,1.0,.5],'Trim',cast,6,5))
for row in range(3):
    z=57+row*9;x=-49+row*3
    for sign in [-1,1]:cape.append(tube('Cloak embroidered leaf',[(x,0,z),(x+1,sign*8,z+6),(x+2,sign*10,z+10),(x+1,sign*3,z+8),(x,0,z)],[.65,.8,.65],'Trim',cast,6,3))
add(merge(cape,'Attention embroidered cape'),'AttentionCape',False)

body=[garment('A-line linen tunic',[(34,36,39,0),(39,37,40,0),(63,33,35,0),(85,29,29,0),(104,28,28,0)],'Linen')]
for row in range(3):
    pts=[(30*math.cos(a),31*math.sin(a),104+row*3+3*math.sin(a*2+row*.6)) for a in np.linspace(0,math.tau,81)]
    body.append(tube('Folded scarf layer',pts,[4,4,4],'Linen',cast,12,2))
body.append(block('Scarf leather clasp',(29,-15,109),(6,9,20),(1,1,1),cast,M['Leather'],0,2,0))
for row in range(3):
    zz=49+row*10;body.append(tube('Apron embroidered stem',[(35,0,zz),(34,0,zz+10)],[.75,.75],'Trim',cast,6,2))
    for side in [-1,1]:body.append(tube('Apron embroidered leaf',[(35,0,zz),(35,side*7,zz+6),(35,side*5,zz+10),(35,0,zz+3)],[.6,.75,.5],'Trim',cast,6,3))
add(merge(body,'Attention linen tunic and scarf'),'AttentionBody',False)
for side in [-1,1]:
    tag='L' if side<0 else 'R'
    arm=[garment('Cuffed sleeve',[(-33,17,17,2),(-29,18,18,2),(-15,15,15,0),(4,13,13,0)],'Sage')]
    arm.append(tube('Linen sleeve cuff',[(2+18*math.cos(a),18*math.sin(a),-29) for a in np.linspace(0,math.tau,49)],[2.7,2.7,2.7],'Linen',cast,10,2))
    arm.append(orb('Little mitten palm',(3,0,-40),(11,10,12),'Linen',cast))
    arm.append(orb('Mitten thumb',(9,-side*8,-38),(6,5,8),'Linen',cast,20))
    for j in range(3):arm.append(tube('Mitten seam',[(10,j*4-4,-40),(11,j*4-4,-47)],[.5,.5],'Trim',cast,5,2))
    add(merge(arm,'Attention sleeve and hand'),'AttentionArm'+tag,False)
    boot=[garment('Gathered trouser',[(7,13,14,0),(20,14,15,0),(35,12,13,0)],'Leather'),orb('Soft boot upper',(8,0,2),(22,14,11),'Leather',cast)]
    boot.append(block('Rounded boot sole',(8,0,-5),(43,29,7),(1,1,1),cast,M['Leather'],0,7,0))
    for k in range(5):
        z=8+k*3;boot.append(tube('Wrapped boot lace',[(14,-12,z),(17,0,z+2),(14,12,z+4)],[1.1,1.1,1.1],'Linen',cast,6,3))
    boot.append(tube('Boot toe seam',[(18,-12,2),(25,-8,7),(28,0,9),(25,8,7),(18,12,2)],[.7,.7,.7],'Trim',cast,6,3))
    add(merge(boot,'Attention soft walking boot'),'AttentionBoot'+tag,False)
