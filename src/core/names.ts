import { RNG } from './rng';
const FIRST_F = ['Maya', 'Priya', 'Jasmine', 'Harper', 'Noor', 'Beatriz', 'Wren', 'Tessa', 'Imani', 'Yuki', 'Dolores', 'Frankie', 'Greta', 'Lupe', 'Anneke', 'Soo-jin', 'Marisol', 'Opal', 'Blythe', 'Farrah'];
const FIRST_M = ['Dante', 'Oskar', 'Malik', 'Kenji', 'Tobias', 'Rafael', 'Desmond', 'Felix', 'Hakeem', 'Linus', 'Bartholomew', 'Gus', 'Teo', 'Anders', 'Rocco', 'Jun', 'Barnaby', 'Ezra', 'Cornelius', 'Vikram'];
const LAST = ['Buffer', 'Ramirez', 'Okafor', 'Lagsworth', 'Nakamura', 'McPixel', 'Vandersnoot', 'Kowalski', 'Ping', 'Delacroix', 'Bitrate', 'Osei', 'Fernsby', 'Quill', 'Renderman', 'Abdi', 'Throttle', 'Castellano', 'Byte', 'Wu', 'Pumpernickel', 'Stutter', 'Ferreira', 'Keyframe', 'Goldblum-ish'];
export function humanName(rng: RNG, g: 'f' | 'm', taken: Set<string> = new Set()): string {
  for (let i = 0; i < 40; i++) { const n = `${rng.pick(g === 'f' ? FIRST_F : FIRST_M)} ${rng.pick(LAST)}`; if (!taken.has(n)) return n; }
  return `${rng.pick(g === 'f' ? FIRST_F : FIRST_M)} ${rng.pick(LAST)} ${rng.pick(['II', 'III', 'Jr.', 'Sr.'])}`;
}
const ADJ = ['sleepy', 'toxic', 'salty', 'soggy', 'epic', 'cursed', 'based', 'tiny', 'angry', 'crispy', 'feral', 'mid', 'goofy', 'spicy', 'silent', 'unhinged', 'certified', 'moist', 'quantum', 'discount', 'haunted', 'caffeinated', 'legally', 'retired', 'turbo', 'damp'];
const NOUN = ['goblin', 'waffle', 'gamer', 'panda', 'toaster', 'wizard', 'pickle', 'moth', 'noodle', 'raccoon', 'potato', 'ferret', 'gremlin', 'lasagna', 'pigeon', 'sock', 'dentist', 'burrito', 'cryptid', 'otter', 'intern', 'walrus', 'nugget', 'shrimp', 'accountant', 'possum'];
const HUMANISH = ['gary', 'kevin', 'brenda', 'steve', 'karen', 'doug', 'linda', 'chad', 'becky', 'todd', 'grandma', 'uncle_rick', 'mrs_henderson', 'tyler', 'dave'];
const ITEMS = ['bathwater', 'ravioli', 'taxes', 'kneecaps', 'wifi', 'cheese', 'crimes', 'socks', 'vibes', 'lag', 'aim', 'loot', 'feelings'];
export function userName(rng: RNG, taken: Set<string> = new Set()): string {
  for (let i = 0; i < 60; i++) {
    const k = rng.int(0, 8); let n: string;
    switch (k) {
      case 0: n = `${rng.pick(ADJ)}_${rng.pick(NOUN)}`; break;
      case 1: n = `xX_${rng.pick(NOUN)}_Xx`; break;
      case 2: n = `${rng.pick(HUMANISH)}${rng.int(1, 99)}`; break;
      case 3: n = `Not${cap(rng.pick(HUMANISH))}`; break;
      case 4: n = `${rng.pick(NOUN)}${rng.pick(['4life', 'tv', '_irl', 'lord', 'mommy', 'dad', 'fan', 'hater', '69', '420', '2009'])}`; break;
      case 5: n = `${cap(rng.pick(ADJ))}${cap(rng.pick(NOUN))}`; break;
      case 6: n = `${rng.pick(HUMANISH)}_steals_${rng.pick(ITEMS)}`; break;
      case 7: n = `i_eat_${rng.pick(ITEMS)}`; break;
      default: n = `${rng.pick(NOUN)}_with_${rng.pick(ITEMS)}`;
    }
    if (!taken.has(n)) return n;
  }
  return `user${rng.int(100000, 999999)}`;
}
export const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const COLORS = ['#ff6a5a', '#ffb02e', '#ffe05a', '#9be15d', '#4fd08a', '#4dd6d0', '#5fb8ff', '#8ea2ff', '#c58bff', '#ff8ad1', '#ff9e7a', '#d6c48f', '#a8e0c0', '#f08a8a'];
export const userColor = (rng: RNG) => rng.pick(COLORS);
export const GAME_RIVALS = [
  { id: 'feast', name: 'Mr. Feast', followers: 212_000_000, bit: 'gives away islands, cries on cue' },
  { id: 'kai', name: 'Kai Cement', followers: 38_000_000, bit: 'screams professionally' },
  { id: 'queasy', name: 'xQueasy', followers: 12_400_000, bit: 'speaks 1.8x speed, owes chat $40' },
  { id: 'pokimeme', name: 'Pokimeme', followers: 9_300_000, bit: 'apologised once, trending since' },
  { id: 'speedbump', name: 'IShowSpeedbump', followers: 5_200_000, bit: 'barks at cars' },
  { id: 'drdis', name: 'Dr Disagreeable', followers: 2_100_000, bit: 'moustache has its own manager' },
  { id: 'ninjaw', name: 'Ninjaw', followers: 640_000, bit: 'blue hair, blue tick, blue mood' },
  { id: 'valkyrate', name: 'Valkyrate', followers: 120_000, bit: 'co-owns everything' },
  { id: 'grandpaggro', name: 'GrandpAggro', followers: 22_000, bit: '81 years old, cracked at Fortknight' },
  { id: 'cousin', name: 'Your cousin Brayden', followers: 340, bit: 'has a ring light and an ego' },
];
