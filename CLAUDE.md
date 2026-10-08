# Motion studio rules

Every video here is a program that renders frames, not a video file. Opus writes the
program; headless Chromium (Playwright) captures frames; ffmpeg encodes them.

## Render contract
- Every film is a pure function of time: `window.seek(t)` paints frame t.
- No CSS transitions, no setTimeout, no requestAnimationFrame in render mode,
  no state carried between frames. Seeded noise only (mulberry32), never Math.random.
- Render with `node render.mjs`, encode H.264 yuv420p, CRF 16.
- Default route: one `index.html` + `render.mjs`, no framework. Use Remotion or
  HyperFrames (skills in `.claude/skills/`) only when the brief asks for one.

## Look
- Banned defaults: centered title on gradient, everything fading in,
  corner labels and frame borders, glow on UI chrome, generic particle bursts.
- One display face, one UI face. One accent color unless the brief says otherwise.
- Every 2 to 4 seconds something new must happen on screen.
- Motion uses closed-form springs, never fixed easing curves.

## Sound
- Score and SFX are synthesized in code unless a track is supplied.
- Place hits on the measured beat grid (beats.json). Loudness -14 LUFS.

## Assets and keys
- Product videos use real screenshots, logos, colors and fonts saved to `./assets`.
  Never redraw product UI from imagination.
- API keys live in `.env` (see `.env.example`). Read them from the environment;
  never print them or write them into source, logs or prompts.

## Loop before you show me anything
1. Render one frame per beat as a contact sheet and LOOK at it.
2. Score it 1-10 on: hook in first 2s, readability at phone size,
   motion quality, variety, brand accuracy, sound sync.
3. Fix the 3 worst problems. Repeat until every score is 8+.
4. Only then do the full render.

## Environment
- Tools: Node 22+, ffmpeg, Python with numpy, librosa, soundfile; Playwright (devDependency).
- First run on a new machine: `npm install && npm run setup:browser`.
- In Claude Code cloud sessions Chromium is preinstalled; if Playwright reports a
  missing browser, launch with `executablePath: '/opt/pw-browsers/chromium'`
  instead of downloading one.
- Effort: medium for small fixes and re-renders, xhigh for new films,
  max for flagship pieces.
