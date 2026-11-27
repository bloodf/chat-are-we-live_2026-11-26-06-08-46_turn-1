import { describe, expect, it } from 'vitest';
import { INCIDENTS, INCIDENT, pickIncident } from '../../src/core/incidents';
import { RNG } from '../../src/core/rng';
import { fresh, rich, session, run, inc } from './helpers';
describe('incident catalogue', () => {
  it('has at least 18 unique problems with text, icon and timer', () => { expect(INCIDENTS.length).toBeGreaterThanOrEqual(18); expect(new Set(INCIDENTS.map((i) => i.id)).size).toBe(INCIDENTS.length); for (const i of INCIDENTS) { expect(i.title.length).toBeGreaterThan(3); expect(i.text.length).toBeGreaterThan(10); expect(i.time).toBeGreaterThan(4); expect(INCIDENT[i.id]).toBe(i); } });
  for (const d of INCIDENTS) {
    d.options.forEach((o, k) => { for (const ok of [true, false]) it(`${d.id} → “${o.label}” (${ok ? 'success' : 'fail'})`, () => { for (let seed = 1; seed <= 6; seed++) { const s = rich({ home: 'bedroom', money: 5000 }, seed); s.staff = []; const ss = session(s); ss.startIncident(d); if (d.id !== 'hacked') expect(ss.incident?.def.id).toBe(d.id); run(ss, 1); if (!(o.can?.(ss) ?? true)) { expect(ss.resolveIncident(k, ok)).toBeNull(); expect(ss.incident).not.toBeNull(); return; } const out = ss.resolveIncident(k, ok); expect(out).toBeTruthy(); expect(ss.incident).toBeNull(); expect(ss.hype).toBeGreaterThanOrEqual(0); expect(ss.hype).toBeLessThanOrEqual(100); expect(ss.cringe).toBeLessThanOrEqual(100); expect(ss.tech).toBeGreaterThan(0.5); expect(Number.isFinite(s.money)).toBe(true); } }); });
    it(`${d.id} times out safely`, () => { for (let seed = 1; seed <= 4; seed++) { const ss = session(rich({ home: 'bedroom' }, seed)); ss.startIncident(d); ss.incident!.left = 0.01; ss.step(0.25); if (d.id !== 'muted') expect(ss.incident).toBeNull(); expect(Number.isFinite(ss.viewers)).toBe(true); } });
  }
});
describe('incident scheduling', () => {
  it('the tutorial always opens with Mom', () => { const ss = session(fresh()); expect(pickIncident(ss, new RNG(1))?.id).toBe('mom'); });
  it('does not repeat the same incident back to back', () => { const ss = session(rich()); const r = new RNG(2); const a = pickIncident(ss, r)!; for (let i = 0; i < 12; i++) expect(pickIncident(ss, r)?.id).not.toBe(a.id); });
  it('phones get phone problems, PCs do not', () => { const s = fresh(); s.tutorial = 2; const ph = session(s), pc = session(rich()); expect(inc('battery').weight(ph)).toBeGreaterThan(0); expect(inc('drop').weight(ph)).toBeGreaterThan(0); expect(inc('battery').weight(pc)).toBe(0); expect(inc('drop').weight(pc)).toBe(0); });
  it('better internet means fewer outages', () => { const s = rich(); const a = inc('net').weight(session(s)); s.owned.push({ id: 'net3', cond: 100, broken: false }); s.equipped.net = 'net3'; expect(inc('net').weight(session(s))).toBeLessThan(a); });
  it('they actually fire during play', () => { const ss = session(rich({ home: 'bedroom' })); let n = 0; for (let t = 0; t < 200; t += 0.25) { ss.step(0.25); for (const f of ss.drainFx()) if (f.type === 'incident') n++; if (ss.incident && ss.incident.def.options.length) ss.resolveIncident(ss.incident.def.options.length - 1); if (ss.muted) ss.toggleMute(); } expect(n).toBeGreaterThanOrEqual(2); });
  it('being muted resolves when you unmute', () => { const ss = session(rich()); ss.nextIncident = 1e9; ss.startIncident(inc('muted')); expect(ss.muted).toBe(true); run(ss, 5); expect(ss.incident).not.toBeNull(); ss.toggleMute(); run(ss, 1); expect(ss.incident).toBeNull(); });
  it('a dropped phone can break for good', () => { const s = fresh(); s.tutorial = 2; s.owned[0].cond = 10; const ss = session(s); ss.startIncident(inc('drop')); ss.resolveIncident(0, false); expect(s.owned[0].broken).toBe(true); });
  it('resolving nothing is a no-op', () => { expect(session(rich()).resolveIncident(0)).toBeNull(); });
});
