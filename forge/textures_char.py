"""Per-character texture synthesis: skin detail, hair tint, outfit recolour + joke-brand prints."""
import numpy as np, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import mh
OUT = os.path.expanduser('~/chat-are-we-live/public/assets/chars/tex')
FONT_B = None

def font(size, path=None):
    p = path or os.path.expanduser('~/.cache/forge/fonts/display.ttf')
    return ImageFont.truetype(p, size)

def noise(n, seed, lo, hi):
    """band-passed gaussian noise, tileable, unit std"""
    r = np.random.RandomState(seed).randn(n, n); f = np.fft.fft2(r)
    k = np.hypot(*np.meshgrid(np.fft.fftfreq(n) * n, np.fft.fftfreq(n) * n))
    f *= np.exp(-(k / hi) ** 2) * (1 - np.exp(-(k / lo) ** 2)); x = np.fft.ifft2(f).real
    return x / x.std()

def raster_attr(uv, ft, faces, val, n):
    """rasterize per-vertex scalar to UV space (n x n), dilated"""
    img = Image.new('F', (n, n), -1); d = ImageDraw.Draw(img)
    for f, t in zip(faces, ft):
        c = float(np.mean([val[i] for i in f]))
        d.polygon([(uv[i][0] * n, (1 - uv[i][1]) * n) for i in t], fill=c, outline=c)
    a = np.array(img); m = a < 0
    a[m] = 0
    return a

def blur(a, r):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(a.astype(np.float32), r)

def smooth_up(im, n):
    return im.resize((n, n), Image.BICUBIC)

def skin(cfg, V, uv, faces, ft, hairmask):
    """returns (head 1024 rgb, body 512 rgb). head = crop of UV [.62,1]x[.15,.85]"""
    seed = cfg.get('seed', 1); N = 2048
    race = cfg['skin']
    src = Image.open(f'{mh.MH}/skins/{race}').convert('RGB')
    a = np.asarray(smooth_up(src, N)).astype(np.float32) / 255
    # soften scan blotches slightly, then re-add controlled detail
    pores = noise(N, seed, 180, 620); mott = noise(N, seed + 1, 6, 40); mid = noise(N, seed + 2, 50, 160)
    a *= (1 + pores[..., None] * .022 + mid[..., None] * .012 + mott[..., None] * .012)
    a[..., 0] *= 1 + mott * .008
    def mask(nm):
        return np.asarray(Image.open(f'{mh.MP}/textures/{nm}').convert('L').resize((N, N))).astype(np.float32) / 255
    lips = blur(mask('mpfb_lips.jpg'), 5)[..., None]; lids = blur(mask('mpfb_eyelids.jpg'), 6)[..., None]
    ears = blur(mask('mpfb_ears.jpg'), 14)[..., None]
    lipc = np.array(cfg.get('lip', [.62, .30, .28])); la = cfg.get('lipA', .38)
    lum = a.mean(-1, keepdims=True)
    a = a * (1 - lips * la) + lips * la * lipc * (0.55 + lum) * (1 + noise(N, seed + 5, 60, 400)[..., None] * .05)
    lidc = np.array(cfg.get('lid', [.80, .58, .52])); a *= 1 - lids * (1 - lidc) * cfg.get('lidA', .35)
    a *= 1 - ears * (1 - np.array([1.0, .88, .86])) * .5
    # positional masks
    P = V
    def gauss(c, s, mirror=True):
        d = ((P - np.array(c)) / np.array(s)); w = np.exp(-(d ** 2).sum(1))
        if mirror:
            c2 = np.array(c) * [-1, 1, 1]; w = np.maximum(w, np.exp(-(((P - c2) / np.array(s)) ** 2).sum(1)))
        return blur(raster_attr(uv, ft, faces, w, N // 2).repeat(2, 0).repeat(2, 1), 9)[..., None]
    eye = V[mh.groups()['joint-l-eye']].mean(0); nose = V[mh.groups()['joint-head']].mean(0)
    ex, ey, ez = eye
    cheek = gauss([ex * 1.35, ey - .42, ez + .1], [.32, .24, .5]); a *= 1 - cheek * (1 - np.array([1.02, .80, .78])) * cfg.get('blush', .45)
    tip = gauss([0, ey - .36, ez + .5], [.14, .14, .3], False); a *= 1 - tip * (1 - np.array([1.0, .84, .82])) * .45
    under = gauss([ex, ey - .16, ez + .2], [.17, .06, .4]); a *= 1 - under * (1 - np.array([.84, .80, .84])) * cfg.get('eyebag', .35)
    if cfg.get('stubble', 0):
        w = np.zeros(len(P)); yc = ey - .80
        for i, p in enumerate(P[:13380]):
            if p[2] < ez - 1.0: continue
            lower = np.clip((ey - .42 - p[1]) / .12, 0, 1) * np.clip((p[1] - (ey - 1.25)) / .15, 0, 1)
            side = np.clip((abs(p[0]) - .30) / .12, 0, 1) * np.clip((ey - .25 - p[1]) / .2, 0, 1)
            w[i] = np.clip(max(lower if abs(p[0]) < .75 else lower, side * lower), 0, 1)
        st = blur(raster_attr(uv, ft, faces, w, N // 2).repeat(2, 0).repeat(2, 1), 8)[..., None] * (1 - lips)
        hairs = (noise(N, seed + 9, 200, 700) > .35).astype(np.float32)[..., None]
        hc = np.array(cfg['hairRGB']) * .7
        k = st * cfg['stubble'] * (.35 + .65 * hairs)
        a = a * (1 - k * .75) + hc * k * .75
    if cfg.get('freckles'):
        fm = gauss([ex * .9, ey - .32, ez + .2], [.5, .24, .6]); fr = np.clip(noise(N, seed + 11, 40, 150) - 1.5, 0, 1)[..., None]
        a *= 1 - fr * fm * cfg['freckles'] * np.array([.25, .45, .5])
    # scalp tint under hair cards
    hm = blur(hairmask.repeat(2, 0).repeat(2, 1), 12)[..., None] * np.clip(1 - blur(mask('mpfb_ears.jpg'), 10)[..., None] * 1.6, 0, 1)
    hc = np.array(cfg['hairRGB']); strands = 1 + noise(N, seed + 13, 80, 500)[..., None] * .2
    a = a * (1 - hm * .92) + hc * .55 * strands * hm * .92
    if 'tone' in cfg: a *= np.array(cfg['tone'])
    a = np.clip(a, 0, 1)
    im = Image.fromarray((a * 255).astype(np.uint8))
    x0, y0, x1, y1 = HEADBOX
    head = im.crop((int(x0 * N), int(y0 * N), int(x1 * N), int(y1 * N))).resize((1024, 1024), Image.LANCZOS)
    return head, im.resize((512, 512), Image.LANCZOS)

HEADBOX = (.625, .17, 1.0, .86)  # in image space (y down)
def head_uv(u, v):
    x0, y0, x1, y1 = HEADBOX; iy = 1 - v
    return ((u - x0) / (x1 - x0), 1 - (iy - y0) / (y1 - y0))

def hair(src, rgb, name, contrast=1.0):
    p = f'{OUT}/{name}.webp'
    im = Image.open(src).convert('RGBA'); a = np.asarray(im).astype(np.float32) / 255
    rgbA, al = a[..., :3], a[..., 3]
    L = rgbA.mean(-1); m = al > .3
    mu, sd = L[m].mean(), L[m].std() + 1e-4
    z = np.clip((L - mu) / sd, -2.5, 2.5)
    c = np.array(rgb)[None, None] * (1 + z[..., None] * .30 * contrast)
    out = np.dstack([np.clip(c, 0, 1), al])
    im = Image.fromarray((out * 255).astype(np.uint8), 'RGBA')
    # bleed colour under alpha so mips don't fringe
    bg = Image.new('RGBA', im.size, tuple(int(x * 255) for x in rgb) + (255,)); b2 = bg.copy(); b2.paste(im, (0, 0), im)
    im = b2.resize((1024, 1024), Image.LANCZOS); al2 = Image.fromarray((al * 255).astype(np.uint8)).resize((1024, 1024), Image.LANCZOS)
    im.putalpha(al2); im.save(p, quality=88, exact=True); return f'{name}.webp'

def hexrgb(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])

def tint(a, mask, col, ref=None, strength=1.0, contrast=1.0):
    L = (a * [.3, .59, .11]).sum(-1); m = mask > .5
    mu = L[m].mean() if m.any() else .5
    shade = np.clip(1 + (L / max(mu, .02) - 1) * contrast, .25, 1.9)
    out = np.clip(np.array(col)[None, None] * shade[..., None], 0, 1)
    k = (mask * strength)[..., None]
    return a * (1 - k) + out * k

def draw_print(im, cx, cy, w, spec, rot=0):
    S = 4; W = int(w * S); lay = Image.new('RGBA', (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    col = spec.get('col', '#fff'); lines = spec['text'].split('\n')
    y = 0
    blocks = []
    for ln in lines:
        sz = W
        f = font(sz); bb = d.textbbox((0, 0), ln, font=f); sc = min(1, W * .96 / (bb[2] - bb[0])); sz = max(8, int(min(sz * sc, W * spec.get('maxh', .5)))); f = font(sz); bb = d.textbbox((0, 0), ln, font=f)
        blocks.append((ln, f, bb))
    tot = sum(b[2][3] - b[2][1] for b in blocks) + int(.06 * W) * (len(blocks) - 1); y = (W - tot) // 2
    if spec.get('box'):
        d.rounded_rectangle((0, y - W * .07, W - 1, y + tot + W * .07), radius=int(W * .04), fill=spec['box'])
    if spec.get('ring'):
        d.ellipse((W * .03, W * .03, W * .97, W * .97), outline=spec['ring'], width=int(W * .05))
    for ln, f, bb in blocks:
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), ln, font=f, fill=col); y += bb[3] - bb[1] + int(.06 * W)
    lay = lay.resize((int(w), int(w)), Image.LANCZOS)
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC)
    a = np.asarray(lay).astype(np.float32); wear = np.clip(.93 + noise(256, 5, 20, 100)[:lay.size[1], :lay.size[0]] * .08, 0, 1) if lay.size[0] <= 256 else .95
    a[..., 3] *= wear; lay = Image.fromarray(a.astype(np.uint8), 'RGBA')
    im.paste(lay, (int(cx - w / 2), int(cy - w / 2)), lay)

LOGO = {  # suit: (cx,cy,r,rot) chest logo; patch offset to clone clean cloth from
    'male_casualsuit02': (222 / 400, 65 / 400, 27 / 400, 0), 'male_casualsuit04': (221 / 400, 65 / 400, 27 / 400, 0),
    'female_casualsuit01': (313 / 400, 84 / 400, 36 / 400, -90), 'female_casualsuit02': (313 / 400, 84 / 400, 36 / 400, -90),
    'female_sportsuit01': (313 / 400, 84 / 400, 36 / 400, -90),
    'male_casualsuit06': (212 / 400, 65 / 400, 36 / 400, 0)}

def outfit(src, suit, cfg, name):
    im = Image.open(src).convert('RGBA'); a = np.asarray(im).astype(np.float32) / 255; al = a[..., 3].copy(); a = a[..., :3].copy(); n = a.shape[0]
    yy, xx = np.mgrid[0:n, 0:n] / n
    if suit in LOGO:
        cx, cy, r, rot = LOGO[suit]
        if suit == 'male_casualsuit06':
            for (x0, x1, y0, y1) in [(.43, .60, .115, .2), (.19, .30, .115, .165), (.72, .78, .14, .2)]:
                sl = np.s_[int(y0 * n):int(y1 * n), int(x0 * n):int(x1 * n)]; h = int(y1 * n) - int(y0 * n)
                a[sl] = a[int(.26 * n):int(.26 * n) + h, int(x0 * n):int(x1 * n)]
        else:
            m = ((xx - cx) ** 2 + (yy - cy) ** 2) < (r * 1.12) ** 2
            dx, dy = (0, int(r * 1.9 * n)) if rot == 0 else (-int(198 / 400 * n), 0)
            src_a = np.roll(a, (-dy, -dx), (0, 1)); k = blur(m.astype(np.float32), 3)[..., None]; k = np.clip(k * 1.6, 0, 1)
            a = a * (1 - k) + src_a * k
    mx, mn = a.max(-1), a.min(-1); sat = (mx - mn) / (mx + 1e-4)
    orange = ((a[..., 0] > a[..., 2] * 1.6) & (a[..., 0] > .5) & (sat > .4)).astype(np.float32)
    top = (yy < .413).astype(np.float32)
    if suit == 'male_casualsuit02': top = np.maximum(top, (xx > .735) & (yy > .585)).astype(np.float32)
    if suit.startswith('female'): top = np.maximum((yy < .42), (xx > .719) & (yy > .58)).astype(np.float32)
    if suit == 'male_casualsuit06': top = np.maximum(yy < .43, xx > .71).astype(np.float32)
    if suit in ('male_casualsuit01',): top = np.ones_like(top) * (cfg.get('topmask', 1))
    if suit == 'male_casualsuit03': bl = blur(((a[..., 2] > a[..., 0] * 1.04) & (yy < .62) & (mx > .12)).astype(np.float32), 2) > .45; top = (~bl & (mx > .05)).astype(np.float32)
    bottom = 1 - top
    if suit.startswith('female') or suit == 'male_casualsuit06': bgm = ((sat < .06) & (mx > .8)).astype(np.float32) if suit.startswith('female') else 0; top = top * (1 - bgm); bottom = bottom * (1 - bgm)
    if cfg.get('shirt') is not None: a = tint(a, blur(top * (1 - orange), .6), hexrgb(cfg['shirt']), contrast=cfg.get('contrast', 1.5))
    if cfg.get('trim') is not None: a = tint(a, blur(orange * top, .6), hexrgb(cfg['trim']))
    if cfg.get('pants') is not None: a = tint(a, bottom, hexrgb(cfg['pants']), contrast=.85)
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((1024, 1024), Image.LANCZOS)
    w = np.asarray(im).astype(np.float32) / 255
    weave = noise(1024, 3, 200, 420); w *= 1 + weave[..., None] * .025
    im = Image.fromarray((np.clip(w, 0, 1) * 255).astype(np.uint8))
    if cfg.get('print') and suit in LOGO:
        cx, cy, r, rot = LOGO[suit]; draw_print(im, cx * 1024, cy * 1024, cfg.get('printW', 104), cfg['print'], rot)
    al2 = Image.fromarray((al * 255).astype(np.uint8)).resize((1024, 1024), Image.LANCZOS)
    if al.min() < .5: im.putalpha(al2)
    im.save(f'{OUT}/{name}.webp', quality=86); return f'{name}.webp'

def passthru(src, name, size=512, tintc=None):
    p = f'{OUT}/{name}.webp'
    im = Image.open(src).convert('RGBA')
    if tintc is not None:
        a = np.asarray(im).astype(np.float32) / 255; rgb = tint(a[..., :3], np.ones(a.shape[:2]), hexrgb(tintc)); im = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), a[..., 3]]) * 255).astype(np.uint8), 'RGBA')
    if np.asarray(im)[..., 3].min() > 250: im = im.convert('RGB')
    im = im.resize((size, size), Image.LANCZOS); im.save(p, quality=86, exact=True) if im.mode == 'RGBA' else im.save(p, quality=86); return f'{name}.webp'
