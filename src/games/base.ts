import { RNG, clamp } from '../core/rng';
import type { GameEvent } from '../core/stream';
export interface Input { x: number; y: number; down: boolean; pressed: boolean; keys: Set<string>; hit: Set<string> }
export const newInput = (): Input => ({ x: 0, y: 0, down: false, pressed: false, keys: new Set(), hit: new Set() });
export interface Out { ev: GameEvent; heat: number; label?: string }
export type Ctx2D = CanvasRenderingContext2D;
/** A game inside the game. Logic never touches the DOM; draw() only reads state. */
export abstract class MiniGame {
  abstract id: string; w = 360; h = 640; t = 0; score = 0; best = 0; over = 0; runs = 0; out: Out[] = []; shake = 0; protected recorded = false; popups: { x: number; y: number; t: number; text: string; c: string }[] = []; sounds: string[] = []; parts: { x: number; y: number; vx: number; vy: number; t: number; c: string; r: number }[] = [];
  constructor(public rng: RNG, best = 0) { this.best = best; }
  abstract reset(): void; abstract update(dt: number, i: Input): void; abstract draw(c: Ctx2D): void;
  tick(dt: number, i: Input) { dt = Math.min(dt, 0.12); while (dt > 0.04) { this.sub(0.04, i); dt -= 0.04; } this.sub(dt, i); }
  private sub(dt: number, i: Input) { this.t += dt; this.shake = Math.max(0, this.shake - dt * 3); for (const p of this.popups) p.t += dt; this.popups = this.popups.filter((p) => p.t < 1); for (const p of this.parts) { p.t += dt; p.x += p.vx * dt; p.y += p.vy * dt; p.vy += 500 * dt; } this.parts = this.parts.filter((p) => p.t < 0.7); this.update(dt, i); i.pressed = false; i.hit.clear(); }
  emit(ev: GameEvent, heat = 1, label?: string) { this.out.push({ ev, heat, label }); }
  drain() { const o = this.out; this.out = []; return o; }
  sfx(s: string) { this.sounds.push(s); if (this.sounds.length > 12) this.sounds.shift(); }
  pop(x: number, y: number, text: string, c = '#fff') { this.popups.push({ x, y, t: 0, text, c }); }
  burst(x: number, y: number, c: string, n = 10, sp = 160) { for (let k = 0; k < n && this.parts.length < 120; k++) { const a = this.rng.range(0, 6.28); this.parts.push({ x, y, vx: Math.cos(a) * sp * this.rng.next(), vy: Math.sin(a) * sp * this.rng.next() - 60, t: 0, c, r: this.rng.range(2, 5) }); } }
  checkRecord() { if (this.score > this.best) { if (this.best > 0 && !this.recorded) { this.recorded = true; this.emit('record', 1.3, `New record: ${this.score}`); this.sfx('record'); } this.best = this.score; } }
  die(heat = 1, label?: string) { if (this.over > 0) return; this.over = 1.5; this.shake = 1; this.emit('fail', heat, label); this.sfx('fail'); this.runs++; }
  overlay(c: Ctx2D) { for (const p of this.parts) { c.globalAlpha = 1 - p.t / 0.7; c.fillStyle = p.c; c.fillRect(p.x - p.r / 2, p.y - p.r / 2, p.r, p.r); } c.globalAlpha = 1; c.textAlign = 'center'; for (const p of this.popups) { c.globalAlpha = 1 - p.t * p.t; txt(c, p.text, p.x, p.y - p.t * 46, 22 + (1 - p.t) * 6, p.c, 4); } c.globalAlpha = 1; }
}
export function rr(c: Ctx2D, x: number, y: number, w: number, h: number, r: number) { c.beginPath(); c.roundRect(x, y, w, h, r); }
const store = new Map<string, HTMLCanvasElement>();
/** draw once, blit forever: keeps the mini-games smooth on CPU rasterisers */
export function sprite(c: Ctx2D, key: string, x: number, y: number, w: number, h: number, draw: (c: Ctx2D) => void, sx = 1) {
  if (typeof document === 'undefined' || !c.getTransform) { c.save(); c.translate(x, y); draw(c); c.restore(); return; }
  const k = Math.max(0.4, Math.min(3, c.getTransform().a || 1)); const id = key + '@' + k.toFixed(2); let s = store.get(id);
  if (!s) { s = document.createElement('canvas'); s.width = Math.max(1, Math.ceil(w * k)); s.height = Math.max(1, Math.ceil(h * k)); const q = s.getContext('2d')!; q.scale(k, k); draw(q); if (store.size > 420) store.delete(store.keys().next().value!); store.set(id, s); }
  c.drawImage(s, x, y, w * sx, h * sx);
}
let fontsReady = false; if (typeof document !== 'undefined' && document.fonts) document.fonts.load('20px Anton').then(() => { fontsReady = true; }, () => { fontsReady = true; });
function rawTxt(c: Ctx2D, s: string, x: number, y: number, size: number, fill: string, stroke: number, align: CanvasTextAlign, font: string) { c.font = `${size}px ${font}, Impact, sans-serif`; c.textAlign = align; c.textBaseline = 'middle'; if (stroke) { c.lineWidth = stroke; c.strokeStyle = 'rgba(12,10,9,.85)'; c.lineJoin = 'round'; c.strokeText(s, x, y); } c.fillStyle = fill; c.fillText(s, x, y); }
const widths = new Map<string, number>();
export function txt(c: Ctx2D, s: string, x: number, y: number, size: number, fill = '#fff', stroke = 0, align: CanvasTextAlign = 'center', font = 'Anton') {
  const sz = Math.round(size * 2) / 2; if (typeof document === 'undefined' || !fontsReady || s.length > 60) { rawTxt(c, s, x, y, sz, fill, stroke, align, font); return; }
  const wk = s + '|' + sz + font; let tw = widths.get(wk); if (tw == null) { c.font = `${sz}px ${font}, Impact, sans-serif`; tw = c.measureText(s).width; if (widths.size > 800) widths.clear(); widths.set(wk, tw); } const pad = stroke + 4, w = tw + pad * 2, h = sz * 1.5 + pad * 2; const ox = align === 'center' ? w / 2 : align === 'right' || align === 'end' ? w - pad : pad; sprite(c, `t:${wk}|${fill}|${stroke}`, x - ox, y - h / 2, w, h, (q) => rawTxt(q, s, w / 2, h / 2, sz, fill, stroke, 'center', font));
}
export function grad(c: Ctx2D, y0: number, y1: number, ...cs: string[]) { const g = c.createLinearGradient(0, y0, 0, y1); cs.forEach((k, i) => g.addColorStop(i / (cs.length - 1), k)); return g; }
export const ease = (t: number) => 1 - Math.pow(1 - clamp(t), 3);
