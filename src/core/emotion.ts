/**
 * Emotional model shared by every NPC (chat viewers, staff, family).
 * Mood = PAD space (pleasure / arousal / dominance, each -1..1), shaped by Big-Five personality.
 * Events are *appraised* (OCC-style) into PAD impulses, then decay toward a personality baseline.
 */
import { RNG, clamp } from './rng';
export interface Traits { o: number; c: number; e: number; a: number; n: number }
export interface Mood { p: number; a: number; d: number }
export interface Appraisal {
  /** how good (+) or bad (-) this is for the NPC */ good: number;
  /** 0 expected .. 1 out of nowhere */ surprise?: number;
  /** praise (+) / insult (-) directed at the NPC */ praise?: number;
  /** did the player cause it */ blame?: 'player' | 'world' | 'self';
  /** energy injected (hype) */ energy?: number;
  /** sense of control for NPC */ control?: number;
}
export type Emotion = 'ecstatic' | 'happy' | 'amused' | 'hyped' | 'calm' | 'content' | 'bored' | 'sad' | 'anxious' | 'angry' | 'furious' | 'smug' | 'shocked' | 'hurt';
export const EMOTIONS: Emotion[] = ['ecstatic', 'happy', 'amused', 'hyped', 'calm', 'content', 'bored', 'sad', 'anxious', 'angry', 'furious', 'smug', 'shocked', 'hurt'];
const ANCHORS: Record<Emotion, [number, number, number]> = {
  ecstatic: [0.85, 0.75, 0.4], happy: [0.6, 0.25, 0.25], amused: [0.45, 0.4, 0.1], hyped: [0.4, 0.85, 0.35], calm: [0.25, -0.5, 0.2], content: [0.3, -0.1, 0.15], bored: [-0.15, -0.65, -0.05],
  sad: [-0.6, -0.35, -0.4], anxious: [-0.4, 0.5, -0.5], angry: [-0.55, 0.55, 0.35], furious: [-0.85, 0.85, 0.55], smug: [0.35, 0.1, 0.75], shocked: [0.0, 0.85, -0.45], hurt: [-0.75, 0.1, -0.6],
};
export const EMOTION_TONE: Record<Emotion, 'good' | 'mid' | 'bad'> = { ecstatic: 'good', happy: 'good', amused: 'good', hyped: 'good', calm: 'mid', content: 'good', bored: 'mid', sad: 'bad', anxious: 'bad', angry: 'bad', furious: 'bad', smug: 'mid', shocked: 'mid', hurt: 'bad' };

export function randomTraits(rng: RNG, bias: Partial<Traits> = {}): Traits {
  const t = (k: keyof Traits) => clamp(rng.gauss(bias[k] ?? 0.5, 0.17), 0.03, 0.97);
  return { o: t('o'), c: t('c'), e: t('e'), a: t('a'), n: t('n') };
}
export function baseline(t: Traits): Mood {
  return { p: clamp(0.12 + 0.35 * (t.e - 0.5) + 0.35 * (t.a - 0.5) - 0.5 * (t.n - 0.5), -1, 1), a: clamp(0.25 * (t.e - 0.5) + 0.3 * (t.n - 0.5) - 0.05, -1, 1), d: clamp(0.3 * (t.e - 0.5) - 0.35 * (t.n - 0.5) + 0.2 * (t.c - 0.5), -1, 1) };
}
export function appraise(t: Traits, ev: Appraisal): Mood {
  const good = clamp(ev.good, -1, 1), sur = clamp(ev.surprise ?? 0.2), praise = clamp(ev.praise ?? 0, -1, 1), en = clamp(ev.energy ?? 0, -1, 1);
  const neg = good < 0 ? 1 + 0.9 * (t.n - 0.5) : 1 + 0.5 * (t.e - 0.5);
  const touchy = praise < 0 ? 1 + 0.8 * (t.n - 0.5) + 0.4 * (0.5 - t.a) : 1 + 0.4 * (0.5 - t.o);
  const blame = ev.blame === 'player' && good < 0 ? 1.2 - 0.4 * t.a : 1;
  return {
    p: clamp((good * 0.55 * neg * blame + praise * 0.5 * touchy) * (1 + 0.25 * sur), -1, 1),
    a: clamp(Math.abs(good) * 0.3 + sur * 0.35 * (0.6 + 0.8 * t.n) + en * 0.55 + Math.abs(praise) * 0.15, -1, 1),
    d: clamp((ev.control ?? 0) * 0.5 + praise * 0.3 + (good < 0 ? (ev.blame === 'player' ? 0.25 * (1 - t.a) : -0.3 * t.n) : 0.15 * good) - sur * 0.2 * t.n, -1, 1),
  };
}
export function applyMood(m: Mood, d: Mood, k = 1): Mood {
  const f = (v: number, x: number) => clamp(v + x * k * (x > 0 ? 1 - Math.max(0, v) * 0.6 : 1 + Math.min(0, v) * 0.6), -1, 1);
  m.p = f(m.p, d.p); m.a = f(m.a, d.a); m.d = f(m.d, d.d); return m;
}
export function decay(m: Mood, b: Mood, dt: number, halfLife = 40): Mood {
  const k = 1 - Math.pow(0.5, dt / halfLife); m.p += (b.p - m.p) * k; m.a += (b.a - m.a) * Math.min(1, k * 1.8); m.d += (b.d - m.d) * k; return m;
}
export function contagion(m: Mood, crowd: Mood, t: Traits, dt: number): Mood {
  const k = clamp(dt * 0.02 * (0.4 + 0.8 * t.a + 0.5 * t.n)); m.p += (crowd.p - m.p) * k; m.a += (crowd.a - m.a) * k; return m;
}
export function emotionOf(m: Mood): Emotion {
  let best: Emotion = 'content', bd = 1e9;
  for (const e of EMOTIONS) { const A = ANCHORS[e]; const d = (m.p - A[0]) ** 2 * 1.35 + (m.a - A[1]) ** 2 + (m.d - A[2]) ** 2 * 0.6; if (d < bd) { bd = d; best = e; } }
  return best;
}
export function describeTraits(t: Traits): string[] {
  const w: [keyof Traits, string, string][] = [['o', 'imaginative', 'down-to-earth'], ['c', 'meticulous', 'chaotic'], ['e', 'outgoing', 'quiet'], ['a', 'kind', 'blunt'], ['n', 'anxious', 'unshakeable']];
  return w.map(([k, hi, lo]) => ({ s: Math.abs(t[k] - 0.5), w: t[k] > 0.5 ? hi : lo })).sort((x, y) => y.s - x.s).slice(0, 2).map((x) => x.w);
}
/** -100..100 relationship with decaying, human-readable memories. */
export interface Memory { text: string; w: number; day: number }
export interface Bond { affinity: number; trust: number; memories: Memory[] }
export const newBond = (affinity = 0, trust = 0): Bond => ({ affinity, trust, memories: [] });
export function remember(b: Bond, text: string, w: number, day: number) {
  b.affinity = clamp(b.affinity + w, -100, 100); b.trust = clamp(b.trust + w * 0.5, -100, 100);
  b.memories.unshift({ text, w, day }); b.memories.sort((x, y) => Math.abs(y.w) - Math.abs(x.w) || y.day - x.day); if (b.memories.length > 8) b.memories.length = 8;
}
export function fadeBond(b: Bond) { b.affinity *= 0.985; for (const m of b.memories) m.w *= 0.93; b.memories = b.memories.filter((m) => Math.abs(m.w) > 0.8); }
export function bondLabel(a: number): string { return a > 70 ? 'Ride or die' : a > 40 ? 'Big fan' : a > 15 ? 'Likes you' : a > -15 ? 'Neutral' : a > -40 ? 'Annoyed' : a > -70 ? 'Dislikes you' : 'Nemesis'; }
