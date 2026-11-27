"""Tileable PBR textures (numpy). albedo webp + 'nr' webp (RG=normal xy, B=roughness)."""
import numpy as np, os, json
from PIL import Image, ImageDraw
OUT = os.path.expanduser('~/chat-are-we-live/public/assets/tex'); os.makedirs(OUT, exist_ok=True)
N = 1024
def bp(seed, lo, hi, n=N, ax=1.0, ay=1.0):
    r = np.random.RandomState(seed).randn(n, n); f = np.fft.fft2(r)
    kx, ky = np.meshgrid(np.fft.fftfreq(n) * n * ax, np.fft.fftfreq(n) * n * ay); k = np.hypot(kx, ky)
    f *= np.exp(-(k / hi) ** 2) * (1 - np.exp(-(k / max(lo, .01)) ** 2)); x = np.fft.ifft2(f).real
    return x / x.std()
def fbm(seed, lo=1, oct=6, ax=1, ay=1, gain=.55):
    o = 0; a = 1
    for i in range(oct): o = o + a * bp(seed + i, lo * 2 ** i * .7, lo * 2 ** i * 1.4, ax=ax, ay=ay); a *= gain
    return o / o.std()
def blur(a, r):
    from scipy.ndimage import gaussian_filter; return gaussian_filter(a, r, mode='wrap')
def nrm(h, s):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * s; dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * s
    l = np.sqrt(dx * dx + dy * dy + 1); return -dx / l, dy / l
AVG = {}
def save(name, alb, h, rough, s=4.0):
    alb = np.clip(alb, 0, 1)
    if alb.ndim == 2: alb = np.repeat(alb[..., None], 3, 2)
    Image.fromarray((alb * 255 + .5).astype(np.uint8)).save(f'{OUT}/{name}.webp', quality=82)
    nx, ny = nrm(h, s); rough = np.broadcast_to(np.clip(rough, .03, 1), (N, N))
    Image.fromarray((np.dstack([nx * .5 + .5, ny * .5 + .5, rough]) * 255 + .5).astype(np.uint8)).save(f'{OUT}/{name}_nr.webp', quality=78)
    AVG[name] = [float(x) for x in (alb ** 2.2).mean((0, 1))]
    print(name, AVG[name])
yy, xx = np.mgrid[0:N, 0:N] / N
def col(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])
def lerp(a, b, t): t = np.clip(t, 0, 1)[..., None]; return a * (1 - t) + b * t

def plaster():
    h = fbm(1, 8, 6) * .5 + bp(7, 100, 300) * .25; save('plaster', .90 + fbm(3, 2, 4) * .010 + bp(4, 60, 200) * .006, h * .4, .86 + fbm(9, 4, 3) * .02, 1.2)
def planks(name, cols, rows, base, dark, seed, rough=.42, gap=.0022, wear=.06):
    alb = np.zeros((N, N, 3)); h = np.zeros((N, N)); rg = np.zeros((N, N)); rs = np.random.RandomState(seed)
    grain = fbm(seed, 2, 7, ay=.08, ax=1.0); fine = bp(seed + 20, 60, 400, ay=.03, ax=1); ring = fbm(seed + 40, 1, 4, ay=.25, ax=1.5)
    for c in range(cols):   # planks run along x
        y0, y1 = int(c * N / cols), int((c + 1) * N / cols); off = rs.rand(); nseg = rows
        cuts = np.sort((off + (np.arange(nseg) + rs.rand(nseg) * .35) / nseg) % 1)
        for k in range(nseg):
            a, b = cuts[k], cuts[(k + 1) % nseg] + (1 if k == nseg - 1 else 0)
            xs = np.arange(int(a * N), int(b * N)) % N; sl = np.ix_(np.arange(y0, y1), xs); dy, dx = rs.randint(0, N, 2)
            g = np.roll(grain, (dy, dx), (0, 1))[sl]; f = np.roll(fine, (dy, dx), (0, 1))[sl]; r = np.roll(ring, (dx, dy), (0, 1))[sl]
            tone = rs.randn() * .5
            t = .42 + .16 * g + .10 * np.sin(r * 5 + g * 1.5) + .07 * f + tone * .14
            cc = lerp(base, dark, t); cc = cc * (1 + rs.randn(3) * .012); alb[sl] = cc; h[sl] = -.25 * f - .15 * g; rg[sl] = rough + .06 * f + rs.randn() * .02
            ed = np.zeros((y1 - y0, len(xs))); ed[:, :2] = 1; ed[:, -1:] = 1; alb[sl] *= (1 - ed * .55)[..., None]; h[sl] -= ed * 2.2
        for yy_ in (y0, y0 + 1, y1 - 1): alb[yy_] *= .5; h[yy_] -= 2.0
    w = np.clip(fbm(seed + 60, 2, 4), -2, 2); alb *= (1 + w * .02)[..., None]
    save(name, alb, h, rg + w * wear, 1.6)
def wood(name, base, dark, seed, rough=.45):
    g = fbm(seed, 1.5, 7, ax=.07, ay=1.0); f = bp(seed + 20, 80, 420, ax=.025, ay=1); r = fbm(seed + 30, .8, 3, ax=.3, ay=1.2)
    t = .42 + .17 * g + .12 * np.sin(r * 6 + g) + .07 * f; save(name, lerp(base, dark, t), -.3 * f, rough + .05 * f, 1.2)
def brick():
    rows, cols = 16, 5; alb = np.zeros((N, N, 3)); h = np.zeros((N, N)); rs = np.random.RandomState(5); n1 = fbm(70, 6, 5); n2 = bp(75, 120, 420)
    mort = col('#b0a597') * (1 + (n1 * .05 + n2 * .05)[..., None]); alb[:] = mort; hm = n2 * .15; jit = fbm(77, 10, 3) * .0011
    X = (xx + jit) % 1; Y = (yy + np.roll(jit, 300, 0)) % 1
    r = (Y * rows).astype(int) % rows; fx = (X * cols + .5 * (r % 2)); c = fx.astype(int) % cols; u = fx % 1; v = (Y * rows) % 1
    tone = rs.rand(rows, cols); hue = rs.rand(rows, cols)
    t = tone[r, c]; hu = hue[r, c]
    edge = np.minimum(np.minimum(u, 1 - u) / cols, np.minimum(v, 1 - v) / rows); m = np.clip((edge - .0052) / .0028, 0, 1)
    bc = lerp(lerp(col('#8d4a37'), col('#6d3a30'), t), col('#a8674a'), hu * .5) * (1 + (n1 * .07 + n2 * .06)[..., None])
    alb = lerp(alb, bc, m); save('brick', alb, m * 2.6 + n1 * .3 * m + n2 * .25, .88 - .05 * m, 2.2)
def concrete():
    b = fbm(80, 1.5, 7, gain=.6); p = np.clip(bp(85, 40, 160) - 2.1, 0, 3); f = bp(87, 150, 450)
    save('concrete', np.clip(.66 + b * .035 + f * .015 - p * .12, 0, 1)[..., None] * col('#fffaf2'), f * .25 - p * 1.2 + b * .2, .72 + b * .05, 1.4)
def carpet():
    f = bp(90, 120, 500); t = bp(92, 30, 100); save('carpet', .74 + f * .09 + t * .035, f * .8 + t * .6, .97, 2.2)
def fabric():
    u = np.sin(xx * 2 * np.pi * 128); v = np.sin(yy * 2 * np.pi * 128); ch = np.sign(np.sin(xx * np.pi * 256) * np.sin(yy * np.pi * 256))
    h = np.where(ch > 0, np.abs(u), np.abs(v)); slub = bp(101, 20, 120, ax=.1) * .4 + bp(102, 20, 120, ay=.1) * .4
    save('fabric', .78 + (h - .6) * .14 + slub * .03 + bp(104, 4, 30) * .012, h * .9 + slub * .4, .93, 1.6)
def knit():
    u = xx * 48; v = yy * 64; s = np.abs(np.sin(np.pi * (u + .35 * np.abs(((v * 2) % 2) - 1)))); h = s ** .6
    save('knit', .72 + (h - .6) * .22 + bp(110, 100, 400) * .03, h * 2, .95, 2)
def leather():
    rs = np.random.RandomState(12); P = rs.rand(2600, 2)
    from scipy.spatial import cKDTree
    T = np.vstack([P + [i, j] for i in (-1, 0, 1) for j in (-1, 0, 1)]); q = np.stack([xx, yy], -1).reshape(-1, 2); d, _ = cKDTree(T).query(q, k=2)
    e = np.clip((d[:, 1] - d[:, 0]).reshape(N, N) * 130, 0, 1); h = blur(e, 1.2)
    save('leather', .80 + (h - .7) * .10 + fbm(115, 3, 4) * .02, h * 1.2 + bp(116, 100, 300) * .08, .46 - (h - .7) * .12, 1.6)
def marble():
    w = fbm(120, 1.2, 6); v1 = 1 - np.abs(bpwarp(w, 121, 1.2)); v2 = 1 - np.abs(bpwarp(w, 131, 2.6))
    vein = np.clip(v1, 0, 1) ** 14 * .75 + np.clip(v2, 0, 1) ** 20 * .35
    a = lerp(np.broadcast_to(col('#efebe4'), (N, N, 3)), col('#8d857b'), vein + np.clip(fbm(141, 1.5, 5) * .05 + .04, 0, 1))
    gr = 2; g = np.minimum((xx * gr) % 1, (yy * gr) % 1); line = (g < .0035).astype(float); a *= (1 - line * .45)[..., None]
    save('marble', a, -line * 1.5, .13 + vein * .05 + line * .4 + fbm(150, 3, 3) * .012, 1.0)
def bpwarp(w, seed, f):
    b = fbm(seed, f, 5); n = np.arange(N); iy, ix = np.mgrid[0:N, 0:N]; return b[(iy + (w * 26).astype(int)) % N, (ix + (np.roll(w, 200, 0) * 26).astype(int)) % N]
def tiles():
    n = 6; u, v = (xx * n) % 1, (yy * n * 1) % 1; e = np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v)); m = np.clip((e - .018) / .02, 0, 1); rs = np.random.RandomState(3); t = rs.rand(n, n)[(yy * n).astype(int), (xx * n).astype(int)]
    a = lerp(np.broadcast_to(col('#a9a39a'), (N, N, 3)), np.array([.93, .92, .90]), m) * (1 + (t * .03 - .015) * m)[..., None]; save('tiles', a, m * 3 + bp(160, 3, 12) * .3, .8 - m * .66, 2.0)
def subway():
    r, c = 12, 6; ro = (yy * r).astype(int); fx = xx * c + .5 * (ro % 2); u, v = fx % 1, (yy * r) % 1; e = np.minimum(np.minimum(u, 1 - u) / c, np.minimum(v, 1 - v) / r); m = np.clip((e - .003) / .004, 0, 1)
    a = lerp(np.broadcast_to(col('#b9b3aa'), (N, N, 3)), np.array([.92, .92, .90]), m); save('subway', a, m * 3 + bp(165, 3, 10) * .35, .85 - m * .72, 2.0)
def brushed():
    f = bp(170, 60, 500, ax=.01); save('brushed', .78 + f * .035, f * .35, .34 + f * .06, .8)
def cardboard():
    f = bp(180, 80, 400, ay=.08); save('cardboard', (.66 + f * .02 + fbm(181, 3, 4) * .02)[..., None] * col('#ffdba8'), f * .4, .92, 1)
def grass():
    a = bp(190, 100, 500, ax=1.6); b = fbm(191, 4, 5); c = lerp(col('#4f7a2c'), col('#87a545'), .5 + .22 * a + .15 * b); save('grass', c, a, .95, 2.5)
def rubber():
    f = bp(200, 200, 500); save('rubber', .8 + f * .03, f * .6, .75, 1)
def foam():
    n = 8; t = np.abs(((xx * n) % 1) - .5) * 2; alt = ((xx * 2).astype(int) + (yy * 2).astype(int)) % 2; t2 = np.abs(((yy * n) % 1) - .5) * 2; h = np.where(alt > 0, t, t2)
    save('foam', .55 + h * .35 + bp(205, 150, 450) * .03, h * 14, .96, 2)
def tarp():
    save('paint', .92 + fbm(210, 2, 5) * .006, bp(211, 60, 200) * .2 + fbm(212, 6, 3) * .2, .38 + fbm(213, 3, 4) * .03, .7)
def rugs():
    # woven kilim-style pattern, drawn then weave-modulated
    im = Image.new('RGB', (N, N), '#7a2f26'); d = ImageDraw.Draw(im); P = ['#d9b36a', '#1f3a4a', '#e8dcc0', '#b5452c']
    for k, inset in enumerate((18, 46, 60, 100, 112)):
        d.rectangle((inset, inset, N - inset, N - inset), outline=P[k % 4], width=[16, 6, 26, 5, 8][k])
    for i in range(4):
        for j in range(4):
            cx, cy = 205 + i * 204, 205 + j * 204
            for q, r in enumerate((92, 70, 48, 26)):
                pts = []
                for a in range(8):
                    rr = r if a % 2 == 0 else r * .72; th = a * np.pi / 4; pts.append((cx + rr * np.cos(th), cy + rr * np.sin(th)))
                d.polygon(pts, fill=P[(q + i + j) % 4])
    for i in range(40):
        x = 30 + i * 24.5; 
        for y in (66, N - 66): d.polygon([(x, y - 11), (x + 11, y), (x, y + 11), (x - 11, y)], fill=P[i % 2 + 2])
        for y in (66, N - 66): d.polygon([(y, x - 11), (y + 11, x), (y, x + 11), (y - 11, x)], fill=P[i % 2 + 2])
    a = np.asarray(im).astype(float) / 255; f = bp(220, 120, 480); w = np.sin(yy * 2 * np.pi * 170) * .06; a = a * (.88 + f[..., None] * .06 + w[..., None]); a = lerp(a, np.broadcast_to(a.mean((0, 1)), a.shape), .12 + fbm(221, 2, 4) * .05)
    save('rug', a, f * .7 + w * 4, .97, 1.6)
if __name__ == '__main__':
    plaster(); planks('floor_oak', 8, 2, col('#c39a6b'), col('#8a5f3a'), 11, .40); planks('floor_old', 10, 2, col('#a8794e'), col('#64422a'), 31, .55); planks('floor_dark', 7, 2, col('#6f4a33'), col('#3c2619'), 51, .30)
    wood('wood_oak', col('#c79f6e'), col('#94683f'), 61); wood('wood_walnut', col('#7d5438'), col('#452b1c'), 63, .38); wood('wood_pine', col('#dcb988'), col('#b98d58'), 65, .5); wood('wood_gray', col('#a39a8e'), col('#6f665b'), 67, .6)
    brick(); concrete(); carpet(); fabric(); knit(); leather(); marble(); tiles(); subway(); brushed(); cardboard(); grass(); rubber(); foam(); tarp(); rugs()
    json.dump(AVG, open(os.path.dirname(os.path.abspath(__file__)) + '/tex_avg.json', 'w'), indent=0)
