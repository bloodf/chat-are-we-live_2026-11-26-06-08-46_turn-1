import mh, textures_char as tx
from cast import CAST
for cid, c in CAST.items():
    for suit, o in c.get('outfit', {}).items():
        if o.get('shirt') or o.get('pants'): p = mh.proxy('clothes', suit); tx.outfit(p.tex(), suit, o, f'{cid}_{suit}')
