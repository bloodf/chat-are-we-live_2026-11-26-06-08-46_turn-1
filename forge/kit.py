"""Modelling kit + Cycles lightmap/probe/reflection baking. Blender coords: x right, y north(back), z up. metres."""
import bpy, bmesh, math, os, json, random, struct, sys, time
import numpy as np
from mathutils import Vector, Matrix, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); PUB = os.path.join(HERE, '..', 'public', 'assets')
AVG = json.load(open(f'{HERE}/tex_avg.json'))
MATS = {}
def col(h):
    if not isinstance(h, str): return list(h)
    h = h.lstrip('#'); s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4) for c in s]
def M(name, tex=None, tint='#ffffff', rough=None, metal=0, scale=1.0, emit=None, chan=None, art=None, alpha=False, bump=1.0, two=False, bakek=1.0):
    """emit: (hex, strength); chan: which light channel the emitter belongs to (lamp/led/day/always)"""
    MATS[name] = dict(tex=tex, tint=col(tint), rough=rough, metal=metal, scale=scale, emit=(col(emit[0]), emit[1]) if emit else None, chan=chan, art=art, alpha=alpha, bump=bump, two=two, bakek=bakek); return name

class Part:
    __slots__ = ('v', 'f', 'n', 'uv', 'mat', 'lm', 'bake_only', 'tag', 'ca')
class Scene:
    def __init__(s, name): s.name = name; s.parts = []; s.lights = []; s.anchors = {}; s.blocks = []; s.meta = {}; s.rnd = random.Random(name); s.xf = [Matrix()]; s.lmw = 1.0
    # ----- transform stack
    def push(s, loc=(0, 0, 0), rot=0, rx=0, ry=0, scale=1): s.xf.append(s.xf[-1] @ Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Scale(scale, 4)); return s
    def pop(s): s.xf.pop()
    def __enter__(s): return s
    def __exit__(s, *a): s.pop()
    def at(s, *a, **k): return s.push(*a, **k)
    # ----- raw mesh add
    def add(s, bm, mat, uv='box', grain=None, sharp=42, lm=None, bake_only=False, two=False):
        bm.verts.index_update(); bm.faces.index_update(); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); bm.normal_update()
        mx = s.xf[-1]; nm = mx.to_3x3().inverted().transposed()
        V = np.array([mx @ v.co for v in bm.verts]); flip = mx.determinant() < 0
        fn = [(nm @ f.normal).normalized() for f in bm.faces]; fa = [f.calc_area() for f in bm.faces]; cs = math.cos(math.radians(sharp))
        uvl = bm.loops.layers.uv.active; sc = MATS[mat]['scale'] if mat in MATS else 1
        P, N, U, T = [], [], [], []
        for fi, f in enumerate(bm.faces):
            n = fn[fi]; ax = max(range(3), key=lambda i: abs(n[i])); base = len(P); loops = list(f.loops)
            if flip: loops.reverse()
            for lp in loops:
                v = lp.vert; p = V[v.index]; nn = Vector((0, 0, 0))
                for g in v.link_faces:
                    if fn[g.index].dot(n) > cs: nn += fn[g.index] * fa[g.index]
                nn = nn.normalized() if nn.length > 1e-9 else n
                P.append(p); N.append(nn[:])
                if uv == 'box':
                    if ax == 0: u = (p[1] * (1 if n[0] > 0 else -1), p[2])
                    elif ax == 1: u = (p[0] * (-1 if n[1] > 0 else 1), p[2])
                    else: u = (p[0], p[1] * (1 if n[2] > 0 else -1))
                    if grain == 'x' and ax != 0: u = (u[1], u[0])
                    if grain == 'y' and ax == 0: u = (u[1], u[0])
                    if grain == 'z' and ax == 2: u = (u[1], u[0])
                    U.append((u[0] / sc, u[1] / sc))
                elif uv == 'mesh': U.append(tuple(lp[uvl].uv))
                else: U.append((0, 0))
            k = len(loops)
            for i in range(1, k - 1): T.append((base, base + i, base + i + 1))
            
        p = Part(); p.v = np.array(P, np.float32); p.n = np.array(N, np.float32); p.uv = np.array(U, np.float32); p.f = np.array(T, np.int32); p.mat = mat; p.lm = (lm or 1.0) * s.lmw; p.bake_only = bake_only; p.tag = None; p.ca = None
        s.parts.append(p); bm.free(); return p
    # ----- primitives
    def box(s, size, loc=(0, 0, 0), mat='plaster', bevel=.006, seg=2, rot=0, rx=0, ry=0, base=False, grain=None, **k):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
        if bevel and min(size) > bevel * 2.2: bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=seg, profile=.5, affect='EDGES', clamp_overlap=True)
        m = Matrix.Translation((loc[0], loc[1], loc[2] + (size[2] / 2 if base else 0))) @ Euler((rx, ry, rot)).to_matrix().to_4x4(); bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
        return s.add(bm, mat, grain=grain, **k)
    def cyl(s, r, h, loc=(0, 0, 0), mat='plaster', seg=24, bevel=.004, axis='z', r2=None, base=False, cap=True, rot=0, **k):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=cap, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
        if bevel and cap and (r2 is None or r2 > .005):
            es = [e for e in bm.edges if len(e.link_faces) == 2 and any(len(f.verts) > 4 for f in e.link_faces)]; bmesh.ops.bevel(bm, geom=es, offset=min(bevel, h * .3, r * .4), segments=2, profile=.5, affect='EDGES')
        m = Matrix.Translation((loc[0], loc[1], loc[2] + (h / 2 if base else 0))) @ Matrix.Rotation(rot, 4, 'Z')
        if axis == 'x': m = m @ Matrix.Rotation(math.pi / 2, 4, 'Y')
        if axis == 'y': m = m @ Matrix.Rotation(math.pi / 2, 4, 'X')
        bmesh.ops.transform(bm, matrix=m, verts=bm.verts); return s.add(bm, mat, **k)
    def sphere(s, r, loc=(0, 0, 0), mat='plaster', seg=20, rings=12, sc=(1, 1, 1), **k):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r); bmesh.ops.scale(bm, vec=sc, verts=bm.verts); bmesh.ops.translate(bm, vec=loc, verts=bm.verts); return s.add(bm, mat, sharp=80, **k)
    def lathe(s, prof, loc=(0, 0, 0), mat='plaster', seg=28, sharp=40, two=False, **k):
        bm = bmesh.new(); rings = []
        for r, z in prof:
            if r < 1e-5: rings.append([bm.verts.new((0, 0, z))] * seg)
            else: rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
        for a, b in zip(rings, rings[1:]):
            for i in range(seg):
                j = (i + 1) % seg; q = []
                for v in (a[i], a[j], b[j], b[i]):
                    if v not in q: q.append(v)
                if len(q) > 2:
                    try: bm.faces.new(q)
                    except ValueError: pass
        bmesh.ops.translate(bm, vec=loc, verts=bm.verts); return s.add(bm, mat, sharp=sharp, **k)
    def tube(s, pts, r, mat, seg=8, closed=False, **k):
        bm = bmesh.new(); pts = [Vector(p) for p in pts]; n = len(pts); rings = []; up = Vector((0, 0, 1))
        for i, p in enumerate(pts):
            a = pts[i - 1] if (i > 0 or closed) else p; b = pts[(i + 1) % n] if (i < n - 1 or closed) else p
            d = (b - a).normalized(); x = d.cross(up); x = x.normalized() if x.length > 1e-3 else Vector((1, 0, 0)); y = x.cross(d).normalized()
            rr = r[i] if isinstance(r, (list, tuple)) else r
            rings.append([bm.verts.new(p + x * rr * math.cos(2 * math.pi * j / seg) + y * rr * math.sin(2 * math.pi * j / seg)) for j in range(seg)])
        pr = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
        for a, b in pr:
            for j in range(seg): bm.faces.new((a[j], a[(j + 1) % seg], b[(j + 1) % seg], b[j]))
        if not closed:
            bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return s.add(bm, mat, sharp=70, **k)
    def curve(s, pts, r, mat, n=16, **k):
        """catmull-rom tube"""
        P = [Vector(p) for p in pts]; P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]; out = []
        for i in range(1, len(P) - 2):
            for q in range(n):
                t = q / n; a, b, c, d = P[i - 1:i + 3]; out.append(.5 * ((2 * b) + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t ** 3))
        out.append(P[-2]); return s.tube(out, r, mat, **k)
    def quad(s, w, h, loc, mat, rot=0, rx=math.pi / 2, uv=(0, 0, 1, 1), two=False, **k):
        """art plane facing -y by default (rx 90deg)"""
        bm = bmesh.new(); l = bm.loops.layers.uv.new(); vs = [bm.verts.new((x * w / 2, y * h / 2, 0)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]; f = bm.faces.new(vs)
        for lp, (a, b) in zip(f.loops, ((uv[0], uv[1]), (uv[2], uv[1]), (uv[2], uv[3]), (uv[0], uv[3]))): lp[l].uv = (a, b)
        m = Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X'); bmesh.ops.transform(bm, matrix=m, verts=bm.verts); return s.add(bm, mat, uv='mesh', **k)
    def cushion(s, size, loc, mat, rot=0, rx=0, ry=0, puff=.5, res=8, noise=.004, grain=None, **k):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2); bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=res, use_grid_fill=True)
        rs = random.Random(int(size[0] * 1000 + loc[0] * 77)); ph = [rs.random() * 6 for _ in range(6)]
        for v in bm.verts:
            x, y, z = v.co; e = 4.2; q = (abs(x) ** e + abs(y) ** e + abs(z) ** e) ** (1 / e); d = Vector((x, y, z)) / q
            b = (1 - min(1, abs(d.x)) ** 2.6) * (1 - min(1, abs(d.y)) ** 2.6); p = Vector((d.x * size[0] / 2, d.y * size[1] / 2, d.z * size[2] / 2 * ((1 - puff) + puff * (.55 + .6 * b))))
            w = math.sin(x * 5 + ph[0]) * math.sin(y * 6 + ph[1]) + math.sin(x * 11 + ph[2] + y * 7) * .5; p += Vector((0, 0, w * noise * (1 if z > 0 else .3))); v.co = p
        m = Matrix.Translation(loc) @ Euler((rx, ry, rot)).to_matrix().to_4x4(); bmesh.ops.transform(bm, matrix=m, verts=bm.verts); return s.add(bm, mat, sharp=80, grain=grain, **k)
    def curtain(s, w, h, loc, mat, rot=0, folds=7, amp=.045, nx=56, nz=8, gather=0, two=True, **k):
        bm = bmesh.new(); rs = random.Random(int(loc[0] * 100 + w * 10)); g = []
        for j in range(nz + 1):
            t = j / nz; row = []
            for i in range(nx + 1):
                u = i / nx; a = amp * (.55 + .45 * (1 - t)); sq = 1 - gather * math.sin(math.pi * min(1, (1 - t) * 1.1)) * .6
                x = (u - .5) * w * sq; y = math.sin(u * folds * 2 * math.pi + .6 * math.sin(u * 9 + t * 1.5)) * a + .012 * math.sin(u * 23 + t * 5); row.append(bm.verts.new((x, y, t * h)))
            g.append(row)
        for j in range(nz):
            for i in range(nx): bm.faces.new((g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]))
        m = Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, 'Z'); bmesh.ops.transform(bm, matrix=m, verts=bm.verts); return s.add(bm, mat, sharp=80, grain='z', **k)
    def cloth(s, w, l, z, colliders, mat, loc=(0, 0), nx=44, ny=44, frames=45, pins=None, rot=0, crumple=.0, lift=None, thick=.012, **k):
        """drape a sheet with blender cloth sim over box colliders [(size,loc)]"""
        before = set(bpy.data.objects)
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=.5); rs = random.Random(5)
        for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * l, rs.random() * .01 + crumple * math.sin(v.co.x * 9 + v.co.y * 5)))
        bmesh.ops.rotate(bm, matrix=Matrix.Rotation(rot, 3, 'Z'), verts=bm.verts); bmesh.ops.translate(bm, vec=(loc[0], loc[1], z), verts=bm.verts)
        me = bpy.data.meshes.new('c'); bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new('c', me); bpy.context.scene.collection.objects.link(ob)
        for sz, lc in colliders:
            bpy.ops.mesh.primitive_cube_add(size=1, location=lc); c = bpy.context.object; c.scale = sz; bpy.ops.object.transform_apply(scale=True); b = c.modifiers.new('b', 'BEVEL'); b.width = .03; b.segments = 3
            cm = c.modifiers.new('col', 'COLLISION'); c.collision.thickness_outer = .006; c.collision.cloth_friction = 18
        cm = ob.modifiers.new('cl', 'CLOTH'); st = cm.settings; st.quality = 6; st.mass = .35; st.tension_stiffness = 12; st.compression_stiffness = 12; st.shear_stiffness = 4; st.bending_stiffness = .25; st.air_damping = 2
        cm.collision_settings.collision_quality = 3; cm.collision_settings.distance_min = .006; cm.collision_settings.use_self_collision = False
        sc = bpy.context.scene; sc.frame_start = 1; sc.frame_end = frames; cm.point_cache.frame_end = frames
        for f in range(1, frames + 1): sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get(); ev = bpy.data.meshes.new_from_object(ob.evaluated_get(dg)); bm = bmesh.new(); bm.from_mesh(ev)
        bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=.4, use_axis_x=True, use_axis_y=True, use_axis_z=True)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        if sum(f.normal.z for f in bm.faces) < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
        for o in list(bpy.data.objects):
            if o not in before: bpy.data.objects.remove(o)
        sc.frame_set(1); return s.add(bm, mat, sharp=80, **k)
    def text(s, txt, size, loc, mat, fontfile=None, depth=.004, rot=0, rx=math.pi / 2, align='CENTER', bevel=0, **k):
        cu = bpy.data.curves.new('t', 'FONT'); cu.body = txt; cu.size = size; cu.extrude = depth; cu.align_x = align; cu.align_y = 'CENTER'; cu.resolution_u = 4; cu.bevel_depth = bevel
        if fontfile: cu.font = bpy.data.fonts.load(fontfile)
        ob = bpy.data.objects.new('t', cu); bpy.context.scene.collection.objects.link(ob); me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get())); bm = bmesh.new(); bm.from_mesh(me); bpy.data.objects.remove(ob)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); m = Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X'); bmesh.ops.transform(bm, matrix=m, verts=bm.verts); return s.add(bm, mat, sharp=30, **k)
    def neon(s, txt, size, loc, mat, fontfile, rot=0, r=.006, **k):
        cu = bpy.data.curves.new('t', 'FONT'); cu.body = txt; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.fill_mode = 'NONE'; cu.bevel_depth = r; cu.bevel_resolution = 1; cu.resolution_u = 3; cu.font = bpy.data.fonts.load(fontfile)
        ob = bpy.data.objects.new('t', cu); bpy.context.scene.collection.objects.link(ob); me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get())); bm = bmesh.new(); bm.from_mesh(me); bpy.data.objects.remove(ob)
        m = Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'X'); bmesh.ops.transform(bm, matrix=m, verts=bm.verts); return s.add(bm, mat, sharp=80, **k)
    def leafy(s, loc, mat, stem, n=14, spread=.35, h=.6, leaf=(.10, .26), droop=.5, seed=1, pairs=5):
        rs = random.Random(seed)
        for i in range(n):
            a = i * 2.399 + rs.random() * .4; t = .35 + .65 * rs.random(); tip = Vector((math.cos(a) * spread * t, math.sin(a) * spread * t, h * (.45 + .55 * rs.random())))
            s.curve([(loc[0], loc[1], loc[2]), (loc[0] + tip.x * .3, loc[1] + tip.y * .3, loc[2] + tip.z * .65), (loc[0] + tip.x * .75, loc[1] + tip.y * .75, loc[2] + tip.z)], [.004] * 17 if False else .0035, stem, n=4, seg=4)
            bm = bmesh.new(); L = leaf[1] * (.75 + .5 * rs.random()); W = leaf[0] * (.75 + .5 * rs.random()); g = []; ns = 6; d = Vector((math.cos(a), math.sin(a), 0)); sd = Vector((-d.y, d.x, 0)); o = Vector(loc) + Vector((tip.x * .75, tip.y * .75, tip.z)); up = .35 + rs.random() * .5
            for j in range(ns + 1):
                u = j / ns; c = o + d * (L * u) + Vector((0, 0, L * (up * u - droop * 1.6 * u * u))); wd = W * math.sin(math.pi * min(1, u * .93 + .05)) ** .8
                g.append([bm.verts.new(c - sd * wd / 2 + Vector((0, 0, wd * .18))), bm.verts.new(c), bm.verts.new(c + sd * wd / 2 + Vector((0, 0, wd * .18)))])
            for j in range(ns):
                for q in range(2): bm.faces.new((g[j][q], g[j][q + 1], g[j + 1][q + 1], g[j + 1][q]))
            s.add(bm, mat, sharp=80)
    # ----- composite helpers
    def room(s, w, d, h, wall='wall', floor='floor', ceil='ceil', t=.12, openings=(), base='trim', crown=None, baseh=.09, walls='NESW'):
        """room from x in [-w/2,w/2], y in [-d/2,d/2]. openings: (wall, centre, width, z0, z1)"""
        def plane(verts, mat, **k):
            bm = bmesh.new(); bm.faces.new([bm.verts.new(v) for v in verts]); s.add(bm, mat, **k)
        W, D = w / 2, d / 2
        plane([(-W, -D, 0), (W, -D, 0), (W, D, 0), (-W, D, 0)], floor); plane([(-W, D, h), (W, D, h), (W, -D, h), (-W, -D, h)], ceil, lm=.45)
        ww = {'N': ((-W, D), (W, D)), 'E': ((W, D), (W, -D)), 'S': ((W, -D), (-W, -D)), 'W': ((-W, -D), (-W, D))}
        for k, (a, b) in ww.items():
            a, b = Vector(a), Vector(b); L = (b - a).length; dr = (b - a) / L
            ops = sorted([(c + (L / 2) - ow / 2, c + L / 2 + ow / 2, z0, z1) for (wl, c, ow, z0, z1) in openings if wl == k]); x = 0; seg = []
            for (o0, o1, z0, z1) in ops:
                seg.append((x, o0, 0, h)); 
                if z0 > 0: seg.append((o0, o1, 0, z0))
                if z1 < h: seg.append((o0, o1, z1, h))
                x = o1
            seg.append((x, L, 0, h)); lw = .5 if k == 'S' else 1
            for (x0, x1, z0, z1) in seg:
                if x1 - x0 < 1e-4: continue
                p, q = a + dr * x0, a + dr * x1; plane([(p.x, p.y, z0), (q.x, q.y, z0), (q.x, q.y, z1), (p.x, p.y, z1)], wall if not isinstance(wall, dict) else wall[k], lm=lw)
            out = Vector((dr.y, -dr.x)) * -1
            for (o0, o1, z0, z1) in ops:  # reveals (going outward, facing opening)
                p, q = a + dr * o0, a + dr * o1; o = -Vector((-dr.y, dr.x)) * -1; o = Vector((-dr.y, dr.x)) * t
                pl = (p.x, p.y), (q.x, q.y), (q.x + o.x, q.y + o.y), (p.x + o.x, p.y + o.y)
                plane([(*pl[0], z1), (*pl[1], z1), (*pl[2], z1), (*pl[3], z1)], 'trim'); 
                if z0 > 0: plane([(*pl[3], z0), (*pl[2], z0), (*pl[1], z0), (*pl[0], z0)], 'trim')
                plane([(*pl[0], z0), (*pl[0], z1), (*pl[3], z1), (*pl[3], z0)], 'trim'); plane([(*pl[2], z0), (*pl[2], z1), (*pl[1], z1), (*pl[1], z0)], 'trim')
            if base and k != 'S':
                x = 0; gaps = [(o0, o1) for (o0, o1, z0, z1) in ops if z0 < baseh]
                for (g0, g1) in gaps + [(L, L)]:
                    if g0 - x > .02:
                        c = a + dr * ((x + g0) / 2); inn = -Vector((-dr.y, dr.x)) * .007
                        s.box((g0 - x, .014, baseh), (c.x + inn.x, c.y + inn.y, baseh / 2), base, bevel=.004, seg=1, rot=math.atan2(dr.y, dr.x))
                    x = g1
                if crown:
                    c = a + dr * (L / 2); inn = -Vector((-dr.y, dr.x)) * .02; s.box((L, .04, .07), (c.x + inn.x, c.y + inn.y, h - .035), crown, bevel=.012, rot=math.atan2(dr.y, dr.x))
        s.meta.update(room=[w, d, h])
    def books(s, w, loc, mats, hmin=.17, hmax=.26, d=.16, rot=0, lean=True):
        x = 0; i = 0
        with s.at(loc, rot):
            while x < w - .02:
                t = s.rnd.uniform(.014, .042); h = s.rnd.uniform(hmin, hmax)
                if x + t > w: break
                m = s.rnd.choice(mats); dd = d * s.rnd.uniform(.8, 1); ly = s.rnd.uniform(0, .012)
                s.box((t - .0015, dd, h), (x + t / 2, ly, h / 2), m, bevel=.002, seg=1, lm=.6); x += t
                if s.rnd.random() < .08: x += .02
    # ----- lights (channel)
    def area(s, loc, size, energy, color, chan, rot=(0, 0, 0), size_y=None, spread=180): s.lights.append(('AREA', loc, size, energy, col(color), chan, rot, size_y, spread))
    def point(s, loc, r, energy, color, chan): s.lights.append(('POINT', loc, r, energy, col(color), chan, (0, 0, 0), None, 0))
    def spot(s, loc, energy, color, chan, rot, angle=60, r=.05): s.lights.append(('SPOT', loc, r, energy, col(color), chan, rot, None, angle))
    def sun(s, rot, energy, color, angle=1.5): s.lights.append(('SUN', (0, 0, 10), angle, energy, col(color), 'day', rot, None, 0))
    def block(s, x0, y0, x1, y1): s.blocks.append([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)])
    def anchor(s, name, loc, rot=0, **k): s.anchors[name] = dict(pos=[loc[0], loc[2] if len(loc) > 2 else 0, -loc[1]], rot=rot, **k)

# ---------------------------------------------------------------- GLB writer
def write_glb(path, prims):
    """prims: list of dict(mat, v, n, uv, f, uv2?, color?) blender coords -> gltf y-up"""
    bin_ = bytearray(); bv, ac, pr, mats, mi = [], [], [], [], {}
    def put(arr, target, typ, ct, mm=False):
        while len(bin_) % 4: bin_.append(0)
        bv.append(dict(buffer=0, byteOffset=len(bin_), byteLength=arr.nbytes, target=target)); bin_.extend(arr.tobytes()); a = dict(bufferView=len(bv) - 1, componentType=ct, count=len(arr) if typ != 'SCALAR' else arr.size, type=typ)
        if mm: a['min'] = [float(x) for x in arr.min(0)]; a['max'] = [float(x) for x in arr.max(0)]
        ac.append(a); return len(ac) - 1
    meshes, nodes = [], []
    for p in prims:
        v = np.stack([p['v'][:, 0], p['v'][:, 2], -p['v'][:, 1]], 1).astype(np.float32); n = np.stack([p['n'][:, 0], p['n'][:, 2], -p['n'][:, 1]], 1).astype(np.float32)
        uv = p['uv'].astype(np.float32).copy(); uv[:, 1] = 1 - uv[:, 1]
        at = dict(POSITION=put(v, 34962, 'VEC3', 5126, True), NORMAL=put(n, 34962, 'VEC3', 5126), TEXCOORD_0=put(uv, 34962, 'VEC2', 5126))
        if p.get('uv2') is not None: u2 = p['uv2'].astype(np.float32).copy(); u2[:, 1] = 1 - u2[:, 1]; at['TEXCOORD_1'] = put(u2, 34962, 'VEC2', 5126)
        if p.get('color') is not None: c = (np.clip(np.c_[p['color'], p['color'], p['color'], np.ones(len(p['color']))], 0, 1) * 255).astype(np.uint8); at['COLOR_0'] = put(c, 34962, 'VEC4', 5121); ac[-1]['normalized'] = True
        if p['mat'] not in mi: mi[p['mat']] = len(mats); mats.append(dict(name=p['mat']))
        meshes.append(dict(name=p['mat'], primitives=[dict(attributes=at, indices=put(p['f'].astype(np.uint32).reshape(-1), 34963, 'SCALAR', 5125), material=mi[p['mat']])])); nodes.append(dict(mesh=len(meshes) - 1, name=p.get('name', p['mat'])))
    g = dict(asset=dict(version='2.0', generator='forge'), scene=0, scenes=[dict(nodes=list(range(len(nodes))))], nodes=nodes, meshes=meshes, materials=mats, accessors=ac, bufferViews=bv, buffers=[dict(byteLength=len(bin_))])
    j = json.dumps(g, separators=(',', ':')).encode(); j += b' ' * (-len(j) % 4); b = bytes(bin_) + b'\0' * (-len(bin_) % 4)
    with open(path, 'wb') as fh: fh.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(b)) + struct.pack('<II', len(j), 0x4E4F534A) + j + struct.pack('<II', len(b), 0x004E4942) + b)

# ---------------------------------------------------------------- baking
def setup_cycles(samples, bounces=6):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; c = sc.cycles; c.device = 'CPU'; c.samples = samples; c.use_denoising = False; c.max_bounces = bounces; c.diffuse_bounces = bounces; c.sample_clamp_indirect = 6; c.caustics_reflective = False; c.caustics_refractive = False; c.use_adaptive_sampling = True; c.adaptive_threshold = .02
    sc.render.threads_mode = 'AUTO'; sc.view_settings.view_transform = 'Raw' if False else 'Standard'
def bmat(name, chan, img=None):
    d = MATS[name]; m = bpy.data.materials.get('B_' + name) or bpy.data.materials.new('B_' + name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfDiffuse'); base = np.array(AVG.get(d['tex'], [1, 1, 1])) * np.array(d['tint'])
    if d['art']: base = np.array(d.get('artavg', [.3, .3, .3])) * np.array(d['tint'])
    if d['metal']: base = base * .6
    b.inputs[0].default_value = (*np.clip(base, 0, .88), 1); sh = b
    if d['emit'] and d['chan'] in (chan, 'always'):
        e = nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value = (*d['emit'][0], 1); e.inputs[1].default_value = (.35 if d['art'] else 1) * d['emit'][1] * d.get('bakek', 1); a = nt.nodes.new('ShaderNodeAddShader'); nt.links.new(b.outputs[0], a.inputs[0]); nt.links.new(e.outputs[0], a.inputs[1]); sh = a
    if d['alpha']:
        t = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs[0].default_value = .35 if d['alpha'] is True else d['alpha']; nt.links.new(t.outputs[0], mx.inputs[1]); nt.links.new(sh.outputs[0], mx.inputs[2]); sh = mx
    nt.links.new(sh.outputs[0], out.inputs[0])
    if img is not None: n = nt.nodes.new('ShaderNodeTexImage'); n.image = img; nt.nodes.active = n; n.select = True
    return m
def denoise(arr, n):
    """OIDN via compositor"""
    sc = bpy.context.scene; im = bpy.data.images.new('dn', n, n, float_buffer=True, alpha=True); im.colorspace_settings.name = 'Linear Rec.709' if 'Linear Rec.709' in [] else 'Non-Color'; buf = np.ones((n, n, 4), np.float32); buf[..., :3] = arr; im.pixels.foreach_set(buf.ravel()); im.update()
    p = '/home/model/.cache/forge/dn_in.exr'; sc.render.image_settings.file_format = 'OPEN_EXR'; im.filepath_raw = p; im.file_format = 'OPEN_EXR'; im.save()
    im2 = bpy.data.images.load(p); im2.colorspace_settings.name = 'Non-Color'
    sc.use_nodes = True; nt = sc.node_tree; nt.nodes.clear(); i = nt.nodes.new('CompositorNodeImage'); i.image = im2; d = nt.nodes.new('CompositorNodeDenoise'); d.use_hdr = True; d.prefilter = 'NONE'; c = nt.nodes.new('CompositorNodeComposite'); nt.links.new(i.outputs[0], d.inputs[0]); nt.links.new(d.outputs[0], c.inputs[0])
    hid = [(o, o.hide_render) for o in bpy.data.objects]
    for o, _ in hid: o.hide_render = True
    if not sc.camera: cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
    sc.render.resolution_x = sc.render.resolution_y = n; sc.render.resolution_percentage = 100; old = sc.cycles.samples; sc.cycles.samples = 1; q = '/home/model/.cache/forge/dn_out.exr'; sc.render.filepath = q; sc.render.image_settings.color_depth = '32'; sc.render.image_settings.color_mode = 'RGB'; bpy.ops.render.render(write_still=True)
    sc.cycles.samples = old; sc.use_nodes = False
    for o, h in hid: o.hide_render = h
    r = bpy.data.images.load(q); r.colorspace_settings.name = 'Non-Color'; a = np.zeros(n * n * 4, np.float32); r.pixels.foreach_get(a); a = a.reshape(n, n, 4)[..., :3]
    for x in (im, im2, r): bpy.data.images.remove(x)
    return np.maximum(a, 0)

def bake_env(S, size=2048, samples=96, texel=None, quick=False, chans=('day', 'lamp', 'led'), probes=(1.1, (.5, 1.4)), reflect_at=None):
    import xatlas
    t0 = time.time(); nm = S.name; out = f'{PUB}/env/{nm}'; os.makedirs(out, exist_ok=True)
    # --- merge by mat for export, atlas on everything
    parts = [p for p in S.parts]
    V = []; F = []; o = 0; SC = []
    for p in parts: V.append(p.v * math.sqrt(p.lm)); F.append(p.f + o); o += len(p.v)
    # xatlas with per-part meshes preserving lm weight (scaled positions); fast chart options
    at = xatlas.Atlas()
    for p in parts: at.add_mesh((p.v * math.sqrt(p.lm)).astype(np.float32), p.f.astype(np.uint32), p.n)
    co = xatlas.ChartOptions(); co.max_iterations = 1; co.normal_deviation_weight = 1.2; co.straightness_weight = 3; co.max_cost = 3
    po = xatlas.PackOptions(); po.resolution = size; po.padding = 2; po.bruteForce = False; po.rotate_charts = True
    area = sum(float(np.linalg.norm(np.cross(p.v[p.f[:, 1]] - p.v[p.f[:, 0]], p.v[p.f[:, 2]] - p.v[p.f[:, 0]]), axis=1).sum() / 2) * p.lm for p in parts)
    po.texels_per_unit = math.sqrt(size * size * .60 / area)
    for k in range(8):
        at = xatlas.Atlas()
        for p in parts: at.add_mesh((p.v * math.sqrt(p.lm)).astype(np.float32), p.f.astype(np.uint32), p.n)
        po.texels_per_unit *= 1 if k == 0 else .93; po.resolution = size; at.generate(co, po)
        if at.atlas_count == 1 and at.width <= size and at.height <= size: break
    print(f'[{nm}] atlas {at.width}x{at.height} count {at.atlas_count} util {at.utilization if hasattr(at,"utilization") else 0} texels/m {po.texels_per_unit:.0f} area {area:.0f} t{time.time()-t0:.0f}'); sys.stdout.flush()
    P2 = []
    for i, p in enumerate(parts):
        vm, idx, uv = at[i]; uv = uv * np.array([at.width, at.height]) / size if at.width != size or at.height != size else uv
        P2.append(dict(mat=p.mat, v=p.v[vm], n=p.n[vm], uv=p.uv[vm], f=idx.astype(np.int32), uv2=uv, bake_only=p.bake_only))
    # --- build one bake object
    av = np.vstack([q['v'] for q in P2]); an = np.vstack([q['n'] for q in P2]); au = np.vstack([q['uv2'] for q in P2]); af = []; mids = []; names = []; o = 0
    for q in P2:
        if q['mat'] not in names: names.append(q['mat'])
        af.append(q['f'] + o); mids += [names.index(q['mat'])] * len(q['f']); o += len(q['v'])
    af = np.vstack(af); me = bpy.data.meshes.new('env'); me.vertices.add(len(av)); me.vertices.foreach_set('co', av.astype(np.float32).ravel()); me.loops.add(len(af) * 3); me.loops.foreach_set('vertex_index', af.ravel().astype(np.int32)); me.polygons.add(len(af)); me.polygons.foreach_set('loop_start', (np.arange(len(af)) * 3).astype(np.int32)); me.polygons.foreach_set('material_index', np.array(mids, np.int32)); me.polygons.foreach_set('use_smooth', np.ones(len(af), bool))
    ul = me.uv_layers.new(name='lm'); ul.data.foreach_set('uv', au[af.ravel()].astype(np.float32).ravel()); me.update(); me.validate(); me.normals_split_custom_set_from_vertices([tuple(x) for x in an])
    ob = bpy.data.objects.new('env', me); bpy.context.scene.collection.objects.link(ob)
    lights = {}
    for i, (k, loc, sz, en, cl, ch, rot, sy, sp) in enumerate(S.lights):
        l = bpy.data.lights.new(f'l{i}', k); l.energy = en; l.color = cl
        if k == 'AREA': l.size = sz; l.shape = 'RECTANGLE' if sy else 'SQUARE'; l.size_y = sy or sz; l.spread = math.radians(sp)
        elif k == 'SUN': l.angle = math.radians(sz)
        elif k == 'SPOT': l.shadow_soft_size = sz; l.spot_size = math.radians(sp); l.spot_blend = .6
        else: l.shadow_soft_size = sz
        lo = bpy.data.objects.new(f'l{i}', l); lo.location = loc; lo.rotation_euler = rot; bpy.context.scene.collection.objects.link(lo); lights.setdefault(ch, []).append(lo)
        lo.visible_camera = False; lo.visible_glossy = False
    w = bpy.context.scene.world or bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[1].default_value = 0
    # --- probe spheres
    from mathutils.geometry import intersect_point_line
    rw, rd, rh = S.meta['room']; st, hs = probes; nx, ny = max(2, int(round(rw / st))), max(2, int(round(rd / st))); gx = [(-rw / 2 + .25) + (rw - .5) * i / (nx - 1) for i in range(nx)]; gy = [(-rd / 2 + .25) + (rd - .5) * i / (ny - 1) for i in range(ny)]
    pv, pf, pn, centers = [], [], [], []; ico = bmesh.new(); bmesh.ops.create_icosphere(ico, subdivisions=2, radius=1); iv = np.array([v.co[:] for v in ico.verts]); iff = np.array([[v.index for v in f.verts] for f in ico.faces]); ico.free()
    for z in hs:
        for y in gy:
            for x in gx: pf.append(iff + len(centers) * len(iv)); pv.append(iv * .03 + [x, y, z]); centers.append((x, y, z))
    pm = bpy.data.meshes.new('pr'); pm.from_pydata([tuple(x) for x in np.vstack(pv)], [], [tuple(map(int, x)) for x in np.vstack(pf)]); pm.polygons.foreach_set('use_smooth', np.ones(len(pm.polygons), bool)); ca = pm.color_attributes.new('c', 'FLOAT_COLOR', 'POINT'); pm.color_attributes.active_color = ca
    po_ = bpy.data.objects.new('pr', pm); bpy.context.scene.collection.objects.link(po_); mt = bpy.data.materials.new('pm'); mt.use_nodes = True; pm.materials.append(mt)
    for at_ in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_camera'): setattr(po_, at_, False)
    probe = dict(nx=nx, ny=ny, nz=len(hs), gx=gx, gy=gy, gz=list(hs), data={})
    pc = bpy.data.objects.new('pan', bpy.data.cameras.new('pan')); bpy.context.scene.collection.objects.link(pc); pc.data.type = 'PANO'; pc.data.panorama_type = 'EQUIRECTANGULAR'; rc = reflect_at or (0, 0, 1.4); pc.location = rc; pc.rotation_euler = (math.pi / 2, 0, 0)
    sc = bpy.context.scene; RANGE = 6.0
    for ch in chans:
        t1 = time.time(); img = bpy.data.images.new('lm_' + ch, size, size, float_buffer=True, alpha=False); img.colorspace_settings.name = 'Non-Color'
        me.materials.clear()
        for n in names: me.materials.append(bmat(n, ch, img))
        for c2, ls in lights.items():
            for l in ls: l.hide_render = (c2 != ch)
        setup_cycles(8 if quick else samples); bk = sc.render.bake; bk.use_pass_direct = True; bk.use_pass_indirect = True; bk.use_pass_color = False; bk.margin = 6; bk.margin_type = 'EXTEND'; bk.use_clear = True
        po_.hide_render = True; bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bk.target = 'IMAGE_TEXTURES'; bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'})
        a = np.zeros(size * size * 4, np.float32); img.pixels.foreach_get(a); a = a.reshape(size, size, 4)[..., :3]; mask = a.sum(-1) > 0
        a = denoise(a, size)
        # flood-fill empty texels so mips/filters don't bleed black
        from scipy.ndimage import distance_transform_edt
        ix = distance_transform_edt(~mask, return_distances=False, return_indices=True); a = a[ix[0], ix[1]]
        e = np.sqrt(np.clip(a / RANGE, 0, 1)); e += (np.random.RandomState(1).rand(*e.shape) - .5) / 255; e = np.clip(e, 0, 1)[::-1]
        from PIL import Image
        im8 = Image.fromarray((e * 255 + .5).astype(np.uint8))
        if ch == 'led': im8 = im8.convert('L').convert('RGB')
        im8.save(f'{out}/lm_{ch}.webp', quality=88, method=6)
        # probes
        po_.hide_render = False; bpy.ops.object.select_all(action='DESELECT'); po_.select_set(True); bpy.context.view_layer.objects.active = po_; sc.cycles.samples = 64 if not quick else 8; bk.target = 'VERTEX_COLORS'; bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'})
        c = np.zeros(len(pm.vertices) * 4, np.float32); pm.color_attributes['c'].data.foreach_get('color', c); c = c.reshape(len(centers), len(iv), 4)[..., :3]
        A = np.stack([np.maximum(iv[:, 0], 0) ** 2, np.maximum(-iv[:, 0], 0) ** 2, np.maximum(iv[:, 2], 0) ** 2, np.maximum(-iv[:, 2], 0) ** 2, np.maximum(-iv[:, 1], 0) ** 2, np.maximum(iv[:, 1], 0) ** 2], 1)  # gltf: +x -x +y -y +z -z
        sol = np.stack([np.linalg.lstsq(A, c[i], rcond=None)[0] for i in range(len(centers))]); probe['data'][ch] = [round(float(x), 4) for x in np.maximum(sol, 0).ravel()]
        po_.hide_render = True
        # reflection panorama
        sc.camera = pc; sc.render.resolution_x = 512; sc.render.resolution_y = 256; setup_cycles(16 if quick else 96); sc.cycles.use_denoising = True; sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_mode = 'RGB'; p = '/home/model/.cache/forge/pano.exr'; sc.render.filepath = p
        # coloured materials for pano
        bpy.ops.render.render(write_still=True); r = bpy.data.images.load(p); r.colorspace_settings.name = 'Non-Color'; a = np.zeros(512 * 256 * 4, np.float32); r.pixels.foreach_get(a); a = a.reshape(256, 512, 4)[::-1, :, :3]; bpy.data.images.remove(r); sc.cycles.use_denoising = False
        Image.fromarray((np.sqrt(np.clip(a / 8.0, 0, 1)) * 255 + .5).astype(np.uint8)).save(f'{out}/refl_{ch}.webp', quality=90)
        print(f'[{nm}] {ch} {time.time() - t1:.0f}s'); sys.stdout.flush(); bpy.data.images.remove(img)
    json.dump(dict(room=S.meta['room'], meta=S.meta, range=RANGE, reflAt=[rc[0], rc[2], -rc[1]], anchors=S.anchors, blocks=[[b[0], -b[3], b[2], -b[1]] for b in S.blocks], probes=dict(**{k: v for k, v in probe.items() if k != 'data'}, gyz=[-y for y in gy], data=probe['data'])), open(f'{out}/env.json', 'w'))
    export_env(S, P2, out)
    print(f'[{nm}] DONE {time.time() - t0:.0f}s tris {len(af)}'); sys.stdout.flush()

def merge(P2):
    by = {}
    for q in P2:
        if q.get('bake_only'): continue
        by.setdefault(q['mat'], []).append(q)
    prims = []
    for m, qs in by.items():
        o = 0; v, n, uv, u2, f, cc = [], [], [], [], [], []
        for q in qs: v.append(q['v']); n.append(q['n']); uv.append(q['uv']); f.append(q['f'] + o); o += len(q['v']); u2.append(q['uv2']) if q.get('uv2') is not None else 0; cc.append(q['color']) if q.get('color') is not None else 0
        prims.append(dict(mat=m, v=np.vstack(v), n=np.vstack(n), uv=np.vstack(uv), f=np.vstack(f), uv2=np.vstack(u2) if u2 else None, color=np.concatenate(cc) if cc else None))
    return prims
def export_env(S, P2, out): write_glb(f'{out}/env.glb', merge(P2)); used = {q['mat'] for q in P2}; json.dump({k: {a: b for a, b in MATS[k].items() if b not in (None, False) and a not in ('bakek', 'artavg')} for k in sorted(used)}, open(f'{out}/materials.json', 'w'))
def save_mats():
    p = f'{PUB}/materials.json'; old = json.load(open(p)) if os.path.exists(p) else {}
    for k, v in MATS.items(): old[k] = {a: b for a, b in v.items() if b not in (None, False) and a not in ('bakek', 'artavg')}
    json.dump(old, open(p, 'w'), indent=0, sort_keys=True)
def preview(S, path, cam, target, lens=24, chans=('day', 'lamp', 'led'), w=960, h=600, samples=48, wts=None):
    """cycles look-dev render with textures, coloured lights"""
    bpy.context.scene.render.film_transparent = False
    pass
