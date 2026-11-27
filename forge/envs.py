import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy; bpy.ops.wm.read_factory_settings(use_empty=True)
from kit import *; from furn import *
PI = math.pi
def bedroom():
    S = Scene('bedroom'); common()
    M('wall', 'plaster', '#8fa3ad', .9, scale=2.2); M('wallS', 'plaster', '#8fa3ad', .9, scale=2.2); M('floor', 'floor_old', '#ffffff', None, scale=1.9)
    W, D, H = 4.4, 4.0, 2.5; win = (.75, 1.35, .95, 2.12)
    S.room(W, D, H, openings=[('N', win[0], win[1], win[2], win[3]), ('E', 1.25, .86, 0, 2.04)], crown='trim')
    window(S, 1.35, .95, 2.12, .75, D / 2, cols=2, rows=2)
    S.cyl(.012, 2.1, (.75, D / 2 - .09, 2.26), 'brass', 10, 0, axis='x')
    S.curtain(.5, 1.75, (-.12, D / 2 - .09, .5), 'fabric_must', folds=5, gather=.25); S.curtain(.5, 1.75, (1.62, D / 2 - .09, .5), 'fabric_must', folds=5, gather=.25)
    with S.at((W / 2 + .05, -1.25, 0), -PI / 2): door(S)
    # bed on west wall
    with S.at((-1.62, .93, 0)): bed(S, 1.05, 1.98, 'wood_pine', blanket='fabric_blue')
    S.block(-2.2, -.12, -1.04, 2.0)
    with S.at((-.82, 1.74, 0)): nightstand(S); table_lamp(S, .5, e=16); S.box((.13, .07, .06), (.12, -.1, .53), 'black', .008); S.box((.1, .004, .035), (.12, -.137, .53), 'red', 0)
    S.block(-1.05, 1.5, -.58, 2.0)
    # desk under window
    with S.at((.75, 1.66, 0)): desk(S, 1.3, .6, .74)
    S.block(.08, 1.34, 1.42, 2.0); S.anchor('desk', (.75, 1.66, .74), 0)
    S.books(.2, (.14, 1.8, .74), BK, .17, .22, .15); mug(S, (1.26, 1.78, .74), 'ceramic_blue')
    S.lathe([(0, 0), (.035, 0), (.038, .1), (.034, .1), (.031, .01), (0, .01)], (1.18, 1.55, .74), 'black', 16)
    for i, m in enumerate(('yellow', 'red', 'blue')): S.cyl(.004, .16, (1.17 + i * .012, 1.55, .82), m, 6, 0, rx=0) if False else S.tube([(1.17 + i * .01, 1.55, .75), (1.16 + i * .02, 1.545 + i * .006, .9)], .004, m, 6)
    # bookshelf NE
    with S.at((1.86, 1.84, 0)): shelf(S, .62, .28, 1.75, 5, 'wood_pine', seed=8)
    S.block(1.52, 1.66, 2.2, 2.0); trophy(S, (1.76, 1.84, 1.75), .22); boxart(S, (.3, .22, .2), (1.98, 1.84, 1.75), 'card', 'box_amazin')
    # wardrobe east
    with S.at((1.9, .62, 0), -PI / 2): wardrobe(S, 1.0, .56, 2.02)
    S.block(1.6, .1, 2.2, 1.14)
    with S.at((1.9, .62, 2.05)): S.box((.4, .5, .24), (0, -.1, .12), 'card', .006); S.cushion((.35, .3, .12), (.02, .3, .06), 'knit_red')
    # laundry, boxes, toys (low)
    with S.at((1.8, -.42, 0)): basket(S); pile(S, 4, ['fabric_rust', 'denim', 'fabric_cream', 'fabric_dark'], .1, 4) if False else S.cushion((.4, .4, .2), (0, 0, .5), 'denim', puff=.6, noise=.02); S.cushion((.3, .26, .1), (-.06, .05, .61), 'fabric_rust', rot=.6, rx=.3, noise=.02); S.cushion((.26, .3, .1), (.1, -.05, .6), 'fabric_cream', rot=2, ry=.3, noise=.02)
    S.block(1.55, -.68, 2.05, -.16)
    with S.at((-1.85, -1.55, 0)): pile(S, 6, ['fabric_rust', 'denim', 'fabric_cream', 'knit_red'], .22, 9)
    S.block(-2.15, -1.85, -1.5, -1.2)
    # skateboard on floor + sneakers + ball
    with S.at((-.5, -1.5, .0), .5): S.box((.2, .78, .014), (0, 0, .1), 'wood_walnut', .006); S.box((.2, .78, .004), (0, 0, .11), 'teal', 0); S.box((.06, .5, .005), (0, 0, .111), 'yellow', 0); [S.cyl(.027, .035, (sx * .075, sy * .25, .03), 'yellow', 14, .005, axis='x') for sx in (-1, 1) for sy in (-1, 1)]; [S.box((.12, .06, .05), (0, sy * .25, .07), 'steel', .006) for sy in (-1, 1)]
    S.sphere(.12, (-2.0, -.42, .12), 'orange', 24, 16)
    # guitar leaning at wall between nightstand & desk
    with S.at((-.36, 1.86, 0), .1, rx=-.16): S.cyl(.19, .09, (0, 0, .24), 'wood_oak', 28, .015, axis='y'); S.cyl(.15, .09, (0, 0, .48), 'wood_oak', 28, .015, axis='y'); S.cyl(.05, .004, (0, -.047, .42), 'black', 20, 0, axis='y'); S.box((.055, .03, .5), (0, -.01, .83), 'wood_walnut', .006); S.box((.08, .02, .16), (0, .0, 1.14), 'wood_walnut', .006)
    rug(S, 1.9, 1.5, (.25, .1), rot=.03)
    # posters W wall & N wall & S wall
    with S.at((-W / 2, 0, 0), PI / 2): poster(S, 'poster_fortknight', 1.35, 1.55, 0, .5, .75); poster(S, 'poster_latency', .72, 1.62, 0, .42, .63); poster(S, 'poster_otter', .1, 1.52, 0, .5, .75); poster(S, 'cert', -.75, 1.5, 0, .42, .315, frame='wood_walnut')
    poster(S, 'poster_eldenbling', -.62, 1.7, D / 2, .4, .6); poster(S, 'calendar', .28 - .6, 1.2, D / 2, .0001, .0001) if False else None
    with S.at((0, -D / 2, 0), PI): poster(S, 'poster_minedcraft', -1.1, 1.55, 0, .5, .75); poster(S, 'poster_amongusb', -.4, 1.6, 0, .45, .68); poster(S, 'poster_grind', 1.0, 1.5, 0, .5, .75)
    with S.at((W / 2, 0, 0), -PI / 2): poster(S, 'poster_darksoles', .28, 1.5, 0, .4, .6); 
    string_lights(S, [(-2.19, -1.0, 2.25), (-2.19, .4, 2.28), (-2.19, 1.98, 2.25), (-1.0, 1.985, 2.27), (-.2, 1.985, 2.25)])
    S.area((-2.0, .4, 2.2), .1, 3.5, '#ffb060', 'lamp', (0, PI / 2, 0), 2.4); S.area((-1.2, 1.85, 2.2), 1.6, 3, '#ffb060', 'lamp', (-PI / 2, 0, 0), .1)
    ceiling_dome(S, (.1, 0, H), .17, 62)
    # router + power strip + wall breaker
    S.box((.18, .12, .03), (1.6, 1.86, .74 - .74 + .02), 'white', .01) if False else None
    with S.at((.3, 1.9, .74)): S.box((.16, .1, .03), (.28, 0, .015), 'blackplastic', .008); S.tube([(.22, .04, .03), (.22, .045, .16)], .005, 'blackplastic', 6); S.tube([(.34, .04, .03), (.34, .045, .16)], .005, 'blackplastic', 6); S.box((.006, .002, .006), (.25, -.0505, .015), 'strip', 0)
    S.box((.03, .26, .36), (W / 2 - .015, -1.95 + .15, 1.5), 'gray', .006)
    # lights
    S.area((.75, D / 2 + .1, 1.53), 1.3, 210, '#cfe2ff', 'day', (-PI / 2, 0, 0), 1.15); S.sun((math.radians(-52), 0, math.radians(28)), 15, '#fff0d8', 1.2)
    # led: monitor glow at desk + strip behind desk
    S.area((.75, 1.5, 1.15), .5, 9, '#ffffff', 'led', (PI / 2, 0, PI), .3); S.area((.75, 1.95, .78), 1.2, 12, '#ffffff', 'led', (-PI * .75, 0, 0), .04); S.area((-2.1, .9, .2), 1.8, 8, '#ffffff', 'led', (0, -PI / 2 + .4, PI), .05)
    # anchors
    S.anchor('spawn', (.2, -.6), PI); S.anchor('bed', (-1.0, .5), -PI / 2, lie=[-1.62, .62, -.95]); S.anchor('phone_seat', (-1.14, .35, .44), PI / 2); S.anchor('seat', (.75, 1.13), PI)
    S.anchor('door', (1.75, -1.25), PI / 2); S.anchor('outside', (3.2, -1.25), -PI / 2); S.anchor('wardrobe', (1.35, .62), PI / 2); S.anchor('food', (1.3, -.42), PI / 2); S.anchor('router', (.05, 1.1), PI); S.anchor('breaker', (1.85, -1.7), PI / 2); S.anchor('idle1', (.9, .3), PI); S.anchor('idle2', (.2, -1.2), 0)
    S.anchor('tower', (1.6, 1.45, 0), 0); S.anchor('decor1', (-.15, 1.93, 1.95), 0); S.anchor('ringlight', (1.52, 1.15, 0), 0); S.anchor('cam', (.75, 1.85, .74)); S.anchor('decor2', (-2.0, -1.0, 0))
    S.meta.update(title='Childhood Bedroom', cam=dict(target=[-.05, .75, -.15], dist=6.6, az=.1, pol=.98, azr=[-.75, .8]), backdrops=[dict(pos=[.75, 1.05, -3.7], size=[5.8, 2.9], rot=0, img='suburb')], windowWalls=['N'], spill=[.75, 1.5, -2])
    return S
def studio():
    S = Scene('studio'); common(); M('wall', 'plaster', '#d9cdb8', .9, scale=2.2); M('brickw', 'brick', '#e8ddd2', None, scale=1.15); M('floor', 'floor_oak', '#c9b49a', None, scale=2.0); M('splash', 'subway', '#ffffff', None, scale=.9)
    W, D, H = 6.6, 5.2, 2.85
    S.room(W, D, H, wall=dict(N='brickw', E='wall', S='wall', W='wall'), openings=[('N', 1.0, 1.9, .85, 2.4), ('W', 1.9, .86, 0, 2.04)])
    window(S, 1.9, .85, 2.4, 1.0, D / 2, cols=3, rows=2, mat='black', fr=.04)
    with S.at((-W / 2 - .05, -1.9, 0), PI / 2): door(S, mat='teal')
    with S.at((W / 2 - .02, -1.3, 0), -PI / 2): door(S, .78, mat='offwhite')
    # kitchen on N wall
    with S.at((-1.95, D / 2 - .31, 0)): kitchen(S, 2.4, 'fabric_green' if False else 'offwhite', 'wood_oak', splash='splash'); mug(S, (-.2, -.1, .9), 'teal'); S.lathe([(0, 0), (.06, 0), (.08, .1), (.08, .14), (.07, .14), (.055, .01), (0, .01)], (.15, .1, .9), 'steel', 20); S.box((.26, .2, .2), (-.95, .08, 1.0), 'red', .03); S.box((.1, .12, .3), (.42, .12, 1.05), 'wood_walnut', .01)
    S.block(-3.2, 1.95, -.72, 2.6)
    with S.at((-W / 2 + .35, 1.62, 0), PI / 2): fridge(S, .66, .66, 1.75)
    S.block(-3.3, 1.25, -2.6, 2.0); S.quad(2.4, .62, (-1.95, D / 2 - .004, 1.2), 'wall', lm=.5) if False else None
    pendant(S, (-1.6, 1.2, H), .75, 'black', 46); pendant(S, (-2.4, 1.2, H), .75, 'black', 46); ceiling_dome(S, (.4, -.9, H), .2, 62)
    # desk
    with S.at((1.0, D / 2 - .36, 0)): desk(S, 1.5, .66, .74, 'wood_walnut', 'black', metal=True); mug(S, (.62, -.15, .74), 'red'); S.books(.18, (-.7, .2, .74), BK, .17, .22, .14); plant(S, (.64, .2, .74), .3, 'ceramic', 10, 4)
    S.block(.22, 1.9, 1.78, 2.6); S.anchor('desk', (1.0, D / 2 - .36, .74), 0)
    with S.at((2.25, D / 2 - .08, 0)): radiator(S, .6)
    # bed east
    with S.at((2.52, .72, 0)): bed(S, 1.4, 2.0, 'wood_walnut', blanket='fabric_must', pillows=2, sheet='linen')
    S.block(1.78, -.35, 3.3, 1.85)
    with S.at((3.06, 2.0, 0)): nightstand(S, 'wood_walnut', .4, .36); table_lamp(S, .5, base='terracotta', e=16)
    S.block(2.8, 1.8, 3.3, 2.25)
    # clothes rack
    with S.at((2.75, -.66, 0)):
        for sx in (-1, 1): S.tube([(sx * .42, -.2, .02), (sx * .42, .2, .02)], .012, 'black', 6); S.tube([(sx * .42, 0, .02), (sx * .42, 0, 1.5)], .012, 'black', 6)
        S.tube([(-.42, 0, 1.5), (.42, 0, 1.5)], .012, 'black', 6)
        for i, m in enumerate(('fabric_rust', 'denim', 'fabric_cream', 'fabric_dark', 'fabric_green', 'knit_red', 'fabric_blue')): S.cushion((.05, .42, .78 - (i % 3) * .08), (-.33 + i * .11, 0, 1.06 + (i % 3) * .04), m, puff=.3, res=6, noise=.012, rot=.1)
    S.block(2.25, -.9, 3.25, -.42)
    # sofa west
    with S.at((-2.75, -.45, 0), PI / 2): sofa(S, 1.8, .86, 'fabric_teal', seats=2, pil=('fabric_must', 'fabric_cream'))
    S.block(-3.25, -1.4, -2.3, .5)
    with S.at((-1.55, -.45, 0), PI / 2): coffee_table(S, 1.0, .5, .4, 'wood_oak')
    pizza_box(S, (-1.55, -.25, .42), .3); pizza_box(S, (-1.53, -.24, .46), .12); can(S, (-1.6, -.72, .42)); can(S, (-1.45, -.78, .42), 'can_redbill'); mug(S, (-1.68, -.6, .42))
    S.block(-1.85, -1.0, -1.25, .1)
    with S.at((-3.0, .78, 0)): floor_lamp(S, 1.5, 64)
    rug(S, 2.4, 1.7, (-1.7, -.45), rot=PI / 2 + .03)
    with S.at((-W / 2, 0, 0), PI / 2): poster(S, 'painting_1', -.45, 1.6, 0, 1.1, .73, frame='black'); poster(S, 'poster_cyberjunk', .55, 1.55, 0, .42, .63)
    with S.at((W / 2, 0, 0), -PI / 2): poster(S, 'poster_latency', -1.0, 1.7, 0, .46, .69, frame='black'); poster(S, 'poster_amongusb', -.4, 1.7, 0, .46, .69, frame='black'); poster(S, 'poster_eldenbling', .2, 1.7, 0, .46, .69, frame='black')
    with S.at((0, -D / 2, 0), PI): poster(S, 'poster_otter', -1.4, 1.6, 0, .55, .82); poster(S, 'poster_darksoles', 0, 1.6, 0, .5, .75); poster(S, 'whiteboard', 1.8, 1.5, 0, 1.1, .69, frame='steel')
    # bike
    with S.at((2.6, -2.3, .0), .12):
        for sx in (-1, 1): S.tube([(sx * .52 + math.cos(i * PI / 14) * .33, 0, .35 + math.sin(i * PI / 14) * .33) for i in range(28)], .017, 'rubber', 6, closed=True); [S.tube([(sx * .52, 0, .35), (sx * .52 + math.cos(i * PI / 5) * .32, 0, .35 + math.sin(i * PI / 5) * .32)], .002, 'steel', 3) for i in range(10)]
        for a, b in (((-.52, 0, .35), (-.1, 0, .33)), ((-.1, 0, .33), (-.2, 0, .85)), ((-.2, 0, .8), (-.52, 0, .35)), ((-.18, 0, .78), (.36, 0, .82)), ((.36, 0, .84), (.52, 0, .35)), ((-.1, 0, .33), (.38, 0, .76)), ((.36, 0, .8), (.33, 0, .98))): S.tube([a, b], .016, 'red', 7)
        S.tube([(.3, -.26, .98), (.36, -.1, 1.0), (.36, .1, 1.0), (.3, .26, .98)], .012, 'black', 6); S.cushion((.24, .13, .06), (-.22, 0, .89), 'leather_black', puff=.3, res=5)
    S.block(1.7, -2.55, 3.3, -2.1)
    plant(S, (-.35, 2.2, 0), .9, 'terracotta', 16, 3); S.block(-.6, 2.0, -.1, 2.5)
    boxart(S, (.45, .4, .35), (.2, -2.2, 0), 'card', 'box_amazin', .3); boxart(S, (.35, .3, .25), (.22, -2.18, .35), 'card', 'box_amazin', -.2); S.block(-.1, -2.5, .5, -1.95)
    string_lights(S, [(-3.28, 2.55, 2.55), (-1.2, 2.56, 2.6), (.9, 2.56, 2.6), (3.28, 2.56, 2.55)], 9); S.area((0, 2.45, 2.5), 6, 12, '#ffb060', 'lamp', (-PI / 2, 0, 0), .1)
    with S.at((1.7, 2.5, .74)): S.box((.16, .1, .03), (-.1, -.05, .015), 'blackplastic', .008)
    S.box((.03, .3, .4), (W / 2 - .015, -2.3, 1.5), 'gray', .006)
    S.area((1.0, D / 2 + .1, 1.62), 1.85, 520, '#cfe2ff', 'day', (-PI / 2, 0, 0), 1.5); S.sun((math.radians(-50), 0, math.radians(34)), 15, '#fff0d8', 1.0)
    S.area((1.0, 2.0, 1.15), .6, 12, '#ffffff', 'led', (PI / 2, 0, PI), .35); S.area((1.0, 2.54, .8), 1.6, 18, '#ffffff', 'led', (-PI * .75, 0, 0), .04); S.area((2.5, .7, .15), 1.6, 12, '#ffffff', 'led', (PI, 0, 0), .1)
    S.anchor('spawn', (0, -.6), PI); S.anchor('bed', (1.6, .3), -PI / 2, lie=[2.5, .62, -.7]); S.anchor('phone_seat', (-2.55, -.45, .5), PI / 2); S.anchor('seat', (1.0, 1.62), PI); S.anchor('door', (-2.8, -1.9), -PI / 2); S.anchor('outside', (-4.2, -1.9), PI / 2); S.anchor('wardrobe', (2.6, -1.15), 0); S.anchor('food', (-2.35, 1.6), -PI / 2); S.anchor('router', (1.5, 1.65), PI); S.anchor('breaker', (2.95, -1.95), PI / 2)
    S.anchor('idle1', (-.6, .9), PI); S.anchor('idle2', (-1.0, -1.6), 0); S.anchor('work1', (-.9, -.45), -PI / 2); S.anchor('tower', (2.0, 2.25, 0), 0); S.anchor('ringlight', (2.05, 1.72, 0), 0); S.anchor('cam', (1.0, 2.5, .74)); S.anchor('decor1', (-.2, D / 2 - .02, 2.05)); S.anchor('decor2', (.5, 2.3, 0))
    S.meta.update(title='The Shoebox Studio', cam=dict(target=[0, .8, -.1], dist=8.8, az=.06, pol=.98, azr=[-.7, .7]), backdrops=[dict(pos=[1.0, 1.3, -4.7], size=[11, 5.5], rot=0, img='city')], spill=[1, 1.6, -2.6])
    return S
def loft():
    S = Scene('loft'); common(); M('wall', 'plaster', '#8b8f8c', .9, scale=2.4); M('wallL', 'plaster', '#e4ddd0', .9, scale=2.4); M('floor', 'floor_dark', '#ffffff', None, scale=2.4); M('foam_dark', 'foam', '#2b2d31', .95, scale=.6); M('foam_acc', 'foam', '#8f2f28', .95, scale=.6); M('slat', 'wood_walnut', '#ffffff', .5, scale=.8); M('neonr', None, '#ffffff', .4, emit=('#ff4a32', 2.2), chan='always', bakek=4)
    W, D, H = 9.4, 6.6, 3.0
    S.room(W, D, H, wall=dict(N='wall', E='wall', S='wallL', W='wallL'), openings=[('N', -2.1, 4.6, .12, 2.8), ('E', 2.1, .9, 0, 2.1)])
    window(S, 4.6, .12, 2.8, -2.1, D / 2, cols=4, rows=1, mat='black', fr=.05, sill=False)
    S.curtain(.7, 2.75, (-4.35, D / 2 - .12, .05), 'linen', folds=6, gather=0, nx=64); S.curtain(.6, 2.75, (.38, D / 2 - .12, .05), 'linen', folds=5, nx=56); S.box((5.6, .06, .05), (-2.0, D / 2 - .1, 2.88), 'black', .004, 1)
    with S.at((W / 2 + .05, -2.1, 0), -PI / 2): door(S, .88, 2.08, 'black', 'steel', False)
    # stream corner
    foam_wall(S, 3.0, 1.5, (2.75, D / 2, 1.75), 0, (6, 3)); 
    with S.at((2.75, D / 2 - .42, 0)): desk(S, 2.0, .78, .74, 'wood_walnut', 'black', metal=True); mug(S, (.85, -.2, .74), 'teal'); can(S, (-.86, .1, .74)); figure(S, (.8, .22, .74), 'red'); figure(S, (.88, .25, .74), 'teal')
    S.block(1.72, 2.45, 3.78, 3.3); S.anchor('desk', (2.75, D / 2 - .42, .74), 0)
    S.box((3.1, .012, .014), (2.75, D / 2 - .03, 2.53), 'strip', 0); S.box((3.1, .012, .014), (2.75, D / 2 - .03, .98), 'strip', 0); S.box((1.9, .01, .012), (2.75, 2.95, .715), 'strip', 0)
    S.neon('GG', .5, (4.0, D / 2 - .08, 2.2), 'neonr', FS) if False else None
    with S.at((W / 2 - .17, 1.35, 0), -PI / 2): shelf(S, 1.6, .32, 2.1, 5, 'wood_walnut', fill=.25, seed=21)
    S.block(4.3, .5, 4.7, 2.2); S.box((.012, 1.55, .012), (W / 2 - .3, 1.35, 2.13), 'strip', 0)
    # slat wall east
    for i in range(22): S.box((.03, .045, 2.9), (W / 2 - .015, 2.35 + i * .043, 1.48), 'slat', .003, 1, lm=.5)
    with S.at((W / 2 - .06, -.35, 0), -PI / 2): poster(S, 'painting_2', 0, 1.6, 0, .8, 1.2, frame='brass')
    # lounge
    rug(S, 3.2, 2.3, (-2.6, .75), 'rugtex2' if 'rugtex2' in MATS else 'rugtex', PI / 2)
    with S.at((-W / 2 + .5, .8, 0), PI / 2): sofa(S, 2.5, .95, 'fabric_gray', seats=3)
    S.block(-4.7, -.5, -3.65, 2.1)
    with S.at((-2.75, .8, 0), PI / 2): coffee_table(S, 1.2, .6, .36, 'wood_walnut', 'black'); S.books(.2, (-.4, 0, .38), BK, .18, .2, .2) if False else None
    S.box((.3, .22, .03), (-2.8, 1.05, .395), 'bk2', .004, 1, rot=.2); S.box((.26, .2, .025), (-2.8, 1.05, .42), 'bk1', .004, 1, rot=-.1); plant(S, (-2.7, .5, .38), .26, 'ceramic', 9, 8); mug(S, (-2.6, .8, .38))
    S.block(-3.1, .15, -2.4, 1.45)
    with S.at((-1.5, 1.75, 0), -.5): S.cushion((.85, .8, .22), (0, 0, .34), 'leather_brown', puff=.4); S.cushion((.8, .22, .6), (0, .36, .62), 'leather_brown', rx=-.25, puff=.5); [S.cushion((.16, .75, .3), (sx * .42, 0, .45), 'leather_brown', puff=.4, res=6) for sx in (-1, 1)]; [S.cyl(.018, .24, (sx * .3, sy * .28, .12), 'black', 8, 0) for sx in (-1, 1) for sy in (-1, 1)]
    S.block(-2.05, 1.2, -.95, 2.3)
    with S.at((-W / 2, 0, 0), PI / 2): poster(S, 'painting_1', .8, 1.75, 0, 1.7, 1.13, frame='wood_walnut')
    plant(S, (-4.3, 2.75, 0), 1.5, 'ceramic', 18, 6, True); S.block(-4.65, 2.4, -3.95, 3.1); plant(S, (.75, 2.95, 0), 1.2, 'ceramic_blue', 15, 2, True); S.block(.45, 2.65, 1.05, 3.2)
    with S.at((-4.35, -.82, 0)): floor_lamp(S, 1.55, 64)
    S.block(-4.6, -1.05, -4.1, -.6)
    # kitchen W-S with island
    with S.at((-W / 2 + .32, -2.2, 0), PI / 2): kitchen(S, 1.8, 'charcoal', 'marble', upper=False, d=.62)
    S.block(-4.7, -3.2, -4.0, -1.25)
    S.box((.7, 1.7, .88), (-2.8, -2.25, .44), 'charcoal', .008); S.box((.86, 1.86, .04), (-2.8, -2.25, .9), 'marble', .008); S.lathe([(0, 0), (.07, 0), (.15, .07), (.145, .07), (.06, .012), (0, .012)], (-2.8, -2.0, .92), 'ceramic', 24); [S.sphere(.04, (-2.83 + (i % 2) * .07, -2.03 + (i // 2) * .06, .975 + (i == 4) * .05), 'orange', 12, 8) for i in range(5)]
    S.block(-3.25, -3.2, -2.35, -1.3)
    for y in (-2.75, -2.2, -1.65):
        with S.at((-2.1, y, 0)): stool(S)
    for y in (-2.7, -1.8): pendant(S, (-2.8, y, H), 1.1, 'brass', 30, .14)
    # platform bed SE
    with S.at((3.3, -1.15, 0), 0):
        pass
    with S.at((3.2, -.35 - 1.0, 0), -PI / 2): bed(S, 1.7, 2.05, 'wood_walnut', blanket='fabric_dark', pillows=2, sheet='linen')
    S.block(2.1, -2.35, 4.7, -.4)
    with S.at((4.4, -.12, 0)): nightstand(S, 'wood_walnut', .42, .36, .45); table_lamp(S, .45, base='ceramic', e=18)
    with S.at((0, -D / 2, 0), PI): poster(S, 'poster_fortknight', -2.6, 1.6, 0, .6, .9, frame='black'); poster(S, 'poster_eldenbling', -1.8, 1.6, 0, .6, .9, frame='black'); poster(S, 'poster_latency', -1.0, 1.6, 0, .6, .9, frame='black'); poster(S, 'poster_grind', 2.0, 1.6, 0, .6, .9, frame='black')
    for (x, y) in ((-2.6, .4), (2.7, 1.5), (0, -1.4), (3.2, -1.4), (.2, 1.4), (3.6, 2.5), (-3.2, -2.2)): S.cyl(.075, .02, (x, y, H - .008), 'panel', 20, .003); S.spot((x, y, H - .03), 290, '#ffd9ae', 'lamp', (0, 0, 0), 110, .08)
    with S.at((3.55, 3.05, .74)): S.box((.2, .13, .035), (0, 0, .018), 'blackplastic', .008); [S.tube([(x, .05, .03), (x * 1.1, .07, .22)], .005, 'blackplastic', 5) for x in (-.08, -.03, .03, .08)]
    S.box((.03, .3, .4), (W / 2 - .015, -2.85, 1.5), 'gray', .006)
    S.area((-2.1, D / 2 + .1, 1.46), 4.5, 1050, '#cfe0ff', 'day', (-PI / 2, 0, 0), 2.6); S.sun((math.radians(-56), 0, math.radians(-24)), 13, '#ffefd8', .8)
    S.area((2.75, 2.55, 1.2), 1.2, 22, '#ffffff', 'led', (PI / 2, 0, PI), .4); S.area((2.75, 3.22, 2.55), 3, 26, '#ffffff', 'led', (-PI * .8, 0, 0), .05); S.area((2.75, 3.22, .8), 2, 22, '#ffffff', 'led', (-PI * .7, 0, 0), .05); S.area((4.4, 1.35, 2.2), .06, 8, '#ffffff', 'led', (0, -PI * .4, 0), 1.6); S.area((3.3, -1.35, .1), 1.8, 16, '#ffffff', 'led', (PI, 0, 0), 1.4)
    S.anchor('spawn', (.2, -.6), PI); S.anchor('bed', (1.95, -1.3), -PI / 2, lie=[3.2, .62, 1.35]); S.anchor('phone_seat', (-3.95, .8, .5), PI / 2); S.anchor('seat', (2.75, 2.15), PI); S.anchor('door', (4.2, -2.7), PI / 2); S.anchor('outside', (5.8, -2.1), -PI / 2); S.anchor('wardrobe', (1.6, -2.7), 0); S.anchor('food', (-3.6, -2.2), -PI / 2); S.anchor('router', (3.5, 2.2), PI); S.anchor('breaker', (4.3, -2.85), PI / 2)
    S.anchor('idle1', (.6, 1.0), PI); S.anchor('idle2', (-1.2, -.9), 0); S.anchor('work1', (-1.75, -1.9), -PI / 2); S.anchor('work2', (-4.0, 1.5, .46), PI / 2, sit=True); S.anchor('idle3', (-1.0, .6), -PI / 2); S.anchor('tower', (3.55, 2.7, .74), 0); S.anchor('ringlight', (1.55, 2.1, 0), 0); S.anchor('cam', (2.75, 3.1, .74)); S.anchor('decor1', (2.75, D / 2 - .06, 2.1)); S.anchor('decor2', (1.45, 2.95, 0))
    S.meta.update(title='Downtown Loft', cam=dict(target=[0, .8, -.1], dist=11, az=.05, pol=.96, azr=[-.6, .6]), backdrops=[dict(pos=[-2.0, 1.15, -5.7], size=[16, 8], rot=0, img='city')], spill=[-2, 1.5, -3.3])
    return S
def hq():
    S = Scene('hq'); common(); M('wall', 'brick', '#cfc4bb', None, scale=1.5); M('wallP', 'plaster', '#4a5254', .9, scale=2.6); M('floor', 'concrete', '#b9b3a8', .42, scale=3.4); M('cyc', 'paint', '#f6f4ee', .7, scale=3); M('foam_dark', 'foam', '#26282c', .95, scale=.6); M('foam_acc', 'foam', '#1f6f74', .95, scale=.6); M('neonr', None, '#ffffff', .4, emit=('#ff3b26', 2.2), chan='always', bakek=4); M('neony', None, '#ffffff', .4, emit=('#ffc93a', 2.2), chan='always', bakek=4); M('stage', 'wood_walnut', '#ffffff', .5, scale=1.2); M('ceil2', 'paint', '#2a2b2c', .8, scale=2)
    W, D, H = 16, 11, 5.0
    ops = [('N', x, 2.6, 2.3, 4.5) for x in (-5.6, 5.8)] + [('W', 2.5, 1.0, 0, 2.15)]
    S.room(W, D, H, wall=dict(N='wall', E='wallP', S='wallP', W='wall'), ceil='ceil2', openings=ops, base=None)
    for x in (-5.6, 5.8): window(S, 2.6, 2.3, 4.5, x, D / 2, cols=5, rows=4, mat='black', fr=.05, sill=False)
    with S.at((-W / 2 - .05, -2.5, 0), PI / 2): door(S, .98, 2.13, 'red', 'steel', False)
    # trusses
    for y in (3.6,):
        for (dx, dz) in ((-.15, 0), (.15, 0), (0, -.28)): S.tube([(-W / 2, y + dx, H - .5 + dz), (W / 2, y + dx, H - .5 + dz)], .025, 'darksteel', 6, lm=.4)
        for i in range(32): x = -W / 2 + i * .5; S.tube([(x, y - .15, H - .5), (x + .25, y, H - .78)], .012, 'darksteel', 4, lm=.3); S.tube([(x + .25, y, H - .78), (x + .5, y + .15, H - .5)], .012, 'darksteel', 4, lm=.3)
        for x in (-6, -2.2, 2.2, 6):
            S.cyl(.16, .3, (x, y, H - .98), 'black', 20, .01); S.cyl(.14, .01, (x, y, H - 1.135), 'panel', 20, 0); S.spot((x, y - 1.2, H - 1.16), 300, '#ffdfb8', 'lamp', (0, 0, 0), 120, .14); S.spot((x, y - 5.6, H - .8), 330, '#ffdfb8', 'lamp', (0, 0, 0), 125, .14)
    # stream stage NW
    S.box((4.4, 3.2, .16), (-5.6, 3.8, .08), 'stage', .012, grain='x'); S.box((4.42, .012, .02), (-5.6, 2.185, .06), 'strip', 0)
    foam_wall(S, 4.2, 1.9, (-5.6, D / 2, 1.25), 0, (8, 4))
    with S.at((-5.6, 4.75, .16)): desk(S, 2.4, .85, .74, 'wood_walnut', 'black', metal=True); can(S, (1.05, -.2, .74)); mug(S, (-1.05, -.15, .74), 'red')
    S.block(-6.85, 4.25, -4.35, 5.5); S.anchor('desk', (-5.6, 4.75, .9), 0)
    for sx in (-1, 1): S.box((.02, .02, 1.9), (-5.6 + sx * 2.12, D / 2 - .03, 1.25), 'strip', 0)
    # cyc set, N centre-right
    bm = __import__('bmesh').new(); R = .9; cols = 2; prof = [(2.0, .012)] + [(4.5 + R * math.sin(a) - .0, R - R * math.cos(a) + .012) for a in [i * PI / 2 / 8 for i in range(9)]] + [(5.4, 3.2)]; rows = [[bm.verts.new((x, y, z)) for x in (-2.6, 3.2)] for y, z in prof]
    for a, b in zip(rows, rows[1:]): bm.faces.new((a[0], a[1], b[1], b[0]))
    S.add(bm, 'cyc', sharp=80); S.block(-2.6, 5.1, 3.2, 5.5)
    with S.at((-2.3, 1.4, 0), .55): softbox(S, 2.2)
    with S.at((3.0, 1.4, 0), -.55): softbox(S, 2.2)
    S.area((-2.1, 1.7, 2.1), .7, 70, '#fff2e0', 'lamp', (math.radians(65), 0, math.radians(-20)), .7); S.area((2.8, 1.7, 2.1), .7, 70, '#fff2e0', 'lamp', (math.radians(65), 0, math.radians(20)), .7); S.block(-2.7, 1.0, -1.9, 1.9); S.block(2.6, 1.0, 3.4, 1.9)
    with S.at((-.5, .15, 0), PI - .1): cine_cam(S, 1.4)
    with S.at((1.4, .25, 0), PI + .2): cine_cam(S, 1.4)
    S.block(-.9, -.3, -.1, .6); S.block(1.0, -.2, 1.8, .7)
    S.neon('ON AIR', .55, (.3, D / 2 - .06, 3.75), 'neonr', FS); S.area((.3, D / 2 - .2, 3.75), 2, 14, '#ff3b26', 'lamp', (-PI / 2, 0, 0), .5)
    # editing bay E
    for i, (x, y, a, b) in enumerate(((5.0, 3.6, 'scr_edit', 'scr_chat'), (7.0, 3.6, 'scr_stats', 'scr_edit'), (5.0, 1.3, 'scr_edit', 'scr_cams'), (7.0, 1.3, 'scr_chat', 'scr_stats'))):
        with S.at((x, y, 0)): workstation(S, a, b, chair=True)
        S.block(x - .78, y - .4, x + .78, y + .38); S.anchor(f'work{i + 1}', (x, y - .62, .46), PI, sit=True)
    for x in (4.1, 6.0): plant(S, (x - .02, 4.9, 0), 1.1, 'ceramic', 14, int(x * 3), True)
    S.block(3.8, 4.6, 6.4, 5.2)
    # lounge SW
    rug(S, 3.4, 2.4, (-4.9, -3.2), rot=.02)
    with S.at((-6.9, -4.3 + .9, 0), PI / 2): sofa(S, 2.4, .95, 'leather_brown', seats=3)
    S.block(-7.4, -4.7, -6.4, -2.1)
    with S.at((-5.3, -3.4, 0), PI / 2): coffee_table(S, 1.2, .6, .4)
    pizza_box(S, (-5.3, -3.2, .42), .4); can(S, (-5.4, -3.7, .42)); can(S, (-5.2, -3.75, .42), 'can_redbill'); S.block(-5.65, -4.05, -4.95, -2.75)
    with S.at((-7.55, .9, 0), PI / 2): arcade(S, 'poster_cyberjunk', 'red')
    with S.at((-7.55, .15, 0), PI / 2): arcade(S, 'poster_otter', 'teal')
    with S.at((-7.55, -.6, 0), PI / 2): arcade(S, 'poster_minedcraft', 'yellow')
    S.block(-8, -1.0, -7.1, 1.3); S.neon('HYPE', .5, (-W / 2 + .06, .15, 2.7), 'neony', FS, rot=PI / 2)
    # coffee bar S-centre (low)
    with S.at((-1.4, -4.9, 0), PI): kitchen(S, 2.4, 'teal', 'wood_oak', upper=False, stove=False)
    S.box((.34, .3, .38), (-1.9, -4.95, 1.09), 'steel', .02); S.lathe([(0, 0), (.06, 0), (.07, .14), (.05, .2), (0, .2)], (-1.2, -4.95, .9), 'glass', 18); [mug(S, (-.7 + i * .1, -4.9, .9), ['red', 'ceramic', 'yellow'][i]) for i in range(3)]; S.block(-2.7, -5.4, -.1, -4.5)
    # meeting SE
    S.box((2.6, 1.1, .05), (4.6, -2.9, .74), 'wood_oak', .012, grain='x'); [S.box((.08, .8, .72), (4.6 + sx * 1.0, -2.9, .36), 'black', .01) for sx in (-1, 1)]; S.block(3.2, -3.5, 6.0, -2.3)
    for i, (x, y, r) in enumerate(((3.9, -3.75, PI), (5.3, -3.75, PI), (3.9, -2.05, 0), (5.3, -2.05, 0))):
        with S.at((x, y, 0), r): office_chair(S, 'fabric_teal')
    with S.at((W / 2 - .02, -2.9, 0), -PI / 2): poster(S, 'whiteboard', 0, 1.65, 0, 2.4, 1.5, frame='steel')
    with S.at((W / 2 - .3, 0 - .3, 0), -PI / 2): shelf(S, 1.8, .5, 2.4, 4, 'darksteel', back=False, items=False); [boxart(S, (.42, .36, .3), (-.6 + (i % 3) * .58, 0, .08 + (i // 3) * .58), 'card', 'box_amazin', (i * 37 % 10 - 5) * .03) for i in range(12)]
    S.block(7.4, -1.3, 8, .7)
    with S.at((0, -D / 2, 0), PI): poster(S, 'poster_fortknight', -6, 1.9, 0, .9, 1.35, frame='black'); poster(S, 'poster_grind', 6, 1.9, 0, .9, 1.35, frame='black'); poster(S, 'poster_latency', 4.8, 1.9, 0, .9, 1.35, frame='black')
    for x in (-3.6, 3.6): S.tube([(x, D / 2 - .2, 0), (x, D / 2 - .2, H)], .09, 'darksteel', 10)
    S.tube([(-W / 2, D / 2 - .5, 4.75), (W / 2, D / 2 - .5, 4.75)], .2, 'steel', 14, lm=.5)
    S.box((.05, .5, .7), (W / 2 - .03, -4.6, 1.5), 'gray', .01); S.box((.3, .2, .05), (-4.0, 5.2, 1.3), 'blackplastic', .01)
    for x in (-5.6, 5.8): S.area((x, D / 2 + .12, 3.4), 2.5, 620, '#cfe0ff', 'day', (-PI / 2, 0, 0), 2.1)
    S.area((0, 0, H - .15), 10, 210, '#dfe9ff', 'day', (0, 0, 0), 6); S.sun((math.radians(-48), 0, math.radians(22)), 14, '#ffefd8', .8)
    S.area((-5.6, 4.4, 1.4), 1.6, 34, '#ffffff', 'led', (PI / 2, 0, PI), .4); S.area((-5.6, 5.35, 1.0), 3.8, 60, '#ffffff', 'led', (-PI * .7, 0, 0), .06); S.area((-5.6, 2.2, .1), 4.2, 26, '#ffffff', 'led', (PI / 2 + .5, 0, 0), .05); S.area((.3, 3.6, 3.6), 4, 60, '#ffffff', 'led', (.2, 0, 0), 1)
    S.anchor('spawn', (-3.5, -.6), PI); S.anchor('bed', (-6.3, -3.4), -PI / 2, lie=[-6.9, .62, 3.4]); S.anchor('phone_seat', (-6.6, -3.4, .5), PI / 2); S.anchor('seat', (-5.6, 4.05, .16), PI); S.anchor('door', (-7.3, -2.5), -PI / 2); S.anchor('outside', (-9, -2.5), PI / 2); S.anchor('wardrobe', (-7.0, 2.0), -PI / 2); S.anchor('food', (-1.4, -4.15), 0); S.anchor('router', (-4.1, 3.9, .16), PI); S.anchor('breaker', (7.3, -4.6), PI / 2)
    S.anchor('idle1', (-2.6, -1.6), PI / 2); S.anchor('idle2', (-.4, -3.6), 0); S.anchor('idle3', (1.6, -1.6), 0); S.anchor('idle4', (-4.1, -3.0), -PI / 2); S.anchor('cam1', (-.5, -.55), PI); S.anchor('cam2', (1.5, -.5), PI); S.anchor('work5', (4.6, -4.1), PI); S.anchor('work6', (2.9, -2.9), PI / 2)
    S.anchor('host', (.3, 2.9), 0); [S.anchor(f'guest{i + 1}', (-1.5 + i * .75 + (0 if i < 3 else -.1), 4.0 - (i % 2) * .35), 0) for i in range(6)]
    S.anchor('tower', (-4.65, 4.95, .9), 0); S.anchor('ringlight', (-6.95, 4.0, .16), 0); S.anchor('cam', (-5.6, 5.1, .9)); S.anchor('decor1', (-5.6, D / 2 - .06, 2.75)); S.anchor('decor2', (-7.45, 4.95, .16))
    S.meta.update(title='Content Warehouse', cam=dict(target=[0, .9, 0], dist=17.5, az=0, pol=.9, azr=[-.5, .5]), backdrops=[dict(pos=[-5.6, 2.6, -8], size=[12, 6], rot=0, img='city'), dict(pos=[5.8, 2.6, -8], size=[12, 6], rot=0, img='city')], spill=[0, 3, -5])
    return S
def mansion():
    S = Scene('mansion'); common(); M('wall', 'plaster', '#e9e0cf', .85, scale=2.8); M('floor', 'marble', '#ffffff', None, scale=2.2); M('crystal', 'paint', '#eef4f6', .05, .6); M('neonr', None, '#ffffff', .4, emit=('#ff3b26', 2.2), chan='always', bakek=4); M('panelw', 'wood_walnut', '#ffffff', .4, scale=1.1); M('carpetr', 'carpet', '#8e1d18', .97, scale=.7); M('ring', 'paint', '#f2331b', .5); M('fire', None, '#ffffff', .5, emit=('#ff7a20', 4), chan='lamp', bakek=3); M('foam_dark', 'foam', '#1d1e21', .95, scale=.6); M('foam_acc', 'foam', '#7a5a1c', .95, scale=.6)
    W, D, H = 20, 13, 6.2; xs = (-4.6, -1.6, 1.4)
    S.room(W, D, H, openings=[('N', x, 2.2, .15, 4.9) for x in xs] + [('E', 3.2, 1.6, 0, 2.6)], base='panelw', baseh=.18, crown=None)
    for x in xs: window(S, 2.2, .15, 4.9, x, D / 2, cols=2, rows=4, mat='white', fr=.06, sill=False); [S.curtain(.55, 5.2, (x + sx * 1.28, D / 2 - .16, .02), 'fabric_cream', folds=4, nx=40, nz=6) for sx in (-1, 1)]; S.cyl(.025, 3.2, (x, D / 2 - .16, 5.25), 'brass', 10, 0, axis='x')
    for x in (-6.15, -3.1, -.1, 2.95):
        with S.at((x, D / 2 - .5, 0)): column(S, H, .24)
        S.block(x - .35, 5.7, x + .35, 6.5)
    with S.at((W / 2 + .05, -3.2, 0), -PI / 2): door(S, .8, 2.55, 'panelw', 'gold'); 
    # wainscot
    for (x0, y0, r, n) in ((-W / 2 + .01, -5.5, PI / 2, 11), (W / 2 - .01, 5.5, -PI / 2, 8)):
        for i in range(n):
            with S.at((x0, y0 + (i * 1.05 if r > 0 else -i * 1.05), 0), r): S.box((.95, .02, .8), (0, 0, .62), 'white', .01, lm=.5); S.box((.75, .02, .6), (0, -.015, .62), 'white', .012, lm=.5)
    # RIG SANCTUM NE
    S.box((5.6, 4.2, .2), (7.0, 4.3, .1), 'marble_dark', .015); S.box((5.62, .015, .025), (7.0, 2.195, .1), 'strip', 0); S.box((.015, 4.2, .025), (4.195, 4.3, .1), 'strip', 0)
    S.box((5.4, .06, 3.6), (7.1, D / 2 - .03, 2.0), 'panelw', .01, grain='z'); foam_wall(S, 3.2, 1.6, (7.1, D / 2 - .06, 1.75), 0, (6, 3))
    hexes(S, [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (1, 2), (2, 1), (3, 0), (2, 2)], .2, (7.95 - 2.9, D / 2 - .06, 2.75)); hexes(S, [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (1, 2)], .2, (8.5, D / 2 - .06, 2.75))
    with S.at((7.1, 5.35, .2)): S.box((3.0, 1.0, .07), (0, 0, .72), 'marble_dark', .015); S.box((3.04, 1.04, .025), (0, 0, .7), 'gold', .006); [S.box((.5, .8, .68), (sx * 1.1, 0, .34), 'gloss', .02) for sx in (-1, 1)]; [S.box((.52, .82, .02), (sx * 1.1, 0, .1), 'gold', .004) for sx in (-1, 1)]; can(S, (1.3, -.3, .755)); trophy(S, (-1.3, .25, .755), .26)
    S.block(5.5, 4.8, 8.7, 6.0); S.anchor('desk', (7.1, 5.35, .955), 0)
    with S.at((9.75, 4.4, .2), -PI / 2): shelf(S, 2.6, .36, 2.6, 5, 'panelw', fill=.1, seed=33)
    S.block(9.4, 3.0, 10, 5.8)
    # fireplace E wall + portrait
    with S.at((W / 2 - .25, .2, 0), -PI / 2): [S.box((.35, .5, 1.25), (sx * .95, 0, .62), 'marble', .015) for sx in (-1, 1)]; S.box((2.5, .62, .16), (0, -.03, 1.33), 'marble', .02); S.box((1.6, .1, 1.25), (0, .22, .62), 'black', 0); S.cushion((.9, .25, .14), (0, .05, .12), 'wood_walnut', puff=.3); [S.lathe([(0, .1), (.09, .18), (.06, .36), (0, .55 + .1 * i % 3 * .1)], (-.3 + i * .15, .05, 0), 'fire', 8) for i in range(5)]; S.box((1.7, .06, 2.1), (0, .2, 2.75), 'gold', .03); S.quad(1.5, 1.88, (0, .165, 2.75), 'portrait_gold')
    S.point((W / 2 - .45, .2, .5), .15, 34, '#ff8a30', 'lamp'); S.block(9.3, -1.2, 10, 1.6)
    # lounge in front of fireplace
    S.box((4.2, 3.4, .014), (6.9, .2, .007), 'carpetr', 0)
    for (y, r) in ((1.55, 0), (-1.2, PI)):
        with S.at((6.9, y, 0), r): sofa(S, 2.4, 1.0, 'leather_white', 'gold', 3, ('fabric_must', 'knit_red'))
    S.block(5.6, 1.0, 8.2, 2.1); S.block(5.6, -1.75, 8.2, -.65)
    S.box((1.3, .7, .04), (6.9, .2, .42), 'marble', .01); [S.tube([(6.9 + sx * .5, .2 + sy * .25, .4), (6.9 + sx * .55, .2 + sy * .28, 0)], .018, 'gold', 6) for sx in (-1, 1) for sy in (-1, 1)]; trophy(S, (6.9, .2, .44), .3); S.block(6.2, -.2, 7.6, .6)
    # aquarium wall on W
    S.box((.5, 3.4, .7), (-W / 2 + .28, 3.2, .35), 'panelw', .015); S.box((.44, 3.3, 1.25), (-W / 2 + .28, 3.2, 1.33), 'glass', 0, bake_only=True) if False else None; 
    with S.at((-W / 2 + .5, 3.2, 1.33), PI / 2): S.quad(3.3, 1.24, (0, 0, 0), 'aquarium')
    S.box((.5, 3.4, .12), (-W / 2 + .28, 3.2, 2.02), 'panelw', .015); S.area((-W / 2 + .55, 3.2, 1.33), .5 if False else 1.2, 26, '#6fc8ff', 'lamp', (0, -PI / 2, 0), 3.2); S.block(-10, 1.4, -9.4, 5.0)
    # staff desks W
    for i, (x, y, a, b) in enumerate(((-7.6, 4.2, 'scr_edit', 'scr_chat'), (-7.6, 1.7, 'scr_stats', 'scr_edit'), (-7.6, -.8, 'scr_cams', 'scr_chat'), (-7.6, -3.3, 'scr_edit', 'scr_stats'))):
        with S.at((x, y, 0)): workstation(S, a, b, 'wood_walnut', chair=True)
        S.block(x - .78, y - .4, x + .78, y + .38); S.anchor(f'work{i + 1}', (x, y - .62, .46), PI, sit=True)
    # challenge ring centre
    bm = __import__('bmesh').new(); n = 64; ring = [[bm.verts.new((math.cos(i * 2 * PI / n) * r, 1.2 + math.sin(i * 2 * PI / n) * r, .006)) for i in range(n)] for r in (2.35, 2.5)]
    for i in range(n): bm.faces.new((ring[0][i], ring[1][i], ring[1][(i + 1) % n], ring[0][(i + 1) % n]))
    S.add(bm, 'ring')
    with S.at((-3.6, -2.4, 0), PI - .7): cine_cam(S, 1.4)
    with S.at((3.2, -2.2, 0), PI + .7): cine_cam(S, 1.4)
    S.block(-4.0, -2.8, -3.2, -2.0); S.block(2.8, -2.6, 3.6, -1.8)
    # piano S-E, palms, statues, gold buttons
    with S.at((6.2, -4.3, 0), -2.4): piano(S)
    S.block(5.0, -5.6, 7.5, -3.2)
    for (x, y) in ((-9.3, 5.9), (9.4, -4.9), (4.0, 5.9), (-9.3, -5.6)):
        with S.at((x, y, 0)): palm(S, 2.6, int(abs(x * 7 + y)))
        S.block(x - .35, y - .35, x + .35, y + .35)
    for (x, y) in ((-5.2, 5.75), (2.1 + 1.6, 2.2)):
        pass
    with S.at((-W / 2 + .03, -3.2, 0), PI / 2): poster(S, 'painting_1', 0, 2.6, 0, 2.6, 1.73, frame='gold'); poster(S, 'painting_2', 2.4, 2.6, 0, 1.1, 1.65, frame='gold'); poster(S, 'painting_2', -2.2, 2.6, 0, 1.1, 1.65, frame='gold')
    with S.at((0, -D / 2, 0), PI): poster(S, 'painting_1', -3, 2.6, 0, 2.4, 1.6, frame='gold'); poster(S, 'portrait_gold', 3, 2.6, 0, 1.4, 1.75, frame='gold')
    chandelier(S, (0, .8, H), 1.15, 190, 1.5); chandelier(S, (-6.8, .6, H), .8, 110, 1.6); chandelier(S, (6.8, .2, H), .8, 110, 1.6)
    # bar S-W
    S.box((3.0, .6, 1.05), (-3.2, -5.3, .525), 'panelw', .015); S.box((3.14, .74, .05), (-3.2, -5.3, 1.07), 'marble_dark', .01); [can(S, (-4.2 + i * .18, -5.3, 1.095), 'can_redbill' if i % 2 else 'can_mobster') for i in range(7)]; S.block(-4.8, -5.7, -1.6, -4.9)
    for x in (-4.1, -3.2, -2.3):
        with S.at((x, -4.6, 0)): stool(S, .75, 'leather_red')
    for x in xs: S.area((x, D / 2 + .12, 2.55), 2.1, 280, '#cfe2ff', 'day', (-PI / 2, 0, 0), 4.7)
    S.sun((math.radians(-50), 0, math.radians(-18)), 9.5, '#ffedd0', .7)
    for (x, y) in ((7, 4.2), (-7.6, 3), (-7.6, -2), (0, -3.5), (6.4, -4.2)): S.cyl(.09, .02, (x, y, H - .01), 'panel', 18, .003, lm=.5); S.spot((x, y, H - .05), 105, '#ffd8a8', 'lamp', (0, 0, 0), 75, .1)
    S.area((7.1, 4.7, 1.6), 2.2, 50, '#ffffff', 'led', (PI / 2, 0, PI), .6); S.area((7.1, 6.35, 3.1), 5, 110, '#ffffff', 'led', (-PI * .65, 0, 0), .5); S.area((7.0, 2.2, .1), 5.4, 46, '#ffffff', 'led', (PI / 2 + .5, 0, 0), .05); S.area((4.2, 4.3, .1), .05, 36, '#ffffff', 'led', (0, PI / 2 - .5, 0) if False else (0, -PI / 2 + .5, PI), 4); S.area((0, 1.2, 5.5), 3, 120, '#ffffff', 'led', (0, 0, 0), 3)
    S.anchor('spawn', (0, -2.6), PI); S.anchor('bed', (8.9, -2.9), PI / 2); S.anchor('phone_seat', (6.9, 1.35, .52), 0); S.anchor('seat', (7.1, 4.4, .2), PI); S.anchor('door', (9.3, -3.6), PI / 2); S.anchor('outside', (11, -3.2), -PI / 2); S.anchor('wardrobe', (8.6, -4.4), PI / 2); S.anchor('food', (-3.2, -4.4), 0); S.anchor('router', (5.3, 4.6, .2), PI); S.anchor('breaker', (9.3, -5.4), PI / 2)
    S.anchor('idle1', (2.6, 4.2), PI); S.anchor('idle2', (-1.0, -4.4), 0); S.anchor('idle3', (-5.4, -2.2), PI / 2); S.anchor('idle4', (3.6, -3.6), 0); S.anchor('idle5', (-5.2, 2.4), PI / 2); S.anchor('cam1', (-4.0, -3.1), PI - .7); S.anchor('cam2', (3.6, -2.9), PI + .7); S.anchor('work5', (4.7, .2), PI / 2); S.anchor('work6', (-5.4, -5.2), -PI / 2)
    S.anchor('host', (0, .1), 0); [S.anchor(f'guest{i + 1}', (math.cos(PI * (.15 + .7 * i / 5)) * 1.75, 1.2 + math.sin(PI * (.15 + .7 * i / 5)) * 1.75), 0) for i in range(6)]
    S.anchor('tower', (8.3, 5.5, .955), 0); S.anchor('ringlight', (5.1, 4.1, .2), 0); S.anchor('cam', (7.1, 5.75, .955)); S.anchor('decor1', (7.1, D / 2 - .1, 2.85)); S.anchor('decor2', (9.3, 2.6, .2))
    S.meta.update(title='The Mansion', cam=dict(target=[0, 1.0, .2], dist=20.5, az=0, pol=.92, azr=[-.5, .5]), backdrops=[dict(pos=[-1.6, .5, -10], size=[34, 17], rot=0, img='ocean')], spill=[-1.6, 3, -6.5])
    return S
ENVS = dict(bedroom=bedroom, studio=studio, loft=loft, hq=hq, mansion=mansion)
if __name__ == '__main__':
    import argparse
    quick = '--quick' in sys.argv; names = [a for a in sys.argv[1:] if not a.startswith('--')] or list(ENVS)
    for n in names:
        bpy.ops.wm.read_factory_settings(use_empty=True); S = ENVS[n](); print(n, 'parts', len(S.parts), 'tris', sum(len(p.f) for p in S.parts)); sys.stdout.flush()
        by = {}
        size, spp = dict(bedroom=(1536, 44), studio=(1536, 44), loft=(2048, 32), hq=(2048, 28), mansion=(2048, 28))[n]; bake_env(S, 1024 if quick else size, spp, quick=quick)
