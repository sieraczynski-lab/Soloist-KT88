import sys
sys.path.insert(0,'.')
import stepw
orig=stepw.prism
recs=[]
def rec_prism(name,color,outer,holes,*a,**k):
    recs.append((name,outer,holes)); return orig(name,color,outer,holes,*a,**k)
stepw.prism=rec_prism
import model
def segs(loop): return [(loop[i],loop[(i+1)%len(loop)]) for i in range(len(loop))]
def inter(a,b,c,d):
    def o(p,q,r): return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    d1,d2,d3,d4=o(a,b,c),o(a,b,d),o(c,d,a),o(c,d,b)
    return (d1*d2<-1e-9) and (d3*d4<-1e-9)
def bbox(l): xs=[p[0] for p in l]; ys=[p[1] for p in l]; return min(xs),min(ys),max(xs),max(ys)
def pip(pt,poly):
    x,y=pt; c=False
    for (a,b) in segs(poly):
        if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: c=not c
    return c
def mindist(h1,h2):
    return min(((p[0]-q[0])**2+(p[1]-q[1])**2)**.5 for p in h1 for q in h2)
problems=0; thin=[]
for name,outer,holes in recs:
    bbs=[bbox(h) for h in holes]
    so=segs(outer)
    for i in range(len(so)):
        for j in range(i+2,len(so)):
            if i==0 and j==len(so)-1: continue
            if inter(*so[i],*so[j]): print('SELF',name); problems+=1; break
    for i,h in enumerate(holes):
        if not all(pip(p,outer) for p in h): print('HOLE OUTSIDE',name,i,bbs[i]); problems+=1
        b=bbs[i]
        for (a,c) in so:
            if max(a[0],c[0])<b[0]-3 or min(a[0],c[0])>b[2]+3 or max(a[1],c[1])<b[1]-3 or min(a[1],c[1])>b[3]+3: continue
            if any(inter(a,c,p,q) for (p,q) in segs(h)): print('HOLE x OUTER',name,i,b); problems+=1; break
        for j in range(i+1,len(holes)):
            b2=bbs[j]
            if b[2]+2<b2[0] or b2[2]+2<b[0] or b[3]+2<b2[1] or b2[3]+2<b[1]: continue
            h2=holes[j]
            if any(inter(p,q,r,t) for (p,q) in segs(h) for (r,t) in segs(h2)) or pip(h2[0],h) or pip(h[0],h2):
                print('HOLES OVERLAP',name,i,j,b,b2); problems+=1
            elif mindist(h,h2)<1.5: thin.append((name,round(mindist(h,h2),2),b,b2))
print('records',len(recs),'problems',problems,'thin webs',len(thin))
for t in thin[:15]: print(' thin',t)
