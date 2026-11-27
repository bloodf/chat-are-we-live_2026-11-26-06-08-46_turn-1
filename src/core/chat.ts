/** Chat text generation. Grammar-based, mood- and context-aware. */
import { RNG, clamp } from './rng';
import type { Viewer, ViewerStyle, Reaction } from './types';
import { emotionOf, type Emotion, type Mood } from './emotion';
import type { Speech } from './nlu';
export type ChatKind = 'msg' | 'system' | 'sub' | 'dono' | 'raid' | 'follow' | 'you' | 'mod';
export interface ChatMsg { id: number; kind: ChatKind; who: string; color: string; text: string; vid?: string; badges: string[]; emo?: Emotion; prompt?: Prompt; amount?: number; t: number; hi?: boolean }
export type PromptKind = 'question' | 'compliment' | 'troll' | 'sad' | 'backseat' | 'request' | 'sus' | 'hypeup' | 'dono' | 'drama' | 'regular';
export interface Prompt { kind: PromptKind; expires: number; done?: boolean; topic?: string; value?: number }
export const EMOTES = ['kekwow', 'pogchomp', 'sadge', 'catjam', 'monkaS', 'heart', 'fire', 'skull', 'clown', 'gg', 'ratio', 'yikes'] as const;
export type EmoteId = (typeof EMOTES)[number];
const E = (id: EmoteId) => `:${id}:`;

export type Ctx = { game: string; verb: string; mood: Mood; hype: number; viewers: number; name: string; min: number; quality: number; homeTitle: string; muted?: boolean; cracked?: boolean; afk?: boolean };

const IDLE: Record<ViewerStyle, string[]> = {
  wholesome: ['hope you drank water today', 'this is my favourite part of the day ngl', 'you’re doing great!! :heart:', 'first time catching you live, cozy in here', 'my cat is watching too', 'proud of you fr', 'sending good vibes from the bus'],
  memer: ['bro is speedrunning poverty :skull:', 'it’s giving side quest', 'he’s just like me fr', 'W stream', 'this is peak cinema', 'who let bro cook', 'live slug reaction', 'new copypasta just dropped', ':catjam: :catjam: :catjam:', 'ohio ahh gameplay', 'not the {home} lighting :kekwow:', 'chat is this real'],
  troll: ['mid', 'L stream', 'my grandma has better aim and she’s soup', 'dead game dead chat', 'is this stream in 144p on purpose', 'ratio', 'bro fell off before he got on', 'imagine watching this', '{n} viewers and three are you'],
  backseat: ['go left', 'you should’ve jumped', 'why didn’t you use the thing', 'trust me do the other strat', 'as a bronze player here’s what you did wrong', 'there’s a secret behind the pipe', 'press the other button'],
  simp: ['that smile tho :heart:', 'notice me pls', 'i told my therapist about you', 'i changed my ringtone to your intro', 'you looked at chat so basically we’re married', 'the voice >>>'],
  critic: ['audio’s a bit hot', 'pacing is better today', 'overlay needs work but content is there', 'bitrate dipped at {m} min', 'the lighting is very “hostage video”', 'unironically improved since last week'],
  kid: ['hi im 9', 'do you like turtles', 'my mom says 5 more minutes', 'can i be mod', 'say hi to my dog', 'PLAY MINEDCRAFT', 'i beat this game when i was 6', 'what’s a tax'],
  lurker: ['o/', 'lurking', 'back', 'nice', 'hm', '.', 'ty for stream'],
  conspiracy: ['pause at {m}:13 the poster blinks', 'he’s reading off a script', 'this is pre-recorded', 'the pipes spell out a name', 'birds aren’t viewers either', 'that’s not the same shirt as yesterday. clone.'],
  elder: ['HELLO IT IS GERALD. HOW DO I TURN ON CHAT', 'Back in my day we streamed uphill both ways', 'My grandson set this up for me. Lovely.', 'Is this the weather channel', 'You have a nice face dear. Eat something.'],
};
const REACT: Record<string, string[]> = {
  fail: ['LMAOOO', ':skull: :skull:', 'L', 'the fall off', 'RIP BOZO', 'nahhh', 'F', 'F in chat', 'I physically felt that', 'skill issue', 'clip it', 'bro.', ':kekwow:', 'we do not talk about that'],
  clutch: ['WHAT', 'NO WAY', ':pogchomp: :pogchomp:', 'HE’S HIM', 'CLIP THAT', 'ACTUALLY CRACKED', 'W', 'WWWWWW', 'HOW', 'aimbot confirmed', ':fire: :fire:'],
  combo: ['ok ok', 'he’s cooking', 'let him cook', ':catjam:', 'smooth', 'W', 'satisfying ngl'],
  record: ['NEW RECORD??', 'HISTORY', 'I WAS HERE', ':pogchomp:', 'mom get the camera', 'screenshotting this'],
  scare: ['MY HEADPHONES', ':monkaS:', 'JUMPED OUT MY CHAIR', 'i spilled soup', 'AAAAAA'],
  win: ['GG', ':gg: :gg: :gg:', 'WINNER WINNER TOFU DINNER', 'LETS GOOOO', 'actual goat', ':fire:'],
  bored: ['...', 'zzz', 'anyone wanna talk about soup', 'brb making toast', 'say something', 'is it frozen', ':sadge:'],
  afk: ['bro is AFK', 'hello??', 'is he ok', 'he’s typing an essay', 'the game is playing itself'],
  mute: ['MIC', 'YOU’RE MUTED', 'mic muted', 'we can’t hear you', 'is this a silent film', 'MUTED MUTED MUTED', 'lip reading rn'],
  lag: ['lag', 'LAGGING', 'powerpoint presentation', '3 fps', 'buffering speedrun', 'is he streaming from a submarine', ':ratio: your ISP'],
  crack: ['bro’s screen has more cracks than my house', 'buy a phone', 'the crack is the real boss'],
};
const REACT_TO: Record<Reaction, string[]> = {
  laugh: [':kekwow:', 'his laugh is contagious', 'LMAO stop', 'wheezing'], hype: ['LETS GOOO', ':fire:', 'I’M UP', 'HYPE', ':pogchomp:'], rage: ['HE’S MALDING', 'rage arc', 'protect the phone', ':skull:', 'breathe king'],
  cry: [':sadge:', 'bro needs a hug', 'don’t cry ur too rich… wait', 'group hug'], shock: [':monkaS:', 'THE FACE', 'new emote just dropped', 'YOUTUBE THUMBNAIL FACE'], dance: [':catjam:', 'HE’S GROOVING', 'the moves are illegal', 'dad at wedding energy', 'BUST IT DOWN'],
};
const WRONG: string[] = ['??? why are you {v}', 'wrong emotion bro', 'forced', ':yikes:', 'acting class when', 'NPC behaviour'];
const PROMPTS: Record<PromptKind, string[]> = {
  question: ['what’s your biggest fear?', 'why did you start streaming?', 'cereal first or milk first??', 'how tall are you', 'what’s your most embarrassing story?', 'favourite game of all time?', 'would you fight one horse-sized duck?', 'do you have a job job?', 'what would you do with a million dollars?', 'is a hot dog a sandwich', 'do your parents know about this?', 'what’s your sleep schedule', 'when are you getting a better {gear}?'],
  compliment: ['you’re genuinely the funniest streamer I’ve found', 'this stream got me through finals', 'your energy is unreal today', 'I told my whole class about you', 'you deserve 100x the viewers', 'best community on Twinge fr'],
  troll: ['you’re only popular because of your chair', 'fake laugh', 'my fridge has more charisma', 'quit streaming challenge (impossible)', '{rival} does this better', 'your mom said I could have your channel', 'carried by the algorithm', 'washed before prime'],
  sad: ['rough day today, got fired', 'my dog passed this morning. thanks for being live', 'feeling pretty alone tbh', 'failed my exam again', 'can’t sleep again, you’re good company', 'my best friend moved away'],
  backseat: ['you’re playing it wrong, hold it sideways', 'literally just go up. UP.', 'you need to farm more before this', 'why would you not just win', 'let me play, give me the controller through the screen'],
  request: ['can you say happy birthday to my sister Kelsey', 'do the worm', 'do an accent!', 'sing something', 'show your room!', 'play with your eyes closed', 'do a handstand on stream', 'call your mom live'],
  sus: ['free followers bit.ly/totally-real', 'hey i am prince, i need your bank for 1 minute', 'click here for hot singles in your router', 'your channel will be deleted, verify at twinge-support.biz', 'I can make you verified, just give password'],
  hypeup: ['chat if we spam he’ll do a backflip', 'HYPE TRAIN WHEN', 'everybody type W', 'can we get a LETS GO', 'we’re so close to the goal!!'],
  dono: ['keep it up!', 'take my lunch money', 'for the new {gear} fund', 'I sold my bike for this', 'use this for therapy', 'my boss is watching me type this'],
  drama: ['did you see what {rival} said about you?', 'is it true you faked that clip?', 'someone on Chirper says you’re an industry plant', 'address the allegations', 'why’d you unfollow {rival}'],
  regular: ['remember when you promised to shoutout my podcast', 'it’s my 3 month watchiversary!', 'I’ve been here since 4 viewers. don’t forget us.', 'I made you fan art (it’s a potato but with your hair)', 'you replied to me last week and I’m still thinking about it'],
};
export const PROMPT_KINDS = Object.keys(PROMPTS) as PromptKind[];
const EMO_SPICE: Partial<Record<Emotion, string[]>> = { ecstatic: ['I’M SO HAPPY', 'best stream ever'], angry: ['im so done', 'this is annoying'], furious: ['REFUND', 'unfollowing'], bored: ['anything happening?', 'zz'], sad: [':sadge:'], hyped: ['LET’S GO', ':fire:'], anxious: [':monkaS: :monkaS:'], amused: [':kekwow:', 'lol'], hurt: ['ouch ok', 'didn’t expect that from you'] };
const TYPOS: Record<string, string> = { the: 'teh', you: 'u', your: 'ur', are: 'r', because: 'cuz', please: 'pls', really: 'rly', what: 'wut' };
export function fill(rng: RNG, s: string, c: Partial<Ctx> & { v?: string } = {}): string {
  return s.replace('{n}', String(Math.max(1, Math.round(c.viewers ?? 3)))).replace('{m}', String(Math.max(1, Math.round(c.min ?? 1)))).replace('{home}', (c.homeTitle ?? 'room').toLowerCase()).replace('{v}', c.v ?? 'doing that')
    .replace('{gear}', () => rng.pick(['mic', 'phone', 'chair', 'webcam', 'ring light'])).replace('{rival}', () => rng.pick(['Mr. Feast', 'Pokimeme', 'xQueasy', 'Kai Cement', 'your cousin Brayden']));
}
const outsideEmotes = (t: string, f: (x: string) => string) => t.split(/(:[a-zA-Z]+:)/g).map((x) => (/^:[a-zA-Z]+:$/.test(x) ? x : f(x))).join('');
export function styleText(rng: RNG, v: Viewer | null, text: string): string {
  if (!v) return rng.chance(0.3) ? outsideEmotes(text, (x) => x.toLowerCase()) : text;
  const emo = emotionOf(v.mood); let t = text;
  if (v.style === 'kid' && rng.chance(0.4)) t = outsideEmotes(t, (x) => x.toUpperCase());
  if ((v.style === 'memer' || v.style === 'troll') && rng.chance(0.5)) t = outsideEmotes(t, (x) => x.toLowerCase());
  if (v.style === 'kid' || v.style === 'memer') t = outsideEmotes(t, (x) => x.replace(/\b(the|you|your|are|because|please|really|what)\b/gi, (m) => (rng.chance(0.35) ? TYPOS[m.toLowerCase()] : m)));
  if ((emo === 'hyped' || emo === 'ecstatic' || emo === 'furious') && rng.chance(0.4) && v.style !== 'elder') t = outsideEmotes(t, (x) => x.toUpperCase());
  if (rng.chance(0.08) && v.catch) t += ' ' + v.catch;
  return t;
}
export function idleLine(rng: RNG, v: Viewer | null, c: Ctx): string {
  if (c.muted && rng.chance(0.75)) return rng.pick(REACT.mute);
  if (c.afk && rng.chance(0.5)) return rng.pick(REACT.afk);
  if (c.quality < 0.45 && rng.chance(0.25)) return rng.pick(REACT.lag);
  if (c.cracked && rng.chance(0.06)) return rng.pick(REACT.crack);
  if (c.hype < 16 && rng.chance(0.3)) return rng.pick(REACT.bored);
  if (v) { const sp = EMO_SPICE[emotionOf(v.mood)]; if (sp && rng.chance(0.3)) return styleText(rng, v, rng.pick(sp)); }
  const st = v?.style ?? rng.weighted(['memer', 'lurker', 'wholesome', 'kid', 'troll'] as ViewerStyle[], (s) => ({ memer: 4, lurker: 2, wholesome: 2, kid: 1, troll: c.mood.p < 0 ? 2.5 : 0.7 } as Record<string, number>)[s]);
  return styleText(rng, v, fill(rng, rng.pick(IDLE[st]), c));
}
export function reactLine(rng: RNG, key: string, v: Viewer | null = null): string { return styleText(rng, v, rng.pick(REACT[key] ?? REACT.combo)); }
export function reactToStreamer(rng: RNG, r: Reaction, ok: boolean): string { return ok ? rng.pick(REACT_TO[r]) : fill(rng, rng.pick(WRONG), { v: { laugh: 'laughing', hype: 'hyped', rage: 'mad', cry: 'crying', shock: 'shocked', dance: 'dancing' }[r] }); }
export function promptLine(rng: RNG, k: PromptKind, c: Partial<Ctx>): string { return fill(rng, rng.pick(PROMPTS[k]), c); }
export function replyToSpeech(rng: RNG, s: Speech, v: Viewer | null, good: number): string {
  const t = s.topic;
  const by: Partial<Record<Speech['intent'], string[]>> = {
    greet: ['hiiii', 'o/', 'YO', 'hello streamer', 'hi mom'], thanks: [':heart:', 'np king', 'we got you', 'awww'], beg: good > 0 ? ['ok fine, followed', 'smashed it', 'took my prime'] : ['bro is begging', 'thirsty', 'say please', ':yikes:'],
    question: t ? [`${t}? definitely`, 'depends', 'yes', 'no', `idk about ${t} but i’m hungry`, 'B', 'hot take: no'] : ['yes', 'no', 'maybe', 'B'], joke: good > 0 ? [':kekwow:', 'LMAOO', 'ok that was good', 'stolen but good'] : ['crickets', 'dad?', ':clown:', 'who asked'],
    hype: ['LETS GOOO', ':fire: :fire:', 'W', 'I’M READY'], insult: v && v.bond.affinity > 25 ? ['lmao roasted', 'we deserved that', 'love you too'] : ['rude', 'ok unfollow', 'damn', 'he hates us', 'emotional damage'],
    apology: good > 0 ? ['all good', 'forgiven :heart:', 'ok ok we move'] : ['notes app apology when', 'not buying it', ':clown:'], vent: [':sadge:', 'we’re here for you', 'take a break king', 'same tbh', 'hugs'], love: [':heart: :heart:', 'awww', 'WE LOVE YOU', 'stop i’m blushing'],
    promise: ['clipped for court', 'we’ll remember that', 'HE PROMISED', 'source: trust me bro'], brag: good > 0 ? ['he’s not wrong', 'king behaviour'] : ['humble challenge: failed', 'ok mr. ego'], bye: ['nooo', 'gn :heart:', 'one more game', 'bye!!'], motivate: ['tearing up', 'PREACH', 'i’m quitting my job rn', 'ok coach'],
    hottake: t ? [`${t} slander?!`, `finally someone said it about ${t}`, 'WRONG', 'based', 'banned'] : ['WRONG', 'based', 'cancelled'], sing: good > 0 ? ['VOCALS', 'drop the album', ':catjam:'] : ['my ears', 'autotune crying', 'the dog left'], poll: ['A', 'B', 'A', 'C?', 'second one'],
    ad: ['sellout (affectionate)', 'get that bag', 'skip ad', 'used the code'], story: ['go on', 'STORYTIME', 'and then??', 'grabs popcorn'], nonsense: ['bro had a stroke', 'translate??', 'new language unlocked', 'keyboard cat?'], game: t ? [`${t} is busted`, 'skill issue', 'facts'] : ['facts', 'skill issue'],
    statement: t ? [`did bro just say ${t}`, `${t} :skull:`, 'true', 'real', `the ${t} lore`, 'ok'] : ['true', 'real', 'ok', 'same'],
  };
  return styleText(rng, v, rng.pick(by[s.intent] ?? by.statement!));
}
export const CATCHES = [':skull:', 'fr fr', 'no cap', 'just saying', 'xD', '>:3', 'tbh', ':clown:', 'lolol', '(real)', 'allegedly'];

const PRON: Record<string, string> = { he: 'she', him: 'her', his: 'her', king: 'queen', dad: 'mom' };
const FEM = new Set(['p_zoe', 'p_mei', 'p_ivy']);
/** chat refers to the player with the right pronouns */
export function pronouns(text: string, body: string): string { if (!FEM.has(body)) return text; return text.replace(/\b(he|him|his|king)\b/gi, (m) => { const r = PRON[m.toLowerCase()]; return m === m.toUpperCase() && m.length > 1 ? r.toUpperCase() : m[0] === m[0].toUpperCase() ? r[0].toUpperCase() + r.slice(1) : r; }); }
