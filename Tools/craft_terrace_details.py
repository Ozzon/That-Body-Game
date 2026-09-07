"""Authored spring cascades, layered banks and raked arrival garden.

Executed in the Blender scene builder's namespace. Each piece follows a fixed
garden feature. Nothing is distributed over the playable center of a path.
"""

# Stone-lined water banks cover the grid boundary and expose the vertical relief.
banks=[];moss_caps=[]
channel=curve([(-1630,1510),(-1930,900),(-1700,380),(-1210,-50),(-970,-630)],9,False)
for i in range(0,len(channel)-1,2):
    p=channel[i];t=channel[min(i+1,len(channel)-1)]-channel[max(0,i-1)];a=math.atan2(t[1],t[0]);side=np.array((-math.sin(a),math.cos(a)))
    for sign in [-1,1]:
        q=p+side*sign*118;_,z,_=fields(q[0],q[1]);z=float(z)
        if min(float(distance(q[0],q[1],curve(r['points'],8,False),False)-r['width']/2) for r in ROUTES)<45:continue
        banks.append(block('Watercourse fitted bank',(q[0],q[1],z-48),(101,65,124),(1,1,1),stone,M['Stone'],a,13,i))
        if i%4==0:moss_caps.append(orb('Moss on damp bank',(q[0],q[1],z+12),(55,29,12),'Moss',stone,16))

def basin(name,c,rx,ry,bottom,spout_width=90):
    x,y,z=c;parts=[];count=32
    for i in range(count):
        a=math.tau*(i+.5)/count
        # An actual opening in the front coping lets the spill leave the basin.
        spill=abs(math.cos(a))*rx<spout_width and math.sin(a)<-.75
        zz=z-24 if spill else z+6
        for row in range(max(1,int((zz-bottom)/73))):
            bz=zz-35-row*73
            parts.append(block('Terraced spring masonry',(x+rx*math.cos(a),y+ry*math.sin(a),bz),(math.tau*(rx+ry)/2/count+5,84,75),(1,1,1),stone,M['Stone'],a+math.pi/2,12,row+i))
        if not spill:parts.append(block('Warm coping on spring',(x+rx*math.cos(a),y+ry*math.sin(a),z+9),(math.tau*(rx+ry)/2/count+2,99,33),(1,1,1),stone,M['Trim'],a+math.pi/2,10,i))
    add(merge(parts,name+' bank'),name+'Bank',tags=['Interactive'])
    verts=[(x,y,z-17)];faces=[]
    for i in range(97):
        a=i*math.tau/96;verts.append((x+(rx-35)*math.cos(a),y+(ry-35)*math.sin(a),z-17))
        if i:faces.append((0,i,i+1))
    add(raw(name+' water',verts,faces,'Water'),name+'Water',tags=['Water'])

basin('UpperSpring',(-1680,1780,1410),255,230,1035)
basin('MiddleSpring',(-1680,1330,1220),280,220,1035)

def waterfall(name,x,y,z,run,drop,width):
    verts=[];faces=[];foam=[]
    for row in range(25):
        t=row/24;yy=y-run*t;zz=z-drop*t*t
        for col in range(13):
            u=col/12;xx=x+(u-.5)*width;verts.append((xx,yy+math.sin(u*math.pi*5)*3,zz+math.sin(u*math.pi*7)*2))
            if row and col:q=(row-1)*13+col-1;faces.append((q,q+1,q+14,q+13))
    add(raw(name,verts,faces,'Water'),name,tags=['Water'])
    for i in range(12):
        a=i*2.399;r=math.sqrt(i/12)*width*.55;foam.append(orb('Foam at water contact',(x+math.cos(a)*r,y-run+math.sin(a)*r*.35,z-drop+5),(18,11,4),'Foam',props,12))
    add(merge(foam,'Soft cascade contact'),name+'Foam')

waterfall('UpperCascade',-1680,1555,1392,140,190,152)
waterfall('LowerCascade',-1680,1120,1202,154,145,160)
# Thin grooves and carved rings on a rooted spring lantern, its own landmark.
lantern=[]
lantern+=masonry_ring((-1680,1820,1390),104,18,49,58,'Stone')
lantern.append(orb('Spring pearl',(-1680,1820,1515),(31,31,88),'Current'))
for i in range(6):
    a=i*math.tau/6;lantern.append(tube('Spring flower stamen',[(-1680+70*math.cos(a),1820+70*math.sin(a),1430),(-1680+91*math.cos(a),1820+91*math.sin(a),1480),(-1680+35*math.cos(a),1820+35*math.sin(a),1500)],[10,7,2],'Trim'))
add(merge(lantern,'Spring lantern'),'SpringLantern',tags=['Interactive'])
if banks:add(merge(banks,'Fitted stream banks'),'StreamBanks',tags=['Occluder'])
if moss_caps:add(merge(moss_caps,'Damp moss coping'),'BankMoss')

# A quiet pocket of combed sand, offset from the arrival's direct movement line.
cx,cy=-2040,-2030;_,cz,_=fields(cx,cy);cz=float(cz)
v=[(cx,cy,cz+3)];f=[]
for i in range(97):
    a=i*math.tau/96;v.append((cx+240*math.cos(a),cy+190*math.sin(a),cz+3))
    if i:f.append((0,i,i+1))
add(raw('Quiet raked sand bed',v,f,'Linen'),'RakedSand')
grooves=[]
for row in range(8):
    r=36+row*23;pts=[]
    for a in np.linspace(.14,math.tau-.14,73):pts.append((cx+r*math.cos(a),cy+r*.76*math.sin(a),cz+5))
    grooves.append(tube('Combed sand curve',pts,[1.6,1.6,1.6],'Earth',props,5,2))
add(merge(grooves,'Raked sand lines'),'SandGrooves')
