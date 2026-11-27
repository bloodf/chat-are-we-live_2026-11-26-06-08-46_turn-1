# Chat, Are We Live?

A 3D live-streamer life sim for the browser. You start on your childhood bed with a cracked Nokidding 3310½ and zero followers. You end in a mansion, on a golden throne, ahead of Mr. Feast.

## Run it

```bash
npm install
npm start          # builds, then serves http://127.0.0.1:4173
npm run dev        # dev server on http://127.0.0.1:5173
npm run test:all   # unit tests + coverage, type-check, production build, end-to-end tests
npm run backup     # zips all source + assets to ~/backups/chat-are-we-live/
```

`test:e2e` needs Playwright's Chromium (`npx playwright install chromium` on a fresh machine).

## How to play

| Where | Keys |
| --- | --- |
| Home | WASD or click to walk, E to use the nearest thing, Tab for your phone, drag to orbit, wheel to zoom, Esc to pause |
| Live | Play the game on screen. 1–6 react to big moments, Tab answers the next highlighted chat, Enter talks to chat in your own words, M mutes |
| Flappy Nerd | Space or click |
| Candy Crash Saga | Click two neighbours |
| Subway Swervers | Arrow keys |
| Fortknight | Mouse, R to reload |
| Beat Slaver | D F J K |
| Elden Bling | J attack, K parry, L dodge, H flask |
| Just Chattering | Z X C pick a story, Space on the punchline |

The loop: stream → collect clips → cut a MeTube video → buy gear → sleep (rent, subs, views) → move up → hire a crew → produce shows → overtake Mr. Feast.

## What's where

- `src/core` – the whole simulation. Pure, seeded, DOM-free TypeScript: emotion model (PAD moods + Big Five + appraisal + memory), chat grammar, language understanding for free text, live session, incidents, staff, economy, life events, goals, save/load.
- `src/games` – the seven playable games inside the game.
- `src/three` – three.js r187 `WebGPURenderer` + TSL materials, baked lighting, probe-lit characters, procedural IK animation, navigation, NPC brains, cameras.
- `src/ui` – Preact + signals interface.
- `src/audio` – everything you hear is synthesised; there are no audio files.
- `forge` – the asset factory: Blender/Cycles scripts that model, light-bake and export every room, prop, person and product photo.
- `tests/unit`, `tests/e2e` – Vitest and Playwright.

## Graphics tiers

Detected automatically; change it in Options.

| Tier | For | What it does |
| --- | --- | --- |
| Potato | software rendering | room cached and progressively anti-aliased, low-poly cast, one draw call per person |
| Midrange | integrated GPUs | cached room, full-detail cast |
| Big Rig | discrete GPUs | everything live, normal maps, box-projected reflections, contact occlusion |
| GeFarce 6090 | strong GPUs | adds ground-truth AO, bloom, vignette, FXAA |

WebGL 2 is the default backend. WebGPU can be switched on in Options.
