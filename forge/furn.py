"""Furniture library. Every function draws around local origin on the floor; caller positions with `with S.at(loc, rot)`. Front faces -y."""
import math, random
from kit import M, MATS
FD = '/home/model/.cache/forge/fonts/display.ttf'; FM = '/home/model/.cache/forge/fonts/marker.ttf'; FS = '/home/model/.cache/forge/fonts/shoulders.ttf'
def common():
    M('trim', 'paint', '#f1ede4', .45, scale=1.5); M('ceil', 'plaster', '#f4f1ea', .95, scale=2)
    M('white', 'paint', '#f2efe9', .38, scale=1.2); M('offwhite', 'paint', '#e4ddcf', .42, scale=1.2); M('black', 'paint', '#17181a', .42, scale=1); M('charcoal', 'paint', '#2c2e31', .5, scale=1); M('gray', 'paint', '#7d7f80', .5)
    M('blackplastic', 'rubber', '#202225', .48, scale=.3); M('rubber', 'rubber', '#161718', .8, scale=.3); M('gloss', 'paint', '#0b0c0e', .09); M('steel', 'brushed', '#c9c8c4', .34, 1, .5); M('darksteel', 'brushed', '#4a4b4e', .4, 1, .5); M('chrome', 'brushed', '#eceae6', .1, 1); M('brass', 'brushed', '#caa45c', .28, 1); M('gold', 'brushed', '#f0c14e', .2, 1); M('copper', 'brushed', '#c77f58', .3, 1)
    for n in ('oak', 'walnut', 'pine', 'gray'): M('wood_' + n, 'wood_' + n, '#ffffff', None, scale=.9)
    M('linen', 'fabric', '#e9e2d4', .95, scale=.5); M('sheet', 'fabric', '#dfe3e6', .95, scale=.7); M('denim', 'fabric', '#41587a', .95, scale=.25); M('fabric_gray', 'fabric', '#8d8f8f', .95, scale=.4); M('fabric_dark', 'fabric', '#3b3e42', .95, scale=.4); M('fabric_green', 'fabric', '#55705a', .95, scale=.4); M('fabric_rust', 'fabric', '#b0573a', .95, scale=.4); M('fabric_must', 'fabric', '#cf9f3e', .95, scale=.4); M('fabric_blue', 'fabric', '#3f5d86', .95, scale=.4); M('fabric_teal', 'fabric', '#2f6570', .95, scale=.4); M('fabric_rose', 'fabric', '#b77a7c', .95, scale=.4); M('fabric_cream', 'fabric', '#e6dcc6', .95, scale=.4); M('knit_red', 'knit', '#9c342b', .96, scale=.3); M('knit_cream', 'knit', '#e5d9c0', .96, scale=.3)
    M('leather_brown', 'leather', '#6f4228', .45, scale=.5); M('leather_black', 'leather', '#1d1c1c', .42, scale=.5); M('leather_white', 'leather', '#e9e4da', .42, scale=.5); M('leather_red', 'leather', '#a8231c', .42, scale=.5)
    M('card', 'cardboard', '#ffffff', .92, scale=.6); M('paper', 'paint', '#f4f0e6', .9); M('concrete', 'concrete', '#ffffff', None, scale=2); M('marble', 'marble', '#ffffff', None, scale=1.6); M('marble_dark', 'marble', '#3a3733', None, scale=1.6)
    M('leaf', None, '#3f6b32', .5, two=True); M('leaf2', None, '#5c8a3c', .5, two=True); M('stem', None, '#4f5f2c', .7); M('soil', 'carpet', '#3a281b', .98, scale=.2); M('terracotta', 'plaster', '#b8653f', .8, scale=.4); M('ceramic', 'paint', '#efe9dd', .14); M('ceramic_blue', 'paint', '#33566b', .14)
    M('bk1', 'fabric', '#8f2d27', .7, scale=.3); M('bk2', 'fabric', '#21404f', .7, scale=.3); M('bk3', 'fabric', '#cfa75a', .7, scale=.3); M('bk4', 'fabric', '#33614f', .7, scale=.3); M('bk5', 'fabric', '#ddd2b8', .7, scale=.3); M('bk6', 'fabric', '#493a55', .7, scale=.3); M('bk7', 'fabric', '#24262b', .7, scale=.3)
    M('red', 'paint', '#c5281c', .4); M('yellow', 'paint', '#e8b81f', .4); M('teal', 'paint', '#1f7f86', .4); M('blue', 'paint', '#2a55a0', .4); M('green', 'paint', '#3c7a48', .4); M('pink', 'paint', '#e08aa0', .4); M('orange', 'paint', '#d9712a', .4)
    M('shade', 'fabric', '#f2e3c4', .95, emit=('#ffc887', 1.9), chan='lamp', scale=.4, bakek=3); M('bulb', None, '#ffffff', .4, emit=('#ffd9a6', 5), chan='lamp', bakek=6); M('bulbs', None, '#ffffff', .4, emit=('#ffc070', 4), chan='lamp', bakek=5); M('panel', None, '#ffffff', .4, emit=('#fff1dc', 3), chan='lamp', bakek=3); M('strip', None, '#ffffff', .4, emit=('#ffffff', 3), chan='led', bakek=4.6)
    M('glass', 'paint', '#cfe0e4', .05, alpha=.18); M('mirror', 'paint', '#dfe4e6', .03, 1)
    for a in ('poster_fortknight', 'poster_eldenbling', 'poster_otter', 'poster_cyberjunk', 'poster_amongusb', 'poster_darksoles', 'poster_grind', 'poster_latency', 'poster_minedcraft', 'cert', 'calendar', 'box_amazin', 'box_pizza', 'can_mobster', 'can_redbill', 'book_spines', 'tv_news', 'keys', 'whiteboard', 'painting_1', 'painting_2', 'portrait_gold'): M(a, None, '#ffffff', .55, art=a)
    for a in ('scr_edit', 'scr_stats', 'scr_chat', 'scr_cams', 'aquarium'): M(a, None, '#ffffff', .3, art=a, emit=('#ffffff', 1.5), chan='always')
    M('rugtex', 'rug', '#ffffff', .97, scale=1)
BK = ['bk1', 'bk2', 'bk3', 'bk4', 'bk5', 'bk6', 'bk7']
def window(S, w, z0, z1, x, wall_y, rot=0, cols=2, rows=2, mat='trim', sill=True, t=.12, fr=.05):
    h = z1 - z0
    with S.at((x, wall_y, 0), rot):
        for sx in (-1, 1): S.box((fr, .05, h), (sx * (w / 2 - fr / 2), .06, z0 + h / 2), mat, bevel=.004, seg=1)
        for z in (z0 + fr / 2, z1 - fr / 2): S.box((w, .05, fr), (0, .06, z), mat, bevel=.004, seg=1)
        for i in range(1, cols): S.box((.03, .035, h), (-w / 2 + w * i / cols, .06, z0 + h / 2), mat, bevel=.003, seg=1)
        for j in range(1, rows): S.box((w, .035, .03), (0, .06, z0 + h * j / rows), mat, bevel=.003, seg=1)
        # casing
        for sx in (-1, 1): S.box((.075, .02, h + .15), (sx * (w / 2 + .035), -.01, z0 + h / 2), mat, bevel=.005, seg=1)
        S.box((w + .2, .03, .085), (0, -.012, z1 + .04), mat, bevel=.006, seg=1)
        if sill: S.box((w + .22, .16, .03), (0, -.05, z0 - .012), mat, bevel=.008)
def door(S, w=.84, h=2.03, mat='white', knob='brass', panels=True):
    S.box((w, .04, h), (0, .0, h / 2), mat, bevel=.003, seg=1)
    if panels:
        for (z, ph) in ((.52, .72), (1.42, .86)):
            for sx in (-1, 1):
                S.box((w * .33, .012, ph), (sx * w * .215, -.022, z), mat, bevel=.009, seg=2)
    for sx in (-1, 1): S.box((.07, .03, h + .07), (sx * (w / 2 + .035), -.005, (h + .07) / 2), 'trim', bevel=.005, seg=1)
    S.box((w + .14, .03, .07), (0, -.005, h + .035), 'trim', bevel=.005, seg=1)
    S.cyl(.026, .012, (w / 2 - .07, -.028, 1.0), knob, axis='y'); S.sphere(.027, (w / 2 - .07, -.07, 1.0), knob); S.cyl(.01, .05, (w / 2 - .07, -.045, 1.0), knob, axis='y')
def bed(S, w=1.05, l=2.0, frame='wood_pine', head=True, sheet='sheet', blanket='fabric_blue', pillows=1, h=.42, duvet=True, throw=None):
    S.box((w + .06, l + .04, .16), (0, 0, h - .22), frame, bevel=.012, grain='y')
    for sx in (-1, 1):
        for sy in (-1, 1): S.box((.07, .07, h - .14), (sx * (w / 2 - .03), sy * (l / 2 - .04), (h - .14) / 2), frame, bevel=.006)
    if head:
        S.box((w + .1, .045, .42), (0, l / 2 + .02, h + .22), frame, bevel=.014, grain='x'); S.box((w + .14, .06, .05), (0, l / 2 + .02, h + .44), frame, bevel=.016, grain='x'); S.box((w + .1, .04, .2), (0, -l / 2 - .02, h - .06), frame, bevel=.014, grain='x')
    S.cushion((w - .02, l - .03, .24), (0, 0, h), sheet, puff=.14, res=7, noise=.002)
    for i in range(pillows):
        px = (i - (pillows - 1) / 2) * (w / pillows); S.cushion((w / pillows * .82, .42, .17), (px + .01, l / 2 - .27, h + .18), 'linen', rx=.28, rot=S.rnd.uniform(-.08, .08), puff=.75, res=9, noise=.006)
    if duvet: S.cloth(w + .62, l * .78, h + .3, [((w + .02, l, .30), (0, 0, h - .03)), ((3, 4, .02), (0, 0, .0))], blanket, loc=(0, -l * .17), nx=46, ny=46, frames=42, crumple=.02, rot=.04)
    if throw: S.cushion((w * .9, .5, .06), (0, -l / 2 + .35, h + .17), throw, puff=.2)
def nightstand(S, mat='wood_pine', w=.42, d=.38, h=.5):
    S.box((w, d, .025), (0, 0, h - .012), mat, grain='x'); S.box((w - .02, d - .02, h - .2), (0, 0, (h - .2) / 2 + .1), mat, bevel=.004, grain='z'); S.box((w - .06, .018, .15), (0, -d / 2 + .005, h - .13), mat, grain='x'); S.sphere(.013, (0, -d / 2 - .018, h - .13), 'brass', 12, 8)
    for sx in (-1, 1):
        for sy in (-1, 1): S.box((.03, .03, .1), (sx * (w / 2 - .03), sy * (d / 2 - .03), .05), mat, bevel=.003, seg=1)
def table_lamp(S, z=0, shade='shade', base='ceramic_blue', light=True, e=14):
    S.lathe([(0, z), (.055, z), (.06, z + .01), (.03, z + .03), (.05, z + .08), (.055, z + .13), (.03, z + .19), (.01, z + .21), (.01, z + .26)], mat=base); S.lathe([(.11, z + .24), (.075, z + .40)], mat=shade, sharp=80, seg=32); S.lathe([(.074, z + .40), (.109, z + .24)], mat=shade, sharp=80, seg=32)
    S.sphere(.025, (0, 0, z + .3), 'bulb', 10, 8)
    if light: S.point((S.xf[-1].translation.x, S.xf[-1].translation.y, S.xf[-1].translation.z + z + .33), .05, e, '#ffbf7f', 'lamp')
def floor_lamp(S, h=1.55, e=30, mat='black'):
    S.cyl(.14, .02, (0, 0, .01), mat, 32); S.cyl(.011, h, (0, 0, h / 2), mat, 10, 0); S.lathe([(.2, h - .02), (.13, h + .26)], mat='shade', sharp=80, seg=36); S.lathe([(.129, h + .26), (.199, h - .02)], mat='shade', sharp=80, seg=36); S.sphere(.035, (0, 0, h + .1), 'bulb', 10, 8)
    p = S.xf[-1].translation; S.point((p.x, p.y, p.z + h + .12), .07, e, '#ffbf7f', 'lamp')
def desk(S, w=1.2, d=.6, h=.74, top='wood_pine', leg='white', drawers=True, metal=False):
    S.box((w, d, .03), (0, 0, h - .015), top, bevel=.006, grain='x')
    if metal:
        for sx in (-1, 1):
            S.box((.05, d - .06, .03), (sx * (w / 2 - .08), 0, .015), leg, bevel=.004, seg=1); S.box((.06, .06, h - .04), (sx * (w / 2 - .08), 0, h / 2 - .02), leg, bevel=.004, seg=1); S.box((.05, d - .1, .04), (sx * (w / 2 - .08), 0, h - .05), leg, bevel=.004, seg=1)
        S.box((w - .2, .04, .05), (0, .05, h - .06), leg, bevel=.004, seg=1)
    else:
        for sy in (-1, 1): S.box((.05, .05, h - .03), (-w / 2 + .045, sy * (d / 2 - .045), (h - .03) / 2), leg, bevel=.005)
        if drawers:
            S.box((.38, d - .05, h - .1), (w / 2 - .22, 0, h / 2 - .02), leg, bevel=.005)
            for i in range(3): S.box((.34, .02, .17), (w / 2 - .22, -d / 2 + .018, h - .17 - i * .19), leg, bevel=.006); S.cyl(.006, .1, (w / 2 - .22, -d / 2 - .012, h - .17 - i * .19), 'steel', 8, 0, axis='x')
        else:
            for sy in (-1, 1): S.box((.05, .05, h - .03), (w / 2 - .045, sy * (d / 2 - .045), (h - .03) / 2), leg, bevel=.005)
        S.box((w - .1, .02, .09), (0, d / 2 - .05, h - .08), leg, bevel=.003, seg=1)
def shelf(S, w=.7, d=.28, h=1.8, n=5, mat='wood_pine', fill=.85, back=True, items=True, seed=3):
    for sx in (-1, 1): S.box((.022, d, h), (sx * (w / 2 - .011), 0, h / 2), mat, bevel=.003, seg=1, grain='z')
    if back: S.box((w - .03, .01, h - .02), (0, d / 2 - .006, h / 2), mat, bevel=0, grain='z')
    rs = random.Random(seed)
    for i in range(n + 1):
        z = .05 + (h - .08) * i / n; S.box((w - .03, d - .01, .022), (0, 0, z), mat, bevel=.003, seg=1, grain='x')
        if items and i < n:
            r = rs.random(); ch = (h - .08) / n - .04
            if r < fill:
                bw = (w - .08) * rs.uniform(.45, .95); S.books(bw, (-w / 2 + .03, .02, z + .012), BK, min(.14, ch * .6), min(.25, ch * .95), d * .7)
                if bw < w * .65: deco(S, (w / 2 - .14, -.02, z + .012), rs)
            else:
                for k in range(2): deco(S, (-w / 4 + k * w / 2, -.01, z + .012), rs)
def deco(S, loc, rs):
    k = rs.choice(['cup', 'vase', 'box', 'fig', 'ball', 'frame'])
    if k == 'cup': trophy(S, loc, .16)
    elif k == 'vase': S.lathe([(0, 0), (.04, 0), (.06, .05), (.055, .1), (.025, .14), (.03, .17)], loc, rs.choice(['ceramic', 'ceramic_blue', 'terracotta']), 18)
    elif k == 'box': S.box((.13, .12, .09), loc, rs.choice(['card', 'red', 'teal', 'yellow']), base=True)
    elif k == 'ball': S.sphere(.055, (loc[0], loc[1], loc[2] + .055), rs.choice(['orange', 'red', 'teal']), 16, 10)
    elif k == 'frame':
        S.box((.15, .015, .2), (loc[0], loc[1] + .03, loc[2] + .1), 'black', rx=-.15); S.quad(.12, .17, (loc[0], loc[1] + .0185, loc[2] + .1), rs.choice(['poster_latency', 'painting_2', 'poster_grind']), rx=math.pi / 2 - .15)
    else: figure(S, loc, rs.choice(['red', 'teal', 'yellow', 'blue', 'green', 'pink']))
def trophy(S, loc, h=.2, mat='gold'):
    k = h / .2
    with S.at(loc, scale=k): S.lathe([(0, 0), (.04, 0), (.04, .03), (.012, .04), (.01, .08), (.03, .1), (.05, .15), (.055, .2), (.05, .2), (.03, .12), (0, .105)], mat=mat, seg=20); S.tube([(.05, 0, .18), (.085, 0, .17), (.075, 0, .13), (.04, 0, .115)], .005, mat, 6); S.tube([(-.05, 0, .18), (-.085, 0, .17), (-.075, 0, .13), (-.04, 0, .115)], .005, mat, 6)
def figure(S, loc, mat):
    with S.at(loc): S.cyl(.035, .008, (0, 0, .004), 'black', 18); S.box((.02, .02, .05), (-.012, 0, .033), mat, .005); S.box((.02, .02, .05), (.012, 0, .033), mat, .005); S.box((.055, .03, .055), (0, 0, .085), mat, .01); S.box((.016, .018, .055), (-.037, -.006, .085), mat, .006, rx=.4); S.box((.016, .018, .055), (.037, 0, .09), mat, .006, ry=-.6); S.sphere(.03, (0, 0, .14), 'offwhite', 14, 10); S.sphere(.0305, (0, .003, .145), mat, 14, 10, (1, 1, .8))
def chair_wood(S, mat='wood_pine', seat='fabric_rust'):
    for sx in (-1, 1):
        S.box((.035, .035, .44), (sx * .18, -.18, .22), mat, .005); S.box((.035, .035, .88), (sx * .18, .19, .44), mat, .005, rx=-.04)
    S.box((.42, .42, .03), (0, 0, .445), mat, .01); S.cushion((.4, .4, .05), (0, 0, .475), seat, puff=.5, res=5)
    for z in (.6, .72, .84): S.box((.36, .018, .06), (0, .2 + (z - .45) * .04, z), mat, .006, grain='x')
def wardrobe(S, w=1.0, d=.55, h=2.0, mat='white', knob='brass'):
    S.box((w, d, h), (0, 0, h / 2), mat, bevel=.008); S.box((w + .04, d + .03, .05), (0, -.005, h + .01), mat, bevel=.012); S.box((w - .02, d - .02, .08), (0, -.02, .03), mat, bevel=.004, seg=1)
    for sx in (-1, 1):
        S.box((w / 2 - .02, .02, h - .18), (sx * w / 4, -d / 2 - .006, h / 2 + .04), mat, bevel=.005); S.box((w / 2 - .14, .01, h - .34), (sx * w / 4, -d / 2 - .018, h / 2 + .04), mat, bevel=.004, seg=1); S.sphere(.014, (sx * .035, -d / 2 - .032, h / 2), knob, 12, 8)
def rug(S, w, d, loc=(0, 0), mat='rugtex', rot=0, circle=False):
    import bmesh
    from mathutils import Matrix
    if circle: S.cyl(w / 2, .012, (loc[0], loc[1], .007), mat, 48, .004); return
    bm = bmesh.new(); l = bm.loops.layers.uv.new(); n = 10; g = [[bm.verts.new(((i / n - .5) * w, (j / n - .5) * d, .013 + .003 * math.sin(i * 1.7 + j))) for i in range(n + 1)] for j in range(n + 1)]
    for j in range(n):
        for i in range(n):
            f = bm.faces.new((g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]))
            for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))): lp[l].uv = (a / n, b / n)
    bmesh.ops.transform(bm, matrix=Matrix.Translation((loc[0], loc[1], 0)) @ Matrix.Rotation(rot, 4, 'Z'), verts=bm.verts); S.add(bm, mat, uv='mesh', sharp=80)
def poster(S, art, x, z, y, w=.5, h=.75, rot=0, tilt=0, frame=None):
    if S.xf[-1][0][0] < -.9: frame = None  # south wall: must vanish from behind
    with S.at((x, y, z), rot, ry=0):
        if frame: S.box((w + .05, .02, h + .05), (0, -.008, 0), frame, .004, 1); S.quad(w, h, (0, -.0195, 0), art)
        else:
            S.quad(w, h, (0, -.004, 0), art)
def string_lights(S, pts, n=7):
    import numpy as np
    for a, b in zip(pts, pts[1:]):
        q = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t - .12 * 4 * t * (1 - t)) for t in np.linspace(0, 1, n + 1)]; S.tube(q, .003, 'black', 4)
        for p in q[:-1]: S.sphere(.014, (p[0], p[1], p[2] - .025), 'bulbs', 8, 6, (1, 1, 1.4))
def mug(S, loc, mat='ceramic'): S.lathe([(0, 0), (.036, 0), (.04, .01), (.04, .09), (.036, .09), (.035, .015), (0, .012)], loc, mat, 20); S.tube([(loc[0] + .038, loc[1], loc[2] + .075), (loc[0] + .065, loc[1], loc[2] + .068), (loc[0] + .065, loc[1], loc[2] + .035), (loc[0] + .038, loc[1], loc[2] + .025)], .006, mat, 6)
def can(S, loc, mat='can_mobster'):
    import bmesh
    bm = bmesh.new(); l = bm.loops.layers.uv.new(); n = 18; r = .027
    a = [[bm.verts.new((r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z)) for i in range(n)] for z in (.01, .145)]
    for i in range(n):
        f = bm.faces.new((a[0][i], a[0][(i + 1) % n], a[1][(i + 1) % n], a[1][i]))
        for lp, (u, v) in zip(f.loops, ((i, 0), (i + 1, 0), (i + 1, 1), (i, 1))): lp[l].uv = (u / n, v)
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts); S.add(bm, mat, uv='mesh', sharp=60); S.lathe([(.022, 0), (.027, .01)], loc, 'steel', n); S.lathe([(.027, .145), (.023, .155), (.02, .153), (0, .153)], loc, 'steel', n)
def boxart(S, size, loc, mat, art, rot=0):
    S.box(size, loc, mat, .004, 1, rot=rot, base=True)
    with S.at((loc[0], loc[1], loc[2] + size[2] / 2), rot): S.quad(size[0] * .96, size[2] * .96, (0, -size[1] / 2 - .0015, 0), art); S.quad(size[0] * .96, size[1] * .96, (0, 0, size[2] / 2 + .0015), art, rx=0)
def pizza_box(S, loc, rot=0): S.box((.36, .36, .04), loc, 'paper', .004, 1, rot=rot, base=True); S.quad(.34, .34, (loc[0], loc[1], loc[2] + .0415), 'box_pizza', rot=rot, rx=0)
def plant(S, loc=(0, 0, 0), h=.7, pot='terracotta', n=14, seed=1, big=False, leaf='leaf'):
    k = h / .7
    with S.at(loc, scale=k): S.lathe([(0, 0), (.11, 0), (.15, .22), (.16, .22), (.16, .26), (.145, .26), (.13, .23), (0, .23)], mat=pot, seg=24); S.cyl(.135, .01, (0, 0, .235), 'soil', 20, 0); S.leafy((0, 0, .23), leaf, 'stem', n, .42 if big else .32, .85 if big else .5, (.16, .36) if big else (.1, .26), seed=seed)
def sofa(S, w=2.0, d=.9, mat='fabric_gray', legs='wood_walnut', seats=3, pil=('fabric_must', 'fabric_rust')):
    S.box((w - .1, d - .1, .2), (0, 0, .24), mat, .03, 3); S.cushion((w, .24, .52), (0, d / 2 - .12, .53), mat, puff=.2, res=7)
    for sx in (-1, 1): S.cushion((.22, d, .46), (sx * (w / 2 - .1), 0, .36), mat, puff=.22, res=6)
    iw = (w - .42) / seats
    for i in range(seats):
        x = -w / 2 + .21 + iw * (i + .5); S.cushion((iw - .01, d - .26, .18), (x, -.1, .42), mat, puff=.4, res=7, noise=.003); S.cushion((iw - .02, .2, .46), (x, d / 2 - .26, .68), mat, rx=-.18, puff=.55, res=7, noise=.004)
    for i, m in enumerate(pil): S.cushion((.42, .14, .42), ((-1) ** i * (w / 2 - .42), .02, .66), m, rx=-.35, rot=(-1) ** i * -.2, puff=.8, res=7)
    for sx in (-1, 1):
        for sy in (-1, 1): S.cyl(.022, .14, (sx * (w / 2 - .12), sy * (d / 2 - .12), .07), legs, 12, .002)
def coffee_table(S, w=1.1, d=.55, h=.4, top='wood_walnut', leg='black'):
    S.box((w, d, .035), (0, 0, h), top, .01, grain='x')
    for sx in (-1, 1):
        for sy in (-1, 1): S.box((.03, .03, h - .02), (sx * (w / 2 - .08), sy * (d / 2 - .07), h / 2 - .01), leg, .003, 1)
    S.box((w - .16, d - .14, .02), (0, 0, .13), top, .004, 1, grain='x')
def kitchen(S, w=2.4, cab='white', top='marble_dark', upper=True, sink=True, stove=True, d=.6, splash=None):
    n = max(2, int(round(w / .6))); cw = w / n
    S.box((w, d - .06, .1), (0, .03, .05), 'charcoal', .002, 1); S.box((w, d, .76), (0, 0, .48), cab, .004, 1); S.box((w + .03, d + .04, .04), (0, -.01, .88), top, .006)
    for i in range(n):
        x = -w / 2 + cw * (i + .5)
        if stove and i == n - 1:
            S.box((cw - .02, .02, .56), (x, -d / 2 - .008, .42), 'gloss', .004, 1); S.cyl(.011, cw - .14, (x, -d / 2 - .045, .68), 'steel', 10, 0, axis='x'); S.box((cw - .02, .02, .11), (x, -d / 2 - .008, .79), 'steel', .003, 1)
            for k in range(4): S.cyl(.018, .02, (x - .18 + k * .12, -d / 2 - .025, .79), 'black', 14, .003, axis='y')
            S.box((cw - .06, d - .1, .008), (x, 0, .903), 'gloss', .003, 1)
            for a, b in ((-.13, -.12), (.13, -.12), (-.13, .13), (.13, .13)): S.cyl(.08, .006, (x + a, b, .909), 'darksteel', 24, .002)
        else:
            S.box((cw - .008, .018, .54), (x, -d / 2 - .008, .41), cab, .004); S.box((cw - .008, .018, .16), (x, -d / 2 - .008, .775), cab, .004); S.cyl(.006, .14, (x, -d / 2 - .035, .775), 'brass', 8, 0, axis='x'); S.cyl(.006, .14, (x + cw * .36, -d / 2 - .035, .6), 'brass', 8, 0)
        if upper and not (stove and i == n - 1): S.box((cw - .006, .33, .66), (x, d / 2 - .165, 1.8), cab, .005); S.box((cw - .014, .018, .64), (x, d / 2 - .338, 1.8), cab, .004); S.cyl(.006, .12, (x + cw * .36, d / 2 - .365, 1.58), 'brass', 8, 0)
        if upper and stove and i == n - 1: S.box((cw - .02, .45, .1), (x, d / 2 - .225, 1.6), 'steel', .006); S.box((.24, .24, .8), (x, d / 2 - .13, 2.0), 'steel', .004, 1)
    if sink: S.box((.5, .4, .012), (-w / 2 + cw * 1.1, -.01, .903), 'steel', .004, 1); S.box((.42, .32, .005), (-w / 2 + cw * 1.1, -.01, .911), 'darksteel', 0); S.curve([(-w / 2 + cw * 1.1, .22, .9), (-w / 2 + cw * 1.1, .22, 1.18), (-w / 2 + cw * 1.1, .1, 1.22), (-w / 2 + cw * 1.1, .02, 1.12)], .012, 'chrome', 5)
    if splash: S.quad(w, .6 if upper else .5, (0, d / 2 - .002, 1.2 if upper else 1.15), splash)
def fridge(S, w=.7, d=.68, h=1.78, mat='steel'):
    S.box((w, d - .06, h), (0, .03, h / 2), 'gray', .01); S.box((w, .06, h * .62), (0, -d / 2 + .03, h * .685), mat, .014); S.box((w, .06, h * .33), (0, -d / 2 + .03, h * .185), mat, .014); S.cyl(.012, .5, (-w / 2 + .07, -d / 2 - .045, h * .62), 'chrome', 10, 0); S.cyl(.012, .25, (-w / 2 + .07, -d / 2 - .045, h * .25), 'chrome', 10, 0)
    for i, m in enumerate(('red', 'yellow', 'teal', 'pink')): S.box((.05, .008, .05), (-.1 + i * .09, -d / 2 - .003, 1.32 + (i % 2) * .1), m, .004, 1)
    S.quad(.18, .24, (.06, -d / 2 - .004, 1.16), 'calendar')
def radiator(S, w=.9, h=.55):
    n = int(w / .075)
    for i in range(n): S.box((.05, .09, h), (-w / 2 + .0375 + i * .075, 0, .12 + h / 2), 'offwhite', .018)
    S.cyl(.02, w, (0, 0, .17), 'offwhite', 10, 0, axis='x'); S.cyl(.02, w, (0, 0, .06 + h), 'offwhite', 10, 0, axis='x')
def pile(S, n, mats, r=.3, seed=2):
    rs = random.Random(seed)
    for i in range(n):
        a = rs.random() * 6.28; q = r * rs.random(); S.cushion((rs.uniform(.25, .4), rs.uniform(.2, .34), rs.uniform(.06, .12)), (math.cos(a) * q, math.sin(a) * q, .05 + i * .045), rs.choice(mats), rot=rs.random() * 6, rx=rs.uniform(-.35, .35), ry=rs.uniform(-.35, .35), puff=.6, res=6, noise=.016)
def basket(S, r=.24, h=.5): S.lathe([(0, .01), (r * .8, 0), (r, h), (r * 1.04, h + .02), (r * .95, h + .01), (r * .76, .03), (0, .03)], mat='wood_pine', seg=24)
def tv(S, w=1.3, art='tv_news', stand=True, z=.75):
    h = w * 9 / 16; S.box((w + .02, .04, h + .02), (0, .03, z + h / 2), 'black', .006); S.quad(w, h, (0, .009, z + h / 2), art if isinstance(art, str) else 'gloss')
    if stand: S.box((w * .5, .22, .015), (0, .02, z - .045), 'black', .004, 1); S.box((.08, .04, .08), (0, .03, z - .02), 'black', .004, 1)
def pendant(S, loc, h=.8, mat='black', e=20, r=.16):
    x, y, z = loc; S.cyl(.004, h, (x, y, z - h / 2), 'black', 6, 0); S.lathe([(.02, z - h + .14), (.05, z - h + .13), (r, z - h), (r * .97, z - h), (.045, z - h + .12)], (x, y, 0), mat, 28); S.sphere(.035, (x, y, z - h + .03), 'bulb', 10, 8); p = S.xf[-1] @ __import__('mathutils').Vector((x, y, z - h - .02)); S.point(tuple(p), .05, e, '#ffcf98', 'lamp')
def ceiling_dome(S, loc, r=.18, e=45, col='#ffd3a0'):
    x, y, z = loc; S.lathe([(0, z - .1), (r * .6, z - .085), (r, z - .03), (r * 1.02, z), (0, z)][::-1], (x, y, 0), 'panel', 28, 80); S.point((x, y, z - .18), .12, e, col, 'lamp')
def tripod(S, h=1.4, mat='black', head=True):
    for i in range(3):
        a = i * 2.094 + .5; S.tube([(math.cos(a) * .42, math.sin(a) * .42, .01), (0, 0, h * .78)], .012, mat, 8)
    S.cyl(.014, h * .4, (0, 0, h * .8), mat, 10, 0)
    if head: S.box((.08, .06, .05), (0, 0, h), mat, .008)
def softbox(S, h=2.0, tilt=.5, e=40):
    tripod(S, h - .1, head=False)
    with S.at((0, 0, h), rx=-tilt): S.box((.7, .02, .7), (0, -.2, 0), 'panel', .01); S.lathe([(.06, .05), (.1, -.02), (.5, -.19)], mat='black', seg=4); S.cyl(.06, .16, (0, .05, 0), 'black', 16, .01, axis='y')
def cine_cam(S, z=1.45):
    S.box((.14, .24, .16), (0, .02, z + .12), 'blackplastic', .014); S.cyl(.055, .18, (0, -.18, z + .12), 'black', 24, .008, axis='y'); S.cyl(.05, .004, (0, -.272, z + .12), 'gloss', 24, 0, axis='y'); S.box((.17, .09, .12), (0, -.28, z + .12), 'black', .006, 1); S.box((.03, .2, .03), (0, 0, z + .26), 'black', .008); S.box((.12, .02, .08), (-.13, .06, z + .17), 'gloss', .004, 1); S.sphere(.008, (.05, -.1, z + .215), 'red', 8, 6); tripod(S, z)
def arcade(S, art='poster_cyberjunk', col='red'):
    S.box((.62, .6, .8), (0, .08, .4), col, .01); S.box((.62, .4, 1.0), (0, .18, 1.25), col, .01); S.box((.62, .5, .22), (0, .02, 1.74), col, .02); S.box((.6, .34, .05), (0, -.16, .86), 'black', .01, rx=.25); S.quad(.5, .44, (0, -.025, 1.25), art, rx=math.pi / 2 - .18); S.quad(.56, .17, (0, -.2315, 1.74), art, uv=(0, .04, 1, .2)); S.cyl(.01, .08, (-.14, -.19, .93), 'chrome', 8, 0); S.sphere(.022, (-.14, -.19, .975), 'red', 12, 8)
    for i in range(4): S.cyl(.016, .014, (.03 + i * .055, -.18 + (i % 2) * .03, .9), ['yellow', 'blue', 'green', 'pink'][i], 12, .003)

def office_chair(S, mat='fabric_dark'):
    for i in range(5):
        a = i * 2 * math.pi / 5; S.tube([(0, 0, .1), (math.cos(a) * .3, math.sin(a) * .3, .065)], .022, 'blackplastic', 6); S.cyl(.028, .04, (math.cos(a) * .3, math.sin(a) * .3, .03), 'black', 12, .006, axis='y', rot=a)
    S.cyl(.03, .34, (0, 0, .26), 'steel', 12, 0); S.cushion((.5, .5, .1), (0, 0, .47), mat, puff=.3, res=6); S.cushion((.46, .09, .56), (0, .24, .84), mat, rx=-.12, puff=.35, res=6); S.box((.06, .03, .3), (0, .29, .58), 'blackplastic', .008)
    for sx in (-1, 1): S.box((.05, .28, .03), (sx * .29, -.02, .68), 'blackplastic', .01); S.box((.03, .04, .2), (sx * .29, .04, .58), 'blackplastic', .006)
def monitor(S, loc, art='scr_edit', w=.6, rot=0):
    h = w * 9 / 16
    with S.at(loc, rot): S.box((.22, .18, .012), (0, .03, .006), 'black', .004, 1); S.box((.04, .03, .24), (0, .06, .12), 'black', .004, 1); S.box((w + .016, .03, h + .016), (0, .035, .17 + h / 2), 'black', .006, 1); S.quad(w, h, (0, .0185, .17 + h / 2), art)
def keyboard(S, loc, rot=0):
    with S.at(loc, rot): S.box((.43, .15, .018), (0, 0, .009), 'blackplastic', .005); S.quad(.41, .14, (0, 0, .0186), 'keys', rx=0); S.box((.06, .1, .025), (.3, 0, .0125), 'blackplastic', .012)
def workstation(S, a='scr_edit', b='scr_chat', top='wood_oak', w=1.5, chair=True):
    desk(S, w, .7, .74, top, 'black', metal=True); monitor(S, (-.3, .14, .74), a, .58, .12); monitor(S, (.34, .14, .74), b, .58, -.14); keyboard(S, (0, -.14, .74)); mug(S, (w / 2 - .15, -.1, .74), S.rnd.choice(['ceramic', 'ceramic_blue', 'red', 'teal'])); 
    p = S.xf[-1].translation; S.area((p.x, p.y, 1.1), .4, 2.2, '#dfe8ff', 'lamp', (math.pi / 2, 0, math.atan2(S.xf[-1][1][0], S.xf[-1][0][0])), .3)
    if chair:
        with S.at((0.05, -.62, 0), math.pi + .25): office_chair(S, S.rnd.choice(['fabric_dark', 'fabric_gray', 'fabric_teal']))
def stool(S, h=.72, mat='wood_walnut'):
    S.cyl(.17, .035, (0, 0, h), mat, 24, .01)
    for i in range(4): a = i * math.pi / 2 + .78; S.tube([(math.cos(a) * .1, math.sin(a) * .1, h - .02), (math.cos(a) * .2, math.sin(a) * .2, 0)], .013, 'black', 6)
    S.tube([(math.cos(i * .5236 * 2) * .17, math.sin(i * .5236 * 2) * .17, .24) for i in range(6)], .008, 'black', 5, closed=True)
def foam_wall(S, w, h, loc, rot=0, n=(5, 3), a='foam_dark', b='foam_acc'):
    cw, ch = w / n[0], h / n[1]
    with S.at(loc, rot):
        for i in range(n[0]):
            for j in range(n[1]): S.box((cw - .012, .045, ch - .012), (-w / 2 + cw * (i + .5), -.023, -h / 2 + ch * (j + .5)), b if (i * 7 + j * 3) % 5 == 0 else a, .006, 1)
def hexes(S, cells, r, loc, rot=0):
    with S.at(loc, rot):
        for (q, k) in cells:
            x = r * 1.76 * (q + .5 * (k & 1)); z = r * 1.53 * k; S.cyl(r, .025, (x, -.0125, z), 'strip', 6, .004, axis='y'); 
def palm(S, h=2.4, seed=3):
    S.lathe([(0, 0), (.24, 0), (.3, .5), (.32, .5), (.32, .55), (.28, .55), (.27, .5), (0, .5)], mat='ceramic', seg=28); S.cyl(.27, .01, (0, 0, .49), 'soil', 20, 0); S.curve([(0, 0, .5), (.04, .02, h * .35), (-.02, .03, h * .62)], .035, 'wood_gray', 6); S.leafy((-.02, .03, h * .55), 'leaf', 'stem', 16, .55, h * .4, (.22, .85), .6, seed)
def chandelier(S, loc, r=.8, e=160, drop=1.2):
    x, y, z = loc; S.cyl(.015, drop, (x, y, z - drop / 2), 'brass', 8, 0)
    with S.at((x, y, z - drop)):
        for (rr, zz, n) in ((r, 0, 14), (r * .6, .28, 9)):
            S.tube([(math.cos(i * 2 * math.pi / 32) * rr, math.sin(i * 2 * math.pi / 32) * rr, zz) for i in range(32)], .018, 'brass', 6, closed=True)
            for i in range(n):
                a = i * 2 * math.pi / n; S.cyl(.012, .09, (math.cos(a) * rr, math.sin(a) * rr, zz + .055), 'ceramic', 8, 0); S.sphere(.022, (math.cos(a) * rr, math.sin(a) * rr, zz + .13), 'bulb', 8, 6, (1, 1, 1.6))
            for i in range(n * 2): a = i * math.pi / n; S.sphere(.02, (math.cos(a) * rr, math.sin(a) * rr, zz - .05), 'crystal', 6, 4, (.7, .7, 1.6))
        for i in range(6): a = i * math.pi / 3; S.tube([(0, 0, .5), (math.cos(a) * r, math.sin(a) * r, 0)], .008, 'brass', 5)
    S.point((x, y, z - drop + .1), .5, e, '#ffcf95', 'lamp')
def column(S, h, r=.28):
    S.box((r * 2.5, r * 2.5, .22), (0, 0, .11), 'marble', .02); S.lathe([(r * 1.15, .22), (r * 1.2, .27), (r * 1.02, .36), (r, .42), (r * .9, h - .5), (r * .95, h - .44), (r * 1.2, h - .36), (r * 1.25, h - .24)], mat='marble', seg=32); S.box((r * 2.6, r * 2.6, .24), (0, 0, h - .12), 'marble', .02)
def piano(S):
    import bmesh
    bm = bmesh.new(); pts = [(-.75, -.75), (.75, -.75), (.75, -.2), (.62, .35), (.25, .75), (-.1, 1.15), (-.45, 1.3), (-.75, 1.15)]
    a = [bm.verts.new((x, y, .7)) for x, y in pts]; b = [bm.verts.new((x, y, 1.0)) for x, y in pts]; n = len(pts); bm.faces.new(list(reversed(a))); bm.faces.new(b)
    for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=.02, segments=2, affect='EDGES'); S.add(bm, 'gloss')
    S.box((1.3, .16, .03), (0, -.8, .74), 'offwhite', .004, 1); [S.box((.018, .09, .02), (-.6 + i * .05 + (.012 if i % 7 in (2, 6) else 0), -.765, .765), 'black', .003, 1) for i in range(25) if i % 7 not in (2, 6)]; S.box((1.5, .22, .05), (0, -.8, .7), 'gloss', .01)
    for (x, y) in ((-.62, -.6), (.62, -.6), (-.35, .95)): S.cyl(.05, .7, (x, y, .35), 'gloss', 12, .004, r2=.03)
    S.box((1.45, 1.9, .03), (-.05, .28, 1.33), 'gloss', .01, ry=-.55); S.box((.9, .35, .06), (0, -1.25, .5), 'leather_black', .02); [S.box((.04, .04, .47), (sx * .4, -1.25 + sy * .13, .235), 'gloss', .004, 1) for sx in (-1, 1) for sy in (-1, 1)]
