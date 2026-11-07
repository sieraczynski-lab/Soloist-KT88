import sys; sys.path.insert(0,'.')
from boards import BOARDS
for fn in BOARDS:
    b=fn(); m=b.check()
    print('==', b.name, len(b.comps), 'elements,', len(b.nets()), 'nets')
    for x in m: print('  ', x)
