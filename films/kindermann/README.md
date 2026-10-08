# Kindermann Catering, 20 s loop

A muted, seamless loop for the hero slot on kindermann-catering.de, plus social cuts with an
original score. One timeline, three formats. Built as `index.html` (a pure function of time,
`window.seek(t)`) + `render.mjs` (Playwright frames into ffmpeg), no framework.

## Deliverables (`dist/`)

| File | Format | Size | Notes |
|---|---|---|---|
| web/kindermann-loop-3x4.mp4 | 1080×1440, H.264 High, 24 fps | 2.49 MB | no audio track, faststart |
| web/kindermann-loop-3x4.webm | 1080×1440, VP9, 24 fps | 2.29 MB | no audio track |
| web/poster.webp | 1080×1440 | 9 KB | frame 0 (logo on white) |
| social/kindermann-3x4.mp4 | 1080×1440, CRF 16 + AAC | 7.3 MB | with score |
| social/kindermann-9x16.mp4 | 1080×1920, CRF 16 + AAC | 8.1 MB | with score |
| social/kindermann-16x9.mp4 | 1920×1080, CRF 16 + AAC | 7.0 MB | with score |

Embed on the site (autoplay needs `muted` and `playsinline`):

```html
<video autoplay muted loop playsinline poster="poster.webp" width="1080" height="1440">
  <source src="kindermann-loop-3x4.webm" type="video/webm">
  <source src="kindermann-loop-3x4.mp4" type="video/mp4">
</video>
```

## Timeline (96 BPM, beat = 0.625 s, 32 beats = 20 s exactly, 15 frames per beat at 24 fps)

| Beat | Time | On screen |
|---|---|---|
| 0 | 0.00 | Logo on white (identical to the last frame) |
| 1, 2, 3 | 0.63–1.88 | „Gutes." „Essen." „Hausgemacht." rise into place word by word; each red dot stamps on the off-beat |
| 5 | 3.13 | The page scrolls up into the album: Bruschetta und Löffel-Häppchen (push) |
| 7, 8, 9 | 4.38–5.63 | Hard cuts: Tomate und Mozzarella (pan), Pfälzer Kartoffelsalat (push to the chalk sign), Desserts im Glas (pan) |
| 11, 13, 15 | 6.88–9.38 | Grey page. Hochzeit, Private Feier, Firmenfeier: each photo is dealt onto the last like a print, the word rises with it |
| 17–20 | 10.63–12.50 | Menükarte: red header drops, then Klassiker, Live-Cooking, Fingerfood, each dotted leader line drawing itself to its price |
| 23 | 14.38 | Page scrolls: the long table, „Seit mehr als 20 Jahren" |
| 25.5–27 | 15.94–16.88 | Red surface rises: „Sie feiern -" / „wir catern!" |
| 29–32 | 18.13–20.00 | The red lifts away and the logo settles to exactly native size on the last frame |

All text is verbatim from the website (slogan, section words, menu card, album captions,
„Seit mehr als 20 Jahren", „Sie feiern - wir catern!"). Red is only ever a flat surface or the
slogan's dots. Motion is closed-form springs; camera moves inside photos are constant-speed dollies.

## Photo resolution: shots that need higher-resolution originals

No photo is ever shown above 0.98 screen pixels per source pixel (the renderer logs a warning
if one would). That is why the food and occasion photos sit in album-style windows instead of
filling the frame. To make these shots full-bleed with a real push-in, these originals are needed:

| Shot | Have | Needed for full-bleed 3:4 (1080×1440) with ~10 % push | Needed for full-bleed 9:16 |
|---|---|---|---|
| Bruschetta und Löffel-Häppchen | 900×1200 | ≥ 1200×1600 | ≥ 1200×2130 |
| Tomate und Mozzarella | 900×1200 | ≥ 1200×1600 | ≥ 1200×2130 |
| Pfälzer Kartoffelsalat | 900×1200 | ≥ 1200×1600 | ≥ 1200×2130 |
| Desserts im Glas | 900×1200 | ≥ 1200×1600 | ≥ 1200×2130 |
| Hochzeit (Blumenbogen) | 800×1000 | ≥ 1200×1600 | ≥ 1200×2130 |
| Private Feier (runder Tisch) | 800×1000 | ≥ 1200×1600 | ≥ 1200×2130 |
| Firmenfeier (Bar) | 800×1000 | ≥ 1200×1600 | ≥ 1200×2130 |
| Tafel zwischen Zypressen | 1200×1600 | ok (used full-width at 0.90–0.97) | ≥ 1200×2130 (in a window for now) |
| Logo | 560×147 PNG | an SVG or PDF logo | the end card could then be larger; at 560 px its thin strokes are faint on a phone |

## Sound (social versions)

`score.py` synthesizes everything (felt piano, upright bass, brushes, quiet knocks and plucks on the
cuts) in F major, 96 BPM, 8 bars. Two cycles are rendered and the second kept, so reverb tails wrap
and the loop is seamless. −14.0 LUFS integrated, −1.6 dBFS peak. `beats.json` holds the grid measured
from the audio with librosa (95.99 BPM, 18 ms onset lag, under one frame, so the written grid is used).
Every hit lands within 12 ms of its cut. The web loop carries no audio and reads completely without it.

## Critique pass (prompts/13-critique-pass)

| Round | Hook | Phone | Motion | Variety | Composition | Brand | Sound | Fixed |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 6 | 7 | 6 | 7 | 9 | – | Hook rebuilt as a same-width lockup (short words get huge); occasions dealt as prints instead of a second window-plus-caption section; menu fine print enlarged |
| 2 | 8 | 7 | 8 | 7 | 7 | 9 | 7 | Logo settles on a critically damped spring so the seam is not a 2.5 s dead hold; menu card enlarged; logo moved to integer pixels (was soft) |
| 3 | 8 | 7 | 8 | 8 | 8 | 9 | 9 | Captions wrap to the photo width (the Kartoffelsalat caption ran off-frame) |
| 4 (all formats) | 8 | 8 | 8 | 8 | 8 | 9 | 9 | 16:9 caption column widened, 16:9 menu enlarged, 9:16 groups centred vertically |

Bugs found by looking at sheets: pages bled through at the end (child `visibility` overrides a hidden
parent, fixed with `display`); five camera moves hit the photo edge (cameras now move inside the
available slack, so they cannot clamp); ffmpeg's `tile` dropped frames from short sequences
(`tile.py` uses PIL instead). Last frame and frame 0 are pixel-identical in the render.
Review sheets are in `review/`.

## Rebuild

```sh
npm install                                   # Playwright
pip install numpy librosa soundfile pyloudnorm
python3 films/kindermann/score.py             # out/kindermann/score.wav + beats.json
node films/kindermann/render.mjs --fmt 3x4 --beats    # contact sheet, one frame per beat
node films/kindermann/render.mjs --fmt 3x4            # lossless master (also 9x16, 16x9)
films/kindermann/deliver.sh                   # dist/web + dist/social
```
