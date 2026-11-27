"""Build rigged, morphing, textured humans. usage: python characters.py [id ...]"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import mh, textures_char as tx
from cast import CAST
PUB = os.path.expanduser('~/chat-are-we-live/public/assets'); OUT = f'{PUB}/chars'
os.makedirs(f'{OUT}/tex', exist_ok=True)
U = 'expression/units/'
MORPHS = {  # runtime morph -> expression units
    'blink_l': [('eye-left-closure', 1)], 'blink_r': [('eye-right-closure', 1)],
    'wide': [('eye-left-opened-up', 1), ('eye-right-opened-up', 1)],
    'squint': [('eye-left-slit', 1), ('eye-right-slit', 1)],
    'brow_up': [('eyebrows-left-up', 1), ('eyebrows-right-up', 1)],
    'brow_down': [('eyebrows-left-down', 1), ('eyebrows-right-down', 1)],
    'brow_sad': [('eyebrows-left-inner-up', 1), ('eyebrows-right-inner-up', 1)],
    'smile': [('mouth-corner-puller', 1)], 'frown': [('mouth-depression', 1)],
    'open': [('mouth-open', 1)], 'pucker': [('mouth-protusion', .8), ('mouth-pursing', .5)],
    'wide_mouth': [('mouth-retraction', 1)], 'sneer': [('mouth-upward-retraction', .8), ('nose-left-elevation', .7), ('nose-right-elevation', .7)],
    'press': [('mouth-compression', 1)],
}
def conv(P): P = np.asarray(P); return np.stack([P[..., 0], -P[..., 2], P[..., 1]], -1) * .1

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def decimate(verts, faces, uv, ft, weights, morphs, ratio):
    from scipy.spatial import cKDTree
    me = bpy.data.meshes.new('tmp'); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    ul = me.uv_layers.new(name='UVMap'); k = 0
    for t in ft:
        for i in t: ul.data[k].uv = (uv[i][0], uv[i][1]); k += 1
    ob = bpy.data.objects.new('tmp', me); bpy.context.scene.collection.objects.link(ob)
    m = ob.modifiers.new('d', 'DECIMATE'); m.ratio = ratio; m.use_collapse_triangulate = False
    dg = bpy.context.evaluated_depsgraph_get(); ev = bpy.data.meshes.new_from_object(ob.evaluated_get(dg)); bpy.data.objects.remove(ob)
    nv = np.array([v.co for v in ev.vertices]); nf = [list(p.vertices) for p in ev.polygons]
    luv = ev.uv_layers[0].data; nuv = []; nft = []
    for p in ev.polygons:
        t = []
        for li in p.loop_indices: t.append(len(nuv)); nuv.append(tuple(luv[li].uv))
        nft.append(t)
    _, ix = cKDTree(np.asarray(verts)).query(nv)
    return nv, nf, np.array(nuv), nft, weights[ix], ({k: d[ix] for k, d in morphs.items()} if morphs else None)

def mk(name, verts, faces, uv, ft, weights, names, arm, morphs=None, ratio=None):
    if ratio: verts, faces, uv, ft, weights, morphs = decimate(verts, faces, uv, ft, weights, morphs, ratio)
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    ul = me.uv_layers.new(name='UVMap'); k = 0
    for f, t in zip(faces, ft):
        for i in t: ul.data[k].uv = (uv[i][0], uv[i][1]); k += 1
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    for j, nm in enumerate(names):
        col = weights[:, j]; nz = np.nonzero(col > .002)[0]
        if len(nz) == 0: continue
        vg = ob.vertex_groups.new(name=nm)
        for i in nz: vg.add([int(i)], float(col[i]), 'REPLACE')
    ob.parent = arm; m = ob.modifiers.new('Armature', 'ARMATURE'); m.object = arm
    if morphs:
        ob.shape_key_add(name='Basis')
        for nm, d in morphs.items():
            kb = ob.shape_key_add(name=nm); pts = verts + d
            kb.data.foreach_set('co', pts.astype(np.float32).ravel())
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name); me.materials.append(mat)
    return ob

def compact(verts_sel, faces, ft):
    """keep faces whose verts are all selected; return index map"""
    ff, tt = [], []
    for f, t in zip(faces, ft):
        if all(verts_sel[i] for i in f): ff.append(f); tt.append(t)
    used = sorted({i for f in ff for i in f}); mp = {v: k for k, v in enumerate(used)}
    return used, [[mp[i] for i in f] for f in ff], tt

def build(cid, portrait=True):
    cfg = CAST[cid]; reset(); rnd = random.Random(cid)
    _, T, F, FT, G = mh.base()
    V = mh.shape(cfg['race'], cfg['gender'], cfg.get('age', .1), cfg.get('muscle', .5), cfg.get('weight', .5), cfg.get('height', .5), cfg.get('prop', .7), cfg.get('details', ()))
    # ground: lowest shoe/body vertex to 0
    clothes = [(mh.proxy('clothes', n)) for n in cfg['clothes']]
    lo = min([V[:13380, 1].min()] + [p.fit(V)[:, 1].min() for p in clothes]); V[:, 1] -= lo
    names, W = mh.weights(); names = list(names)
    ri = cfg['race'] if isinstance(cfg['race'], str) else max(cfg['race'], key=cfg['race'].get)
    MD = {k: sum(mh.target(f'{U}{ri}/{n}') * w for n, w in us) for k, us in MORPHS.items()}
    # ---- armature
    ad = bpy.data.armatures.new('Rig'); arm = bpy.data.objects.new('Rig', ad); bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
    rg = mh.rig()
    for nm, b in rg.items():
        eb = ad.edit_bones.new(nm); eb.head = conv(mh.joint(V, b['head'])); eb.tail = conv(mh.joint(V, b['tail'])); eb.roll = b['roll']
        if (eb.tail - eb.head).length < .005: eb.tail = eb.head + Vector((0, 0, .03))
    for nm, b in rg.items():
        if b['parent']: ad.edit_bones[nm].parent = ad.edit_bones[b['parent']]
    eyes = {}
    for s in 'lr':
        c = conv(V[mh.groups()[f'joint-{s}-eye']].mean(0)); eb = ad.edit_bones.new(f'eye_{s}'); eb.head = c; eb.tail = Vector(c) + Vector((0, -.03, 0)); eb.parent = ad.edit_bones['head']; eyes[s] = c
    bpy.ops.object.mode_set(mode='OBJECT')
    allnames = names + ['eye_l', 'eye_r']; W2 = np.hstack([W, np.zeros((len(W), 2), np.float32)])
    objs = []
    # ---- body
    dele = np.zeros(len(V), bool)
    for p in clothes:
        if p.name not in ('glasses',): dele |= p.delete
    if cfg.get('hair_delete'): pass
    vis = np.zeros(len(V), bool); vis[:13380] = True; vis &= ~dele
    bodyF = [(f, t) for f, t, g in zip(F, FT, G) if g == 'body']
    headv = np.zeros(len(V), bool)
    hi, ni = names.index('head'), names.index('neck_01')
    # split by UV island: head island lies at u>.625 and .14<v<.83
    def is_head(t): return all(T[i][0] > .622 and .13 < T[i][1] < .84 for i in t)
    hf = [(f, t) for f, t in bodyF if is_head(t) and all(vis[i] for i in f)]
    bf = [(f, t) for f, t in bodyF if not is_head(t) and all(vis[i] for i in f)]
    def submesh(lst):
        used = sorted({i for f, _ in lst for i in f}); mp = {v: k for k, v in enumerate(used)}
        return used, [[mp[i] for i in f] for f, _ in lst], [t for _, t in lst]
    P = conv(V)
    # hair proxies first (for scalp mask)
    hairs = [(mh.proxy('hair', h)) for h in cfg.get('hair', [])]
    from scipy.spatial import cKDTree
    scalp = np.zeros(len(V))
    eyeY, eyeZ = V[mh.groups()['joint-l-eye']].mean(0)[1:]
    sh = [p for p in hairs if p.name not in ('Full_beard', 'Moustache')]
    if sh:
        tree = cKDTree(np.vstack([p.fit(V) for p in sh])); d, _ = tree.query(V[:13380]); scalp[:13380] = np.clip(1 - (d - .10) / .22, 0, 1)
        # never paint face or neck below ears
        fz = V[:13380, 2] > eyeZ - .25; fy = V[:13380, 1] < eyeY + .48; scalp[:13380][fz & fy] = 0
        scalp[:13380][V[:13380, 1] < eyeY - .55] = 0
    hmask = tx.raster_attr(T, [t for _, t in bodyF], [f for f, _ in bodyF], scalp, 1024)
    headim, bodyim = tx.skin(cfg, V, T, [f for f, _ in bodyF], [t for _, t in bodyF], hmask)
    headim.save(f'{OUT}/tex/{cid}_head.webp', quality=88); bodyim.save(f'{OUT}/tex/{cid}_body.webp', quality=86)
    tex = {'head': f'{cid}_head.webp', 'body': f'{cid}_body.webp'}
    T2 = T.copy(); hu = {i for _, t in hf for i in t}
    for i in hu: T2[i] = tx.head_uv(*T[i])
    used, ff, tt = submesh(hf)
    # include neck seam: keep head normals continuous by exporting neck part in body
    objs.append(mk('head', P[used], ff, T2, tt, W2[used], allnames, arm, {k: conv(d[used]) for k, d in MD.items()}))
    used, ff, tt = submesh(bf); objs.append(mk('body', P[used], ff, T, tt, W2[used], allnames, arm))
    # seam normals: copy from full body mesh
    full = bpy.data.meshes.new('full'); full.from_pydata([tuple(p) for p in P[:13380]], [], [f for f, _ in bodyF]); full.update()
    nrm = np.zeros(13380 * 3, np.float32); full.vertices.foreach_get('normal', nrm); nrm = nrm.reshape(-1, 3)
    for ob, lst in ((objs[0], hf), (objs[1], bf)):
        us = sorted({i for f, _ in lst for i in f}); ob.data.normals_split_custom_set_from_vertices([tuple(nrm[i]) for i in us])
    def addproxy(p, name, morph=False, eye=False, uv=None):
        pv = conv(p.fit(V)); w = (W2[p.ref] * np.clip(p.w, 0, 1)[..., None]).sum(1); w /= np.maximum(w.sum(1, keepdims=True), 1e-6)
        if eye:
            w[:] = 0
            for i, q in enumerate(pv): w[i, allnames.index('eye_l' if q[0] > 0 else 'eye_r')] = 1
        if name in ('teeth', 'brows', 'lashes', 'hair', 'glasses', 'beard', 'hat') and cfg.get('rigidhead', True):
            if name != 'hair': w[:] = 0; w[:, hi] = 1
        md = None
        if morph:
            md = {}
            for k, d in MD.items():
                x = conv(p.delta(d))
                if np.abs(x).max() > 1e-4: md[k] = x
        n = len(p.faces); tgt = {'teeth': 700, 'glasses': 700, 'shoes': 900, 'hair': 2300, 'tongue': 120}.get(name, 2600)
        ob = mk(name, pv, p.faces, p.uv, p.ft, w, allnames, arm, md, ratio=tgt / n if n > tgt * 1.15 else None); objs.append(ob); return ob
    addproxy(mh.proxy('eyes', 'Low-Poly'), 'eyes', eye=True)
    tex['eyes'] = tx.passthru(f'{mh.MH}/proxies/eyes/Low-Poly/textures/{cfg.get("eye", "brown")}_eye.png', f'eye_{cfg.get("eye", "brown")}')
    b = mh.proxy('eyebrows', cfg.get('brow', 'eyebrow001')); addproxy(b, 'brows', True); tex['brows'] = tx.hair(b.tex(), np.array(cfg.get('browRGB', np.array(cfg['hairRGB']) * .75)), f'brow_{b.name}_{cid}', .4)
    l = mh.proxy('eyelashes', cfg.get('lash', 'eyelashes02')); addproxy(l, 'lashes', True); tex['lashes'] = tx.hair(l.tex(), np.array([.05, .04, .04]), f'lash_{l.name}', .2)
    t = mh.proxy('teeth', 'Teeth_Base'); addproxy(t, 'teeth', True); tex['teeth'] = tx.passthru(t.tex(), 'teeth')
    tg = [d for d in os.listdir(f'{mh.MH}/proxies/tongue')]
    if tg and os.path.isdir(f'{mh.MH}/proxies/tongue/{tg[0]}'):
        try: q = mh.proxy('tongue', tg[0]); ob = addproxy(q, 'tongue', True); tex['tongue'] = tx.passthru(q.tex(), 'tongue', 256)
        except Exception as e: print('tongue', e)
    for p in hairs:
        nm = 'beard' if p.name in ('Full_beard', 'Moustache') else 'hair'
        addproxy(p, nm, nm == 'beard'); tex[nm] = tx.hair(p.tex(), np.array(cfg['hairRGB']) * (1 if nm == 'hair' else .85), f'hair_{p.name}_{cid}', cfg.get('hairContrast', 1))
    for i, p in enumerate(clothes):
        o = cfg.get('outfit', {}).get(p.name, {})
        nm = 'glasses' if p.name == 'glasses' else ('shoes' if p.name.startswith('shoe') or 'Boots' in p.name else ('hat' if p.name.startswith('fedora') else f'cloth{i}'))
        addproxy(p, nm)
        if p.name in tx.LOGO or o.get('shirt') or o.get('pants'): tex[nm] = tx.outfit(p.tex(), p.name, o, f'{cid}_{p.name}')
        else: tex[nm] = tx.passthru(p.tex(), f'{cid}_{p.name}' if o.get('tint') else f'c_{p.name}', 512, o.get('tint'))
        nt = p.tex('mapNormal')
        if nt and os.path.exists(nt): tex[nm + '_n'] = tx.passthru(nt, f'n_{p.name}')
    pass
    # ---- vertex AO
    vs, fs = [], []
    for ob in objs:
        if ob.name.split('.')[0] in ('lashes', 'brows'): continue
        o = len(vs); vs += [v.co.copy() for v in ob.data.vertices]; fs += [[i + o for i in p.vertices] for p in ob.data.polygons]
    bvh = BVHTree.FromPolygons(vs, fs); rs = np.random.RandomState(1); N = 40
    dirs = rs.randn(N, 3); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    for ob in objs:
        me = ob.data; nv = len(me.vertices); ao = np.ones(nv)
        nl = np.zeros(len(me.loops) * 3, np.float32); me.corner_normals.foreach_get('vector', nl); nl = nl.reshape(-1, 3)
        vn = np.zeros((nv, 3)); li = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', li); np.add.at(vn, li, nl); vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-6)
        hairy = ob.name.startswith(('hair', 'beard'))
        if not ob.name.startswith(('lashes', 'brows')):
            for i in range(nv):
                n = vn[i]; c = np.array(me.vertices[i].co); hit = 0; tot = 0
                dd = dirs + n * 1.02; dd /= np.linalg.norm(dd, axis=1, keepdims=True)
                up = .55 + .45 * dd[:, 2]
                for k in range(N):
                    h = bvh.ray_cast(Vector(c + n * .003), Vector(dd[k]), .45)
                    w = up[k]; tot += w
                    if h[0] is not None: hit += w * (1 - h[3] / .45) ** .6
                ao[i] = 1 - hit / tot
            ao = np.clip(ao, 0, 1) ** (.8 if hairy else 1.0)
            # smooth once
            ed = np.zeros(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', ed); ed = ed.reshape(-1, 2)
            s = ao.copy(); c = np.ones(nv); np.add.at(s, ed[:, 0], ao[ed[:, 1]]); np.add.at(c, ed[:, 0], 1); np.add.at(s, ed[:, 1], ao[ed[:, 0]]); np.add.at(c, ed[:, 1], 1); ao = s / c
        ca = me.color_attributes.new('COL', 'FLOAT_COLOR', 'POINT'); arr = np.ones((nv, 4), np.float32); arr[:, :3] = ao[:, None]; ca.data.foreach_set('color', arr.ravel())
        me.color_attributes.active_color = ca
    # ---- meta
    hpts = conv(V[:13380]); hw = W[:13380, hi] > .9
    meta = dict(id=cid, height=float(hpts[:, 2].max()), headTop=float(hpts[hw][:, 2].max()), headWidth=float(hpts[hw][:, 0].max() * 2),
                eye=[float(eyes['l'][0]), float(eyes['l'][2]), float(-eyes['l'][1])], tex=tex, gender='m' if cfg['gender'] > .5 else 'f', hairRGB=[float(x) for x in cfg['hairRGB']])
    json.dump(meta, open(f'{OUT}/{cid}.json', 'w'))
    # ---- export
    for o in bpy.data.objects: o.select_set(False)
    for o in objs + [arm]: o.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(filepath=f'{OUT}/{cid}.glb', export_format='GLB', use_selection=True, export_yup=True, export_skins=True, export_morph=True, export_morph_normal=True,
        export_animations=False, export_materials='PLACEHOLDER', export_vertex_color='ACTIVE', export_texcoords=True, export_normals=True, export_influence_nb=4)
    print('EXPORTED', cid, os.path.getsize(f'{OUT}/{cid}.glb') // 1024, 'KB verts', sum(len(o.data.vertices) for o in objs), 'faces', sum(len(o.data.polygons) for o in objs))
    if portrait: render_portrait(cid, objs, arm, meta, tex, cfg)

def texmat(ob, path, rough, alpha=False, sss=0, spec=.4):
    m = ob.data.materials[0]; m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(path); im.image.alpha_mode = 'CHANNEL_PACKED'; mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = .35
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'COL'
    nt.links.new(im.outputs['Color'], mul.inputs[6]); nt.links.new(vc.outputs['Color'], mul.inputs[7]); nt.links.new(mul.outputs[2], bs.inputs['Base Color'])
    if alpha: nt.links.new(im.outputs['Alpha'], bs.inputs['Alpha'])
    bs.inputs['Roughness'].default_value = rough; bs.inputs['Specular IOR Level'].default_value = spec
    if sss: bs.inputs['Subsurface Weight'].default_value = sss; bs.inputs['Subsurface Radius'].default_value = (.012, .005, .003); bs.inputs['Subsurface Scale'].default_value = 1.0

def render_portrait(cid, objs, arm, meta, tex, cfg, full=False, size=512, samples=32):
    sc = bpy.context.scene
    for ob in objs:
        k = ob.name.split('.')[0]; path = f'{OUT}/tex/{tex[k]}'
        if k in ('head', 'body'): texmat(ob, path, .5, sss=.18)
        elif k in ('hair', 'brows', 'lashes', 'beard'): texmat(ob, path, .55, True, spec=.25)
        elif k == 'eyes': texmat(ob, path, .06, False, spec=.6)
        elif k == 'glasses': texmat(ob, path, .2, True)
        else: texmat(ob, path, .85, Image_has_alpha(path))
        sk = ob.data.shape_keys
        if sk:
            for n, v in cfg.get('face', {'smile': .55, 'squint': .15}).items():
                if n in sk.key_blocks: sk.key_blocks[n].value = v
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True; sc.render.resolution_x = sc.render.resolution_y = size
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.5, .55, .62, 1); w.node_tree.nodes['Background'].inputs[1].default_value = .35
    bgc = cfg.get('bg', (.83, .72, .52))
    bm = bpy.data.materials.new('bg'); bm.use_nodes = True; bm.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (*bgc, 1); bm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 1.1, 1.5), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(bm)
    ey = meta['eye'][1]
    def area(loc, e, s, col=(1, 1, 1)):
        l = bpy.data.lights.new('a', 'AREA'); l.energy = e; l.size = s; l.color = col; o = bpy.data.objects.new('a', l); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector((0, 0, ey - .05)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    area((-1.1, -1.3, ey + .7), 38, .9, (1, .95, .88)); area((1.4, -.8, ey + .1), 12, 1.2, (.8, .9, 1)); area((.9, .9, ey + .7), 12, .7, (1, .9, .8))
    cam = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co
    if full: cam.lens = 50; co.location = (0, -4.6, .95); co.rotation_euler = (math.pi / 2, 0, 0)
    else:
        cam.lens = 112; co.location = (.28, -1.35, ey + .02); t = Vector((0, 0, ey - .025)); co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.image_settings.file_format = 'WEBP'; sc.render.image_settings.quality = 88
    sc.render.filepath = f'{OUT}/{cid}{"_full" if full else ""}.webp'; bpy.ops.render.render(write_still=True)

def Image_has_alpha(p):
    from PIL import Image
    return Image.open(p).mode == 'RGBA'

if __name__ == '__main__':
    ids = sys.argv[1:] or list(CAST)
    for c in ids: build(c)
