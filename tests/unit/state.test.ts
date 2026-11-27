import { describe, expect, it } from 'vitest';
import { canPlay, deserialize, device, deviceState, earn, equippedItem, gainFollowers, newState, note, ownedItem, primeTime, quality, serialize, skillUp, stat, timeStr, weekday, withRng, SAVE_VERSION } from '../../src/core/state';
import { fresh, rich } from './helpers';
describe('new game', () => {
  it('starts broke, unknown and on a cracked phone in a childhood bedroom', () => { const s = fresh(); expect(s.followers).toBe(0); expect(s.money).toBeLessThan(150); expect(s.home).toBe('bedroom'); expect(s.equipped.device).toBe('phone0'); expect(deviceState(s).cond).toBeLessThan(100); expect(s.day).toBe(1); expect(s.chapter).toBe(1); });
  it('same seed, same world', () => { expect(serialize(newState({ seed: 77 }))).toBe(serialize(newState({ seed: 77 }))); expect(serialize(newState({ seed: 77 }))).not.toBe(serialize(newState({ seed: 78 }))); });
  it('chill difficulty starts with more cash', () => expect(newState({ difficulty: 'chill', seed: 1 }).money).toBeGreaterThan(newState({ difficulty: 'grind', seed: 1 }).money));
});
describe('save / load', () => {
  it('round-trips losslessly', () => { const s = rich(); expect(deserialize(serialize(s))).toEqual(s); });
  it.each([['garbage', 'not json'], ['null', 'null'], ['wrong version', JSON.stringify({ ...fresh(), v: SAVE_VERSION + 1 })], ['missing inventory', JSON.stringify({ ...fresh(), owned: undefined })], ['number', '42'], ['array', '[]']])('rejects %s', (_n, j) => expect(deserialize(j)).toBeNull());
  it('fills fields missing from older saves', () => { const o: any = JSON.parse(serialize(fresh())); delete o.posts; expect(deserialize(JSON.stringify(o))!.posts).toEqual([]); });
});
describe('helpers', () => {
  it('quality rises with gear and home, collapses when broken', () => { const a = fresh(), b = rich(); expect(quality(b)).toBeGreaterThan(quality(a)); const q = quality(b); deviceState(b).broken = true; expect(quality(b)).toBeLessThan(q); expect(quality(a)).toBeGreaterThanOrEqual(0.15); });
  it('camera operators improve quality', () => { const s = rich(); const q = quality(s); s.staff.push({ role: 'camera', skill: 0.9, morale: 90 } as any); expect(quality(s)).toBeGreaterThan(q); });
  it('canPlay gates by device, followers and breakage', () => { const s = fresh(); expect(canPlay(s, 'flappy')).toBe(true); expect(canPlay(s, 'souls')).toBe(false); expect(canPlay(s, 'runner')).toBe(false); s.followers = 30; expect(canPlay(s, 'runner')).toBe(true); deviceState(s).broken = true; expect(canPlay(s, 'flappy')).toBe(false); expect(canPlay(s, 'chat')).toBe(true); expect(canPlay(s, 'nope')).toBe(false); expect(canPlay(rich(), 'souls')).toBe(true); });
  it('time formatting and weekdays', () => { expect(timeStr(0)).toBe('12:00 AM'); expect(timeStr(13 * 60 + 5)).toBe('1:05 PM'); expect(timeStr(25 * 60)).toBe('1:00 AM'); expect(weekday(1)).toBe('Moanday'); expect(weekday(8)).toBe('Moanday'); });
  it('evenings beat mornings; weekends beat weekdays', () => { const s = fresh(); s.min = 20.5 * 60; const e = primeTime(s); s.min = 9 * 60; expect(primeTime(s)).toBeLessThan(e); s.day = 1; s.min = 20 * 60; const wd = primeTime(s); s.day = 6; expect(primeTime(s)).toBeGreaterThan(wd); });
  it('money, followers, notes, stats, skills', () => { const s = fresh(); earn(s, 10, 'x'); earn(s, -3, 'y'); expect(s.stats.earned).toBe(10); expect(s.stats.spent).toBe(3); expect(s.stats.earn_x).toBe(10); gainFollowers(s, -50); expect(s.followers).toBe(0); gainFollowers(s, 7.6); expect(s.followers).toBe(8); expect(s.peakFollowers).toBe(8); for (let i = 0; i < 80; i++) note(s, 'a', 'b'); expect(s.notes.length).toBe(60); expect(new Set(s.notes.map((n) => n.id)).size).toBe(60); stat(s, 'k'); stat(s, 'k', 4); expect(s.stats.k).toBe(5); let up = false; for (let i = 0; i < 10; i++) up = skillUp(s, 'tech', 1) || up; expect(up).toBe(true); for (let i = 0; i < 5000; i++) skillUp(s, 'tech', 5); expect(s.skills.tech).toBeLessThanOrEqual(20); });
  it('withRng advances the saved generator', () => { const s = fresh(); const b = s.rng; withRng(s, (r) => r.next()); expect(s.rng).not.toBe(b); });
  it('lookup helpers', () => { const s = fresh(); expect(device(s).id).toBe('phone0'); expect(equippedItem(s, 'mic')).toBeUndefined(); expect(ownedItem(s, 'nope')).toBeUndefined(); });
});
