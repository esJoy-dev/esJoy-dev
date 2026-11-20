#!/usr/bin/env python3
"""Fade the banner into the page background and write the shipped WebP.

The bottom of the art dissolves via an alpha ramp (hold, then fall), the dead
floor below the artwork is trimmed so the heading sits close to the art, and the
canvas extends with a thin fully transparent band. The band is TRANSPARENT, not
black: that is what makes the banner sit correctly on both the dark and the
light GitHub theme.

Input:  work/originalbanner.png -> work/art-enhanced.png -> ../banner.webp
See WORKFLOW.md."""
from PIL import Image
import numpy as np
import os

SRC = os.environ.get("SRC", "work/art-enhanced.png")   # override to skip stage 1
OUT = os.environ.get("OUT", "../banner.webp")
MARGIN_RATIO  = 0.0162   # breathing room kept below the lowest coloured pixel
FADE_RATIO    = 0.0430   # px of art that dissolve, as a fraction of canvas width
PAD_RATIO     = 0.0020   # fully transparent band below the art
EXP           = 0.65     # <1 = hold the brightness, then drop late (natural fall-off)
QUALITY       = 95       # visually indistinguishable from the source at 5x zoom
ALPHA_Q       = 100      # keep the alpha ramp exact
CONTENT_SAT   = 0.25     # a pixel counts as content if it is this saturated...
CONTENT_LUM   = 0.06     # ...and at least this bright
Y = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def content_bottom(im):
    """Lowest row holding neon/led content, so the trim follows the artwork."""
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    lum = a @ Y
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 0.05, (mx - mn) / np.maximum(mx, 1e-6), 0)
    rows = np.where(((sat > CONTENT_SAT) & (lum > CONTENT_LUM)).any(axis=1))[0]
    return int(rows.max()) if len(rows) else im.height - 1


im = Image.open(SRC).convert("RGBA")
w, h = im.size
bottom = content_bottom(im)
crop_h = min(h, bottom + round(w * MARGIN_RATIO))
im = im.crop((0, 0, w, crop_h))
fade = min(round(w * FADE_RATIO), crop_h)
pad = round(w * PAD_RATIO)

alpha = np.array(im)[:, :, 3].astype(np.float64)
alpha[crop_h - fade:, :] *= (np.linspace(1.0, 0.0, fade) ** EXP)[:, None]
im.putalpha(Image.fromarray(alpha.astype("uint8")))

out = Image.new("RGBA", (w, crop_h + pad), (0, 0, 0, 0))
out.paste(im, (0, 0), im)
out.save(OUT, format="WEBP", quality=QUALITY, alpha_quality=ALPHA_Q, method=6)
print(f"content ends at y={bottom}; wrote {OUT}: {w}x{crop_h + pad} "
      f"(crop_h={crop_h}, fade={fade}, pad={pad}, q={QUALITY})")
