#!/usr/bin/env python3
"""Merge the banner into the README page background for any GitHub theme.
Bottom of the art dissolves via an alpha ramp (hold, then fall), then the
canvas extends with a fully transparent band so the H1/blockquote below the
image sits on the page background seamlessly — no text baked into pixels.
Input:  work/art-enhanced.png (output of enhance.py)  ->  Output: ../banner.png
See WORKFLOW.md rows 16-17."""
from PIL import Image
import numpy as np

SRC = "work/art-enhanced.png"
W    = 2560
FADE = 110    # px of art that dissolve (at 2560 wide)
PAD  = 40     # px of fully transparent band below the art
EXP  = 0.65   # <1 = hold the brightness, then drop late (natural light fall-off)

im = Image.open(SRC).convert("RGBA")
im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
w, h = im.size

alpha = np.array(im)[:, :, 3].astype(np.float64)
alpha[h - FADE:, :] *= (np.linspace(1.0, 0.0, FADE) ** EXP)[:, None]
im.putalpha(Image.fromarray(alpha.astype("uint8")))

out = Image.new("RGBA", (w, h + PAD), (0, 0, 0, 0))
out.paste(im, (0, 0), im)
out.save("../banner.png")
print(f"wrote ../banner.png: {w}x{h + PAD} (fade={FADE}, pad={PAD})")
