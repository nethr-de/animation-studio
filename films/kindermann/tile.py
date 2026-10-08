"""Tile PNG stills into one review image: python3 tile.py OUT COLS WIDTH IN1 IN2 ..."""
import sys
from PIL import Image

out, cols, w, files = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4:]
ims = [Image.open(f).convert('RGB') for f in files]
h = round(ims[0].height * w / ims[0].width)
pad = 6
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (w + pad) + pad, rows * (h + pad) + pad), (128, 128, 128))
for i, im in enumerate(ims):
    sheet.paste(im.resize((w, h), Image.LANCZOS), (pad + (i % cols) * (w + pad), pad + (i // cols) * (h + pad)))
sheet.save(out)
