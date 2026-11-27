import { MiniGame, rr, txt, grad, sprite, type Input, type Ctx2D } from './base';
import { clamp } from '../core/rng';
const COLS = [['#b5452c', '#e8dcc0'], ['#2f6b75', '#f6c419'], ['#6a4c93', '#f0c9ff'], ['#33614f', '#e8dcc0'], ['#c98a2e', '#2b1a10']];
const SPINES = ['ALGEBRA', 'MOBY DUCK', 'C++--', 'TAX LAW', 'DUNE BUGGY', 'BIOLOGY', 'SOUP', '1985', 'HOW TO FLY', 'PHYSICS'];
export class Flappy extends MiniGame {
  id = 'flappy'; y = 300; vy = 0; pipes: { x: number; gap: number; gy: number; passed: boolean; c: number[] }[] = []; started = false; flap = 0; speed = 138; scroll = 0; streak = 0;
  reset() { this.y = 300; this.vy = 0; this.pipes = []; this.started = false; this.score = 0; this.over = 0; this.recorded = false; this.speed = 138; this.streak = 0; for (let i = 0; i < 3; i++) this.addPipe(460 + i * 215); }
  addPipe(x: number) { const gap = clamp(178 - this.score * 1.4, 132, 178); this.pipes.push({ x, gap, gy: this.rng.range(130, 500 - gap), passed: false, c: Array.from({ length: 16 }, () => this.rng.int(0, COLS.length - 1)) }); }
  update(dt: number, i: Input) {
    if (!this.pipes.length) this.reset();
    const press = i.pressed || i.hit.has(' ') || i.hit.has('arrowup');
    if (this.over > 0) { this.over -= dt; this.vy += 1400 * dt; this.y = Math.min(560, this.y + this.vy * dt); if (this.over <= 0) this.reset(); return; }
    if (!this.started) { this.y = 300 + Math.sin(this.t * 4) * 8; if (press) { this.started = true; this.vy = -365; this.flap = 0.2; this.sfx('flap'); } this.scroll += dt * 60; return; }
    if (press) { this.vy = -365; this.flap = 0.2; this.sfx('flap'); }
    this.flap = Math.max(0, this.flap - dt); this.vy = Math.min(620, this.vy + 1130 * dt); this.y += this.vy * dt; this.speed = Math.min(205, 138 + this.score * 2.2); this.scroll += this.speed * dt;
    for (const p of this.pipes) {
      p.x -= this.speed * dt; const bx = 104, br = 15;
      if (p.x < bx + br + 4 && p.x + 62 > bx - br) { if (this.y - br < p.gy || this.y + br > p.gy + p.gap) { this.burst(bx, this.y, '#ffe05a', 16); this.die(this.score > 8 ? 1.5 : 0.9, this.score > 8 ? `Face-planted at ${this.score}` : undefined); return; } }
      if (!p.passed && p.x + 62 < bx - br) { p.passed = true; this.score++; this.streak++; this.sfx('point'); this.emit('score', 1); const m = Math.min(this.y - br - p.gy, p.gy + p.gap - this.y - br); if (m < 9) { this.pop(bx + 20, this.y - 30, 'CLOSE!', '#ffe05a'); this.emit('clutch', 1.1, 'Shaved the textbook'); } else if (this.score % 5 === 0) { this.pop(bx + 20, this.y - 30, `${this.score}!`, '#7cf0c8'); this.emit('combo', 1 + this.score / 30); } this.checkRecord(); }
    }
    if (this.pipes[0]?.x < -80) { this.pipes.shift(); this.addPipe(this.pipes[this.pipes.length - 1].x + 215); }
    if (this.y > 556 || this.y < -30) this.die(1);
  }
  draw(c: Ctx2D) {
    const s = this.scroll; sprite(c, 'fl_sky', 0, 0, 360, 640, (q) => { q.fillStyle = grad(q, 0, 640, '#3d9bd1', '#8fd3e8', '#fbe6b8'); q.fillRect(0, 0, 360, 640); });
    for (let k = 0; k < 5; k++) { const x = ((k * 130 - s * 0.12) % 560 + 560) % 560 - 90, y = 70 + (k * 67) % 150; sprite(c, 'fl_cloud', x - 42, y - 28, 94, 46, (q) => { q.fillStyle = 'rgba(255,255,255,.75)'; q.beginPath(); q.ellipse(42, 28, 38, 13, 0, 0, 7); q.ellipse(64, 18, 24, 14, 0, 0, 7); q.ellipse(24, 22, 18, 10, 0, 0, 7); q.fill(); }); }
    for (let L = 0; L < 2; L++) { const W = 576, off = (s * (0.22 + L * 0.2)) % W; for (let r = 0; r < 2; r++) sprite(c, 'fl_city' + L, r * W - off, 330, W, 242, (q) => { for (let k = 0; k < 9; k++) { const h = 70 + ((k * 53 + L * 31) % 90), x = k * 64, y0 = 230 - h - (L ? 0 : 40); q.fillStyle = L ? '#5a9b7a' : '#9cc7b0'; q.fillRect(x, y0, 60, h + 60); q.fillStyle = L ? '#4a8567' : '#8bb9a1'; for (let a = 0; a < 3; a++) for (let b = 0; b < 4; b++) q.fillRect(x + 9 + a * 18, y0 + 12 + b * 22, 9, 12); } }); }
    for (const p of this.pipes) { this.stack(c, p.x, p.gy, -1, p.c); this.stack(c, p.x, p.gy + p.gap, 1, p.c); }
    sprite(c, 'fl_ground', -((s) % 24), 560, 408, 80, (q) => { q.fillStyle = '#d9b36a'; q.fillRect(0, 12, 408, 70); q.fillStyle = '#6b9b3c'; q.fillRect(0, 6, 408, 12); q.fillStyle = '#83b84c'; for (let x = 0; x < 408; x += 24) { q.beginPath(); q.moveTo(x, 18); q.lineTo(x + 12, 6); q.lineTo(x + 24, 6); q.lineTo(x + 12, 18); q.fill(); } });
    // the nerd
    c.save(); c.translate(104, this.y); c.rotate(clamp(this.vy / 700, -0.45, 1.1)); const wing = this.flap > 0 ? -10 : 5 + Math.sin(this.t * 16) * 2;
    c.fillStyle = '#8a5a36'; c.beginPath(); c.arc(0, 0, 19, 0, 7); c.fill(); c.fillStyle = '#f4c9a0'; c.beginPath(); c.arc(1, 2, 17, 0, 7); c.fill(); c.fillStyle = '#5a3a22'; c.beginPath(); c.arc(0, -5, 17, Math.PI, 0); c.fill();
    c.fillStyle = '#e0402c'; c.beginPath(); c.arc(0, -9, 14, Math.PI, 0); c.fill(); c.fillStyle = '#f6c419'; c.beginPath(); c.arc(0, -9, 14, Math.PI * 1.33, Math.PI * 1.66); c.lineTo(0, -9); c.fill(); c.fillStyle = '#333'; c.fillRect(-1, -28, 2, 7); c.fillStyle = '#5fb8ff'; const pw = Math.cos(this.t * 30) * 13; c.fillRect(-Math.abs(pw), -30, Math.abs(pw) * 2, 4);
    c.fillStyle = '#f4c9a0'; c.beginPath(); c.ellipse(-13, 4 + wing * 0.4, 9, 5, wing * 0.05, 0, 7); c.fill(); c.strokeStyle = '#1d1a16'; c.lineWidth = 2.4; c.fillStyle = '#eaf6ff'; for (const x of [3, 13]) { c.beginPath(); c.arc(x, 0, 6, 0, 7); c.fill(); c.stroke(); } c.fillStyle = '#111'; c.beginPath(); c.arc(5, 1, 2, 0, 7); c.arc(15, 1, 2, 0, 7); c.fill(); c.strokeStyle = '#7a2f22'; c.lineWidth = 2; c.beginPath(); this.over > 0 ? c.arc(9, 12, 4, Math.PI, 0) : c.arc(9, 8, 4, 0.2, 2.9); c.stroke(); c.restore();
    txt(c, String(this.score), 180, 70, 64, '#fff', 8); if (this.best) txt(c, `BEST ${this.best}`, 180, 116, 18, '#ffe9a8', 4);
    if (!this.started && this.over <= 0) { txt(c, 'FLAPPY NERD', 180, 190, 46, '#ffe05a', 8); txt(c, 'TAP / SPACE', 180, 400, 26, '#fff', 5); }
    if (this.over > 0) { c.fillStyle = 'rgba(20,10,8,.35)'; c.fillRect(0, 0, 360, 640); txt(c, 'ASTHMA!', 180, 280, 58, '#ff6a5a', 8); txt(c, `${this.score} pipes of regret`, 180, 330, 22, '#fff', 4); }
    this.overlay(c);
  }
  private stack(c: Ctx2D, x: number, y: number, dir: 1 | -1, cs: number[]) { const n = 14; for (let k = 0; k < n; k++) { const h = 34, yy = dir > 0 ? y + k * h : y - (k + 1) * h; if (yy > 575 || yy < -40) continue; const off = ((cs[k] * 7 + k * 3) % 9) - 4, sp = (cs[k] * 3 + k) % SPINES.length; sprite(c, `fl_b${cs[k]}_${sp}`, x + off, yy, 62, h, (q) => { const [a, b] = COLS[cs[k]]; q.fillStyle = a; rr(q, 0, 0, 62, h - 2, 3); q.fill(); q.fillStyle = 'rgba(0,0,0,.18)'; q.fillRect(0, h - 9, 62, 7); q.fillStyle = '#f4ecd8'; q.fillRect(54, 4, 8, h - 10); q.fillStyle = b; q.fillRect(4, 3, 3, h - 8); txt(q, SPINES[sp], 30, h / 2 - 1, 12, b, 0, 'center', 'Big Shoulders Display'); }); } }
}
