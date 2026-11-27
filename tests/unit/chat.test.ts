import { describe, expect, it } from 'vitest';
import { RNG } from '../../src/core/rng';
import { EMOTES, PROMPT_KINDS, fill, idleLine, promptLine, reactLine, reactToStreamer, pronouns, replyToSpeech, styleText, type Ctx } from '../../src/core/chat';
import { makeViewer } from '../../src/core/viewers';
import { understand } from '../../src/core/nlu';
import { humanName, userName, userColor, GAME_RIVALS } from '../../src/core/names';
import type { Reaction, ViewerStyle } from '../../src/core/types';
const ctx: Ctx = { game: 'Flappy Nerd', verb: 'flapping', mood: { p: 0, a: 0, d: 0 }, hype: 40, viewers: 12, name: 'Max', min: 5, quality: 1, homeTitle: 'bedroom' };
const styles: ViewerStyle[] = ['wholesome', 'memer', 'troll', 'backseat', 'simp', 'critic', 'kid', 'lurker', 'conspiracy', 'elder'];
const noHoles = (t: string) => { expect(t.length).toBeGreaterThan(0); expect(t).not.toMatch(/\{[a-z]+\}/i); expect(t).not.toMatch(/undefined|NaN|\[object/); for (const m of t.matchAll(/:([a-zA-Z]+):/g)) expect(EMOTES as readonly string[]).toContain(m[1]); };
describe('chat text', () => {
  it('never leaves template holes in any style, mood or context', () => { const r = new RNG(1); for (const st of styles) for (let i = 0; i < 120; i++) { const v = makeViewer(r, 1, new Set(), st); v.mood = { p: r.range(-1, 1), a: r.range(-1, 1), d: r.range(-1, 1) }; noHoles(idleLine(r, v, { ...ctx, hype: r.range(0, 100), muted: r.chance(0.1), cracked: r.chance(0.3), afk: r.chance(0.1), quality: r.chance(0.1) ? 0.3 : 1 })); } });
  it('anonymous lurkers also make sense', () => { const r = new RNG(2); for (let i = 0; i < 200; i++) noHoles(idleLine(r, null, ctx)); });
  it('complains when muted', () => { const r = new RNG(3); let n = 0; for (let i = 0; i < 200; i++) if (/mute|mic|hear|silent|lip/i.test(idleLine(r, null, { ...ctx, muted: true }))) n++; expect(n).toBeGreaterThan(110); });
  it('prompts exist for every kind', () => { const r = new RNG(4); for (const k of PROMPT_KINDS) for (let i = 0; i < 30; i++) noHoles(promptLine(r, k, ctx)); });
  it('reacts to events and to the streamer', () => { const r = new RNG(5); for (const k of ['fail', 'clutch', 'combo', 'record', 'scare', 'win', 'bored', 'afk', 'mute', 'lag', 'crack', 'unknown']) noHoles(reactLine(r, k)); for (const k of ['laugh', 'hype', 'rage', 'cry', 'shock', 'dance'] as Reaction[]) { noHoles(reactToStreamer(r, k, true)); noHoles(reactToStreamer(r, k, false)); } });
  it('answers anything the player says', () => { const r = new RNG(6); const v = makeViewer(r, 1, new Set(), 'memer'); for (const t of ['hi', 'thanks', 'follow me', 'what is love?', 'lol joke', 'LETS GO', 'you suck', 'sorry', 'im sad', 'love you', 'i promise a giveaway', 'i am the goat', 'bye', 'believe', 'unpopular opinion cereal', 'la la la song', 'vote', 'use code CHAT', 'once yesterday a story happened', 'zxcvbnmqw', 'the boss game level', 'plain words']) for (const g of [-0.6, 0.6]) { noHoles(replyToSpeech(r, understand(t), v, g)); noHoles(replyToSpeech(r, understand(t), null, g)); } });
  it('styles shouty kids and keeps emote codes intact when upper-casing', () => { const r = new RNG(7); const k = makeViewer(r, 1, new Set(), 'kid'); k.mood = { p: 0.9, a: 0.9, d: 0.4 }; for (let i = 0; i < 100; i++) noHoles(styleText(r, k, 'nice :catjam: ok :monkaS:')); });
  it('fill substitutes every token', () => { const r = new RNG(8); noHoles(fill(r, '{n} {m} {home} {v} {gear} {rival}', ctx)); });
});
describe('pronouns', () => {
  it('follow the chosen body and keep case', () => { expect(pronouns('HE’S HIM, let him cook, the king returns, his aim', 'p_zoe')).toBe('SHE’S HER, let her cook, the queen returns, her aim'); expect(pronouns('He is here', 'p_mei')).toBe('She is here'); expect(pronouns('HE’S HIM', 'p_max')).toBe('HE’S HIM'); expect(pronouns('the cheese is here', 'p_ivy')).toBe('the cheese is here'); });
});
describe('names', () => {
  it('user names are unique when told what is taken', () => { const r = new RNG(9); const t = new Set<string>(); for (let i = 0; i < 900; i++) { const n = userName(r, t); expect(t.has(n)).toBe(false); expect(n).toMatch(/^[\w]+$/); t.add(n); } });
  it('human names avoid collisions', () => { const r = new RNG(10); const t = new Set<string>(); for (let i = 0; i < 300; i++) t.add(humanName(r, i % 2 ? 'f' : 'm', t)); expect(t.size).toBeGreaterThan(290); });
  it('colours are valid hex and rivals are ordered jokes', () => { const r = new RNG(1); for (let i = 0; i < 30; i++) expect(userColor(r)).toMatch(/^#[0-9a-f]{6}$/); expect(GAME_RIVALS[0].followers).toBe(Math.max(...GAME_RIVALS.map((x) => x.followers))); });
});
