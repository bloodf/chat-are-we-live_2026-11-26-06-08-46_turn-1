import { describe, expect, it } from 'vitest';
import { RNG } from '../../src/core/rng';
import { botDay, botStream } from '../../src/core/sim';
import { newState, serialize } from '../../src/core/state';
const play = (seed: number, skill: number, days: number) => { const s = newState({ seed }); const r = new RNG(seed); const hist: { d: number; f: number; home: string; m: number }[] = []; for (let d = 1; d <= days && !s.ended; d++) { botDay(s, skill, r, 1); hist.push({ d, f: s.followers, home: s.home, m: s.money }); expect(Number.isFinite(s.money + s.followers + s.subs + s.energy + s.rep + s.drama)).toBe(true); } return { s, hist }; };
describe('the whole arc', () => {
  it('day one feels small but not hopeless', () => { let f = 0; for (let i = 1; i <= 8; i++) f += play(i, 0.6, 1).s.followers; expect(f / 8).toBeGreaterThan(4); expect(f / 8).toBeLessThan(60); });
  it.each([[1, 0.7], [2, 0.45], [3, 0.9]])('seed %s skill %s reaches every home and beats Mr. Feast in a sane number of days', (seed, skill) => { const { s, hist } = play(seed, skill, 75); expect(s.ended).toBe(true); const first = (h: string) => hist.find((x) => x.home === h)?.d ?? 999; expect(first('studio')).toBeGreaterThan(3); expect(first('loft')).toBeGreaterThan(first('studio')); expect(hist.length).toBeGreaterThan(18); expect(hist.length).toBeLessThan(75); });
  it('skilled players progress faster than sloppy ones', () => { let a = 0, b = 0; for (let i = 1; i <= 4; i++) { a += Math.log(1 + play(i + 10, 0.9, 10).s.followers); b += Math.log(1 + play(i + 10, 0.25, 10).s.followers); } expect(a).toBeGreaterThan(b); });
  it('nobody goes irrecoverably bankrupt', () => { for (let i = 1; i <= 4; i++) { const { hist } = play(i + 30, 0.4, 20); expect(Math.min(...hist.map((h) => h.m))).toBeGreaterThan(-5000); } });
  it('simulation is deterministic end to end', () => { expect(serialize(play(9, 0.6, 6).s)).toBe(serialize(play(9, 0.6, 6).s)); });
  it('a single bot stream produces a log', () => { const s = newState({ seed: 3 }); const ss = botStream(s, 'flappy', 60, 0.7, new RNG(3)); expect(ss.ended).toBe(true); expect(s.logs).toHaveLength(1); });
});
