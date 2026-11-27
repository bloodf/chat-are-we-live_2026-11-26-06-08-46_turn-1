export interface Quality { tier: 0 | 1 | 2 | 3; name: string; scale: number; normalMaps: boolean; post: boolean; fps: number; charLOD: number; lm: number; cached: boolean; cpuSkin: boolean }
export const QUALITY: Record<string, Quality> = {
  low: { tier: 0, name: 'Potato', scale: 1, normalMaps: false, post: false, fps: 30, charLOD: 1, lm: 1024, cached: true, cpuSkin: true },
  medium: { tier: 1, name: 'Midrange', scale: 1, normalMaps: false, post: false, fps: 60, charLOD: 0, lm: 2048, cached: true, cpuSkin: false },
  high: { tier: 2, name: 'Big Rig', scale: 1, normalMaps: true, post: false, fps: 60, charLOD: 0, lm: 2048, cached: false, cpuSkin: false },
  ultra: { tier: 3, name: 'GeFarce 6090', scale: 1, normalMaps: true, post: true, fps: 144, charLOD: 0, lm: 2048, cached: false, cpuSkin: false },
};
export function detectQuality(): string {
  try {
    const c = document.createElement('canvas'); const gl = c.getContext('webgl2'); if (!gl) return 'low';
    const e = gl.getExtension('WEBGL_debug_renderer_info'); const r = String(gl.getParameter(e ? e.UNMASKED_RENDERER_WEBGL : gl.RENDERER)).toLowerCase();
    gl.getExtension('WEBGL_lose_context')?.loseContext();
    if (/swiftshader|llvmpipe|software|basic render/.test(r)) return 'low';
    if (/nvidia|geforce|rtx|radeon rx|arc a|apple m[2-9]|apple gpu/.test(r)) return 'ultra';
    if (/apple|radeon|iris|adreno 7/.test(r)) return 'high';
    return 'medium';
  } catch { return 'low'; }
}
