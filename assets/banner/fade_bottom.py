#!/usr/bin/env python3
"""Fade the banner into the page background and write the shipped WebP.

Default input: work/art-enhanced.png (stage 1 output). To run on the master
directly and skip stage 1, set SRC, e.g.:
    SRC=work/originalbanner.png python3 fade_bottom.py

What it does, in order:
1. Trim: find the lowest row of coloured content and keep only a small margin of
   floor below it, so the heading in README sits close to the artwork.
2. Fade: dissolve the bottom of the art on an alpha ramp (hold, then fall).
3. Pad: extend the canvas with a thin FULLY TRANSPARENT band below the art.

Geometry, thresholds and the transparent-band rationale are documented in
WORKFLOW.md, the authority for this pipeline."""
from PIL import Image
import numpy as np
import os

SRC = os.environ.get("SRC", "work/art-enhanced.png")   # override to skip stage 1
OUT = os.environ.get("OUT", "../banner.webp")           # default: repo assets/

# All geometry is a fraction of the canvas width, so the merge looks the same at
# any resolution and the trim follows the art instead of a hardcoded height.
MARGIN_RATIO = 0.0080   # floor kept below the lowest coloured row: 0.8 % of width
FADE_RATIO   = 0.0500   # rows that dissolve: 5.0 % of width (starts above the art's lowest content)
PAD_RATIO    = 0.0020   # fully transparent band below the art
EXP          = 0.65     # <1 = hold the brightness, then drop late (natural fall-off)
QUALITY      = 95       # visually indistinguishable from the source at 5x zoom
ALPHA_Q      = 100      # keep the alpha ramp exact

# Coloured-content detection. A pixel counts as content when BOTH hold:
#   - it is saturated (neon, LED, glow: chroma >> luminance here), and
#   - it is brighter than the floor.
# The values are tuned for this artwork's palette: the navy floor and its
# reflections sit under BOTH thresholds; map outlines and dome glow clear both.
# If a future master uses a different palette, re-check the printed row and the
# rendered result before shipping — a misfire crops visible art WITHOUT failing.
CONTENT_SAT = 0.25      # saturation (max-min)/max above which a pixel is "coloured"
CONTENT_LUM = 0.06      # luminance above which a pixel is lit rather than floor
LUMA_WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)  # Rec. 709 luma — CONTENT_LUM is measured with this weighting


def content_bottom(im):
    """Lowest row containing coloured content; None when nothing classifies."""
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    lum = a @ LUMA_WEIGHTS
    mx, mn = a.max(axis=2), a.min(axis=2)
    # Zero-guard: np.where evaluates both branches eagerly, so the divisor
    # floor (not the mx > 0 mask) is what keeps black pixels (mx == 0) from
    # dividing by zero. Removing the floor breaks the run with warnings.
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-12), 0.0)
    rows = np.where(((sat > CONTENT_SAT) & (lum > CONTENT_LUM)).any(axis=1))[0]
    return int(rows.max()) if len(rows) else None


im = Image.open(SRC).convert("RGBA")
w, h = im.size
bottom = content_bottom(im)
if bottom is None:
    # No coloured content detected: skip the trim (keep full height) and report
    # it, so a silent mis-crop cannot happen on an unexpected master.
    print("no coloured content detected — skipping trim, fading full height")
    crop_h, fade_h = h, min(round(w * FADE_RATIO), h)  # never exceed the canvas
else:
    crop_h = min(h, bottom + round(w * MARGIN_RATIO))
    fade_h = min(round(w * FADE_RATIO), crop_h)
pad = round(w * PAD_RATIO)

im = im.crop((0, 0, w, crop_h))
alpha = np.array(im)[:, :, 3].astype(np.float64)
alpha[crop_h - fade_h:, :] *= (np.linspace(1.0, 0.0, fade_h) ** EXP)[:, None]
im.putalpha(Image.fromarray(alpha.astype("uint8")))

out = Image.new("RGBA", (w, crop_h + pad), (0, 0, 0, 0))
out.paste(im, (0, 0), im)
out.save(OUT, format="WEBP", quality=QUALITY, alpha_quality=ALPHA_Q, method=6)
print(f"content ends at y={bottom if bottom is not None else 'not detected (no trim)'}; "
      f"wrote {OUT}: {w}x{crop_h + pad} "
      f"(crop_h={crop_h}, fade={fade_h}, pad={pad}, q={QUALITY})")
