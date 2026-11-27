import { describe, expect, it } from 'vitest';
import { RNG } from '../../src/core/rng';
import { EMOTIONS, EMOTION_TONE, applyMood, appraise, baseline, bondLabel, contagion, decay, describeTraits, emotionOf, fadeBond, newBond, randomTraits, remember, type Traits } from '../../src/core/emotion';
const mid: Traits = { o: 0.5, c: 0.5, e: 0.5, a: 0.5, n: 0.5 };
describe('personality', () => {
  it('random traits stay in range and follow bias', () => { const r = new RNG(1); let a = 0; for (let i = 0; i < 400; i++) { const t = randomTraits(r, { a: 0.85 }); for (const v of Object.values(t)) { expect(v).toBeGreaterThanOrEqual(0.03); expect(v).toBeLessThanOrEqual(0.97); } a += t.a; } expect(a / 400).toBeGreaterThan(0.75); });
  it('neurotic people have a worse baseline than stable ones', () => { expect(baseline({ ...mid, n: 0.9 }).p).toBeLessThan(baseline({ ...mid, n: 0.1 }).p); });
  it('extraverts are more energetic at rest', () => { expect(baseline({ ...mid, e: 0.9 }).a).toBeGreaterThan(baseline({ ...mid, e: 0.1 }).a); });
  it('describes people by their two strongest traits', () => { expect(describeTraits({ o: 0.95, c: 0.5, e: 0.05, a: 0.5, n: 0.5 }).sort()).toEqual(['imaginative', 'quiet']); });
});
describe('appraisal', () => {
  it('good news raises pleasure, bad news lowers it', () => { expect(appraise(mid, { good: 0.8 }).p).toBeGreaterThan(0); expect(appraise(mid, { good: -0.8 }).p).toBeLessThan(0); });
  it('neuroticism amplifies bad events', () => { expect(appraise({ ...mid, n: 0.95 }, { good: -0.6 }).p).toBeLessThan(appraise({ ...mid, n: 0.05 }, { good: -0.6 }).p); });
  it('insults hurt touchy people more', () => { expect(appraise({ ...mid, n: 0.9, a: 0.2 }, { good: 0, praise: -0.8 }).p).toBeLessThan(appraise({ ...mid, n: 0.1, a: 0.9 }, { good: 0, praise: -0.8 }).p); });
  it('disagreeable people get dominant (angry) when you are to blame; anxious ones shrink when the world is', () => { const angry = appraise({ ...mid, a: 0.05 }, { good: -0.8, blame: 'player' }); const scared = appraise({ ...mid, n: 0.95 }, { good: -0.8, blame: 'world' }); expect(angry.d).toBeGreaterThan(scared.d); });
  it('surprise and energy raise arousal', () => { expect(appraise(mid, { good: 0, surprise: 1 }).a).toBeGreaterThan(appraise(mid, { good: 0, surprise: 0 }).a); expect(appraise(mid, { good: 0, energy: 1 }).a).toBeGreaterThan(0.3); });
  it('outputs are always bounded', () => { const r = new RNG(2); for (let i = 0; i < 500; i++) { const d = appraise(randomTraits(r), { good: r.range(-3, 3), praise: r.range(-3, 3), energy: r.range(-3, 3), surprise: r.range(-1, 3), control: r.range(-2, 2), blame: r.pick(['player', 'world', 'self'] as const) }); for (const v of Object.values(d)) expect(Math.abs(v)).toBeLessThanOrEqual(1); } });
});
describe('mood dynamics', () => {
  it('never leaves the PAD cube under stress', () => { const m = { p: 0, a: 0, d: 0 }; for (let i = 0; i < 200; i++) applyMood(m, { p: 1, a: 1, d: -1 }); for (const v of Object.values(m)) expect(Math.abs(v)).toBeLessThanOrEqual(1); });
  it('decays back to the baseline', () => { const b = baseline(mid); const m = { p: -1, a: 1, d: -1 }; for (let i = 0; i < 100; i++) decay(m, b, 20); expect(m.p).toBeCloseTo(b.p, 1); expect(m.a).toBeCloseTo(b.a, 1); expect(m.d).toBeCloseTo(b.d, 1); });
  it('catches the crowd mood, agreeable people faster', () => { const x = { p: 0, a: 0, d: 0 }, y = { p: 0, a: 0, d: 0 }; for (let i = 0; i < 20; i++) { contagion(x, { p: 1, a: 1, d: 0 }, { ...mid, a: 0.95, n: 0.9 }, 1); contagion(y, { p: 1, a: 1, d: 0 }, { ...mid, a: 0.05, n: 0.1 }, 1); } expect(x.p).toBeGreaterThan(y.p); expect(y.p).toBeGreaterThan(0); });
  it.each([[{ p: 0.9, a: 0.8, d: 0.4 }, 'ecstatic'], [{ p: -0.85, a: 0.85, d: 0.55 }, 'furious'], [{ p: -0.6, a: -0.35, d: -0.4 }, 'sad'], [{ p: -0.15, a: -0.65, d: 0 }, 'bored'], [{ p: 0.35, a: 0.1, d: 0.75 }, 'smug'], [{ p: 0, a: 0.85, d: -0.45 }, 'shocked']])('classifies %o as %s', (m, e) => expect(emotionOf(m as any)).toBe(e));
  it('every emotion has a tone and every label is reachable', () => { const seen = new Set<string>(); for (let p = -1; p <= 1; p += 0.1) for (let a = -1; a <= 1; a += 0.1) for (let d = -1; d <= 1; d += 0.2) seen.add(emotionOf({ p, a, d })); for (const e of EMOTIONS) { expect(EMOTION_TONE[e]).toBeTruthy(); expect(seen.has(e)).toBe(true); } });
});
describe('bonds and memory', () => {
  it('remembers, sorts by weight and caps the list', () => { const b = newBond(); for (let i = 1; i <= 14; i++) remember(b, 'm' + i, i, 1); expect(b.memories).toHaveLength(8); expect(b.memories[0].text).toBe('m14'); expect(b.affinity).toBe(100); });
  it('affinity is clamped both ways', () => { const b = newBond(); remember(b, 'x', -500, 1); expect(b.affinity).toBe(-100); });
  it('fades and forgets small things', () => { const b = newBond(20); remember(b, 'tiny', 1, 1); remember(b, 'huge', 40, 1); for (let i = 0; i < 8; i++) fadeBond(b); expect(b.memories.map((m) => m.text)).toEqual(['huge']); });
  it('labels cover the range', () => { expect(new Set([90, 50, 20, 0, -30, -50, -90].map(bondLabel)).size).toBe(7); });
});
