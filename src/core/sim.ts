/** Headless bot player — used for balance tests. */
import { RNG } from './rng';
import { newState, canPlay, quality } from './state';
import { StreamSession, EXPECT, replyOptions, toneFit, type GameEvent } from './stream';
import { GAMES, HOMES, ITEMS, ITEM } from './catalog';
import { buy, canMove, move, sleep, eat, makeVideo, titleOptions, THUMBS, doPost, acceptSponsor, checkGoals, canShow, showConcepts, startShow, showChoose, finishShow, pickLife, train, repair } from './life';
import { hire } from './staff';
import type { GameState, Reaction } from './types';
export function botStream(s: GameState, game: string, secs: number, skill: number, r: RNG): StreamSession {
  const ss = new StreamSession(s, game); let nextEv = 4; const rx: Reaction[] = ['laugh', 'hype', 'rage', 'cry', 'shock', 'dance'];
  for (let t = 0; t < secs && !ss.ended; t += 0.25) {
    ss.step(0.25); nextEv -= 0.25;
    if (game !== 'chat' && nextEv <= 0) { nextEv = r.range(3, 9); const ev = r.weighted(['fail', 'combo', 'clutch', 'record', 'score', 'win'] as GameEvent[], (e) => ({ fail: 3, combo: 3, clutch: 1.6, record: 0.35, score: 6, win: 0.4 } as Record<string, number>)[e]); ss.onGame(ev, r.range(0.6, 1.6)); if (ev !== 'score' && r.chance(skill)) { ss.step(0.25); ss.react(r.pick(EXPECT[ev])); } else if (r.chance(0.05)) ss.react(r.pick(rx)); }
    const m = ss.chat.find((c) => c.prompt && !c.prompt.done); if (m && r.chance(0.06 * skill)) { const o = replyOptions(m); const best = o.slice().sort((a, b) => toneFit(m.prompt!.kind, b.tone) - toneFit(m.prompt!.kind, a.tone)); ss.reply(m.id, r.chance(skill) ? best[0].tone : r.pick(o).tone); }
    if (ss.incident && r.chance(0.1)) { if (ss.incident.def.id === 'muted') { if (ss.muted) ss.toggleMute(); } else if (ss.incident.def.options.length) ss.resolveIncident(r.int(0, ss.incident.def.options.length - 1), r.chance(skill)); }
    if (r.chance(0.01 * skill)) ss.talk(r.pick(['lets go chat!', 'love you guys', 'what do you think?', 'thanks for watching', 'that was insane', 'hello everyone']));
    if (r.chance(0.006)) { const id = r.pick(['qna', 'poll', 'challenge', 'giveaway', 'subgoal'] as const); if (id !== 'giveaway' || s.money > ss.giveawayCost() * 8) ss.segment(id); } if (ss.activeSponsor && r.chance(0.01)) ss.doSponsor();
  }
  if (!ss.ended) ss.end(); return ss;
}
export function botDay(s: GameState, skill: number, r: RNG, streams = 1, secs = 170) {
  for (const sp of s.sponsors) if (sp.shady < 0.5) acceptSponsor(s, sp.id);
  const l = r.chance(0.5) ? pickLife(s, r) : null; if (l) { const o = l.options.filter((x) => x.can?.(s) ?? true); r.pick(o).run(s, r); }
  for (let i = 0; i < streams; i++) { if (s.energy < 30) break; const gs = GAMES.filter((g) => canPlay(s, g.id)); const g = gs.slice().sort((a, b) => ((s.trend[b.id] ?? 1) - (s.gameFatigue[b.id] ?? 0) * 0.08) - ((s.trend[a.id] ?? 1) - (s.gameFatigue[a.id] ?? 0) * 0.08))[0]; s.min = 19 * 60 + i * 200; botStream(s, g.id, secs, skill, r); checkGoals(s); }
  if (s.food < 50) eat(s); if (s.clips.length && !s.staff.some((x) => x.role === 'editor')) { const cl = s.clips.slice().sort((a, b) => b.heat - a.heat).slice(0, 3); const t = titleOptions(s, cl, r); makeVideo(s, cl, t[r.int(0, 2)], r.pick(THUMBS), r); }
  doPost(s, r.pick(['meme', 'bts']), r);
  const d = s.owned.find((o) => o.id === s.equipped.device)!; if (d.cond < 40 || d.broken) repair(s, d.id);
  for (const h of HOMES) if (!canMove(s, h.id) && s.money > h.price * 1.15) move(s, h.id);
  for (const it of ITEMS.slice().sort((a, b) => b.q - a.q)) { const cur = s.equipped[it.slot]; if (cur && ITEM[cur].q >= it.q) continue; if (it.price < s.money * 0.6 && (!it.unlock || s.followers >= it.unlock) && it.price > 0) buy(s, it.id); }
  for (const c of [...s.candidates]) if (s.money > c.salary * 25) hire(s, c.id);
  if (canShow(s) && s.money > 60000 && s.day % 3 === 0 && s.energy > 30) { const c = showConcepts(s, r).sort((a, b) => a.cost - b.cost)[1]; const st = startShow(s, c, r); if (typeof st !== 'string') { while (!st.done) showChoose(st, r.int(0, st.beats[st.beat].options.length - 1), r); finishShow(s, st, r); } }
  checkGoals(s); sleep(s); void quality; void train;
}
export { newState };
