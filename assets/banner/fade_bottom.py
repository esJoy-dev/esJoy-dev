#!/usr/bin/env python3
"""Fade the banner into the page background and write the shipped WebP.

The bottom of the art dissolves via an alpha ramp (hold, then fall), and the
canvas extends with a fully transparent band so the H1/blockquote below the
image sits on the page background seamlessly — on a dark AND a light theme,
with no text baked into pixels. Nothing here is black-specific: the band is
transparent, so it merges with whatever colour the theme paints behind it.

Input:  work/art-enhanced.png  ->  Output: ../banner.webp
See WORKFLOW.md."""
from PIL import Image
import numpy as np

SRC = "work/art-enhanced.png"
OUT = "../banner.webp"
FADE_RATIO = 0.0430   # px of art that dissolve, as a fraction of canvas width
PAD_RATIO  = 0.0156   # px of fully transparent band below the art
EXP        = 0.65     # <1 = hold the brightness, then drop late (natural light fall-off)
QUALITY    = 95       # visually indistinguishable from the source at 5x zoom
ALPHA_Q    = 100      # keep the alpha ramp exact

im = Image.open(SRC).convert("RGBA")
w, h = im.size
fade = min(round(w * FADE_RATIO), h)   # never exceed the canvas
pad  = round(w * PAD_RATIO)

alpha = np.array(im)[:, :, 3].astype(np.float64)
alpha[h - fade:, :] *= (np.linspace(1.0, 0.0, fade) ** EXP)[:, None]
im.putalpha(Image.fromarray(alpha.astype("uint8")))

out = Image.new("RGBA", (w, h + pad), (0, 0, 0, 0))
out.paste(im, (0, 0), im)
out.save(OUT, format="WEBP", quality=QUALITY, alpha_quality=ALPHA_Q, method=6)
print(f"wrote {OUT}: {w}x{h + pad} (fade={fade}, pad={pad}, q={QUALITY})")
