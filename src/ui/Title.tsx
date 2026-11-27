import { useEffect, useState } from 'preact/hooks';
import { game, PLAYERS } from '../game';
import { initAudio, sfx } from '../audio/audio';
import { Rich, img, fmt, money } from './bits';
import { Brand, Dice } from './icons';
import { RNG } from '../core/rng';
import { userName, userColor } from '../core/names';
import { weekday } from '../core/state';
import { HOME } from '../core/catalog';
import { PrefsPanel } from './Overlays';
const LINES = ['are we live?', 'chat is he live', 'the light is on but nobody’s home', 'first', ':kekwow:', 'bro forgot to press the button', 'is this the pizza place', 'mom says hi', 'hello from the bus', 'W intro', 'i’ve been here since before the big bang', 'LIVE :fire: :fire:', 'who is this', 'mods are asleep post feet', 'my cat clicked this', 'ratio', 'why is the loading screen better than the content', ':catjam: :catjam:', 'say something in raccoon'];
export function Title() {
  const saved = game.peek(); const [log, setLog] = useState<{ n: string; c: string; t: string }[]>([]); const [opt, setOpt] = useState(false);
  useEffect(() => { const r = new RNG(Date.now() & 0xffff); const iv = setInterval(() => setLog((l) => [...l.slice(-13), { n: userName(r), c: userColor(r), t: r.pick(LINES) }]), 900); return () => clearInterval(iv); }, []);
  const go = (f: () => void) => () => { initAudio(); sfx('click'); f(); };
  return <div class="title" data-testid="title">
    <div class="left">
      <h1 class="logo"><span class="l1">Chat, are we</span><span class="onair"><i />LIVE?</span></h1>
      <p class="sub">You have a cracked phone, a bed and zero followers. Somewhere out there is a mansion with your name on it.</p>
      <nav class="menu hit">
        {saved && <button class="item hit" data-testid="continue" onClick={go(() => game.continueGame())}>Continue<small>{saved.channel}, {weekday(saved.day)} (day {saved.day}), {fmt(saved.followers)} followers, {money(saved.money)}, {HOME[saved.home].name}</small></button>}
        <button class="item hit" data-testid="new-game" onClick={go(() => saved ? (game.dialog.value = { kind: 'confirm', data: { title: 'Start over?', text: `This deletes ${saved.channel} and all ${fmt(saved.followers)} followers. They will never know why.`, yes: 'Start over', no: 'Keep it', act: () => { game.dialog.value = null; game.openCreator(); } } }) : game.openCreator())}>{saved ? 'New streamer' : 'Go live'}</button>
        <button class="item hit" data-testid="options" onClick={go(() => setOpt(true))}>Options</button>
      </nav>
      <div class="foot">A game about being watched. All brands are fake. Any resemblance is their problem. Rendered with {game.eng?.backend ?? 'hope'}.</div>
    </div>
    <div class="ghostchat">{log.map((m, i) => <div key={i + m.n}><b style={{ color: m.c }}>{m.n}</b><Rich text={m.t} /></div>)}</div>
    {opt && <div class="scrim" onClick={(e) => e.target === e.currentTarget && setOpt(false)}><div class="pm" data-testid="options-panel"><h2>Options</h2><PrefsPanel /><button class="btn ghost" onClick={() => setOpt(false)}>Back</button></div></div>}
  </div>;
}
const CH = ['Plays', 'TV', 'Live', 'Gaming', 'OnAir', 'Unhinged', 'IRL', 'Zone'];
export function Creator() {
  const [i, setI] = useState(0); const [name, setName] = useState(PLAYERS[0].name); const [ch, setCh] = useState(PLAYERS[0].name + 'Plays'); const [dif, setDif] = useState<'chill' | 'normal' | 'grind'>('normal'); const [err, setErr] = useState(''); const p = PLAYERS[i]; const [touched, setT] = useState(false);
  const pick = (k: number) => { setI(k); game.pickCreator(k); if (!touched) { setName(PLAYERS[k].name); setCh(PLAYERS[k].name + 'Plays'); } };
  const start = (e: Event) => { e.preventDefault(); const n = name.trim(), c = ch.trim().replace(/\s+/g, ''); if (!n) return setErr('You need a name. Even “Steve” counts.'); if (c.length < 3) return setErr('Channel names need at least 3 characters.'); setErr(''); sfx('cash'); game.newGame({ name: n.slice(0, 16), channel: c.slice(0, 20), body: p.id, difficulty: dif }); };
  return <div class="creator" data-testid="creator">
    <div class="pick"><h2>{p.name}</h2><p>{p.bio}</p><div class="strip hit">{PLAYERS.map((q, k) => <button key={q.id} class={'hit ' + (k === i ? 'on' : '')} aria-label={`Choose ${q.name}`} data-testid={'body-' + q.id} onClick={() => pick(k)}><img src={img(`chars/${q.id}.webp`)} alt="" /></button>)}</div></div>
    <form class="form" onSubmit={start}>
      <div class="br">{Brand.twinge}Twinge</div><h3>Create your channel</h3><p class="l">Join 9 million streamers with an average audience of one (their mom).</p>
      <label for="nm">Your name</label><input id="nm" data-testid="name" maxLength={16} value={name} onInput={(e) => { setT(true); setName(e.currentTarget.value); }} />
      <label for="cn">Channel</label><div class="row"><input id="cn" data-testid="channel" maxLength={20} value={ch} onInput={(e) => { setT(true); setCh(e.currentTarget.value); }} /><button type="button" class="dice" aria-label="Random channel name" onClick={() => { sfx('tick'); setT(true); const r = new RNG(Math.random() * 1e9); setCh(r.chance(0.5) ? name.replace(/\s/g, '') + r.pick(CH) : userName(r).slice(0, 20)); }}><Dice /></button></div>
      <label>How hard should life be?</label><div class="row">{([['chill', 'Chill', 'Kind algorithm'], ['normal', 'Normal', 'As intended'], ['grind', 'Grindset', 'No sleep']] as const).map(([k, a, b]) => <button type="button" key={k} data-testid={'dif-' + k} class={'dif ' + (dif === k ? 'on' : '')} onClick={() => { sfx('click'); setDif(k); }}><b>{a}</b><span>{b}</span></button>)}</div>
      <div class="err" role="alert">{err}</div><p class="tos">By continuing you agree to the Terms, the other Terms, and that your sleep schedule now belongs to Twinge Interactive.</p><button class="btn big" data-testid="create" type="submit">Start streaming</button>
    </form>
  </div>;
}
