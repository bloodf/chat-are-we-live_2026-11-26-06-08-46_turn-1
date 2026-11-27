import type { HomeId, Role, SlotId } from './types';
export interface Item { id: string; slot: SlotId; brand: string; name: string; price: number; tier: number; q: number; dur: number; blurb: string; prop?: string; unlock?: number; caps?: ('mobile' | 'pc' | 'aaa')[]; rate: string; stars: number }
export const ITEMS: Item[] = [
  // devices -----------------------------------------------------------------
  { id: 'phone0', slot: 'device', brand: 'Nokidding', name: '3310½ (screen: mostly there)', price: 0, tier: 0, q: 0.5, dur: 0.62, caps: ['mobile'], prop: 'phone0', blurb: 'A hand-me-down from your mom. Battery lasts one (1) opinion.', rate: 'still works if u squint', stars: 2 },
  { id: 'phone1', slot: 'device', brand: 'Samsnug', name: 'Galaxy Brain A13', price: 180, tier: 1, q: 0.72, dur: 0.8, caps: ['mobile'], prop: 'phone1', blurb: 'Four cameras. Three are stickers.', rate: 'explodes less than the last one', stars: 4 },
  { id: 'phone2', slot: 'device', brand: 'Pear', name: 'pPhone 27 Pro Max Ultra Tax', price: 1199, tier: 2, q: 0.95, dur: 0.88, caps: ['mobile'], prop: 'phone2', unlock: 150, blurb: 'Titanium. Charger, box and dignity sold separately.', rate: 'sold a kidney, 10/10', stars: 5 },
  { id: 'laptop0', slot: 'device', brand: 'Hewlett-Hackard', name: 'StoveBook 15', price: 640, tier: 3, q: 0.92, dur: 0.72, caps: ['mobile', 'pc'], prop: 'laptop0', unlock: 120, blurb: 'Doubles as a panini press under load.', rate: 'burned my thighs AND my savings', stars: 3 },
  { id: 'pc0', slot: 'device', brand: 'Beast Buy', name: 'Prebuilt of Regret', price: 1500, tier: 4, q: 1.1, dur: 0.8, caps: ['mobile', 'pc', 'aaa'], prop: 'pc0', unlock: 700, blurb: 'One stick of RAM, twelve fans, all RGB.', rate: 'cable management by raccoons', stars: 3 },
  { id: 'pc1', slot: 'device', brand: 'Nvidiot', name: 'GeFarce RTZ 4070 Rig', price: 3800, tier: 5, q: 1.32, dur: 0.88, caps: ['mobile', 'pc', 'aaa'], prop: 'pc1', unlock: 6000, blurb: 'Ray tracing so real it files taxes.', rate: 'my room is now a sauna', stars: 4 },
  { id: 'pc2', slot: 'device', brand: 'Nvidiot × AMDone', name: 'RTZ 6090 Tie + Ryzin 9', price: 14500, tier: 6, q: 1.6, dur: 0.93, caps: ['mobile', 'pc', 'aaa'], prop: 'pc2', unlock: 90000, blurb: 'Draws more power than Luxembourg.', rate: 'lights dim when I alt-tab', stars: 5 },
  { id: 'pc3', slot: 'device', brand: 'NASA’nt', name: 'THE MAINFRAME (golden loop)', price: 240000, tier: 7, q: 2.0, dur: 0.97, caps: ['mobile', 'pc', 'aaa'], prop: 'pc3', unlock: 4_000_000, blurb: '24-karat water cooling. The water is also rich.', rate: 'it called me “sir”', stars: 5 },
  // mics ---------------------------------------------------------------------
  { id: 'mic0', slot: 'mic', brand: 'Pear', name: 'AirPoddles (left one only)', price: 49, tier: 1, q: 0.08, dur: 0.8, prop: undefined, blurb: 'Sounds like you’re calling from inside a whale.', rate: 'dog ate the right one too', stars: 2 },
  { id: 'mic1', slot: 'mic', brand: 'Bleu', name: 'Abominable Yeti', price: 139, tier: 2, q: 0.18, dur: 0.92, prop: 'mic1', unlock: 40, blurb: 'Picks up your voice, your neighbours, and Tuesday.', rate: 'heard my landlord think', stars: 4 },
  { id: 'mic2', slot: 'mic', brand: 'Sure Jan', name: 'SM7Bee', price: 420, tier: 3, q: 0.3, dur: 0.96, prop: 'mic2', unlock: 2500, blurb: 'Every podcaster’s emotional support object.', rate: 'I have opinions now', stars: 5 },
  // cams ---------------------------------------------------------------------
  { id: 'cam0', slot: 'cam', brand: 'Logitick', name: 'C92-Oh-No', price: 79, tier: 1, q: 0.1, dur: 0.9, prop: 'cam0', unlock: 60, blurb: '1080p, where the p stands for “probably”.', rate: 'I am 14 pixels of handsome', stars: 3 },
  { id: 'cam1', slot: 'cam', brand: 'Elgoto', name: 'Facecam Pro-ish', price: 299, tier: 2, q: 0.2, dur: 0.93, prop: 'cam0', unlock: 1500, blurb: 'So sharp your mom texts about your pores.', rate: 'my pores have fans', stars: 4 },
  { id: 'cam2', slot: 'cam', brand: 'Sonny', name: 'A7 IV (the Roman one)', price: 3600, tier: 3, q: 0.36, dur: 0.95, prop: 'cam2', unlock: 40000, blurb: 'Shallow depth of field for deep feelings.', rate: 'background so blurry I forgot I live here', stars: 5 },
  // lights ---------------------------------------------------------------------
  { id: 'light0', slot: 'light', brand: 'IKEYÅ', name: 'LÅMPJE', price: 19, tier: 1, q: 0.05, dur: 0.9, prop: 'lamp0', blurb: 'Includes 1 spare screw and 3 spare feelings.', rate: 'assembled it upside down, still a lamp', stars: 4 },
  { id: 'light1', slot: 'light', brand: 'Precious', name: 'Lord of the Ring Light', price: 89, tier: 2, q: 0.13, dur: 0.9, prop: 'ring', unlock: 25, blurb: 'One ring to light them all.', rate: 'my eyes have halos now', stars: 5 },
  { id: 'light2', slot: 'light', brand: 'Elgoto', name: 'Key Light & Peele', price: 520, tier: 3, q: 0.22, dur: 0.95, prop: 'softbox', unlock: 5000, blurb: 'Cinema lighting for horror-level bills.', rate: 'looks like a film, lit like a crime', stars: 5 },
  // chairs ---------------------------------------------------------------------
  { id: 'chair0', slot: 'chair', brand: 'Grandma', name: 'Kitchen Chair (haunted)', price: 0, tier: 0, q: 0, dur: 0.9, prop: 'chair0', blurb: 'Creaks in B flat.', rate: 'it remembers me', stars: 3 },
  { id: 'chair1', slot: 'chair', brand: 'Office Despot', name: 'Swivel of Mediocrity', price: 95, tier: 1, q: 0.04, dur: 0.9, prop: 'chair1', blurb: 'Ergonomic, in the sense that it is a chair.', rate: 'rolled into traffic', stars: 3 },
  { id: 'chair2', slot: 'chair', brand: 'SecretLabrador', name: 'Titan Good Boy XL', price: 480, tier: 2, q: 0.1, dur: 0.95, prop: 'chair2', unlock: 900, blurb: 'Racing seat for people who never move.', rate: 'back pain but with stripes', stars: 4 },
  { id: 'chair3', slot: 'chair', brand: 'Herman Millionaire', name: 'Aeron’t You Rich', price: 1900, tier: 3, q: 0.16, dur: 0.98, prop: 'chair1', unlock: 60000, blurb: 'Mesh woven from shredded invoices.', rate: 'my spine sent a thank-you card', stars: 5 },
  { id: 'chair4', slot: 'chair', brand: 'Monarchy Depot', name: 'The Golden Throne', price: 55000, tier: 4, q: 0.22, dur: 0.99, prop: 'chair4', unlock: 2_000_000, blurb: 'Heavy is the head. Numb is the butt.', rate: 'bowed to myself', stars: 5 },
  // internet -------------------------------------------------------------------
  { id: 'net0', slot: 'net', brand: 'Neighbour', name: '“Pretty Fly for a Wi-Fi”', price: 0, tier: 0, q: -0.12, dur: 0.6, blurb: 'Password: password. Shared with eleven vapers.', rate: 'stop changing the password Greg', stars: 2 },
  { id: 'net1', slot: 'net', brand: 'Comcrash', name: 'Xfinitely Buffering 20', price: 60, tier: 1, q: 0, dur: 0.78, blurb: 'Technician arrives between 8 AM and the heat death of the universe.', rate: 'on hold since 2019', stars: 1 },
  { id: 'net2', slot: 'net', brand: 'Spectrumble', name: 'Fiber (high in)', price: 240, tier: 2, q: 0.12, dur: 0.93, unlock: 800, blurb: 'Up to gigabit! “Up to” is doing heavy lifting.', rate: 'regular and fast', stars: 4 },
  { id: 'net3', slot: 'net', brand: 'Starlunk', name: 'Orbital Laser Uplink', price: 2600, tier: 3, q: 0.2, dur: 0.97, unlock: 50000, blurb: 'Pew pew, but for bandwidth.', rate: 'ping visible from space', stars: 5 },
  // vibe ---------------------------------------------------------------------
  { id: 'led0', slot: 'led', brand: 'Goveeeee', name: 'Epilepsy-Lite LED Strips', price: 35, tier: 1, q: 0.05, dur: 0.93, unlock: 15, blurb: 'Sixteen million colours. You will use purple.', rate: 'my room is a vape', stars: 4 },
  { id: 'led1', slot: 'led', brand: 'Nanothief', name: 'Hex Panels of Hubris', price: 640, tier: 2, q: 0.1, dur: 0.96, unlock: 8000, blurb: 'Geometric proof you have disposable income.', rate: 'bees are interested', stars: 5 },
  { id: 'plant', slot: 'decor2', brand: 'Fernando’s', name: 'Emotional Support Plant', price: 28, tier: 1, q: 0.03, dur: 1, prop: 'plant', blurb: 'Photosynthesises. Judges you.', rate: 'outlived my relationship', stars: 5 },
  { id: 'plush', slot: 'decor2', brand: 'Squishmehlow', name: 'Gerald the Unbothered', price: 60, tier: 2, q: 0.05, dur: 1, prop: 'plush', unlock: 200, blurb: 'A round guy. Zero ambition. Icon.', rate: 'he is my manager now', stars: 5 },
  { id: 'neon', slot: 'decor1', brand: 'Live Laugh Lag', name: 'Custom Neon “GG”', price: 150, tier: 1, q: 0.06, dur: 1, prop: 'neon', unlock: 300, blurb: 'Illegally bright. Legally binding.', rate: 'burned GG into my retina', stars: 4 },
  { id: 'silver', slot: 'decor1', brand: 'MeTube', name: 'Silver-ish Play Button', price: 0, tier: 2, q: 0.1, dur: 1, prop: 'silver', unlock: 100000, blurb: 'Awarded at 100K. Smells like achievement.', rate: 'cried on it', stars: 5 },
  { id: 'goldbtn', slot: 'decor1', brand: 'MeTube', name: 'Gold-ish Play Button', price: 0, tier: 3, q: 0.16, dur: 1, prop: 'goldbtn', unlock: 1_000_000, blurb: 'One million people can’t be right.', rate: 'licked it', stars: 5 },
];
export const ITEM = Object.fromEntries(ITEMS.map((i) => [i.id, i])) as Record<string, Item>;
export interface Home { id: HomeId; name: string; price: number; rent: number; need: number; beds: string; blurb: string; staffCap: number; q: number; listing: string; sqft: string }
export const HOMES: Home[] = [
  { id: 'bedroom', name: 'Childhood Bedroom', price: 0, rent: 0, need: 0, beds: '1 twin bed', sqft: '180 sq ft', staffCap: 0, q: 0, blurb: 'Free rent, free snacks, free judgement.', listing: 'Cozy. Poster-forward. Landlord knocks without waiting and calls you “sweetie”.' },
  { id: 'studio', name: 'The Shoebox Studio', price: 900, rent: 38, need: 250, beds: 'Studio (the bed is the living room)', sqft: '360 sq ft', staffCap: 0, q: 0.08, blurb: 'Your own place. Every appliance within arm’s reach.', listing: 'Charming exposed brick! (the rest of the wall left). Motivated landlord, unmotivated plumbing.' },
  { id: 'loft', name: 'Downtown Loft', price: 9500, rent: 190, need: 8000, beds: '1 bed, 1 personality', sqft: '1,150 sq ft', staffCap: 2, q: 0.18, blurb: 'Skyline views and a dedicated streaming corner. First hires unlocked.', listing: 'Floor-to-ceiling windows so your enemies can see you thriving.' },
  { id: 'hq', name: 'Content Warehouse', price: 160000, rent: 1600, need: 150000, beds: '1 couch (industrial)', sqft: '9,400 sq ft', staffCap: 6, q: 0.32, blurb: 'Sets, edit bay, arcade. Produce full-scale shows.', listing: 'Former sock factory. Zoned for commercial, residential and chaos.' },
  { id: 'mansion', name: 'The Mansion', price: 4_000_000, rent: 9000, need: 8_000_000, beds: '11 beds, 14 baths, 1 aquarium', sqft: '31,000 sq ft', staffCap: 8, q: 0.5, blurb: 'Ocean views, golden battle station, a ring for life-changing challenges.', listing: 'Built for a hedge fund manager, foreclosed by karma. Fish included.' },
];
export const HOME = Object.fromEntries(HOMES.map((h) => [h.id, h])) as Record<HomeId, Home>;
export interface GameDef { id: string; name: string; need: 'mobile' | 'pc' | 'aaa' | 'none'; verb: string; blurb: string; controls: string; tags: string[]; col: string; dev: string; unlock: number }
export const GAMES: GameDef[] = [
  { id: 'flappy', name: 'Flappy Nerd', need: 'mobile', verb: 'flapping', dev: 'Regret Interactive', blurb: 'Guide a nerd through pipes. He has asthma.', controls: 'Space / click to flap', tags: ['rage', 'casual'], col: '#5fb8d8', unlock: 0 },
  { id: 'candy', name: 'Candy Crash Saga', need: 'mobile', verb: 'crashing candy', dev: 'Kingpin', blurb: 'Match three. Your dentist buys a boat.', controls: 'Click two neighbours to swap', tags: ['casual', 'cozy'], col: '#e0569a', unlock: 0 },
  { id: 'runner', name: 'Subway Swervers', need: 'mobile', verb: 'swerving', dev: 'Sybo-ish', blurb: 'Fare evasion, the sport.', controls: '← → dodge, ↑ jump, ↓ slide', tags: ['casual', 'rage'], col: '#f0a030', unlock: 20 },
  { id: 'chat', name: 'Just Chattering', need: 'none', verb: 'yapping', dev: 'Your mouth', blurb: 'No game. Only you, chat and consequences.', controls: 'Pick topics, answer everyone', tags: ['irl'], col: '#c9b48a', unlock: 10 },
  { id: 'shooter', name: 'Fortknight', need: 'pc', verb: 'fortknighting', dev: 'Epoch Games', blurb: '100 knights, one winner, zero chivalry.', controls: 'Aim with mouse, click to shoot, R to reload', tags: ['fps', 'hype'], col: '#3f78d8', unlock: 0 },
  { id: 'rhythm', name: 'Beat Slaver', need: 'pc', verb: 'beat slaving', dev: 'Activationist', blurb: 'Hit notes. Hurt fingers. Annoy neighbours.', controls: 'D F J K on the beat', tags: ['hype', 'music'], col: '#a04fd8', unlock: 0 },
  { id: 'souls', name: 'Elden Bling', need: 'aaa', verb: 'getting humbled', dev: 'FromSoftwhere', blurb: 'A dying kingdom. A fabulous ring. A boss named Gary.', controls: 'J attack, K parry, L dodge', tags: ['rage', 'hype'], col: '#c89438', unlock: 0 },
];
export const GAME = Object.fromEntries(GAMES.map((g) => [g.id, g])) as Record<string, GameDef>;
export interface RoleDef { id: Role; name: string; need: number; base: number; blurb: string; effect: string }
export const ROLES: RoleDef[] = [
  { id: 'mod', name: 'Chat Moderator', need: 4000, base: 70, blurb: 'Holds the banhammer. Sleeps with it.', effect: 'Removes trolls, softens drama' },
  { id: 'editor', name: 'Video Editor', need: 8000, base: 140, blurb: 'Turns 6 hours of you into 8 minutes of someone better.', effect: 'Auto-edits daily videos, +quality' },
  { id: 'thumbs', name: 'Thumbnail Artist', need: 30000, base: 120, blurb: 'Makes your mouth open wider than nature allows.', effect: '+CTR on every video' },
  { id: 'manager', name: 'Talent Manager', need: 60000, base: 260, blurb: 'Takes 20%. Answers 10% of emails.', effect: 'Better sponsors, fewer scandals' },
  { id: 'camera', name: 'Camera Operator', need: 150000, base: 220, blurb: 'Never drops focus. Sometimes drops camera.', effect: '+stream quality, unlocks shows' },
  { id: 'producer', name: 'Show Producer', need: 250000, base: 340, blurb: 'Clipboard. Headset. Unresolved rage.', effect: 'Bigger, smoother shows' },
  { id: 'chef', name: 'Private Chef', need: 800000, base: 200, blurb: 'Will not make nuggets. Makes nuggets.', effect: 'Keeps you and the crew fed' },
  { id: 'security', name: 'Security', need: 1500000, base: 280, blurb: 'Wears sunglasses indoors, legally.', effect: 'Stops real-life incidents' },
];
export const ROLE = Object.fromEntries(ROLES.map((r) => [r.id, r])) as Record<Role, RoleDef>;
export const SPONSORS = [
  { brand: 'BordVPN', product: 'the VPN for people with nothing to hide', shady: 0.1, line: 'Hackers want my memes. BordVPN says no.' },
  { brand: 'Raid: Shadow Ledgers', product: 'the accounting RPG', shady: 0.25, line: 'Recruit 600 champions of double-entry bookkeeping.' },
  { brand: 'HelloFrush', product: 'meals that almost cook themselves', shady: 0.05, line: 'I chopped one onion and now I am a chef.' },
  { brand: 'SquareSpaced', product: 'websites for people who forget', shady: 0.05, line: 'My website has a website now.' },
  { brand: 'Mobster Energy', product: 'a drink you can’t refuse', shady: 0.2, line: 'I can hear colours. They are all green.' },
  { brand: 'Manscraped', product: 'the lawnmower for your secrets', shady: 0.1, line: 'Use code CHAT for 20% off your shame.' },
  { brand: 'CoinFlop', product: 'crypto, but on purpose', shady: 0.85, line: 'This is financial advice. (It is not.)' },
  { brand: 'BetterHalp', product: 'therapy by chatbot', shady: 0.45, line: 'It asked how I feel and then crashed. Relatable.' },
  { brand: 'Ridge-ish Wallet', product: 'a metal rectangle', shady: 0.1, line: 'Holds twelve cards and zero money.' },
  { brand: 'Casino Royale-ish', product: 'totally legal slots', shady: 0.95, line: 'The house always wins. I do not own the house.' },
  { brand: 'Dollar Shame Club', product: 'razors & regret', shady: 0.1, line: 'Smooth face, rough life.' },
  { brand: 'Lazer', product: 'RGB toothbrushes', shady: 0.05, line: 'My molars are now 16.8 million colours.' },
];
