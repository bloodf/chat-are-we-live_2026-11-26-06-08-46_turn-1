/** A live broadcast. Real seconds = stream minutes. Drives audience, chat NPCs, prompts, incidents, money. */
import { RNG, clamp, countFor, lerp } from './rng';
import { GAME, SPONSORS } from './catalog';
import { appraise, applyMood, emotionOf, type Mood, type Emotion } from './emotion';
import { idleLine, reactLine, reactToStreamer, promptLine, replyToSpeech, PROMPT_KINDS, EMOTES, pronouns, type ChatMsg, type ChatKind, type PromptKind, type Ctx } from './chat';
import { understand, type Speech } from './nlu';
import { attendance, bondWith, feel, makeViewer, tickViewers } from './viewers';
import { canPlay, deviceState, device, earn, equippedItem, gainFollowers, note, ownedItem, primeTime, quality, skillUp, stat } from './state';
import { userName, userColor } from './names';
import type { GameState, Reaction, Tone, Viewer, StreamLog } from './types';
import { pickIncident, type Incident, INCIDENTS } from './incidents';

export type GameEvent = 'fail' | 'clutch' | 'combo' | 'record' | 'scare' | 'win' | 'score';
export const EXPECT: Record<GameEvent, Reaction[]> = { fail: ['rage', 'laugh', 'cry'], clutch: ['hype', 'shock'], combo: ['hype', 'dance'], record: ['hype', 'dance', 'shock'], scare: ['shock', 'cry'], win: ['dance', 'hype', 'laugh'], score: [] };
export type StreamFx = { type: 'react' | 'alert' | 'follow' | 'sub' | 'dono' | 'raid' | 'incident' | 'resolved' | 'prompt' | 'clip' | 'speak' | 'level' | 'end' | 'goal' | 'poll' | 'miss'; text?: string; amount?: number; who?: string; reaction?: Reaction; ok?: boolean; id?: string; good?: number };
export interface ActiveIncident { def: Incident; left: number; taken?: boolean }
export interface Poll { q: string; opts: string[]; votes: number[]; left: number; kind: 'poll' | 'predict' }
const CONV = 0.0115;
export const baseViewers = (f: number) => 6.5 + 0.4 * Math.pow(f, 0.72);
export const SEGMENTS = {
  qna: { name: 'Q&A', cd: 45, min: 0, tip: 'Opens the floodgates: lots of questions' },
  poll: { name: 'Poll', cd: 40, min: 0, tip: 'Let chat decide something pointless' },
  challenge: { name: 'Dare me', cd: 60, min: 30, tip: 'Risky dare. Nail your next moment.' },
  giveaway: { name: 'Giveaway', cd: 90, min: 100, tip: 'Costs money, buys love' },
  subgoal: { name: 'Sub goal', cd: 90, min: 150, tip: 'Rally chat to a sub target' },
  raid: { name: 'Raid out', cd: 9999, min: 50, tip: 'End by sending viewers to a friend' },
} as const;
export type SegmentId = keyof typeof SEGMENTS;
export const GAMEABLE = (gid: string) => gid !== 'chat';

export class StreamSession {
  t = 0; viewers: number; peak = 0; sumViewers = 0; hype = 32; cringe = 0; crowd: Mood = { p: 0.15, a: 0.1, d: 0 };
  chat: ChatMsg[] = []; fx: StreamFx[] = []; present: Viewer[]; newFollowers = 0; newSubs = 0; earned = 0; ended = false; endReason = '';
  incident: ActiveIncident | null = null; nextIncident: number; window: { ev: GameEvent; left: number; from: number } | null = null; combo = 0; bestMoment = { heat: 0, text: 'Starting soon screen' };
  poll: Poll | null = null; segCd: Partial<Record<SegmentId, number>> = {}; dare: { text: string; left: number; need: GameEvent[] } | null = null; subGoal: { target: number; got: number; left: number } | null = null;
  muted = false; mutedFor = 0; tech = 1; afk = 0; speechLog: string[] = []; lastSpeak = 0; silence = 0; said = ''; sponsorRead = 0; lastReact: Partial<Record<Reaction, number>> = {}; handled = 0; missed = 0; modsActive: number; repeated = 0;
  private fAgg = 0; private fT = 0; private subQ = 0; private subT = 0; private msgAcc = 0; private promptAcc = 6; private id = 1; private followAcc = 0; private seen = 0; private donoAcc = 0; private names: Set<string>; rng: RNG; title: string; sentBurst = 0; lastClip = -99; hypeTrain = 0; raidIn = 0; private novelty: number; trained = false;
  constructor(public s: GameState, public game: string, title = '') {
    this.rng = new RNG(s.rng ^ 0x9e3779b9); this.title = title || autoTitle(this.rng, s, game);
    this.present = attendance(s, this.rng); this.viewers = Math.max(1, baseViewers(s.followers) * 0.3); this.names = new Set(s.viewers.map((v) => v.name));
    this.nextIncident = s.tutorial < 1 ? 70 : this.rng.range(34, 58); this.modsActive = s.staff.filter((x) => x.role === 'mod').length;
    this.novelty = 1.12 - Math.min(0.5, (s.gameFatigue[game] ?? 0) * 0.09);
    this.push('system', '', `LIVE: ${this.title}`); s.streamsToday++;
    for (const v of this.present.slice(0, 3)) this.say(v, v.bond.affinity > 30 ? this.rng.pick(['FIRST', 'finally!!', 'missed you', 'the king returns']) : this.rng.pick(['first', 'o/', 'hi', 'oh you’re live']));
  }
  // ------------------------------------------------------------ helpers
  get minutes() { return this.t; }
  get quality() { return clamp(quality(this.s) * this.tech * (this.muted ? 0.55 : 1), 0.08, 4); }
  get charisma() { return this.s.skills.charisma; }
  ctx(): Ctx { const ds = deviceState(this.s); return { game: GAME[this.game].name, verb: GAME[this.game].verb, mood: this.crowd, hype: this.hype, viewers: this.viewers, name: this.s.name, min: this.t, quality: this.tech < 0.7 ? 0.3 : 1, homeTitle: this.s.home, muted: this.muted, cracked: !!ds && ds.cond < 45 && device(this.s).caps?.length === 1, afk: this.afk > 9 }; }
  push(kind: ChatKind, who: string, text: string, o: Partial<ChatMsg> = {}) { const m: ChatMsg = { id: this.id++, kind, who, color: o.color ?? '#d8cfbd', text: kind === 'msg' || kind === 'system' ? pronouns(text, this.s.body) : text, badges: o.badges ?? [], t: this.t, ...o }; this.chat.push(m); if (this.chat.length > 90) this.chat.splice(0, this.chat.length - 90); return m; }
  say(v: Viewer, text: string, o: Partial<ChatMsg> = {}) { if (v.timeout > 0 || v.banned) return null; v.msgs++; const b: string[] = []; if (v.mod) b.push('mod'); if (v.sub) b.push('sub'); if (v.spent > 50) b.push('gem'); if (this.s.day - v.joined > 6) b.push('og'); return this.push('msg', v.name, text, { color: v.color, vid: v.id, emo: emotionOf(v.mood), badges: b, ...o }); }
  anon(text: string, o: Partial<ChatMsg> = {}) { return this.push('msg', userName(this.rng), text, { color: userColor(this.rng), ...o }); }
  chatter(key: string, n: number) { for (let i = 0; i < n; i++) { const v = this.present.length && this.rng.chance(0.55) ? this.rng.pick(this.present) : null; const t = reactLine(this.rng, key, v); v ? this.say(v, t) : this.anon(t); } }
  mood(ev: Parameters<typeof appraise>[1], k = 1) { applyMood(this.crowd, appraise({ o: 0.5, c: 0.5, e: 0.55, a: 0.5, n: 0.5 }, ev), k * 0.55); for (const v of this.present) feel(v, ev, k * 0.7); }
  addHype(n: number) { this.hype = clamp(this.hype + (n > 0 ? n * (1 + this.s.skills.charisma * 0.012) * (1 - this.hype / 138) * (this.hypeTrain > 0 ? 1.5 : 1) : n), 0, 100); }
  burst() { return clamp(Math.round(1 + Math.sqrt(this.viewers) * 0.22), 1, 7); }
  // ------------------------------------------------------------ step
  step(dt: number) {
    if (this.ended) return; dt = Math.min(dt, 0.5); const s = this.s; this.t += dt; const r = this.rng;
    // --- audience
    const staleness = clamp(1.15 - this.t / 420, 0.55, 1.1); const hypeMul = 0.45 + (this.hype / 50) * 0.72; const silencePen = this.silence > 22 ? clamp(1 - (this.silence - 22) / 90, 0.6, 1) : 1;
    const target = baseViewers(s.followers) * (0.62 + 0.36 * Math.min(2.4, this.quality)) * (s.trend[this.game] ?? 1) * this.novelty * primeTime(s) * hypeMul * staleness * s.algo * (1 - this.cringe / 190) * (0.75 + s.rep / 200) * silencePen * (1 - s.drama / 320) + this.raidIn;
    this.raidIn *= Math.pow(0.985, dt); const k = target > this.viewers ? 0.055 : 0.04; this.viewers = Math.max(0, this.viewers + (target - this.viewers) * Math.min(1, k * dt)); this.peak = Math.max(this.peak, this.viewers); this.sumViewers += this.viewers * dt;
    // --- decay
    this.hype = clamp(this.hype - dt * (0.5 + this.hype * 0.021) * (this.hypeTrain > 0 ? 0.45 : 1), 0, 100); this.hypeTrainTick(dt); this.cringe = clamp(this.cringe - dt * 0.4, 0, 100);
    this.crowd.p += (0.08 + (this.hype - 40) / 160 - this.crowd.p) * dt * 0.012; this.crowd.a += ((this.hype - 35) / 90 - this.crowd.a) * dt * 0.03; tickViewers(this.present, this.crowd, dt);
    this.silence += dt; if (this.game === 'chat') { if (this.silence > 14) this.addHype(-dt * 0.5); }
    if (this.muted) { this.mutedFor += dt; if (this.mutedFor > 6) this.addHype(-dt * 0.9); }
    // --- follows
    const perf = Math.pow(clamp(this.hype / 55, 0.08, 1.7), 1.25) * clamp(0.62 + 0.26 * this.quality, 0.4, 1.6) * (1 - this.cringe / 140) * (0.55 + s.rep / 110);
    const diff = s.difficulty === 'chill' ? 1.45 : s.difficulty === 'grind' ? 0.72 : 1; const disc = CONV * Math.pow(1 + s.followers, 0.062);
    this.followAcc += (0.026 * perf + this.viewers * disc * perf) * (1 / (1 + s.followers / 3.2e8)) * diff * dt; const nf = Math.floor(this.followAcc); this.fT -= dt;
    if (nf > 0) { this.followAcc -= nf; gainFollowers(s, nf); this.newFollowers += nf; this.fAgg += nf; if (this.fT <= 0) { this.fx.push({ type: 'follow', amount: this.fAgg, who: userName(r) }); this.fAgg = 0; this.fT = 0.7; } if (nf < 6 && r.chance(0.5)) this.push('follow', userName(r), 'followed', { color: '#17b5c4' }); }
    // --- subs & donations
    const love = clamp(0.4 + this.crowd.p * 0.8 + this.hype / 160, 0.1, 1.6); const subRate = Math.pow(this.viewers, 0.92) * 0.0011 * love * (s.followers >= 50 ? 1 : 0) * (this.subGoal ? 2.2 : 1);
    const ns = countFor(r, subRate * dt); this.subQ += ns; this.subT -= dt; if (this.subQ > 0 && this.subT <= 0) { this.sub(this.subQ); this.subT = this.subQ > 3 ? 2.2 : 0.9; this.subQ = 0; }
    this.donoAcc += Math.pow(this.viewers + 1, 0.4) * 0.0085 * love * (this.cringe > 55 ? 0.4 : 1) * dt; if (this.donoAcc > 1 && r.chance(0.6)) { this.donoAcc -= 1; this.donate(); }
    // --- chat
    const rate = clamp(0.16 + 0.2 * Math.pow(this.viewers, 0.42) * (0.6 + this.hype / 70), 0.12, 4.2); this.msgAcc += rate * dt;
    while (this.msgAcc >= 1) { this.msgAcc -= 1; const pool = this.present.filter((v) => v.timeout <= 0 && !v.banned); const v = pool.length && r.chance(clamp(pool.length / (this.viewers * 0.35 + 4), 0.25, 0.85)) ? r.weighted(pool, (x) => 0.3 + x.traits.e + (x.style === 'lurker' ? -0.4 : 0)) : null; const line = idleLine(r, v, this.ctx()); v ? this.say(v, line) : this.anon(line); }
    // --- prompts
    this.promptAcc -= dt; if (this.promptAcc <= 0) { this.promptAcc = clamp(11 - Math.log10(this.viewers + 1) * 1.6, 4.2, 12) * r.range(0.7, 1.35) * (this.game === 'chat' ? 0.6 : 1); this.spawnPrompt(); }
    for (const m of this.chat) if (m.prompt && !m.prompt.done && this.t > m.prompt.expires) this.expirePrompt(m);
    // --- reaction window
    if (this.window) { this.window.left -= dt; if (this.window.left <= 0) { if (this.window.ev !== 'combo' && this.window.ev !== 'score') { this.addHype(-1.5); this.combo = 0; this.fx.push({ type: 'miss' }); } this.window = null; } }
    // --- incidents
    if (this.incident) { this.incident.left -= dt; const d = this.incident.def; if (d.tick) d.tick(this, dt); if (this.incident && this.incident.left <= 0) this.resolveIncident(-1); }
    else if (this.t > this.nextIncident) { const inc = pickIncident(this, r); this.nextIncident = this.t + r.range(38, 66) * (s.difficulty === 'grind' ? 0.8 : 1); if (inc) this.startIncident(inc); }
    // --- segments
    for (const kk of Object.keys(this.segCd) as SegmentId[]) this.segCd[kk] = Math.max(0, (this.segCd[kk] ?? 0) - dt);
    if (this.poll) { this.poll.left -= dt; if (r.chance(dt * 4)) { const i = r.int(0, this.poll.opts.length - 1); this.poll.votes[i] += Math.max(1, Math.round(this.viewers * r.range(0.01, 0.06))); } if (this.poll.left <= 0) { const p = this.poll; this.poll = null; const w = p.votes.indexOf(Math.max(...p.votes)); this.push('system', '', `Poll closed: “${p.opts[w]}” wins`); this.addHype(7); this.mood({ good: 0.35, energy: 0.4 }); this.fx.push({ type: 'poll', text: p.opts[w] }); } }
    if (this.dare) { this.dare.left -= dt; if (this.dare.left <= 0) { this.push('system', '', `Dare failed: ${this.dare.text}`); this.dare = null; this.addHype(-8); this.cringe += 6; this.chatter('fail', this.burst()); } }
    if (this.subGoal) { this.subGoal.left -= dt; if (this.subGoal.got >= this.subGoal.target) { this.push('system', '', 'SUB GOAL SMASHED'); this.addHype(22); this.mood({ good: 0.8, energy: 0.8 }); this.fx.push({ type: 'goal', text: 'Sub goal smashed' }); this.chatter('record', this.burst() + 2); this.clip('Sub goal pop-off', 24); this.subGoal = null; } else if (this.subGoal.left <= 0) { this.push('system', '', 'Sub goal missed. We do not speak of it.'); this.addHype(-5); this.subGoal = null; } }
    // --- player body
    s.energy = clamp(s.energy - dt * 0.115 * (1 - Math.min(0.3, (equippedItem(s, 'chair')?.tier ?? 0) * 0.07)), 0, 100); s.food = clamp(s.food - dt * 0.085, 0, 100); s.vibe = clamp(s.vibe + dt * (this.crowd.p * 0.05 - this.cringe * 0.0006), 0, 100); s.min += dt; const ds = deviceState(s); if (ds) ds.cond = clamp(ds.cond - dt * 0.013 * (1.9 - (device(s).dur ?? 0.8)), 0, 100);
    if (s.energy <= 0) this.end('You passed out on stream. Chat made fan art.');
    if (this.viewers < 0.5 && this.t > 40 && s.followers > 5) this.viewers = 0.6;
  }

  private hypeTrainTick(dt: number) { if (this.hypeTrain > 0) { this.hypeTrain -= dt; if (this.hypeTrain <= 0) this.push('system', '', 'The hype train has left the station.'); } else if (this.hype > 88 && !this.trained) { this.trained = true; this.hypeTrain = 30; this.push('system', '', 'HYPE TRAIN! Everything counts double.'); this.fx.push({ type: 'goal', text: 'Hype train!' }); this.chatter('win', this.burst()); } else if (this.hype < 50) this.trained = false; }
  sub(n = 1) { const v = this.present.filter((x) => !x.sub && x.bond.affinity > 5); const who = v.length && this.rng.chance(0.6) ? this.rng.pick(v) : null; if (who) who.sub = 1; const name = who?.name ?? userName(this.rng, this.names); this.s.subs += n; this.newSubs += n; if (this.subGoal) this.subGoal.got += n; this.push('sub', name, n > 1 ? `and ${(n - 1).toLocaleString('en-US')} ${n === 2 ? 'other' : 'others'} subscribed!` : 'just subscribed!', { color: '#f6c419', vid: who?.id }); this.fx.push({ type: 'sub', who: name, amount: n }); this.addHype(2.4); }
  donate(amt?: number) {
    const r = this.rng; const v = this.present.length && r.chance(0.5) ? r.weighted(this.present, (x) => 1 + Math.max(0, x.bond.affinity) / 20 + (x.style === 'simp' ? 3 : 0)) : null;
    const a = amt ?? Math.max(1, Math.round(r.lognormal(2.4 + Math.pow(this.viewers, 0.5), 0.8))); const name = v?.name ?? userName(r, this.names); if (v) v.spent += a; earn(this.s, a, 'donos'); this.earned += a; stat(this.s, 'donos');
    const m = this.push('dono', name, promptLine(r, 'dono', this.ctx()), { color: '#4fd08a', amount: a, vid: v?.id, prompt: { kind: 'dono', expires: this.t + 15, value: a } }); this.fx.push({ type: 'dono', who: name, amount: a, text: m.text }); this.addHype(Math.min(12, 2 + Math.log2(a + 1))); return m;
  }
  // ------------------------------------------------------------ prompts
  spawnPrompt(kind?: PromptKind) {
    const r = this.rng; const pool = this.present.filter((v) => v.timeout <= 0 && !v.banned); const open = this.chat.filter((m) => m.prompt && !m.prompt.done).length; if (open >= 4) return null;
    let v = pool.length && r.chance(0.75) ? r.pick(pool) : null;
    const w = (k: PromptKind) => ({ question: 5, compliment: 2 + this.crowd.p * 3, troll: 2.2 - this.crowd.p * 1.5 + (this.s.drama > 20 ? 2 : 0) - this.modsActive * 1.2, sad: 0.9, backseat: this.game === 'chat' ? 0 : 2.2, request: 2, sus: 0.8 - this.modsActive * 0.5, hypeup: this.hype > 45 ? 2 : 0.5, dono: 0, drama: this.s.drama > 15 ? 3 : this.s.followers > 3000 ? 0.6 : 0.1, regular: v && this.s.day - v.joined > 2 ? 2 : 0 } as Record<PromptKind, number>)[k];
    const k = kind ?? r.weighted(PROMPT_KINDS, w); if (k === 'dono') return this.donate();
    if (k === 'troll') v = pool.find((x) => x.style === 'troll') ?? v; if (k === 'sus') v = null; if (k === 'regular' && !v) v = pool[0] ?? null;
    const text = promptLine(r, k, this.ctx()); const p = { kind: k, expires: this.t + r.range(13, 18) }; const m = v ? this.say(v, text, { prompt: p, hi: true }) : this.anon(text, { prompt: p, hi: true }); if (m) this.fx.push({ type: 'prompt', id: String(m.id) }); return m;
  }
  private expirePrompt(m: ChatMsg) { m.prompt!.done = true; m.hi = false; this.missed++; const v = this.viewerOf(m); const k = m.prompt!.kind; if (k === 'troll' || k === 'sus' || k === 'backseat') { if (k === 'sus') this.cringe += 3; return; } if (v) { feel(v, { good: k === 'sad' ? -0.6 : -0.3, praise: -0.2, blame: 'player' }); bondWith(v, k === 'sad' ? 'ignored me when I was down' : k === 'dono' ? 'didn’t thank me' : 'ignored my message', k === 'sad' ? -6 : -2.5, this.s.day); if (k === 'dono') { this.say(v, this.rng.pick(['no thanks?', 'ok cool', 'guess I’ll go'])); this.addHype(-3); } } this.addHype(-1.2); }
  viewerOf(m: ChatMsg): Viewer | undefined { return m.vid ? this.s.viewers.find((v) => v.id === m.vid) : undefined; }
  optionsFor(m: ChatMsg): { tone: Tone; label: string }[] { return replyOptions(m, this.rng); }
  reply(msgId: number, tone: Tone): { good: number; text: string } | null {
    const m = this.chat.find((x) => x.id === msgId); if (!m || !m.prompt || m.prompt.done) return null; m.prompt.done = true; m.hi = false; const v = this.viewerOf(m); const r = this.rng; const k = m.prompt.kind; this.handled++; this.silence = 0; this.lastSpeak = this.t;
    if (tone === 'timeout' || tone === 'ban') {
      const just = k === 'troll' || k === 'sus' || k === 'drama'; if (v) { if (tone === 'ban') { v.banned = true; this.present = this.present.filter((x) => x !== v); } else v.timeout = 120; bondWith(v, tone === 'ban' ? 'banned me' : 'timed me out', -25, this.s.day); }
      this.push('mod', '', `${m.who} was ${tone === 'ban' ? 'banned' : 'timed out for 10 minutes'}`); m.text = '<message deleted>'; const g = just ? (k === 'sus' ? 0.6 : 0.25) : -0.7; this.mood({ good: g, praise: 0, blame: 'player' }); this.addHype(just ? 2 : -6); if (!just) { this.cringe += 10; this.chatter('fail', 1); this.anon(r.pick(['bro banned him for THAT?', 'power trip', 'freedom of speech died today'])); } else this.anon(r.pick(['bonk', 'justice', 'mods on fire', 'get rekt'])); stat(this.s, tone === 'ban' ? 'bans' : 'timeouts'); return { good: g, text: tone === 'ban' ? 'And that’s a ban.' : 'Cool off, champ.' };
    }
    if (tone === 'click') { this.startIncident(INCIDENTS.find((i) => i.id === 'hacked')!); return { good: -1, text: 'Ooh, free followers! *click*' }; }
    let good = toneFit(k, tone) + (this.charisma - 1) * 0.03 + r.gauss(0, 0.18) - this.repeated * 0.05; if (v) { if (v.style === 'memer' && tone === 'roast') good += 0.2; if (v.style === 'kid' && tone === 'roast') good -= 0.35; if (v.style === 'simp') good += 0.15; if (v.style === 'critic' && tone === 'honest') good += 0.3; if (v.style === 'elder' && tone === 'warm') good += 0.25; if (v.traits.n > 0.7 && tone === 'roast') good -= 0.2; good += v.bond.affinity / 300; }
    good = clamp(good, -1, 1); const text = lineFor(k, tone, m.who, r);
    if (v) { feel(v, { good, praise: tone === 'roast' ? (good > 0 ? 0.2 : -0.7) : tone === 'warm' ? 0.7 : 0.3, surprise: 0.4, blame: 'player', energy: tone === 'hype' ? 0.6 : 0.2 }, 1.2); bondWith(v, good > 0.2 ? memoryFor(k, true) : memoryFor(k, false), good > 0 ? 4 + good * 7 : good * 12, this.s.day); if (good > 0.55 && !v.sub && this.s.followers >= 50 && r.chance(0.28)) { v.sub = 1; this.sub(); } }
    this.mood({ good: good * 0.5, energy: tone === 'hype' ? 0.4 : 0.1, praise: good > 0 ? 0.15 : -0.1, blame: 'player' }); this.addHype(good > 0 ? 3.5 + good * 8 : good * 7); if (good < -0.15) this.cringe += 7; skillUp(this.s, 'charisma', 0.035);
    if (k === 'sad' && good > 0.3) { this.s.rep = clamp(this.s.rep + 0.4, 0, 100); this.clip('Kindest moment on Twinge', 12 + good * 10); }
    if (k === 'drama') { this.s.drama = clamp(this.s.drama + (good > 0 ? -5 : 7) + (tone === 'roast' ? 3 : 0), 0, 100); if (tone === 'roast') this.clip('Shots fired', 26 + r.range(0, 14)); }
    if (k === 'troll' && tone === 'roast' && good > 0.25) this.clip(`Destroying ${m.who}`, 18 + good * 16);
    if (k === 'question' && tone === 'funny' && good > 0.6 && r.chance(0.4)) this.clip('Best answer ever', 16 + good * 8);
    this.reactions(good, v); this.speak(text, good); return { good, text };
  }
  private reactions(good: number, v?: Viewer) { const n = clamp(Math.round(this.burst() * 0.6), 1, 4); for (let i = 0; i < n; i++) this.anon(good > 0.5 ? this.rng.pick(['LMAO', ':heart:', 'W answer', 'he’s so real', ':kekwow:', 'based']) : good > 0 ? this.rng.pick(['lol', 'ok', 'fair', 'true']) : this.rng.pick([':yikes:', 'yikes', 'tf', 'not like this', 'awkward', ':clown:'])); if (v && good > 0.3) this.say(v, this.rng.pick(['HE NOTICED ME', 'omg thank you', ':heart: :heart:', 'framing this', 'lol love you'])); else if (v && good < -0.2) this.say(v, this.rng.pick(['ouch', 'ok wow', 'damn', 'unfollowing'])); }
  speak(text: string, good = 0) { this.said = text; this.fx.push({ type: 'speak', text, good }); }
  // ------------------------------------------------------------ free speech
  talk(raw: string): { speech: Speech; good: number } | null {
    if (this.ended || !raw.trim()) return null; const sp = understand(raw, this.present.map((v) => v.name)); const r = this.rng; this.silence = 0; this.afk = 0;
    const norm = raw.trim().toLowerCase(); const rep = this.speechLog.filter((x) => x === norm).length; this.speechLog.push(norm); if (this.speechLog.length > 12) this.speechLog.shift(); this.push('you', this.s.channel, raw.trim(), { color: '#f2331b' });
    if (this.muted) { this.chatter('mute', 2); this.addHype(-1); return { speech: sp, good: -0.2 }; }
    const recent = this.speechLog.length; let good = 0.18 + sp.sentiment * 0.35 + sp.energy * 0.15 + (this.charisma - 1) * 0.025 + r.gauss(0, 0.15) - rep * 0.45; const since = this.t - this.lastSpeak; this.lastSpeak = this.t; if (since < 2.5) good -= 0.12;
    const open = this.chat.filter((m) => m.prompt && !m.prompt.done && m.prompt.kind !== 'sus').reverse(); const hit = sp.target ? open.find((m) => m.who === sp.target) : undefined;
    switch (sp.intent) {
      case 'beg': good -= 0.3 + (this.s.flags.begs ?? 0) * 0.12; this.s.flags.begs = (this.s.flags.begs ?? 0) + 1; if (good > -0.1) this.followAcc += 0.6 + this.viewers * 0.03; this.cringe += 3; break;
      case 'insult': good = sp.target ? -0.2 : -0.35; { const tv = sp.target ? this.present.find((v) => v.name === sp.target) : undefined; if (tv && tv.style === 'troll') { good = 0.45; } } if (r.chance(0.35)) { good += 0.5; } this.s.drama = clamp(this.s.drama + 0.8, 0, 100); break;
      case 'apology': good += this.cringe > 20 || this.s.drama > 15 ? 0.5 : 0; this.cringe = Math.max(0, this.cringe - 18); this.s.drama = Math.max(0, this.s.drama - 2); break;
      case 'vent': good = 0.25 + r.gauss(0, 0.15); this.s.vibe = clamp(this.s.vibe + 3, 0, 100); break;
      case 'hottake': good += r.range(-0.5, 0.55); if (r.chance(0.25)) this.clip('Unhinged hot take', 14 + r.range(0, 20)); break;
      case 'sing': good += r.range(-0.45, 0.5); if (good > 0.45) this.clip('Surprise vocals', 20); break;
      case 'ad': if (this.s.sponsors.some((x) => x.accepted)) { this.doSponsor(); good = 0.1; } else good = -0.1; break;
      case 'question': good += 0.15; break; case 'love': case 'thanks': good += 0.2; break; case 'joke': good += r.range(-0.2, 0.45); break;
      case 'nonsense': good = r.chance(0.3) ? 0.4 : -0.15; break; case 'promise': if (/giveaway/.test(sp.raw.toLowerCase())) { this.s.flags.promised = this.s.day; good += 0.35; } break;
    }
    if (sp.swear) { good += r.chance(0.5) ? 0.08 : -0.1; if (this.s.followers > 5000 && r.chance(0.06)) this.s.drama += 2; }
    if (sp.len > 26) good -= 0.08; good = clamp(good, -1, 1);
    if (hit) { hit.prompt!.done = true; hit.hi = false; this.handled++; good = clamp(good + 0.2, -1, 1); }
    else if (open.length && (sp.intent === 'thanks' || sp.intent === 'love' || sp.intent === 'greet' || sp.intent === 'statement')) { const m = open.find((x) => x.prompt!.kind === 'dono') ?? (sp.intent === 'statement' ? undefined : open[0]); if (m) { m.prompt!.done = true; m.hi = false; this.handled++; const v = this.viewerOf(m); if (v) bondWith(v, 'thanked me', 5, this.s.day); } }
    const tv = sp.target ? this.present.find((v) => v.name === sp.target) : undefined; if (tv) { feel(tv, { good, praise: sp.sentiment, surprise: 0.6, blame: 'player' }, 1.3); bondWith(tv, good > 0 ? 'talked to me by name' : 'called me out', good * 9, this.s.day); }
    this.mood({ good: good * 0.55, energy: sp.energy * 0.7, praise: sp.sentiment * 0.3, blame: 'player' }); this.addHype(good > 0 ? 2 + good * 7.5 + sp.energy * 2 : good * 7); if (good < -0.2) this.cringe += 6; skillUp(this.s, 'charisma', 0.03); stat(this.s, 'talks');
    const n = clamp(this.burst() + 1, 2, 6); for (let i = 0; i < n; i++) { const v = this.present.length && r.chance(0.6) ? r.pick(this.present) : null; const t = replyToSpeech(r, sp, v, good); v ? this.say(v, t) : this.anon(t); }
    if (tv) this.say(tv, good > 0 ? r.pick(['OMG HI', 'he said my name', ':heart:']) : r.pick(['wow ok', 'caught strays']));
    this.said = raw.trim(); this.fx.push({ type: 'speak', text: raw.trim(), good }); void recent; return { speech: sp, good };
  }
  // ------------------------------------------------------------ gameplay → hype
  onGame(ev: GameEvent, heat = 1, label = '') {
    if (this.ended) return; this.afk = 0; const s = this.s; if (ev === 'score') { this.addHype(0.55 * heat); return; }
    const base: Record<string, number> = { fail: 2.2, clutch: 8, combo: 4, record: 13, scare: 7, win: 15 }; this.addHype((base[ev] ?? 2) * Math.min(1.8, heat) * 0.62); this.chatter(ev, clamp(Math.round(this.burst() * (ev === 'combo' ? 0.5 : 1)), 1, 6));
    this.mood({ good: ev === 'fail' ? 0.05 : 0.35, energy: ev === 'fail' ? 0.25 : 0.6, surprise: 0.4 }, 0.8); this.window = { ev, left: 3.4, from: this.t }; skillUp(s, 'gaming', 0.04); if (heat > 1.2 && ev !== 'fail') this.clip(label || `${GAME[this.game].name} ${ev}`, 9 + heat * 7);
    if (this.dare && this.dare.need.includes(ev)) { this.push('system', '', `Dare complete: ${this.dare.text}`); this.dare = null; this.addHype(20); this.mood({ good: 0.8, energy: 0.8 }); this.clip('Dare completed', 26); this.chatter('win', this.burst() + 1); this.fx.push({ type: 'goal', text: 'Dare complete' }); if (this.viewers > 20) this.donate(); }
  }
  react(r: Reaction): { ok: boolean; good: number } {
    if (this.ended) return { ok: false, good: 0 }; const last = this.lastReact[r] ?? -99; const spam = this.t - last; this.lastReact[r] = this.t; this.silence = Math.max(0, this.silence - 6); const w = this.window; let ok = false, good = 0;
    if (w && EXPECT[w.ev].includes(r)) { ok = true; const speed = clamp(w.left / 3.4); good = 0.5 + 0.5 * speed; this.combo++; this.addHype(5 + 7 * speed + Math.min(6, this.combo)); this.mood({ good: 0.45, energy: 0.7, surprise: 0.3 }); if (speed > 0.45 && this.rng.chance(w.ev === 'combo' ? 0.28 : w.ev === 'fail' ? 0.5 : 0.9)) this.clip(clipTitle(this.rng, r, w.ev, GAME[this.game].name), 13 + this.combo * 2 + speed * 9); this.window = null; skillUp(this.s, 'charisma', 0.04); }
    else if (w) { good = -0.35; this.combo = 0; this.addHype(-2); this.cringe += 5; this.window = null; }
    else if (spam < 9) { good = -0.25; this.repeated++; this.addHype(-1.5); this.cringe += 3.5; } else { const tired = this.hype > 50 ? 0.25 : 0.1; good = r === 'dance' || r === 'laugh' ? 0.2 + tired : 0.05; this.addHype(good * 8); ok = good > 0.1; }
    const n = clamp(Math.round(this.burst() * 0.7), 1, 4); for (let i = 0; i < n; i++) this.anon(reactToStreamer(this.rng, r, good >= 0)); this.fx.push({ type: 'react', reaction: r, ok, good }); stat(this.s, 'reactions'); return { ok, good };
  }
  clip(title: string, heat: number) { const s = this.s; heat = clamp(heat * (0.8 + this.hype / 120) * (0.8 + 0.2 * this.quality), 1, 100); if (heat < 9) return; if (this.t - this.lastClip < 6.5 && heat < this.bestMoment.heat * 1.12) return; this.lastClip = this.t; const c = { id: this.rng.id('c'), title, heat, game: this.game, day: s.day, kind: this.game }; s.clips.unshift(c); if (s.clips.length > 24) { s.clips.sort((a, b) => b.heat - a.heat); s.clips.length = 24; } if (heat > this.bestMoment.heat) this.bestMoment = { heat, text: title }; this.fx.push({ type: 'clip', text: title, amount: heat }); }
  // ------------------------------------------------------------ segments
  canSegment(id: SegmentId) { const d = SEGMENTS[id]; if (this.s.followers < d.min) return false; if ((this.segCd[id] ?? 0) > 0) return false; if (id === 'giveaway' && this.s.money < this.giveawayCost()) return false; if (id === 'poll' && this.poll) return false; if (id === 'subgoal' && this.subGoal) return false; if (id === 'challenge' && (this.dare || this.game === 'chat')) return false; return !this.ended; }
  giveawayCost() { return Math.max(20, Math.round(Math.pow(this.s.followers + 10, 0.62) * 1.1 / 5) * 5); }
  segment(id: SegmentId): boolean {
    if (!this.canSegment(id)) return false; const r = this.rng; this.segCd[id] = SEGMENTS[id].cd; this.silence = 0; const s = this.s;
    switch (id) {
      case 'qna': this.push('system', '', 'Q&A mode: ask me anything'); for (let i = 0; i < 3; i++) this.spawnPrompt('question'); this.addHype(4); this.speak('Alright chat, Q and A. Ask me anything. Almost anything.'); break;
      case 'poll': { const p = r.pick([['Best breakfast?', 'Cereal', 'Cold pizza', 'Regret'], ['What am I?', 'Goat', 'Fraud', 'Soup'], ['Next outfit?', 'Suit', 'Onesie', 'Knight armour'], ['Is water wet?', 'Yes', 'No', 'Ban him'], ['Who wins?', '1 bear', '100 toddlers', 'Mom']]); this.poll = { q: p[0], opts: p.slice(1), votes: p.slice(1).map(() => 0), left: 14, kind: 'poll' }; this.speak(`Poll time! ${p[0]}`); break; }
      case 'challenge': { const d = r.pick([{ text: 'hit a clutch in 30 seconds', need: ['clutch', 'record', 'win'] as GameEvent[] }, { text: 'land a combo right now', need: ['combo', 'clutch', 'record'] as GameEvent[] }, { text: 'beat your record or eat a lemon', need: ['record', 'win'] as GameEvent[] }]); this.dare = { ...d, left: 34 }; this.push('system', '', `DARE: ${d.text}`); this.addHype(8); this.speak(`Chat dares me to ${d.text}. Bet.`); break; }
      case 'giveaway': { const c = this.giveawayCost(); earn(s, -c, 'giveaway'); this.push('system', '', `GIVEAWAY: $${c} to a random viewer`); this.addHype(18); this.mood({ good: 0.8, praise: 0.4, energy: 0.7, surprise: 0.5, blame: 'player' }); this.followAcc += 4 + this.viewers * 0.35 * Math.pow(1 + s.followers, 0.1); s.rep = clamp(s.rep + 1.2, 0, 100); const v = this.present.length ? r.pick(this.present) : null; if (v) { bondWith(v, 'won the giveaway', 25, s.day); this.say(v, 'I WON?? I WON!!!'); } this.chatter('record', this.burst() + 1); this.clip('Giveaway pop-off', 16); this.speak(`I’m giving one of you ${c} dollars. Right now.`); if (s.flags.promised) { delete s.flags.promised; s.rep += 2; } break; }
      case 'subgoal': { const t = Math.max(2, Math.round(Math.pow(this.viewers, 0.9) * 0.05)); this.subGoal = { target: t, got: 0, left: 50 }; this.push('system', '', `SUB GOAL: ${t} subs`); this.speak(`${t} subs and I do something I’ll regret.`); break; }
      case 'raid': { const rv = r.pick(s.rivals.filter((x) => x.followers < Math.max(800, s.followers * 4)) ?? s.rivals); rv.heat = clamp(rv.heat - 20, -100, 100); s.flags['raided_' + rv.id] = s.day; s.rep = clamp(s.rep + 1.5, 0, 100); this.push('system', '', `Raiding ${rv.name} with ${Math.round(this.viewers)} viewers`); this.end(`You raided ${rv.name}. They owe you one.`); break; }
    }
    return true;
  }
  get activeSponsor() { return this.s.sponsors.find((x) => x.accepted && x.progress < 1); }
  doSponsor(): boolean { const sp = this.activeSponsor; if (!sp) return false; sp.progress = 1; const pay = sp.pay; earn(this.s, pay, 'sponsors'); this.earned += pay; this.sponsorRead++; this.silence = 0; const cost = sp.shady * 26 + 3 + this.sponsorRead * 4 - this.s.skills.business * 0.8; this.addHype(-Math.max(1, cost * 0.6)); this.cringe += cost * 0.6; this.s.drama = clamp(this.s.drama + sp.shady * 9, 0, 100); this.s.rep = clamp(this.s.rep - sp.shady * 4, 0, 100); this.push('system', '', `#ad ${sp.brand}: +$${pay}`); this.speak(sp.line); for (let i = 0; i < this.burst(); i++) this.anon(this.rng.pick(sp.shady > 0.6 ? ['is this legal', 'SELLOUT', ':yikes:', 'bro needs rent money', 'unfollowed'] : ['get that bag', 'used the code', 'smooth transition ngl', 'ad break snack break', ':clown:'])); skillUp(this.s, 'business', 0.5); stat(this.s, 'sponsorReads'); return true; }
  // ------------------------------------------------------------ incidents
  startIncident(def: Incident) { if (this.ended) return; this.incident = { def, left: def.time }; def.start?.(this); this.fx.push({ type: 'incident', id: def.id, text: def.title }); stat(this.s, 'incidents'); }
  resolveIncident(i: number, ok = true) { const inc = this.incident; if (!inc) return null; this.incident = null; const d = inc.def; const opt = i >= 0 ? d.options[i] : undefined; if (opt && !(opt.can?.(this) ?? true)) { this.incident = inc; return null; } const out = opt ? opt.run(this, ok) : d.timeout(this); this.push('system', '', out); this.fx.push({ type: 'resolved', id: d.id, text: out }); if (this.t > this.nextIncident - 14) this.nextIncident = this.t + this.rng.range(22, 40); return out; }
  toggleMute() { this.muted = !this.muted; this.mutedFor = 0; if (!this.muted) { this.push('system', '', 'Mic is back. Civilization resumes.'); } }
  // ------------------------------------------------------------ end
  end(reason = '') {
    if (this.ended) return; if (this.subQ > 0) { this.sub(this.subQ); this.subQ = 0; } this.ended = true; this.endReason = reason; const s = this.s; const avg = this.sumViewers / Math.max(1, this.t); const adv = avg * (this.t / 60) * 0.03 * (s.followers > 500 ? 1 : 0); const pay = Math.round(adv * 100) / 100; if (pay > 0) { earn(s, pay, 'ads'); this.earned += pay; }
    s.gameFatigue[this.game] = (s.gameFatigue[this.game] ?? 0) + 1; for (const g in s.gameFatigue) if (g !== this.game) s.gameFatigue[g] = Math.max(0, s.gameFatigue[g] - 0.5);
    if (s.lastStreamDay === s.day - 1) s.streak++; else if (s.lastStreamDay !== s.day) s.streak = 1; s.lastStreamDay = s.day; s.rng = this.rng.s; s.burnout = clamp(s.burnout + this.t / 60 * 2.2 - 1, 0, 100); stat(s, 'streams'); stat(s, 'liveMinutes', this.t); s.tutorial = Math.max(s.tutorial, 1); s.flags.begs = 0;
    const log: StreamLog = { day: s.day, game: this.game, mins: Math.round(this.t), peak: Math.round(this.peak), avg: Math.round(avg), followers: this.newFollowers, subs: this.newSubs, money: Math.round(this.earned * 100) / 100, grade: this.grade(), best: this.bestMoment.text, title: this.title }; s.logs.unshift(log); if (s.logs.length > 30) s.logs.length = 30; this.fx.push({ type: 'end', text: reason }); return log;
  }
  grade(): string { const avg = this.sumViewers / Math.max(1, this.t); const f0 = Math.max(0, this.s.followers - this.newFollowers); const exp = baseViewers(f0) * (0.85 + 0.085 * Math.log10(1 + f0)); const ratio = avg / exp; const care = this.handled / Math.max(1, this.handled + this.missed); const sc = ratio * 55 + care * 22 + Math.min(23, this.bestMoment.heat * 0.5) - this.cringe * 0.1; return sc > 104 ? 'S' : sc > 84 ? 'A' : sc > 66 ? 'B' : sc > 48 ? 'C' : sc > 30 ? 'D' : 'F'; }
  drainFx(): StreamFx[] { const f = this.fx; this.fx = []; return f; }
}
const FIT: Record<PromptKind, Partial<Record<Tone, number>>> = {
  question: { funny: 0.45, honest: 0.4, warm: 0.3, roast: 0.05 }, compliment: { warm: 0.65, funny: 0.35, roast: -0.25, hype: 0.5 }, troll: { roast: 0.42, funny: 0.4, warm: 0.15, honest: -0.15 }, sad: { warm: 0.8, honest: 0.55, funny: -0.15, roast: -0.95 }, backseat: { funny: 0.4, roast: 0.2, honest: 0.15, warm: 0.25 },
  request: { hype: 0.5, funny: 0.4, warm: 0.35, honest: 0.0 }, sus: { funny: 0.35, roast: 0.3, honest: 0.3, warm: -0.5 }, hypeup: { hype: 0.75, funny: 0.3, roast: -0.2, warm: 0.3 }, dono: { warm: 0.6, hype: 0.65, funny: 0.4, roast: -0.5 }, drama: { honest: 0.3, funny: 0.25, roast: 0.0, warm: 0.2 }, regular: { warm: 0.7, funny: 0.35, roast: -0.1, hype: 0.45 },
};
export const toneFit = (k: PromptKind, t: Tone) => FIT[k]?.[t] ?? 0;
export function replyOptions(m: ChatMsg, _r?: RNG): { tone: Tone; label: string }[] {
  const k = m.prompt?.kind ?? 'question'; const L = (tone: Tone, label: string) => ({ tone, label });
  switch (k) {
    case 'troll': return [L('roast', 'Roast them'), L('funny', 'Laugh it off'), L('warm', 'Kill with kindness'), L('timeout', 'Time out'), L('ban', 'Ban')];
    case 'sus': return [L('funny', 'Make it a bit'), L('timeout', 'Time out'), L('ban', 'Ban'), L('click', 'Click the link')];
    case 'sad': return [L('warm', 'Comfort'), L('honest', 'Share your own'), L('funny', 'Cheer up with a joke'), L('roast', 'Roast')];
    case 'dono': return [L('warm', 'Thank by name'), L('hype', 'Scream thanks'), L('funny', 'Thank with a bit'), L('roast', 'Ask for more')];
    case 'drama': return [L('honest', 'Address it'), L('funny', 'Deflect with humour'), L('roast', 'Clap back'), L('timeout', 'Time out')];
    case 'backseat': return [L('funny', '“You come play then”'), L('honest', 'Try the tip'), L('warm', 'Thanks coach'), L('roast', 'Roast')];
    case 'request': return [L('hype', 'DO IT'), L('funny', 'Do a bad version'), L('warm', 'Sweet version'), L('honest', 'Decline politely')];
    case 'hypeup': return [L('hype', 'GO NUTS'), L('funny', 'Negotiate terms'), L('warm', 'Thank the chat'), L('roast', 'Play it cool')];
    case 'compliment': return [L('warm', 'Heartfelt thanks'), L('hype', 'Get loud'), L('funny', 'Self-own'), L('roast', 'Humblebrag')];
    case 'regular': return [L('warm', 'I remember!'), L('hype', 'Give them a moment'), L('funny', 'Pretend to forget'), L('roast', 'Tease')];
    default: return [L('funny', 'Joke answer'), L('honest', 'Real answer'), L('warm', 'Turn it around'), L('roast', 'Roast the question')];
  }
}
const LINES: Partial<Record<PromptKind, Partial<Record<Tone, string[]>>>> = {
  question: { funny: ['Legally, I can’t answer that until 2031.', 'My lawyer is a pigeon and even he said no.', 'The answer is soup. It’s always soup.'], honest: ['Honestly? I was bored and the Wi-Fi worked.', 'Real answer: I’m still figuring it out.', 'Truth? I’m terrified, and it’s fun.'], warm: ['Great question, {u}. What about you?', '{u}, you first. I want to know.'], roast: ['{u}, did a committee write that?', 'That question has a helmet on.'] },
  compliment: { warm: ['{u}, that actually means the world.', 'You’re making me emotional, {u}.'], hype: ['{u} IS A LEGEND!', 'CHAT, CLAP FOR {u}!'], funny: ['I peaked in a dentist waiting room, but thank you.'], roast: ['I know. I have mirrors.'] },
  troll: { roast: ['{u}, your opinion is buffering.', '{u} types with oven mitts.', 'Imagine logging in just to lose, {u}.'], funny: ['Put that on a T-shirt, I’ll buy ten.', 'My mom agrees with you, actually.'], warm: ['Hope your day gets better, {u}. Truly.', 'You’re still here though. I appreciate the watch time.'], honest: ['Okay, that one stung a bit.'] },
  sad: { warm: ['{u}, I’m really glad you’re here tonight.', 'Hey {u}. You matter. Stay as long as you like.'], honest: ['I’ve been there, {u}. It gets quieter, then better.'], funny: ['Would a very bad dance help?'], roast: ['Skill issue?'] },
  backseat: { funny: ['{u}, come over. I’ll make a sandwich. You play.'], honest: ['Okay {u}, trying it your way.'], warm: ['Coach {u} has spoken.'], roast: ['{u}, your rank is “spectator”.'] },
  request: { hype: ['SAY LESS! HERE WE GO!'], funny: ['I can do it, but you’ll wish I hadn’t.'], warm: ['Anything for you, {u}.'], honest: ['I’ll sit that one out, {u}. My knees have a union.'] },
  sus: { funny: ['A prince! In MY chat! Royalty!'], roast: ['{u}, even my router blocked you.'], honest: ['Don’t click that, everyone.'], warm: ['Aw, thanks for the offer?'] },
  hypeup: { hype: ['LET’S GOOOOO!', 'EVERYBODY UP!'], funny: ['Backflip costs extra. I have one spine.'], warm: ['You lot are unreal.'], roast: ['Calm down, it’s a Moanday.'] },
  dono: { warm: ['{u}, thank you. That’s dinner!', 'Thank you so much, {u}!'], hype: ['{u} WITH THE BAG! LET’S GO!'], funny: ['{u}, I will waste this responsibly.'], roast: ['Is that all, {u}?'] },
  drama: { honest: ['Fine. Here’s what happened, no edits.'], funny: ['I plead the fifth, sixth and seventh.'], roast: ['Tell them I said it to their ring light.'], warm: ['I wish them well. Really.'] },
  regular: { warm: ['Of course I remember you, {u}!', '{u}! Day one! Chat, show respect.'], hype: ['{u} IS THE BACKBONE OF THIS CHANNEL!'], funny: ['Have we met? …kidding, {u}.'], roast: ['{u}, you again? Do you pay rent here?'] },
};
function lineFor(k: PromptKind, tone: Tone, who: string, r: RNG): string { const a = LINES[k]?.[tone] ?? ['Ha. Okay, {u}.']; return r.pick(a).replaceAll('{u}', who); }
function memoryFor(k: PromptKind, good: boolean): string { const g: Record<string, string> = { question: 'answered my question', compliment: 'made me feel seen', troll: 'took my heckle well', sad: 'was there on a bad day', backseat: 'listened to my advice', request: 'did my request', sus: 'joked with me', hypeup: 'hyped us up', dono: 'thanked me properly', drama: 'was straight about the drama', regular: 'remembered me' }; const b: Record<string, string> = { question: 'dodged my question', compliment: 'brushed off my kindness', troll: 'humiliated me', sad: 'joked about my pain', backseat: 'mocked my advice', request: 'refused me', sus: 'laughed at me', hypeup: 'killed the vibe', dono: 'was ungrateful', drama: 'lied about the drama', regular: 'forgot me' }; return good ? g[k] : b[k]; }
export function autoTitle(r: RNG, s: GameState, game: string): string { const g = GAME[game].name; return r.pick([`${g} but I cry if I lose`, `day ${s.day} of being famous (not yet)`, `${g} | !drip !mom !why`, `chill ${g} (lying)`, `road to ${nextMilestone(s.followers).toLocaleString('en-US')} | ${g}`, `I have never played ${g} (1000 hours)`, `${g} until my ${r.pick(['mom', 'landlord', 'lawyer', 'dog'])} stops me`]); }
const CT: Record<Reaction, string[]> = { laugh: ['Wheezes for a full minute', 'The laugh that broke the mic', 'Laughs at own funeral'], hype: ['Pops off', 'Neighbours call the police (hype)', 'Loses voice, gains clip', 'Absolutely unhinged pop-off'], rage: ['Full gamer rage', 'Threatens a pipe', 'Phone survives, dignity does not'], cry: ['Actual tears', 'Cries over pixels', 'Someone hug this person'], shock: ['THE face', 'New emote unlocked', 'Jaw found on floor'], dance: ['Victory dance', 'Illegal dance moves', 'Dad-at-a-wedding energy'] };
const CE: Record<string, string> = { fail: 'after a tragic fail', clutch: 'on a clutch', combo: 'mid-combo', record: 'on a new record', scare: 'after a jump scare', win: 'on the win' };
export function clipTitle(r: RNG, re: Reaction, ev: string, game: string): string { return `${r.pick(CT[re])} ${r.chance(0.6) ? CE[ev] ?? 'live' : `(${game})`}`; }
export function nextMilestone(f: number) { const m = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1e6, 2.5e6, 5e6, 1e7, 2.5e7, 5e7, 1e8, 2e8, 2.5e8]; return m.find((x) => x > f) ?? 1e9; }
export { canPlay, EMOTES, ownedItem, lerp, note, SPONSORS };
