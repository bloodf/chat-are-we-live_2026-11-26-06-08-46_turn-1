import { game } from '../game';
import { VU, Key, fmt, money } from './bits';
import { Bolt, Fork, Smile, PhoneI, Mic, Bed } from './icons';
import { HOME } from '../core/catalog';
import { timeStr, weekday } from '../core/state';
import { CHAPTERS, openGoals } from '../core/life';
import { EMOTION_TONE } from '../core/emotion';
const TONE = { good: '#2fa84f', mid: '#f6c419', bad: '#f2331b' };
export function Markers() {
  const ms = game.markers.value; return <>{ms.filter((m) => m.on).map((m) => <div key={m.id} class={`mk ${m.near ? 'near' : ''} ${m.kind}`} style={{ transform: `translate(${m.x.toFixed(1)}px,${m.y.toFixed(1)}px) translate(-50%,-100%)` }}>{m.kind === 'bubble' ? <div>{m.text}</div> : <button class="hit" data-testid={'spot-' + m.id} onClick={() => game.interact(m.id)}>{m.kind === 'npc' && <i class="dot" style={{ background: TONE[EMOTION_TONE[m.emo ?? 'calm']] }} />}{m.label}<Key k="E" /></button>}</div>)}</>;
}
export function Hud() {
  void game.ver.value; const s = game.s; if (!s) return null; const busy = !!game.phone.value || !!game.dialog.value; const goals = openGoals(s); const un = game.unreadCount();
  return <div class="hud" data-testid="hud">
    {!busy && <Markers />}
    <div class="bug"><div class="cell ch"><b>{s.channel}</b><span>{CHAPTERS[s.chapter]}</span></div><div class="cell"><b data-testid="clock">{timeStr(s.min)}</b><span>{weekday(s.day)}, day {s.day}</span></div><div class={'cell cash ' + (s.money < 0 ? 'neg' : '')}><b data-testid="money">{money(Math.floor(s.money))}</b><span>{s.subs ? `${fmt(s.subs)} subs` : 'cash'}</span></div><div class="cell"><b data-testid="followers">{fmt(s.followers)}</b><span>followers</span></div></div>
    {!busy && <div class="needs"><VU v={s.energy} icon={<Bolt s={17} c="#efe7d6" />} label="Energy" /><VU v={s.food} icon={<Fork s={17} c="#efe7d6" />} label="Food" /><VU v={s.vibe} icon={<Smile s={17} c="#efe7d6" />} label="Vibe" /></div>}
    {!busy && goals.length > 0 && <div class="todo" data-testid="todo"><h4><span>to do</span><span>ch. {s.chapter}</span></h4><ul>{goals.map((g) => { const p = g.prog?.(s); return <li key={g.id}><i />{g.text}{p && p[1] > 1 && <span class="pg">{fmt(Math.min(p[0], p[1]))}/{fmt(p[1])}</span>}</li>; })}</ul></div>}
    {!busy && <div class="dock"><button class="hit" data-testid="open-phone" onClick={() => game.openApp('home')}><PhoneI s={20} />Phone <Key k="Tab" />{un > 0 && <span class="bub">{un}</span>}</button><button class="hit" data-testid="sleep" onClick={() => game.interact('bed')}><Bed s={20} />Sleep</button><button class="hit go" data-testid="go-live" onClick={() => game.openApp('twinge')}><Mic s={22} />Go live</button></div>}
    {!busy && <div class="crawl"><b>News</b>{s.headline} <span style={{ color: '#8a7f6b' }}>{HOME[s.home].name}</span></div>}
  </div>;
}
