import type { Traits, Mood, Bond } from './emotion';
export type HomeId = 'bedroom' | 'studio' | 'loft' | 'hq' | 'mansion';
export type SlotId = 'device' | 'mic' | 'cam' | 'light' | 'chair' | 'net' | 'decor1' | 'decor2' | 'led';
export type Reaction = 'laugh' | 'hype' | 'rage' | 'cry' | 'shock' | 'dance';
export type Skill = 'charisma' | 'gaming' | 'editing' | 'tech' | 'business';
export type Tone = 'warm' | 'funny' | 'roast' | 'hype' | 'honest' | 'timeout' | 'ban' | 'click';
export type ViewerStyle = 'wholesome' | 'memer' | 'troll' | 'backseat' | 'simp' | 'critic' | 'kid' | 'lurker' | 'conspiracy' | 'elder';
export interface Viewer { id: string; name: string; color: string; style: ViewerStyle; traits: Traits; mood: Mood; bond: Bond; sub: number; mod: boolean; banned: boolean; timeout: number; joined: number; spent: number; msgs: number; catch: string }
export type Role = 'editor' | 'camera' | 'mod' | 'manager' | 'thumbs' | 'chef' | 'producer' | 'security';
export interface Staff { id: string; name: string; body: string; gender: 'f' | 'm'; role: Role; skill: number; salary: number; asked: number; traits: Traits; mood: Mood; bond: Bond; energy: number; morale: number; loyalty: number; hired: number; quirk: string; backstory: string; rel: Record<string, number>; task: string; lastTalk: number; raises: number; wants?: string }
export interface ItemState { id: string; cond: number; broken: boolean }
export interface Clip { id: string; title: string; heat: number; game: string; day: number; kind: string }
export interface Video { id: string; title: string; thumb: string; quality: number; ctr: number; day: number; views: number; target: number; revenue: number; likes: number; followers: number; viral: number; done: boolean; comments: string[] ; kind: 'highlight' | 'vlog' | 'show' | 'apology' }
export interface Sponsor { id: string; brand: string; product: string; pay: number; ask: string; minutes: number; shady: number; expires: number; accepted?: boolean; progress: number; line: string }
export interface Note { id: string; day: number; min: number; from: string; text: string; kind: 'msg' | 'alert' | 'money' | 'good' | 'bad'; read: boolean }
export interface Post { id: string; who: string; text: string; likes: number; day: number; mine?: boolean; replies: string[] }
export interface StreamLog { day: number; game: string; mins: number; peak: number; avg: number; followers: number; subs: number; money: number; grade: string; best: string; title: string }
export interface GameState {
  v: number; seed: number; rng: number; name: string; channel: string; body: string; difficulty: 'chill' | 'normal' | 'grind';
  day: number; min: number; money: number; debt: number; followers: number; subs: number; peakFollowers: number;
  energy: number; food: number; vibe: number; rep: number; drama: number; burnout: number;
  skills: Record<Skill, number>; home: HomeId; owned: ItemState[]; equipped: Partial<Record<SlotId, string>>;
  viewers: Viewer[]; staff: Staff[]; candidates: Staff[]; clips: Clip[]; videos: Video[]; sponsors: Sponsor[]; notes: Note[]; posts: Post[]; logs: StreamLog[];
  goals: string[]; flags: Record<string, number>; gameFatigue: Record<string, number>; trend: Record<string, number>; best: Record<string, number>; rivals: { id: string; name: string; followers: number; bit: string; heat: number }[];
  streak: number; lastStreamDay: number; streamsToday: number; headline: string; algo: number; chapter: number; ended: boolean; momBond: Bond; momMood: Mood; stats: Record<string, number>; tutorial: number;
}
