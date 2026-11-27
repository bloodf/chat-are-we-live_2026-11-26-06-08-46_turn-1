import { newState } from '../../src/core/sim';
import { StreamSession } from '../../src/core/stream';
import { INCIDENTS } from '../../src/core/incidents';
import type { GameState, HomeId } from '../../src/core/types';
export const rich = (over: Partial<GameState> = {}, seed = 5): GameState => { const s = newState({ seed }); s.tutorial = 3; s.followers = 50000; s.money = 1e6; s.subs = 400; s.home = 'hq'; s.chapter = 4; s.owned.push({ id: 'pc1', cond: 90, broken: false }, { id: 'mic2', cond: 100, broken: false }); s.equipped.device = 'pc1'; s.equipped.mic = 'mic2'; return Object.assign(s, over); };
export const fresh = (seed = 1) => newState({ seed, name: 'Tess', channel: 'TessTests' });
export const session = (s: GameState, game = 'flappy') => new StreamSession(s, game, 'test');
export const run = (ss: StreamSession, sec: number, dt = 0.25) => { for (let t = 0; t < sec && !ss.ended; t += dt) ss.step(dt); };
export const quiet = (ss: StreamSession) => { ss.nextIncident = 1e9; return ss; };
export const inc = (id: string) => INCIDENTS.find((i) => i.id === id)!;
export const HOMES: HomeId[] = ['bedroom', 'studio', 'loft', 'hq', 'mansion'];
/** a canvas context that accepts every call, so draw() code can be exercised in node */
export function stubCtx(): any { const calls: Record<string, number> = {}; const grad = { addColorStop() {} }; return new Proxy({ __calls: calls } as any, { get(t, k: string) { if (k === '__calls') return calls; if (k === 'measureText') return (s: string) => ({ width: s.length * 8 }); if (k.startsWith?.('create')) return () => grad; if (k in t) return t[k]; return (...a: any[]) => { calls[k] = (calls[k] ?? 0) + 1; for (const v of a) if (typeof v === 'number' && Number.isNaN(v)) throw new Error(`NaN passed to ${k}`); }; }, set(t, k, v) { t[k as any] = v; return true; } }); }
