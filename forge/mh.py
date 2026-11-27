"""MakeHuman / MPFB data access: base mesh, shape targets, proxies, rig. Pure numpy."""
import os, json, gzip, functools
import numpy as np
ROOT = os.path.expanduser('~/.cache/forge/dl')
MP = f'{ROOT}/anny/anny/data/mpfb2'
MH = f'{ROOT}/npm/makehuman-data/package/public/data'

@functools.lru_cache(None)
def base():
    V, T, F, FT, G = [], [], [], [], []
    g = None
    for line in open(f'{MP}/3dobjs/base.obj'):
        p = line.split()
        if not p: continue
        if p[0] == 'v': V.append([float(x) for x in p[1:4]])
        elif p[0] == 'vt': T.append([float(x) for x in p[1:3]])
        elif p[0] == 'g': g = p[1]
        elif p[0] == 'f':
            a = [q.split('/') for q in p[1:]]
            F.append([int(q[0]) - 1 for q in a]); FT.append([int(q[1]) - 1 for q in a]); G.append(g)
    return np.array(V), np.array(T), F, FT, G

@functools.lru_cache(None)
def target(path):
    n = len(base()[0]); d = np.zeros((n, 3))
    with gzip.open(f'{MP}/targets/{path}.target.gz', 'rt') as fh:
        for line in fh:
            if line[0] == '#': continue
            p = line.split()
            if len(p) == 4: d[int(p[0])] = [float(x) for x in p[1:]]
    return d

def has(path): return os.path.exists(f'{MP}/targets/{path}.target.gz')

def tri(v):  # 0..1 -> min/average/max blend
    return {'min': max(0, 1 - 2 * v), 'average': 1 - abs(2 * v - 1), 'max': max(0, 2 * v - 1)}

def shape(race, gender, age=.25, muscle=.5, weight=.5, height=.5, prop=.6, details=()):
    """race: dict or str; gender 0=female 1=male; age 0=young(25) 1=old(90)"""
    V = base()[0].copy()
    if isinstance(race, str): race = {race: 1.0}
    gs = {'female': 1 - gender, 'male': gender}
    ages = {'young': 1 - age, 'old': age}
    mu, we = tri(muscle), tri(weight)
    for g, gw in gs.items():
        if gw <= 0: continue
        for a, aw in ages.items():
            if aw <= 0: continue
            for r, rw in race.items():
                V += target(f'macrodetails/{r}-{g}-{a}') * gw * aw * rw
            for m, mw in mu.items():
                for w, ww in we.items():
                    k = gw * aw * mw * ww
                    if k <= 0: continue
                    p = f'macrodetails/universal-{g}-{a}-{m}muscle-{w}weight'
                    if has(p): V += target(p) * k
                    hn = 'maxheight' if height > .5 else 'minheight'
                    p = f'macrodetails/height/{g}-{a}-{m}muscle-{w}weight-{hn}'
                    if has(p): V += target(p) * k * abs(2 * height - 1)
                    pn = 'idealproportions' if prop > .5 else 'uncommonproportions'
                    p = f'macrodetails/proportions/{g}-{a}-{m}muscle-{w}weight-{pn}'
                    if has(p): V += target(p) * k * abs(2 * prop - 1)
    for path, w in details:
        if '/l-' in path:
            V += target(path) * w; V += target(path.replace('/l-', '/r-')) * w
        else: V += target(path) * w
    return V

class Proxy:
    def __init__(self, kind, name):
        self.dir = f'{MH}/proxies/{kind}/{name}'
        d = json.load(open(f'{self.dir}/{name}.json')); self.name = name; self.kind = kind
        self.ref = np.array(d['ref_vIdxs']); self.w = np.array(d['weights']); self.off = np.array(d['offsets'])
        self.uv = np.array(d['uvs'][0]).reshape(-1, 2) if d['uvs'] else None
        self.faces, self.ft = [], []
        f = d['faces']; i = 0
        while i < len(f):
            t = f[i]; i += 1; n = 4 if t & 1 else 3
            self.faces.append(f[i:i + n]); i += n
            if t & 2: i += 1
            if t & 4: i += 1
            if t & 8: self.ft.append(f[i:i + n]); i += n
            if t & 16: i += 1
            if t & 32: i += n
            if t & 64: i += 1
            if t & 128: i += n
        self.delete = np.array(d['metadata'].get('deleteVerts') or d.get('deleteVerts') or [0] * 19158, bool)
        self.mat = d['materials'][0] if d.get('materials') else {}
    def fit(self, V): return (V[self.ref] * self.w[..., None]).sum(1) + self.off
    def delta(self, D): return (D[self.ref] * self.w[..., None]).sum(1)
    def tex(self, key='mapDiffuse'):
        m = self.mat.get(key); return f'{self.dir}/{m}' if m else None

@functools.lru_cache(None)
def proxy(kind, name): return Proxy(kind, name)

@functools.lru_cache(None)
def groups():
    g = json.load(open(f'{MP}/mesh_metadata/basemesh_vertex_groups.json')); out = {}
    for k, rs in g.items():
        idx = []
        for a, b in rs: idx += list(range(a, b + 1))
        out[k] = np.array(idx)
    return out

@functools.lru_cache(None)
def rig():
    r = json.load(open(f'{MP}/rigs/standard/rig.game_engine.json')); return r.get('bones', r)

@functools.lru_cache(None)
def weights():
    w = json.load(open(f'{MP}/rigs/standard/weights.game_engine.json'))['weights']
    names = sorted(w); n = len(base()[0]); M = np.zeros((n, len(names)), np.float32)
    for j, k in enumerate(names):
        for vi, x in w[k]: M[int(vi), j] = x
    s = M.sum(1, keepdims=True); s[s == 0] = 1
    return names, M / s

def joint(V, spec):
    st = spec.get('strategy', 'CUBE')
    if st == 'CUBE': return V[groups()[spec['cube_name']]].mean(0)
    if st == 'VERTEX': return V[spec['vertex_index']]
    if st == 'MEAN': return V[spec['vertex_indices']].mean(0)
    raise Exception(st)
