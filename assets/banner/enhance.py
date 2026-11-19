#!/usr/bin/env python3
"""Gentle deterministic beauty pass: hue-preserving bloom + a light luminance lift.

No saturation push, no diffusion — colour identity is preserved by construction,
because every step scales luminance and keeps per-pixel channel ratios.

Input:  work/originalbanner.png  ->  Output: work/art-enhanced.png
Canvas stays at the source resolution; see WORKFLOW.md."""
from PIL import Image, ImageFilter
import numpy as np

SRC, OUT = "work/originalbanner.png", "work/art-enhanced.png"
BLOOM    = 0.12    # glow strength (additive light, in the SAME hues)
THRESH   = 0.55    # only pixels brighter than this emit glow (keeps navy flat)
SOFT     = 0.25    # ramp width above the threshold
CLAR     = 0.18    # luminance local-contrast gain ("clarity")
CURVE    = 0.03    # gentle S-curve on luminance: deeper darks, lift on lights
SHARP    = dict(radius=1.2, percent=20, threshold=3)  # final linework crispness

im = Image.open(SRC).convert("RGB")
W = im.width
a = np.asarray(im, dtype=np.float32) / 255.0
Y = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

# 1) hue-preserving bloom: extract bright neon cores, blur wide, screen back
lum = a @ Y
m = np.clip((lum - THRESH) / SOFT, 0, 1)
cores = (a * m[..., None] * 255).astype(np.uint8)
g = np.asarray(Image.fromarray(cores).filter(
    ImageFilter.GaussianBlur(int(W * 0.012))), dtype=np.float32) / 255.0
out = 1.0 - (1.0 - a) * (1.0 - g * BLOOM)

# 2) clarity + S-curve in luminance ONLY (per-pixel channel ratios kept -> hue kept)
l0 = np.clip(out, 0, 1) @ Y
lb = np.asarray(Image.fromarray((l0 * 255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(int(W * 0.0055))), dtype=np.float32) / 255.0
l1 = l0 + CLAR * (l0 - lb)
l1 = (1 - CURVE) * l1 + CURVE * (l1 * l1 * (3 - 2 * l1))
ratio = np.clip(l1 / (l0 + 1e-4), 0, 4)
out = np.clip(out * ratio[..., None], 0, 1)

# 3) thresholded unsharp: crisps icons/terminal text without white halos on neon edges
Image.fromarray((out * 255).astype(np.uint8)).filter(
    ImageFilter.UnsharpMask(**SHARP)).save(OUT)
print(f"wrote {OUT} at {im.width} wide")
