import { RNG, clamp } from './rng';
import { newBond, baseline } from './emotion';
import { ITEM, HOME, GAMES, GAME } from './catalog';
import { GAME_RIVALS } from './names';
import { refreshCommunity } from './viewers';
import type { GameState, Note, SlotId, Skill } from './types';
export const SAVE_VERSION = 1;
export function newState(o: { name?: string; channel?: string; body?: string; seed?: number; difficulty?: GameState['difficulty'] } = {}): GameState {
  const seed = o.seed ?? Math.floor(Math.random() * 2 ** 31); const rng = new RNG(seed); const diff = o.difficulty ?? 'normal';
  const s: GameState = {
    v: SAVE_VERSION, seed, rng: seed, name: o.name ?? 'Max', channel: o.channel ?? 'MaxPlays', body: o.body ?? 'p_max', difficulty: diff, day: 1, min: 16 * 60, money: diff === 'chill' ? 120 : 45, debt: 0, followers: 0, subs: 0, peakFollowers: 0,
    energy: 90, food: 80, vibe: 75, rep: 50, drama: 0, burnout: 0, skills: { charisma: 1, gaming: 1, editing: 1, tech: 1, business: 1 }, home: 'bedroom',
    owned: [{ id: 'phone0', cond: 62, broken: false }, { id: 'net0', cond: 100, broken: false }, { id: 'chair0', cond: 90, broken: false }], equipped: { device: 'phone0', net: 'net0', chair: 'chair0' },
    viewers: [], staff: [], candidates: [], clips: [], videos: [], sponsors: [], notes: [], posts: [], logs: [], goals: [], flags: {}, gameFatigue: {}, trend: {}, best: {},
    rivals: GAME_RIVALS.map((r) => ({ ...r, heat: 0 })), streak: 0, lastStreamDay: 0, streamsToday: 0, headline: 'Local person considers streaming. Nation unmoved.', algo: 1, chapter: 1, ended: false, momBond: newBond(55, 60), momMood: baseline({ o: 0.5, c: 0.7, e: 0.6, a: 0.85, n: 0.55 }), stats: {}, tutorial: 0,
  };
  for (const g of GAMES) s.trend[g.id] = clamp(rng.gauss(1, 0.18), 0.65, 1.45);
  refreshCommunity(s, rng); s.rng = rng.s; return s;
}
export function withRng<T>(s: GameState, f: (r: RNG) => T): T { const r = new RNG(s.rng); const v = f(r); s.rng = r.s; return v; }
export const stat = (s: GameState, k: string, d = 1) => { s.stats[k] = (s.stats[k] ?? 0) + d; };
export function note(s: GameState, from: string, text: string, kind: Note['kind'] = 'msg') { s.notes.unshift({ id: `n${s.day}_${s.min | 0}_${s.notes.length}_${(s.stats.notes = (s.stats.notes ?? 0) + 1)}`, day: s.day, min: s.min | 0, from, text, kind, read: false }); if (s.notes.length > 60) s.notes.length = 60; }
export const ownedItem = (s: GameState, id: string) => s.owned.find((i) => i.id === id);
export const equippedItem = (s: GameState, slot: SlotId) => { const id = s.equipped[slot]; return id ? ITEM[id] : undefined; };
export const device = (s: GameState) => ITEM[s.equipped.device ?? 'phone0'];
export const deviceState = (s: GameState) => ownedItem(s, s.equipped.device ?? 'phone0')!;
/** overall production quality 0.2..3.6 */
export function quality(s: GameState): number {
  const dev = device(s); const ds = deviceState(s);
  let q = dev.q * (ds?.broken ? 0.25 : 0.62 + 0.38 * clamp((ds?.cond ?? 100) / 70));
  for (const slot of ['mic', 'cam', 'light', 'chair', 'net', 'led', 'decor1', 'decor2'] as SlotId[]) { const it = equippedItem(s, slot); if (it && !ownedItem(s, it.id)?.broken) q += it.q; }
  q += HOME[s.home].q; q += Math.min(0.3, s.skills.tech * 0.02);
  for (const st of s.staff) if (st.role === 'camera') q += 0.1 + 0.15 * st.skill * (0.5 + st.morale / 200);
  return clamp(q, 0.15, 3.6);
}
export function canPlay(s: GameState, gid: string): boolean { const g = GAME[gid]; if (!g || s.followers < g.unlock) return false; if (g.need === 'none') return true; return !!device(s).caps?.includes(g.need) && !deviceState(s)?.broken; }
export const skillUp = (s: GameState, k: Skill, xp: number) => { const before = Math.floor(s.skills[k]); s.skills[k] = Math.min(20, s.skills[k] + xp / (1 + s.skills[k] * 0.55)); return Math.floor(s.skills[k]) > before; };
export function earn(s: GameState, amt: number, why: string) { s.money += amt; if (amt > 0) { stat(s, 'earned', amt); stat(s, 'earn_' + why, amt); } else stat(s, 'spent', -amt); }
export function gainFollowers(s: GameState, n: number) { s.followers = Math.max(0, s.followers + Math.round(n)); s.peakFollowers = Math.max(s.peakFollowers, s.followers); }
export const timeStr = (min: number) => { const m = ((Math.floor(min) % 1440) + 1440) % 1440; const h = Math.floor(m / 60); const mm = m % 60; return `${((h + 11) % 12) + 1}:${String(mm).padStart(2, '0')} ${h < 12 ? 'AM' : 'PM'}`; };
export const WEEK = ['Moanday', 'Chewsday', 'Wenesdayish', 'Thirstday', 'Friyay', 'Caturday', 'Sunyay'];
export const weekday = (day: number) => WEEK[(day - 1) % 7];
/** audience availability through the day (peaks in evening, more on weekends) */
export function primeTime(s: GameState): number { const h = (s.min / 60) % 24; const eve = Math.exp(-((h - 20.5) ** 2) / 18); const late = Math.exp(-((h - 0.5) ** 2) / 6) * 0.4; const we = (s.day - 1) % 7 >= 4 ? 1.12 : 1; return clamp((0.62 + 0.55 * eve + late) * we, 0.5, 1.35); }
export function serialize(s: GameState): string { return JSON.stringify(s); }
export function deserialize(j: string): GameState | null { try { const o = JSON.parse(j); if (!o || typeof o !== 'object' || o.v !== SAVE_VERSION || !Array.isArray(o.owned) || typeof o.followers !== 'number') return null; return { ...newState({ seed: o.seed }), ...o }; } catch { return null; } }
