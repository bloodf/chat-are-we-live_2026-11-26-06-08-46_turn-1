import { RNG, clamp } from './rng';
import { randomTraits, baseline, newBond, appraise, applyMood, decay, contagion, remember, fadeBond, type Mood, type Appraisal } from './emotion';
import { userName, userColor } from './names';
import { CATCHES } from './chat';
import type { GameState, Viewer, ViewerStyle } from './types';
const STYLE_W: Record<ViewerStyle, number> = { wholesome: 16, memer: 24, troll: 10, backseat: 11, simp: 7, critic: 8, kid: 8, lurker: 12, conspiracy: 4, elder: 4 };
const BIAS: Record<ViewerStyle, { o?: number; c?: number; e?: number; a?: number; n?: number }> = { wholesome: { a: 0.8 }, memer: { o: 0.7, e: 0.7 }, troll: { a: 0.2, n: 0.6 }, backseat: { c: 0.7, a: 0.4 }, simp: { n: 0.75, a: 0.7 }, critic: { c: 0.8, o: 0.6 }, kid: { e: 0.8, c: 0.25 }, lurker: { e: 0.2 }, conspiracy: { o: 0.85, n: 0.7 }, elder: { a: 0.7, n: 0.3 } };
export function makeViewer(rng: RNG, day: number, taken: Set<string>, style?: ViewerStyle): Viewer {
  const st = style ?? rng.weighted(Object.keys(STYLE_W) as ViewerStyle[], (s) => STYLE_W[s]);
  const traits = randomTraits(rng, BIAS[st]); const name = userName(rng, taken); taken.add(name);
  return { id: rng.id('v'), name, color: userColor(rng), style: st, traits, mood: baseline(traits), bond: newBond(st === 'troll' ? -8 : st === 'wholesome' || st === 'simp' ? 10 : 2), sub: 0, mod: false, banned: false, timeout: 0, joined: day, spent: 0, msgs: 0, catch: rng.chance(0.4) ? rng.pick(CATCHES) : '' };
}
export const regularCap = (followers: number) => Math.min(48, 6 + Math.floor(Math.log10(followers + 1) * 8));
/** keep the set of named regulars in proportion to the channel size */
export function refreshCommunity(s: GameState, rng: RNG) {
  const taken = new Set(s.viewers.map((v) => v.name));
  s.viewers = s.viewers.filter((v) => v.bond.affinity > -72 || rng.chance(0.5) || v.style === 'troll');
  const cap = regularCap(s.followers);
  let n = 0; while (s.viewers.filter((v) => !v.banned).length < cap && n++ < 12) s.viewers.push(makeViewer(rng, s.day, taken));
  if (s.viewers.length > 80) { s.viewers.sort((a, b) => Math.abs(b.bond.affinity) - Math.abs(a.bond.affinity)); s.viewers.length = 80; }
}
export function feel(v: Viewer, ev: Appraisal, k = 1) { applyMood(v.mood, appraise(v.traits, ev), k); }
export function bondWith(v: Viewer, text: string, w: number, day: number) { remember(v.bond, text, w, day); }
export function tickViewers(vs: Viewer[], crowd: Mood, dt: number) { for (const v of vs) { decay(v.mood, baseline(v.traits), dt, 45); contagion(v.mood, crowd, v.traits, dt); if (v.timeout > 0) v.timeout = Math.max(0, v.timeout - dt); } }
export function nightly(s: GameState, rng: RNG) { for (const v of s.viewers) { fadeBond(v.bond); if (v.sub > 0 && rng.chance(0.02 + (v.bond.affinity < 0 ? 0.1 : 0))) v.sub = 0; } refreshCommunity(s, rng); }
/** who shows up tonight: bond, novelty and habit */
export function attendance(s: GameState, rng: RNG): Viewer[] { return s.viewers.filter((v) => !v.banned && rng.chance(clamp(0.42 + v.bond.affinity / 160 + (v.sub ? 0.2 : 0) + (v.style === 'troll' ? 0.05 : 0), 0.08, 0.95))); }
