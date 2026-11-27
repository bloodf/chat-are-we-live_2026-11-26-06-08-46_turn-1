/** Tiny on-device language understanding: turns whatever the player types to chat into a speech act. */
import { clamp } from './rng';
export type Intent = 'greet' | 'thanks' | 'beg' | 'question' | 'joke' | 'hype' | 'insult' | 'apology' | 'vent' | 'love' | 'game' | 'promise' | 'brag' | 'bye' | 'motivate' | 'hottake' | 'sing' | 'poll' | 'ad' | 'story' | 'nonsense' | 'statement';
export interface Speech { intent: Intent; sentiment: number; energy: number; target?: string; topic?: string; words: string[]; swear: boolean; len: number; raw: string }
const L: Record<string, string[]> = {
  greet: ['hi', 'hello', 'hey', 'yo', 'sup', 'welcome', 'hiya', 'howdy', 'morning', 'evening', 'wassup', 'heya', 'hola', 'oi', 'ola', 'salut'],
  thanks: ['thanks', 'thank', 'ty', 'thx', 'appreciate', 'grateful', 'cheers', 'obrigado', 'gracias', 'merci'],
  beg: ['follow', 'subscribe', 'sub', 'subs', 'donate', 'dono', 'bits', 'tip', 'gift', 'gifted', 'prime', 'smash'],
  joke: ['lol', 'lmao', 'haha', 'hahaha', 'rofl', 'joke', 'kidding', 'knock', 'pun', 'funny', 'bazinga', 'jk'],
  hype: ['lets', 'letsgo', 'pog', 'poggers', 'hype', 'insane', 'clutch', 'woo', 'yes', 'goated', 'fire', 'lit', 'epic', 'cracked', 'gooo', 'goo', 'go', 'win', 'ez'],
  insult: ['stupid', 'idiot', 'dumb', 'trash', 'noob', 'loser', 'ugly', 'hate', 'shut', 'clown', 'cringe', 'ratio', 'worst', 'pathetic', 'annoying', 'moron', 'suck', 'sucks'],
  apology: ['sorry', 'apologize', 'apologise', 'apology', 'forgive', 'regret', 'mybad'],
  vent: ['sad', 'tired', 'depressed', 'lonely', 'stressed', 'exhausted', 'cry', 'crying', 'anxious', 'burnout', 'struggling', 'broke', 'hard', 'miss'],
  love: ['love', 'adore', 'family', 'best', 'amazing', 'beautiful', 'wholesome', 'kind', 'sweet', 'awesome', 'legends', 'legend', 'goats', 'cute'],
  game: ['game', 'level', 'boss', 'play', 'playing', 'aim', 'score', 'pipe', 'lag', 'nerf', 'buff', 'controller', 'speedrun', 'respawn', 'combo'],
  promise: ['giveaway', 'promise', 'swear', 'tomorrow', 'next', 'will', 'gonna', 'soon'],
  brag: ['rich', 'famous', 'best', 'goat', 'better', 'easy', 'talented', 'genius', 'handsome', 'gorgeous', 'million'],
  bye: ['bye', 'goodbye', 'goodnight', 'gn', 'cya', 'later', 'peace', 'raid', 'tchau', 'adios'],
  motivate: ['believe', 'dream', 'never', 'proud', 'grind', 'together', 'chase', 'achieve', 'hustle'],
  hottake: ['actually', 'overrated', 'underrated', 'opinion', 'unpopular', 'controversial', 'pineapple', 'politics', 'anime', 'cereal', 'hotdog', 'sandwich', 'fact'],
  sing: ['la', 'lala', 'sing', 'singing', 'song', 'beatbox', 'rap', 'music', 'karaoke'],
  poll: ['vote', 'poll', 'type', 'choose', 'pick', 'option'],
  ad: ['sponsor', 'sponsored', 'code', 'promo', 'discount', 'link', 'bordvpn', 'vpn', 'raid:', 'hellofrush', 'partnered'],
  story: ['once', 'yesterday', 'remember', 'story', 'storytime', 'happened', 'when', 'childhood', 'kid'],
};
const SWEAR = new Set(['damn', 'hell', 'crap', 'fuck', 'shit', 'bitch', 'ass', 'wtf', 'stfu', 'bastard', 'fucking', 'fucked', 'bullshit']);
const POS = new Set([...L.thanks, ...L.love, ...L.hype, 'good', 'great', 'nice', 'happy', 'fun', 'cool', 'wow', 'perfect', 'excited', 'glad', 'win', 'won', 'yay', 'brilliant', 'sick']);
const NEG = new Set([...L.insult, ...L.vent, 'bad', 'terrible', 'awful', 'angry', 'lose', 'lost', 'boring', 'broken', 'worse', 'die', 'dead', 'ugh', 'no', 'never', 'fail', 'pain', 'mad', 'toxic']);
const NEGATE = new Set(['not', "don't", 'dont', "isn't", 'isnt', "ain't", 'never', "can't", 'cant', "won't", 'no']);
const STOP = new Set('the a an i you we they he she it is are was were be been to of in on for and or but so that this my your our me u do does did have has had just really very with at as if not im its can all what who why how when where there here get got like'.split(' '));
const PRI: Record<string, number> = { apology: 1.7, thanks: 1.55, greet: 1.25, bye: 1.35, beg: 1.3, ad: 1.3, insult: 1.25, love: 1.1, vent: 1.15, joke: 1.1, poll: 1.0, hottake: 1.05, motivate: 1, hype: 1, sing: 1.15, brag: 0.85, promise: 0.85, story: 0.8, game: 0.75 };
export function understand(raw: string, names: string[] = []): Speech {
  const text = raw.trim().slice(0, 240); const low = text.toLowerCase();
  const words: string[] = (low.match(/[@a-z0-9_à-ÿ':]+/g) ?? []);
  const score: Record<string, number> = {};
  let s = 0, neg = 0;
  words.forEach((w) => {
    const b = w.replace(/^@/, '').replace(/(.)\1{2,}/g, '$1$1');
    for (const k in L) if (L[k].includes(b) || L[k].includes(w)) score[k] = (score[k] ?? 0) + PRI[k];
    if (NEGATE.has(b)) { neg = 3; } const flip = neg > 0 && !NEGATE.has(b) ? -0.8 : 1; if (neg > 0) neg--;
    if (POS.has(b)) s += flip; if (NEG.has(b)) s -= flip;
  });
  if (/\b(let'?s+ go+|lfg+)\b/.test(low)) score.hype = (score.hype ?? 0) + 2;
  if (/\b(link in|use code|today'?s sponsor|brought to you)\b/.test(low)) score.ad = (score.ad ?? 0) + 2.4;
  if (/\b(good ?night|see (you|ya)|end(ing)? (the )?stream)\b/.test(low)) score.bye = (score.bye ?? 0) + 2;
  if (/\b(my bad|i'?m sorry)\b/.test(low)) score.apology = (score.apology ?? 0) + 2;
  if (/\b(i|we) love\b/.test(low)) score.love = (score.love ?? 0) + 1.4;
  if (/\bwhy did the|walks into a bar|knock knock|your mom\b/.test(low)) score.joke = (score.joke ?? 0) + 2.5;
  if (/\?\s*$/.test(text) || /^(what|who|why|how|when|where|do|does|did|are|is|should|would|can|which)\b/.test(low)) score.question = (score.question ?? 0) + 1.2;
  let target: string | undefined;
  for (const n of names) { const ln = n.toLowerCase(); if (low.includes('@' + ln) || words.includes(ln)) { target = n; break; } }
  const letters = text.replace(/[^a-zA-Z]/g, ''); const caps = letters.length > 3 ? letters.replace(/[^A-Z]/g, '').length / letters.length : 0;
  const ex = (text.match(/!/g) ?? []).length;
  const energy = clamp(caps * 0.7 + ex * 0.15 + (score.hype ? 0.3 : 0) + (/(.)\1{3,}/.test(low) ? 0.2 : 0));
  const swear = words.some((w) => SWEAR.has(w));
  let intent: Intent = 'statement', best = 0.7;
  for (const k in score) if (score[k] > best) { best = score[k]; intent = k as Intent; }
  const vowels = (low.match(/[aeiouyà-ÿ]/g) ?? []).length; const gib = letters.length >= 6 && (vowels / letters.length < 0.14 || /([bcdfghjklmnpqrstvwxz])(?!\1)[bcdfghjklmnpqrstvwxz]{5,}/.test(low));
  if (gib && best <= 0.7) intent = 'nonsense';
  const topics = words.filter((w) => w.length > 3 && !STOP.has(w) && !SWEAR.has(w)).sort((a, b) => b.length - a.length);
  let sentiment = clamp(s / Math.max(1.6, Math.sqrt(words.length) * 1.1), -1, 1);
  if (intent === 'insult' && sentiment > -0.3) sentiment = -0.4; if ((intent === 'love' || intent === 'thanks') && sentiment < 0.3) sentiment = 0.4;
  return { intent, sentiment, energy, target, topic: topics[0], words, swear, len: words.length, raw: text };
}
