# Critique pass

Source: article section 11 · Critique.

**What it does:** Makes Claude look at its own frames, score them, and fix the 3 worst problems.

**Use it for:** After every render, until every score is 8 or higher.

**Placeholders:** none

**Tips:** Generate `out/contact.png`, `out/strip.png` and `out/phone.png` first with the ffmpeg commands below.

The prompt is in [`prompt.md`](prompt.md).

## Make the review images first

```sh
# Contact sheet: 2 frames per second, 6 across
ffmpeg -i out/final.mp4 -vf "fps=2,scale=270:-1,tile=6x5" -frames:v 1 out/contact.png
# Strip: 12 consecutive frames around a fast action at 4.2s
ffmpeg -ss 4.1 -i out/final.mp4 -vf "scale=320:-1,tile=12x1" -frames:v 1 out/strip.png
# Phone test: how it reads at 360 px wide
ffmpeg -i out/final.mp4 -vf "fps=1,scale=360:-1,tile=5x3" -frames:v 1 out/phone.png
# Loop check: play it twice back to back and watch the seam
ffmpeg -stream_loop 1 -i out/final.mp4 -c copy out/loop_check.mp4
```
