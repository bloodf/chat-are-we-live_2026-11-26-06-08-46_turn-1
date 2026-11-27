"""Dynamic props: geometry + vertex AO -> GLB, plus Cycles product shots for the in-game shop."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy; bpy.ops.wm.read_factory_settings(use_empty=True)
from kit import *; from furn import *; import furn
from mathutils.bvhtree import BVHTree
PI = math.pi; OUT = f'{PUB}/props'; SHOP = f'{PUB}/shop'; os.makedirs(OUT, exist_ok=True); os.makedirs(SHOP, exist_ok=True)
def mats():
    common(); M('screen', 'paint', '#0a0c10', .15); M('screen2', 'paint', '#0a0c10', .15); M('fan', None, '#ffffff', .4, emit=('#ffffff', 2.6), chan='led'); M('ringglow', None, '#ffffff', .4, emit=('#fff4e6', 3), chan='always'); M('neonp', None, '#ffffff', .4, emit=('#ff4a8a', 2.4), chan='always'); M('crackglass', 'paint', '#14171c', .1); M('skin_pink', 'knit', '#d99ab0', .95, scale=.3); M('plush', 'knit', '#9fb7a0', .97, scale=.25); M('plushd', 'knit', '#5f7a66', .97, scale=.25); M('silver', 'brushed', '#dfe2e6', .16, 1); M('wcool', None, '#ffd27a', .2, emit=('#ffb030', 2.2), chan='always'); M('cork', 'cardboard', '#c69a6b', .9, scale=.3); M('navy', 'paint', '#22304a', .4); M('lilac', 'paint', '#b9a4d8', .3); M('titan', 'brushed', '#b9ab98', .3, 1, .4); M('yellowtape', 'paint', '#e8b81f', .7)
def slab(S, w, h, t, body, r=.008, z=0, screen='screen', notch=False):
    S.box((w, t, h), (0, 0, z), body, r * .6, 3); S.quad(w * .92, h * .93, (0, -t / 2 - .0006, z), screen)
    S.box((w * .98, t * .9, h * .985), (0, -.0003, z), 'gloss', r * .5, 2)
def phone0(S):
    slab(S, .068, .142, .012, 'charcoal'); S.box((.07, .0125, .02), (0, .0002, .06), 'yellowtape', .002, 1, rx=0, rot=0); S.box((.018, .004, .018), (.018, .007, .05), 'black', .002, 1)
def phone1(S): slab(S, .074, .16, .009, 'navy'); [S.cyl(.006, .004, (.02, .006, .06 - i * .017), 'black', 14, .001, axis='y') for i in range(4)]
def phone2(S): slab(S, .078, .164, .0085, 'titan'); S.box((.036, .004, .036), (.016, .0058, .056), 'titan', .004, 2); [S.cyl(.0075, .005, (.016 + x, .008, .056 + y), 'gloss', 16, .001, axis='y') for x, y in ((-.008, .008), (.008, .008), (-.008, -.008))]
def laptop0(S):
    S.box((.36, .25, .018), (0, -.02, .009), 'steel', .005); S.quad(.31, .115, (0, .02, .0186), 'keys', rx=0); S.box((.1, .065, .0012), (0, -.085, .0185), 'darksteel', 0)
    with S.at((0, .105, .02), rx=-.28): S.box((.36, .012, .235), (0, .006, .118), 'steel', .004); S.quad(.335, .205, (0, -.0008, .122), 'screen')
    mouse(S, (.26, -.04, 0))
def mouse(S, loc, m='blackplastic'): S.cushion((.062, .11, .042), (loc[0], loc[1], loc[2] + .016), m, puff=.5, res=5, noise=0); S.box((.004, .03, .003), (loc[0], loc[1] - .02, loc[2] + .037), 'fan', 0)
def mpad(S, w=.8, d=.34): S.box((w, d, .004), (0, -.13, .002), 'rubber', .0015, 1)
def mon(S, loc, w, rot=0, mat='screen', curved=False):
    h = w * 9 / 16 if not curved else w * .42
    with S.at(loc, rot): S.cyl(.11, .012, (0, .07, .006), 'black', 32, .004); S.box((.05, .03, .26), (0, .08, .13), 'black', .006); S.box((w + .014, .03, h + .014), (0, .035, .16 + h / 2), 'black', .006); S.quad(w, h, (0, .0185, .16 + h / 2), mat); S.box((.2, .012, .012), (0, .056, .2), 'fan', .002, 1)
def kb(S, loc=(0, -.16, .004), led=False): keyboard(S, loc); S.box((.42, .004, .006), (loc[0], loc[1] + .075, loc[2] + .012), 'fan', 0) if led else None
def rig_pc0(S): mon(S, (0, .06, 0), .54); kb(S); mouse(S, (.33, -.16, .0)); 
def rig_pc1(S): mpad(S); mon(S, (-.12, .08, 0), .6, .08); mon(S, (.5, .02, 0), .5, -.42, 'screen2'); kb(S, led=True); mouse(S, (.33, -.16, .004))
def rig_pc2(S): mpad(S, .95, .38); mon(S, (0, .1, 0), .92, 0, 'screen', True); mon(S, (.82, -.04, 0), .46, -.75, 'screen2'); kb(S, led=True); mouse(S, (.36, -.16, .004)); S.box((.16, .1, .05), (-.5, -.08, .025), 'blackplastic', .008); [S.box((.022, .022, .006), (-.55 + i * .033, -.1 + j * .03, .052), 'fan' if (i + j) % 2 else 'screen2', .002, 1) for i in range(4) for j in range(2)]
def rig_pc3(S): mpad(S, 1.3, .42); mon(S, (0, .14, 0), 1.05, 0, 'screen', True); mon(S, (-.98, .0, 0), .62, .62, 'screen2'); mon(S, (.98, .0, 0), .62, -.62, 'screen2'); kb(S, led=True); mouse(S, (.4, -.16, .004), 'gold'); S.box((.2, .12, .06), (-.62, -.14, .03), 'gold', .01); [S.box((.024, .024, .006), (-.68 + i * .036, -.16 + j * .034, .062), 'fan', .002, 1) for i in range(4) for j in range(2)]
def tower(S, w=.21, d=.44, h=.46, body='black', fans=3, glass=True, extra=None):
    S.box((w, d, .012), (0, 0, .02), body, .003, 1); S.box((w, d, .012), (0, 0, h), body, .003, 1); S.box((.012, d, h - .02), (w / 2 - .006, 0, h / 2 + .01), body, .003, 1); S.box((w, .012, h - .02), (0, d / 2 - .006, h / 2 + .01), body, .003, 1); S.box((w, .014, h - .02), (0, -d / 2 + .007, h / 2 + .01), 'gloss' if fans else body, .003, 1)
    for sx in (-1, 1):
        for sy in (-1, 1): S.box((.03, .05, .016), (sx * (w / 2 - .03), sy * (d / 2 - .05), .008), 'rubber', .003, 1)
    for i in range(fans):
        z = .09 + i * (h - .12) / max(1, fans) + .02; S.tube([(math.cos(a * PI / 12) * .055, -d / 2 - .002, z + math.sin(a * PI / 12) * .055) for a in range(24)], .005, 'fan', 5, closed=True); S.cyl(.018, .006, (0, -d / 2 - .002, z), 'black', 16, .002, axis='y')
        for k in range(7): a = k * .9; S.box((.012, .004, .036), (math.cos(a) * .033, -d / 2 - .001, z + math.sin(a) * .033), 'darksteel', .001, 1, ry=-a + 1.2)
    # internals seen through the glass side
    S.box((.006, d - .05, h - .07), (w / 2 - .02, 0, h / 2), 'charcoal', .001, 1); S.box((.05, .27, .06), (w / 2 - .055, .03, h * .42), 'blackplastic', .006); S.box((.052, .25, .006), (w / 2 - .055, .03, h * .42 + .034), 'fan', 0); S.box((.05, .09, .09), (w / 2 - .05, .06, h * .72), 'steel', .006)
    for i in range(4): S.box((.04, .006, .1), (w / 2 - .045, -.03 - i * .012, h * .73), 'fan' if i % 2 else 'black', .002, 1)
    if extra: extra()
def tower_pc0(S): tower(S, body='charcoal', fans=2); S.box((.1, .002, .03), (0, -.222, .43), 'yellow', 0)
def tower_pc1(S): tower(S, .22, .46, .48, 'black', 3)
def tower_pc2(S):
    def ex(): S.curve([(.02, .1, .4), (-.04, .05, .46), (-.04, -.1, .44), (.02, -.12, .3)], .009, 'black', 6); S.tube([(math.cos(a * PI / 12) * .05, math.sin(a * PI / 12) * .05 + .06, .505) for a in range(24)], .005, 'fan', 5, closed=True); S.tube([(math.cos(a * PI / 12) * .05, math.sin(a * PI / 12) * .05 - .08, .505) for a in range(24)], .005, 'fan', 5, closed=True)
    tower(S, .24, .5, .5, 'white', 3, extra=ex)
def tower_pc3(S):
    def ex():
        S.cyl(.045, .34, (-.06, -.14, .3), 'wcool', 24, .004); S.cyl(.05, .02, (-.06, -.14, .12), 'gold', 24, .004); S.cyl(.05, .02, (-.06, -.14, .48), 'gold', 24, .004)
        for pts in ([(-.06, -.14, .47), (-.06, .02, .52), (.03, .08, .46)], [(.03, .05, .4), (-.05, .12, .3), (-.05, .05, .14), (-.06, -.1, .12)], [(.04, .1, .28), (-.07, .16, .24), (-.07, .02, .34)]): S.curve(pts, .011, 'wcool', 8)
    tower(S, .3, .56, .62, 'gold', 4, extra=ex); S.text('MAINFRAME', .04, (0, -.284, .62 - .05), 'gold', FD, .002)
def mic1(S): S.cyl(.06, .014, (0, 0, .007), 'darksteel', 28, .004); S.tube([(-.05, 0, .01), (-.06, 0, .1), (-.05, 0, .16)], .006, 'darksteel', 6); S.tube([(.05, 0, .01), (.06, 0, .1), (.05, 0, .16)], .006, 'darksteel', 6); S.cyl(.038, .12, (0, 0, .13), 'steel', 28, .006); S.lathe([(.038, .19), (.04, .2), (.038, .25), (.02, .275), (0, .278)], mat='darksteel', seg=28); S.cyl(.012, .006, (0, -.04, .14), 'red', 16, .002, axis='y'); S.box((.02, .002, .01), (0, -.0385, .1), 'white', 0)
def mic2(S):
    S.box((.05, .05, .06), (-.42, .18, .03), 'black', .006); S.tube([(-.42, .18, .06), (-.46, .2, .42)], .011, 'black', 8); S.tube([(-.46, .2, .42), (-.14, .02, .5)], .011, 'black', 8); S.sphere(.02, (-.46, .2, .42), 'black', 12, 8); S.tube([(-.14, .02, .5), (-.13, .0, .44)], .008, 'black', 6)
    with S.at((-.11, -.03, .40), .5, rx=.25): S.cyl(.034, .12, (0, .03, 0), 'charcoal', 24, .008, axis='y'); S.cyl(.04, .07, (0, -.06, 0), 'black', 24, .016, axis='y'); S.cyl(.036, .004, (0, .092, 0), 'yellow', 24, 0, axis='y')
def cam0(S): S.box((.095, .03, .032), (0, .02, .015), 'black', .012, 3); S.cyl(.012, .008, (0, .003, .015), 'gloss', 20, .002, axis='y'); S.cyl(.003, .002, (.028, .004, .015), 'red', 8, 0, axis='y'); S.box((.05, .035, .02), (0, .03, -.008), 'black', .005)
def cam2(S):
    for i in range(3): a = i * 2.094 + .5; S.tube([(math.cos(a) * .07, math.sin(a) * .07, .005), (0, 0, .1)], .006, 'black', 6)
    S.cyl(.012, .05, (0, 0, .12), 'black', 10, .002); S.box((.128, .06, .085), (0, 0, .19), 'blackplastic', .01); S.box((.05, .05, .03), (0, 0, .242), 'blackplastic', .01); S.cyl(.035, .09, (0, -.07, .19), 'black', 28, .004, axis='y'); S.cyl(.037, .012, (0, -.09, .19), 'charcoal', 28, .002, axis='y'); S.cyl(.03, .003, (0, -.116, .19), 'gloss', 28, 0, axis='y'); S.cyl(.01, .01, (.042, 0, .237), 'red', 14, .002); S.box((.03, .05, .075), (-.056, -.012, .188), 'rubber', .012)
def lamp0(S): furn.table_lamp(S, 0, light=False)
def ring(S):
    tripod(S, 1.3, head=False); S.tube([(math.cos(a * PI / 20) * .2, -.02, 1.5 + math.sin(a * PI / 20) * .2) for a in range(40)], .024, 'ringglow', 8, closed=True); S.tube([(math.cos(a * PI / 20) * .2, .012, 1.5 + math.sin(a * PI / 20) * .2) for a in range(40)], .02, 'white', 8, closed=True); S.box((.03, .03, .1), (0, 0, 1.28), 'black', .006); S.box((.075, .01, .15), (0, -.02, 1.5), 'black', .006)
def softbox_(S): 
    tripod(S, 1.5, head=False)
    with S.at((0, 0, 1.72), rx=.35): S.box((.52, .02, .52), (0, -.16, 0), 'ringglow', .012); S.lathe([(.06, .05), (.09, 0), (.37, -.148)], mat='black', seg=4) if False else S.box((.5, .12, .5), (0, -.09, 0), 'black', .03); S.cyl(.055, .16, (0, .03, 0), 'black', 16, .01, axis='y')
def chair0(S): chair_wood(S)
def chair1(S): office_chair(S, 'fabric_dark')
def chair2(S):
    for i in range(5): a = i * 2 * PI / 5; S.tube([(0, 0, .1), (math.cos(a) * .32, math.sin(a) * .32, .065)], .026, 'black', 6); S.cyl(.03, .045, (math.cos(a) * .32, math.sin(a) * .32, .032), 'red', 12, .006, axis='y', rot=a)
    S.cyl(.03, .32, (0, 0, .26), 'steel', 12, 0); S.cushion((.5, .5, .13), (0, 0, .47), 'leather_black', puff=.3, res=6); [S.cushion((.1, .48, .17), (sx * .23, 0, .49), 'leather_red', puff=.4, res=5) for sx in (-1, 1)]
    S.cushion((.42, .13, .86), (0, .26, .96), 'leather_black', rx=-.16, puff=.3, res=7); [S.cushion((.13, .16, .62), (sx * .21, .22, .9), 'leather_red', rx=-.16, puff=.4, res=6) for sx in (-1, 1)]; S.cushion((.32, .12, .14), (0, .25, 1.3), 'leather_red', rx=-.16, puff=.6, res=6); S.cushion((.3, .1, .16), (0, .18, .68), 'leather_red', rx=-.1, puff=.6, res=6)
    for sx in (-1, 1): S.box((.07, .28, .03), (sx * .31, -.02, .7), 'blackplastic', .012); S.box((.03, .04, .2), (sx * .31, .02, .6), 'black', .006)
def chair4(S):
    S.box((.74, .7, .3), (0, .02, .15), 'gold', .02); S.cushion((.56, .56, .16), (0, -.02, .4), 'knit_red', puff=.4, res=7); S.box((.7, .12, 1.2), (0, .3, .9), 'gold', .02); S.cushion((.5, .1, .86), (0, .24, .86), 'knit_red', puff=.3, res=7)
    for sx in (-1, 1):
        S.box((.1, .6, .12), (sx * .33, 0, .62), 'gold', .02); S.box((.1, .1, .34), (sx * .33, -.24, .45), 'gold', .016); S.sphere(.07, (sx * .33, -.28, .67), 'gold', 16, 10); S.sphere(.09, (sx * .35, .3, 1.56), 'gold', 16, 10); S.lathe([(.05, 1.4), (.07, 1.45), (.03, 1.5)], (sx * .35, .3, 0), 'gold', 16)
    for i in range(5): x = (i - 2) * .13; S.lathe([(.05, 1.5), (.03, 1.58), (0, 1.72 - abs(i - 2) * .05)], (x, .3, 0), 'gold', 10); S.sphere(.028, (x, .3, 1.74 - abs(i - 2) * .05), 'red', 10, 8)
def plant_(S): plant(S, (0, 0, 0), .62, 'ceramic', 14, 5)
def plush_(S): S.sphere(.28, (0, 0, .25), 'plush', 28, 18, (1, .92, .9)); S.sphere(.15, (0, -.13, .2), 'linen', 20, 14, (1, .7, .9)); [S.sphere(.03, (sx * .1, -.235, .33), 'black', 14, 10) for sx in (-1, 1)]; [S.sphere(.035, (sx * .16, -.2, .27), 'pink', 12, 8, (1, .4, .7)) for sx in (-1, 1)]; [S.sphere(.08, (sx * .17, .0, .47), 'plushd', 14, 10) for sx in (-1, 1)]; [S.sphere(.09, (sx * .13, -.12, .05), 'plushd', 14, 10, (1, 1.2, .6)) for sx in (-1, 1)]; S.tube([(-.03, -.262, .28), (0, -.267, .272), (.03, -.262, .28)], .005, 'black', 5)
def neon_(S): S.box((.62, .02, .34), (0, .012, 0), 'gloss', .01); S.neon('GG', .34, (0, -.015, .0), 'neonp', FS, r=.009)
def award(S, m): S.box((.5, .03, .38), (0, .015, 0), 'black', .008); S.box((.3, .02, .2), (0, -.012, .03), m, .04, 4); import_tri(S, m); S.box((.2, .004, .03), (0, -.002, -.13), m, .003, 1)
def import_tri(S, m):
    bm = bmesh.new(); a = [bm.verts.new(p) for p in ((-.03, -.0235, -.015), (-.03, -.0235, .075), (.05, -.0235, .03))]; f = bm.faces.new(a); S.add(bm, 'black'); bm = bmesh.new(); a = [bm.verts.new(p) for p in ((.05, -.0235, .03), (-.03, -.0235, .075), (-.03, -.0235, -.015))]; bm.faces.new(a); S.add(bm, 'black')
def silver(S): award(S, 'silver')
def goldbtn(S): award(S, 'gold')
def headset(S):
    S.tube([(math.cos(a) * .093, .005, math.sin(a) * .112) for a in [PI * (.02 + .96 * i / 20) for i in range(21)]], .010, 'blackplastic', 8); S.tube([(math.cos(a) * .097, .005, math.sin(a) * .118) for a in [PI * (.25 + .5 * i / 12) for i in range(13)]], .013, 'leather_black', 8)
    for sx in (-1, 1): S.cyl(.042, .03, (sx * .094, .0, -.012), 'blackplastic', 28, .01, axis='x'); S.cyl(.038, .02, (sx * .078, .0, -.012), 'leather_black', 28, .009, axis='x'); S.tube([(sx * .11, math.cos(a * PI / 10) * .026, -.012 + math.sin(a * PI / 10) * .026) for a in range(20)], .0035, 'fan', 5, closed=True)
    S.curve([(.1, -.02, -.04), (.1, -.07, -.085), (.06, -.105, -.105)], .004, 'blackplastic', 6); S.sphere(.012, (.055, -.108, -.106), 'rubber', 12, 8)
def airpods(S): [(S.sphere(.016, (sx * .03, 0, .06), 'white', 14, 10), S.tube([(sx * .03, 0, .055), (sx * .034, 0, .015)], .006, 'white', 8)) for sx in (-1,)]; S.box((.07, .03, .055), (.05, .02, .028), 'white', .014, 3)
def router0(S): S.box((.2, .14, .035), (0, 0, .018), 'blackplastic', .008); [S.tube([(x, .06, .03), (x * 1.15, .07, .2)], .006, 'blackplastic', 6) for x in (-.08, .08)]; [S.box((.008, .002, .006), (-.05 + i * .025, -.071, .018), 'green' if i < 3 else 'red', 0) for i in range(5)]
def router2(S): S.lathe([(0, 0), (.07, 0), (.075, .02), (.06, .19), (.05, .21), (0, .212)], mat='white', seg=32); S.tube([(math.cos(a * PI / 14) * .064, math.sin(a * PI / 14) * .064, .15) for a in range(28)], .003, 'wcool', 4, closed=True)
def dish(S): S.lathe([(0, .28), (.16, .3), (.3, .37), (.31, .375), (.3, .365), (.16, .285), (0, .265)], mat='white', seg=36); S.tube([(0, 0, .02), (0, 0, .28)], .02, 'white', 10); S.cyl(.16, .02, (0, 0, .01), 'darksteel', 28, .004); S.tube([(0, 0, .28), (.05, -.1, .46)], .008, 'darksteel', 6); S.sphere(.025, (.05, -.1, .46), 'darksteel', 12, 8)
def ledroll(S):
    pts = [(math.cos(a * .35) * (.05 + a * .0016), math.sin(a * .35) * (.05 + a * .0016), .03) for a in range(70)]; S.tube(pts, .006, 'fan', 5); S.tube([(p[0], p[1], .05) for p in pts[::2]], .006, 'neonp', 5)
def hexp(S): hexes(S, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (2, 0)], .1, (-.15, 0, .14))
PROPS = {**{k: globals()[k] for k in ('phone0', 'phone1', 'phone2', 'laptop0', 'rig_pc0', 'rig_pc1', 'rig_pc2', 'rig_pc3', 'tower_pc0', 'tower_pc1', 'tower_pc2', 'tower_pc3', 'mic1', 'mic2', 'cam0', 'cam2', 'lamp0', 'ring', 'chair0', 'chair1', 'chair2', 'chair4', 'silver', 'goldbtn', 'headset')}, 'softbox': softbox_, 'plant': plant_, 'plush': plush_, 'neon': neon_}
def bundle(*fs):
    def f(S):
        for fn, loc, rot, sc in fs:
            with S.at(loc, rot, scale=sc): fn(S)
    return f
SHOPS = {'phone0': (phone0, '#b9b2a3', .19), 'phone1': (phone1, '#9fb6d0', .21), 'phone2': (phone2, '#d8c9b4', .21), 'laptop0': (laptop0, '#c9c4ba', .62), 'pc0': (bundle((tower_pc0, (.42, 0, 0), .5, 1), (rig_pc0, (-.12, 0, 0), -.2, 1)), '#d9c36a', 1.25), 'pc1': (bundle((tower_pc1, (.62, 0, 0), .5, 1), (rig_pc1, (-.1, 0, 0), -.15, 1)), '#7fb08a', 1.6), 'pc2': (bundle((tower_pc2, (.85, -.2, 0), .5, 1), (rig_pc2, (-.1, 0, 0), -.1, 1)), '#a8a2c8', 1.95), 'pc3': (bundle((tower_pc3, (.95, -.35, 0), .45, 1), (rig_pc3, (-.1, .1, 0), -.1, 1)), '#3a2c1a', 2.3),
 'mic0': (airpods, '#6f97b5', .16), 'mic1': (mic1, '#8fa8b8', .36), 'mic2': (mic2, '#c7b8a0', .8), 'cam0': (cam0, '#c2ccd4', .14), 'cam1': (cam0, '#3f4a58', .13), 'cam2': (cam2, '#d4b8a0', .48), 'light0': (lamp0, '#e3cf9a', .7), 'light1': (ring, '#d9a5b4', 2.4), 'light2': (softbox_, '#8fa0a8', 2.5), 'chair0': (chair0, '#c9b08a', 1.4), 'chair1': (chair1, '#a8adb0', 1.6), 'chair2': (chair2, '#c96a5a', 1.95), 'chair3': (chair1, '#2f3336', 1.6), 'chair4': (chair4, '#5a1f1a', 2.5), 'net0': (router0, '#a8b0a0', .4), 'net1': (router0, '#c86a5a', .4), 'net2': (router2, '#4f7396', .42), 'net3': (dish, '#1f2a3a', .85), 'led0': (ledroll, '#241a33', .34), 'led1': (hexp, '#1c1a2a', .62), 'plant': (plant_, '#cbd4b8', 1.35), 'plush': (plush_, '#e0c8b0', .95), 'neon': (neon_, '#1f1a26', .85), 'silver': (silver, '#3a4048', .75), 'goldbtn': (goldbtn, '#4a2f1a', .75)}
def ao(S):
    vs, fs, o = [], [], 0
    for p in S.parts: vs += [Vector(v) for v in p.v.astype(float)]; fs += [tuple(int(q) + o for q in t) for t in p.f]; o += len(p.v)
    bvh = BVHTree.FromPolygons(vs, fs); rs = np.random.RandomState(1); N = 26; dirs = rs.randn(N, 3); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True); size = float(np.ptp(np.vstack([p.v for p in S.parts]), axis=0).max()); R = min(.5, size * .5)
    for p in S.parts:
        if MATS[p.mat].get('emit'): p.ca = np.ones(len(p.v)); continue
        key = {}; a = np.ones(len(p.v))
        for i in range(len(p.v)):
            k = (tuple(np.round(p.v[i], 4)), tuple(np.round(p.n[i], 2)))
            if k in key: a[i] = key[k]; continue
            n = p.n[i]; c = p.v[i]; hit = 0
            d = dirs + n * 1.02; d /= np.linalg.norm(d, axis=1, keepdims=True)
            for q in d:
                h = bvh.ray_cast(Vector((c + n * .0015).astype(float)), Vector(q.astype(float)), R)
                if h[0] is not None: hit += (1 - h[3] / R) ** .7
            a[i] = key[k] = max(.12, 1 - hit / N)
        p.ca = a
SCR = 'scr_edit'
def emat(name):
    d = MATS[name]; m = bpy.data.materials.get('P_' + name) or bpy.data.materials.new('P_' + name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*d['tint'], 1); b.inputs['Roughness'].default_value = d['rough'] if d['rough'] is not None else .5; b.inputs['Metallic'].default_value = d['metal']
    tx = f'{PUB}/tex/{d["tex"]}.webp' if d['tex'] else f'{PUB}/art/{d["art"]}.webp' if d['art'] else None
    if tx:
        im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(tx, check_existing=True); mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1; mx.inputs[7].default_value = (*d['tint'], 1); nt.links.new(im.outputs[0], mx.inputs[6]); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    if name in ('screen', 'screen2'):
        im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{PUB}/art/' + (SCR if name == 'screen' else 'scr_chat') + '.webp', check_existing=True); nt.links.new(im.outputs[0], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.1
    if d['emit']:
        c = (.9, .08, .5) if name in ('fan', 'strip', 'neonp') else d['emit'][0]; b.inputs['Base Color'].default_value = (*[x * .5 for x in c], 1); b.inputs['Emission Color'].default_value = (*c, 1); b.inputs['Emission Strength'].default_value = .85 if name in ('fan', 'strip', 'neonp') else 2.2
    return m
def render(S, name, bg, span, samples=40):
    bm_all = []
    for p in S.parts:
        me = bpy.data.meshes.new('m'); me.from_pydata([tuple(map(float, v)) for v in p.v], [], [tuple(map(int, t)) for t in p.f]); me.update(); ul = me.uv_layers.new(); ul.data.foreach_set('uv', p.uv[p.f.ravel()].astype(np.float32).ravel()); me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), bool)); me.normals_split_custom_set_from_vertices([tuple(map(float, n)) for n in p.n]); o = bpy.data.objects.new('o', me); o.data.materials.append(emat(p.mat)); bpy.context.scene.collection.objects.link(o)
    V = np.vstack([p.v for p in S.parts]); lo, hi = V.min(0), V.max(0); c = (lo + hi) / 2; sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True; sc.render.resolution_x = sc.render.resolution_y = 384; sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.9, .95, 1, 1); w.node_tree.nodes['Background'].inputs[1].default_value = .45
    bmt = bpy.data.materials.new('bg'); bmt.use_nodes = True; bmt.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (*col(bg), 1); bmt.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .7; z = float(lo[2]) - .001; R = span * .9; pr = [(-3 * span, z)] + [(R * math.sin(a) + span * .55, z + R - R * math.cos(a)) for a in [i * PI / 2 / 10 for i in range(11)]] + [(R + span * .55, z + 5 * span)]
    bm = bmesh.new(); rows = [[bm.verts.new((x, y, zz)) for x in (-6 * span, 6 * span)] for y, zz in pr]; [bm.faces.new((a[0], a[1], b[1], b[0])) for a, b in zip(rows, rows[1:])]; me = bpy.data.meshes.new('b'); bm.to_mesh(me); [setattr(p, 'use_smooth', True) for p in me.polygons]; o = bpy.data.objects.new('b', me); o.location = (float(c[0]), float(c[1]), 0); o.data.materials.append(bmt); sc.collection.objects.link(o)
    def area(loc, e, s, cl=(1, 1, 1)):
        l = bpy.data.lights.new('a', 'AREA'); l.energy = e * span * span; l.size = s * span; l.color = cl; q = bpy.data.objects.new('a', l); sc.collection.objects.link(q); q.location = Vector(map(float, c)) + Vector(loc) * span; q.rotation_euler = (Vector(map(float, c)) - q.location).to_track_quat('-Z', 'Y').to_euler()
    area((-1.1, -1.2, 1.3), 60, .9, (1, .95, .88)); area((1.4, -.4, .6), 22, 1.2, (.85, .92, 1)); area((.3, 1.0, 1.2), 30, .6)
    cam = bpy.data.cameras.new('c'); cam.lens = 70; q = bpy.data.objects.new('c', cam); sc.collection.objects.link(q); sc.camera = q; d = Vector((.52, -1.25, .55)).normalized() * span * 2.05; q.location = Vector(map(float, c)) + d; q.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.render.image_settings.file_format = 'WEBP'; sc.render.image_settings.quality = 86; sc.render.filepath = f'{SHOP}/{name}.webp'; bpy.ops.render.render(write_still=True)
if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'; only = sys.argv[2:]
    if what in ('all', 'glb'):
        allm = {}
        for k, f in PROPS.items():
            bpy.ops.wm.read_factory_settings(use_empty=True); mats(); S = Scene(k); f(S); ao(S); P2 = [dict(mat=p.mat, v=p.v, n=p.n, uv=p.uv, f=p.f, color=p.ca) for p in S.parts]; write_glb(f'{OUT}/{k}.glb', merge(P2)); allm.update({q: MATS[q] for q in {p.mat for p in S.parts}}); print('prop', k, sum(len(p.f) for p in S.parts)); sys.stdout.flush()
        json.dump({k: {a: b for a, b in v.items() if b not in (None, False)} for k, v in allm.items()}, open(f'{OUT}/materials.json', 'w'), indent=0, sort_keys=True)
    if what in ('all', 'shop'):
        for k, (f, bg, span) in SHOPS.items():
            if only and k not in only: continue
            bpy.ops.wm.read_factory_settings(use_empty=True); mats(); S = Scene(k); SCR = 'poster_fortknight' if k == 'phone0' else 'poster_otter' if k == 'phone1' else 'poster_cyberjunk' if k == 'phone2' else 'scr_edit'; f(S); render(S, k, bg, span); print('shop', k); sys.stdout.flush()
