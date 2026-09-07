"""Editable sculptural modeling helpers for the organ garden levels."""
import bpy,numpy as np,math
from mathutils import Vector
from organ_math import curve

def collection(name):
    c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);return c
def material(name,emission=0,roughness=.65):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');v=m.node_tree.nodes.new('ShaderNodeVertexColor');v.layer_name='HeartColor';m.node_tree.links.new(v.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=roughness
    if emission:m.node_tree.links.new(v.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=emission
    p.inputs['Subsurface Weight'].default_value=.045
    return m
def mesh(name,V,F,C,coll,mat,N=None):
    me=bpy.data.meshes.new(name);me.from_pydata(V,[],F);me.update();o=bpy.data.objects.new(name,me);coll.objects.link(o);me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    col=np.array(C,float)
    if col.ndim==1:col=np.tile(col,(len(V),1))
    a=me.color_attributes.new(name='HeartColor',type='FLOAT_COLOR',domain='POINT');a.data.foreach_set('color',np.column_stack([col,np.ones(len(V))]).ravel())
    if N is not None:me.normals_split_custom_set_from_vertices(N)
    return o
def merge(objects,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
def ellipsoid(name,p,s,color,coll,mat,seed=0,segments=24,rings=14):
    V=[];F=[];C=[]
    for i in range(rings+1):
        a=i*math.pi/rings
        for j in range(segments):
            b=j*math.tau/segments;noise=1+.035*math.sin(b*3+a*4+seed)+.018*math.cos(b*5-a*7)
            V.append((p[0]+s[0]*math.sin(a)*math.cos(b)*noise,p[1]+s[1]*math.sin(a)*math.sin(b)*noise,p[2]+s[2]*math.cos(a)*noise));C.append(np.array(color)*(.86+.13*(1+math.cos(a))*.5))
            if i<rings:q=i*segments+j;k=i*segments+(j+1)%segments;F.append((q,k,k+segments,q+segments))
    return mesh(name,V,F,C,coll,mat)
def sweep(name,points,radii,color,coll,mat,sides=24,sub=8,ridge=.025):
    pts=curve(points,sub,False);V=[];F=[];C=[]
    for i,p in enumerate(pts):
        t=i/(len(pts)-1);r=float(np.interp(t,np.linspace(0,1,len(radii)),radii));forward=Vector(pts[min(len(pts)-1,i+1)]-pts[max(0,i-1)]).normalized();u=forward.cross(Vector((0,0,1))).normalized()
        if u.length<.1:u=Vector((1,0,0))
        v=forward.cross(u).normalized()
        for j in range(sides):
            a=j*math.tau/sides;rib=math.cos(a*7+t*17)+.35*math.sin(a*13-t*11);rr=r*(1+ridge*rib)
            V.append(tuple(Vector(p)+rr*(math.cos(a)*u+math.sin(a)*v)));C.append(np.array(color)*(.87+.07*rib+.1*t))
            if i:q=(i-1)*sides+j;k=(i-1)*sides+(j+1)%sides;F.append((q,k,k+sides,q+sides))
    # Sealed tapered ends are part of the branch, not blunt cylinder caps.
    for end in [0,len(pts)-1]:
        k=len(V);V.append(tuple(pts[end]));C.append(color)
        for j in range(sides):a=end*sides+j;b=end*sides+(j+1)%sides;F.append((k,b,a) if end==0 else (k,a,b))
    return mesh(name,V,F,C,coll,mat)
def leaf(name,p,direction,length,width,color,coll,mat,curl=.25):
    axis=Vector(direction).normalized();side=axis.cross(Vector((0,0,1))).normalized()
    if side.length<.1:side=Vector((1,0,0))
    up=side.cross(axis).normalized();V=[];F=[];C=[];rows=7
    for layer in [-1,1]:
        for i in range(rows+1):
            t=i/rows;w=width*math.sin(math.pi*t)**.72
            for k in [-1,0,1]:
                q=Vector(p)+axis*length*t+side*w*k+up*(length*curl*math.sin(math.pi*t)-abs(k)*w*.20+layer*1.2)
                V.append(tuple(q));C.append(np.array(color)*(.78+.22*t+.04*(k==0)))
        start=0 if layer==-1 else (rows+1)*3
        for i in range(rows):
            for j in range(2):a=start+i*3+j;face=(a,a+1,a+4,a+3);F.append(face if layer==1 else face[::-1])
    return mesh(name,V,F,C,coll,mat)
def block(name,p,size,color,coll,mat,angle=0,bevel=6,seed=0):
    # An eight-corner chamfered block with real side faces and a soft rolled top.
    x,y,z=p;w,d,h=size;c,s=math.cos(angle),math.sin(angle);b=min(bevel,w*.2,d*.2)
    profile=[(-w/2+b,-d/2),(w/2-b,-d/2),(w/2,-d/2+b),(w/2,d/2-b),(w/2-b,d/2),(-w/2+b,d/2),(-w/2,d/2-b),(-w/2,-d/2+b)]
    V=[];C=[];F=[]
    for inset,zz in [(0,-h/2),(0,h/2-b),(b*.5,h/2)]:
        for i,(a,k) in enumerate(profile):
            a-=np.sign(a)*inset;k-=np.sign(k)*inset;V.append((x+a*c-k*s,y+a*s+k*c,z+zz));C.append(np.array(color)*(1+.025*math.sin(seed*1.7+i)))
    for l in range(2):
        for i in range(8):j=(i+1)%8;F.append((l*8+i,l*8+j,(l+1)*8+j,(l+1)*8+i))
    F.append(tuple(range(16,24)));F.append(tuple(range(7,-1,-1)))
    return mesh(name,V,F,C,coll,mat)
