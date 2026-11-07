import re, sys, math, collections
fn=sys.argv[1]
s=open(fn).read().split('DATA;')[1]
ent={}
for m in re.finditer(r'#(\d+)=([A-Z_0-9]+)\((.*?)\);\s*$', s, re.M):
    ent[int(m.group(1))]=(m.group(2), m.group(3))
def refs(a): return [int(x) for x in re.findall(r'#(\d+)',a)]
def pt(i):
    t,a=ent[i]; assert t=='CARTESIAN_POINT'
    return tuple(float(x) for x in re.findall(r'\(([^()]*)\)\)?$',a)[0].split(','))
def vpt(i):
    t,a=ent[i]; return pt(refs(a)[0])
bad=0; nsol=0
for i,(t,a) in ent.items():
    if t!='MANIFOLD_SOLID_BREP': continue
    nsol+=1
    name=a.split("'")[1]
    sh=refs(a)[0]; faces=refs(ent[sh][1])
    use=collections.Counter()
    for f in faces:
        ft,fa=ent[f]
        r=refs(fa)
        bounds=[x for x in r if ent[x][0] in('FACE_OUTER_BOUND','FACE_BOUND')]
        for b in bounds:
            lp=refs(ent[b][1])[0]
            oes=refs(ent[lp][1])
            seq=[]
            for oe in oes:
                oa=ent[oe][1]; e=refs(oa)[0]; fwd=oa.strip().endswith('.T.')
                ea=ent[e][1]; vs,ve,crv=refs(ea)[:3]
                if not fwd: vs,ve=ve,vs
                seq.append((vs,ve)); use[(e,fwd)]+=1
            for k in range(len(seq)):
                if seq[k][1]!=seq[(k+1)%len(seq)][0]:
                    print('LOOP BREAK',name,f); bad+=1; break
    edges=set(e for e,_ in use)
    for e in edges:
        if use[(e,True)]!=1 or use[(e,False)]!=1:
            print('EDGE USE',name,e,use[(e,True)],use[(e,False)]); bad+=1; break
    # circle vertex consistency
    for e in edges:
        ea=ent[e][1]; vs,ve,crv=refs(ea)[:3]
        if ent[crv][0]=='CIRCLE':
            axr,_=refs(ent[crv][1])[0],0
            c=pt(refs(ent[axr][1])[0]); r=float(ent[crv][1].split(',')[-1])
            for v in (vs,ve):
                p=vpt(v); d=math.dist(p,c)
                if abs(d-r)>1e-3: print('ARC VERTEX',name,d,r); bad+=1
print(fn,'solids',nsol,'problems',bad)
