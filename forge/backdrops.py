"""Cycles-rendered views outside the windows (day + night)."""
import bpy, math, random, os, sys
from mathutils import Vector
OUT = os.path.expanduser('~/chat-are-we-live/public/assets/env/bg'); os.makedirs(OUT, exist_ok=True)
def mat(name, col, rough=.8, emit=None, es=0, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = es
    return m
def windows_mat(name, wall, night, sx, sz, seed):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; lk = nt.links.new; b = N['Principled BSDF']; b.inputs['Roughness'].default_value = .5
    g = N.new('ShaderNodeNewGeometry'); sp = N.new('ShaderNodeSeparateXYZ'); lk(g.outputs['Position'], sp.inputs[0])
    def math_(op, a, bv): n = N.new('ShaderNodeMath'); n.operation = op; (lk(a, n.inputs[0]) if hasattr(a, 'is_linked') or not isinstance(a, (int, float)) else setattr(n.inputs[0], 'default_value', a)); (lk(bv, n.inputs[1]) if not isinstance(bv, (int, float)) else setattr(n.inputs[1], 'default_value', bv)); return n.outputs[0]
    h = math_('ADD', sp.outputs[0], sp.outputs[1]); u = math_('MULTIPLY', h, sx); v = math_('MULTIPLY', sp.outputs[2], sz); fu = math_('FRACT', u, 0); fv = math_('FRACT', v, 0)
    mu = math_('MULTIPLY', math_('GREATER_THAN', fu, .22), math_('LESS_THAN', fu, .82)); mv = math_('MULTIPLY', math_('GREATER_THAN', fv, .25), math_('LESS_THAN', fv, .8)); mk = math_('MULTIPLY', mu, mv)
    c = N.new('ShaderNodeCombineXYZ'); lk(math_('FLOOR', u, 0), c.inputs[0]); lk(math_('FLOOR', v, 0), c.inputs[1]); c.inputs[2].default_value = seed; wn = N.new('ShaderNodeTexWhiteNoise'); lk(c.outputs[0], wn.inputs[0])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; lk(mk, mix.inputs[0]); mix.inputs[6].default_value = (*wall, 1); mix.inputs[7].default_value = (.05, .09, .13, 1) if not night else (.02, .02, .03, 1); lk(mix.outputs[2], b.inputs['Base Color'])
    if night:
        lit = math_('MULTIPLY', mk, math_('GREATER_THAN', wn.outputs[0], .62)); st = math_('MULTIPLY', lit, math_('ADD', math_('MULTIPLY', wn.outputs[0], 3.5), .4)); lk(st, b.inputs['Emission Strength']); r = N.new('ShaderNodeValToRGB'); lk(wn.outputs[1], r.inputs[0]); r.color_ramp.elements[0].color = (1, .55, .22, 1); r.color_ramp.elements[1].color = (.75, .88, 1, 1); lk(r.outputs[0], b.inputs['Emission Color'])
    else:
        ro = math_('SUBTRACT', .6, math_('MULTIPLY', mk, .5)); lk(ro, b.inputs['Roughness'])
    return m
def base(night, sun=(50, 30), strength=1.0, haze=None):
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 20; sc.cycles.use_denoising = True; sc.render.resolution_x = 1280; sc.render.resolution_y = 640; sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; nt = w.node_tree; bg = nt.nodes['Background']; tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sp.inputs[0]); rp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(sp.outputs[2], rp.inputs[0]); nt.links.new(rp.outputs[0], bg.inputs[0]); e = rp.color_ramp.elements
    if night: e[0].color = (.16, .09, .16, 1); e[0].position = 0; e[1].color = (.006, .011, .035, 1); e[1].position = .4; x = e.new(.08); x.color = (.055, .05, .12, 1); bg.inputs[1].default_value = .7
    else: e[0].color = (.95, .86, .74, 1); e[0].position = 0; e[1].color = (.16, .38, .75, 1); e[1].position = .5; x = e.new(.1); x.color = (.66, .78, .9, 1); bg.inputs[1].default_value = 1.0; l = bpy.data.lights.new('s', 'SUN'); l.energy = 4; l.color = (1, .9, .75); l.angle = .01; o = bpy.data.objects.new('s', l); sc.collection.objects.link(o); o.rotation_euler = (math.radians(sun[0]), 0, math.radians(sun[1]))
    c = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', c); sc.collection.objects.link(co); sc.camera = co; c.lens = 30; c.clip_end = 5000
    return sc, co
def box(s, l, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=l); o = bpy.context.object; o.scale = s; o.data.materials.append(m); return o
def save(sc, name):
    sc.render.image_settings.file_format = 'WEBP'; sc.render.image_settings.quality = 86; sc.render.filepath = f'{OUT}/{name}.webp'; bpy.ops.render.render(write_still=True); print('bg', name); sys.stdout.flush()
def tree(loc, h, m, tr, seed):
    r = random.Random(seed); box((.25, .25, h * .5), (loc[0], loc[1], loc[2] + h * .25), tr)
    for i in range(5):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=h * r.uniform(.2, .3), location=(loc[0] + r.uniform(-.2, .2) * h, loc[1] + r.uniform(-.2, .2) * h, loc[2] + h * r.uniform(.5, .85))); o = bpy.context.object; o.data.materials.append(m); t = bpy.data.textures.new('n', 'CLOUDS'); t.noise_scale = .28; d = o.modifiers.new('d', 'DISPLACE'); d.texture = t; d.strength = .75; [setattr(pp, 'use_smooth', True) for pp in o.data.polygons]
def city(night):
    sc, co = base(night, (52, -40)); co.location = (0, -90, 62); co.data.lens = 24; co.rotation_euler = (math.radians(86), 0, 0); r = random.Random(4); cols = [(.42, .36, .32), (.30, .31, .34), (.55, .50, .44), (.22, .25, .30), (.48, .30, .24), (.62, .60, .56)]
    ms = [windows_mat(f'w{i}', tuple(c * (1 if not night else .35) for c in cols[i % 6]), night, [.32, .45, .25, .6, .38, .5][i % 6], [.3, .28, .33, .27, .3, .31][i % 6], i) for i in range(12)]
    for row in range(9):
        y = 70 + row * 46
        for i in range(-7, 8):
            if r.random() < .12: continue
            x = i * (24 + row * 5) + r.uniform(-8, 8); h = r.uniform(18, 46) + (row ** 1.2) * r.uniform(2, 11) + (40 if r.random() < .12 else 0); w = r.uniform(12, 22) + row * 1.5; d = r.uniform(12, 20); m = r.choice(ms); box((w, d, h), (x, y, h / 2), m)
            if r.random() < .35: box((w * .5, d * .5, h * .18), (x, y, h * 1.09), m)
            if r.random() < .15: box((.5, .5, 14), (x, y, h + 7), ms[0])
    box((3000, 3000, 1), (0, 1400, -.5), mat('g', (.12, .12, .13) if not night else (.03, .03, .04)))
    # haze layers
    for k, y in enumerate((160, 280, 430)):
        m = bpy.data.materials.new('hz'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); o = nt.nodes.new('ShaderNodeOutputMaterial'); t = nt.nodes.new('ShaderNodeBsdfTransparent'); e = nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value = (.72, .78, .88, 1) if not night else (.10, .07, .13, 1); e.inputs[1].default_value = .9; mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs[0].default_value = .2; nt.links.new(t.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], o.inputs[0]); bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, y, 0), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(m); bpy.context.object.visible_shadow = False
    save(sc, f'city_{"night" if night else "day"}')
def suburb(night):
    sc, co = base(night, (50, 30)); co.location = (0, 0, 5.2); co.rotation_euler = (math.radians(86), 0, 0); r = random.Random(2); g = mat('grass', (.09, .18, .04) if not night else (.02, .035, .02)); rd = mat('road', (.09, .09, .1)); tr = mat('trunk', (.1, .06, .04)); lf = [mat('l1', (.07, .17, .03)), mat('l2', (.12, .2, .04)), mat('l3', (.25, .17, .03))]
    box((400, 400, .1), (0, 150, -.05), g); box((400, 7, .12), (0, 26, 0), rd); box((400, 1.6, .16), (0, 21, 0), mat('pv', (.45, .44, .42)))
    for i in range(-4, 5):
        x = i * 15 + r.uniform(-2, 2); wl = [(.72, .66, .55), (.45, .55, .60), (.70, .45, .36), (.78, .76, .70), (.42, .50, .40)][i % 5]; wm = mat('wl', tuple(c * (1 if not night else .25) for c in wl)); rf = mat('rf', [(.22, .10, .08), (.12, .12, .14), (.2, .15, .12)][i % 3]); y = 40 + r.uniform(-2, 3); box((9.5, 8, 5.4), (x, y, 2.7), wm)
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=8, depth=3.6, location=(x, y, 7.2), rotation=(0, 0, math.pi / 4)); o = bpy.context.object; o.scale = (1, .9, 1); o.data.materials.append(rf)
        for wx in (-3, 0, 3):
            for wz in (1.5, 4):
                on = night and r.random() < .45; box((1.3, .1, 1.3), (x + wx, y - 4.03, wz), mat('wi', (.1, .13, .17), .15, (1, .65, .3) if on else None, 5 if on else 0)); box((1.6, .06, 1.6), (x + wx, y - 4.0, wz), mat('wt', (.8, .8, .78) if not night else (.2, .2, .2)))
        tree((x + 7.2, y - 9 + r.uniform(-2, 2), 0), r.uniform(5, 8.5), r.choice(lf), tr, i + 50)
    for i in range(16): tree((r.uniform(-70, 70), r.uniform(54, 85), 0), r.uniform(7, 12), r.choice(lf), tr, i)
    tree((-9, 13, 0), 6.5, lf[1], tr, 91); tree((12, 16, 0), 5.5, lf[2], tr, 92)
    if night:
        for x in (-22, 0, 22): box((.14, .14, 6), (x, 22, 3), rd); box((.6, .5, .16), (x, 22.4, 6), mat('lamp', (1, 1, 1), .5, (1, .7, .35), 40)); l = bpy.data.lights.new('p', 'POINT'); l.energy = 900; l.color = (1, .7, .4); o = bpy.data.objects.new('p', l); sc.collection.objects.link(o); o.location = (x, 22.4, 5.7)
    cm = mat('car', (.35, .05, .04), .25); rb = mat('tyre', (.02, .02, .02)); gl = mat('glass', (.05, .07, .09), .1)
    for cx, cc in ((7, cm), (-14, mat('car2', (.08, .16, .26), .25))):
        a = box((4.3, 1.75, .75), (cx, 24.4, .72), cc); b = box((2.3, 1.55, .62), (cx - .15, 24.4, 1.35), gl); [setattr(q.modifiers.new('b', 'BEVEL'), 'width', .16) for q in (a, b)]; [setattr(q.modifiers[0], 'segments', 3) for q in (a, b)]
        for wx in (-1.35, 1.35): bpy.ops.mesh.primitive_cylinder_add(radius=.34, depth=1.8, location=(cx + wx, 24.4, .34), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(rb)
    save(sc, f'suburb_{"night" if night else "day"}')
def ocean(night):
    sc, co = base(night, (60, 150)); co.location = (0, 0, 4.2); co.rotation_euler = (math.radians(87), 0, 0); r = random.Random(3)
    def water(c, sc_, st):
        m = mat('wa', c, .06); nt = m.node_tree; n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = sc_; n.inputs['Detail'].default_value = 6; tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, .35, 1); nt.links.new(tc.outputs['Object'], mp.inputs[0]); nt.links.new(mp.outputs[0], n.inputs['Vector']); b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = st; nt.links.new(n.outputs[0], b.inputs['Height']); nt.links.new(b.outputs[0], nt.nodes['Principled BSDF'].inputs['Normal']); return m
    box((4000, 3000, .1), (0, 1560, -6), water((.01, .09, .14), .6, .5)); box((80, 34, .6), (0, 20, -.4), mat('deck', (.62, .55, .46) if not night else (.2, .18, .16), .5)); pm = water((.03, .42, .5), 2.5, .15)
    if night: pm.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (.05, .6, .75, 1); pm.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 1.6
    box((34, 13, .1), (0, 25, -.08), pm); box((35, .5, .25), (0, 18.3, 0), mat('cop', (.8, .78, .74)))
    tr = mat('ptr', (.25, .17, .1)); fr = [mat('pf', (.06, .18, .04)), mat('pf2', (.1, .22, .05))]
    for (x, y, h) in ((-19, 24, 9), (-15, 33, 8), (19, 26, 10), (15, 34, 8.5), (-27, 28, 11), (27, 22, 9), (24, 35, 7.5)):
        for k in range(6): box((.34 - k * .02, .34 - k * .02, h / 6), (x + math.sin(k * .4) * .4, y, h / 6 * (k + .5)), tr)
        for k in range(16):
            a = k * math.pi / 8; bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=2, size=1, location=(0, 0, 0)); o = bpy.context.object; o.data.materials.append(fr[k % 2])
            for v in o.data.vertices: t = v.co.x + .5; v.co = Vector((t * 3.6, v.co.y * .75 * math.sin(math.pi * min(1, t * .9 + .08)), .9 * t - 2.4 * t * t + abs(v.co.y) * -.3))
            o.rotation_euler = (0, 0, a); o.location = (x + .4, y, h)
    for i in range(5): x = -12 + i * 6; box((2, .8, .12), (x, 15.6, .45), mat('lo', (.85, .83, .78))); bpy.ops.transform if False else None; box((.8, .8, .1), (x - .95, 15.6, .75), mat('lo2', (.85, .83, .78)))
    # islands
    for (x, y, s) in ((-300, 900, 60), (180, 1200, 90), (420, 1000, 45)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=s, location=(x, y, -s * .72)); o = bpy.context.object; o.scale = (2.4, 1, .9); o.data.materials.append(mat('isl', (.14, .2, .2) if not night else (.02, .025, .05)))
    if night:
        for x in (-18, 18): l = bpy.data.lights.new('p', 'POINT'); l.energy = 700; l.color = (1, .7, .4); o = bpy.data.objects.new('p', l); sc.collection.objects.link(o); o.location = (x, 18, 2)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=26, location=(260, 1400, 330)); bpy.context.object.data.materials.append(mat('moon', (1, 1, 1), 1, (1, .95, .85), 5))
    save(sc, f'ocean_{"night" if night else "day"}')
only = sys.argv[1:]
for f in (city, suburb, ocean):
    for n in (False, True):
        nm = f.__name__ + ('_night' if n else '_day')
        if not only or nm in only: f(n)
