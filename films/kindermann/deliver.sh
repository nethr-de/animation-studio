#!/usr/bin/env bash
# Encode deliverables from the lossless masters (node render.mjs --fmt ...) and the score (python3 score.py).
#   web/    3:4 hero loop for kindermann-catering.de: H.264 MP4 + VP9 WebM, no audio track, < 3 MB each, poster.webp = frame 0
#   social/ 3:4, 9:16, 16:9 with the score: H.264 yuv420p CRF 16 + AAC
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT=out/kindermann
DIST=films/kindermann/dist
mkdir -p "$DIST/web" "$DIST/social"
LIMIT=$((3 * 1000 * 1000))

# --- web: two-pass to a bitrate budget (20 s x 1.05 Mbit/s ~ 2.6 MB) ---
VB=${VB:-1050k}
P=$OUT/x264pass
ffmpeg -v error -y -i $OUT/master-3x4.mkv -an -c:v libx264 -preset veryslow -tune film -profile:v high -level 4.0 \
  -pix_fmt yuv420p -b:v $VB -maxrate 1800k -bufsize 3600k -g 48 -pass 1 -passlogfile $P -f mp4 /dev/null
ffmpeg -v error -y -i $OUT/master-3x4.mkv -an -c:v libx264 -preset veryslow -tune film -profile:v high -level 4.0 \
  -pix_fmt yuv420p -b:v $VB -maxrate 1800k -bufsize 3600k -g 48 -pass 2 -passlogfile $P -movflags +faststart \
  "$DIST/web/kindermann-loop-3x4.mp4"
V=$OUT/vp9pass
ffmpeg -v error -y -i $OUT/master-3x4.mkv -an -c:v libvpx-vp9 -b:v 950k -pix_fmt yuv420p -row-mt 1 -tile-columns 2 \
  -deadline good -cpu-used 1 -g 96 -pass 1 -passlogfile $V -f webm /dev/null
ffmpeg -v error -y -i $OUT/master-3x4.mkv -an -c:v libvpx-vp9 -b:v 950k -pix_fmt yuv420p -row-mt 1 -tile-columns 2 \
  -deadline good -cpu-used 1 -g 96 -pass 2 -passlogfile $V "$DIST/web/kindermann-loop-3x4.webm"
ffmpeg -v error -y -i $OUT/master-3x4.mkv -frames:v 1 -c:v libwebp -quality 88 "$DIST/web/poster.webp"

for f in "$DIST/web/kindermann-loop-3x4.mp4" "$DIST/web/kindermann-loop-3x4.webm"; do
  s=$(stat -c %s "$f")
  [ "$s" -lt $LIMIT ] || { echo "TOO BIG: $f ($s bytes)"; exit 1; }
done

# --- social: house encode, with the score ---
for fmt in 3x4 9x16 16x9; do
  ffmpeg -v error -y -i $OUT/master-$fmt.mkv -i $OUT/score.wav -map 0:v -map 1:a \
    -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high \
    -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$DIST/social/kindermann-$fmt.mp4"
done
ls -la "$DIST"/web "$DIST"/social
