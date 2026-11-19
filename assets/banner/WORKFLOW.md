# Banner pipeline

The shipped banner is produced from a supplied artwork file by two deterministic
scripts. No generative model is involved in the output, so the same input always
produces the same `banner.webp`.

## Inputs and outputs

| Stage | Script | Input | Output |
| --- | --- | --- | --- |
| 1. Enhance | `enhance.py` | `work/originalbanner.png` | `work/art-enhanced.png` |
| 2. Fade | `fade_bottom.py` | `work/art-enhanced.png` | `../banner.webp` |

The canvas stays at the source resolution (2172 px wide) — upscaling a render
adds no detail and only costs bytes. `work/` holds the master and the
intermediates and is git-ignored.

## Stage 1 — enhance (`enhance.py`)

A gentle, hue-preserving pass, deliberately restrained:

- **Bloom** on bright cores only (`BLOOM 0.12`, threshold `0.55`, ramp `0.25`),
  screened back so flat dark areas stay flat.
- **Clarity** on luminance alone (`CLAR 0.18`, blur `0.0055`), then a light
  luminance S-curve (`CURVE 0.03`). Per-pixel channel ratios are preserved, so
  colours are unchanged by construction — nothing pushes saturation.
- **Thresholded unsharp** (`radius 1.2`, `percent 20`, `threshold 3`) so linework
  and small text stay crisp without halos on neon edges.

Stronger settings exist (the 2026-11-19 pass used `BLOOM 0.17 / CLAR 0.40 /
percent 35`); they read as over-processed on the neon arcs and are not used.

## Stage 2 — fade (`fade_bottom.py`)

Merges the art into the page background: the last `4.3 %` of the canvas width
dissolves on an alpha ramp (`EXP 0.65`, hold then fall), and the canvas extends
`1.56 %` of its width as a fully transparent band below the art. The ramp is a
fraction of the width, not a fixed pixel count, so the merge looks the same at
any resolution.

The band is **transparent, not black**: that is what makes the banner sit
correctly on both the dark and the light GitHub theme. A baked black band would
leave a visible stripe on the light theme.

## Encode

`fade_bottom.py` writes WebP at `quality 95`, `alpha_quality 100`, `method 6`.
At 5× zoom on the hardest regions (the dome glow arc, the dotted mesh, the leaf
detail) this is visually indistinguishable from a lossless encode, at ~330 KiB
instead of ~1 450 KiB or ~2 900 KiB for PNG. `alpha_quality 100` keeps the fade
ramp bit-exact.

## Run

```sh
cd assets/banner
mkdir -p work
cp /path/to/artwork.png work/originalbanner.png
python3 enhance.py
python3 fade_bottom.py          # writes ../banner.webp
```

Requires `Pillow` and `numpy`.

## Checklist before swapping the art

- [ ] No readable text baked into the image.
- [ ] Sharp at 100 % zoom.
- [ ] Composes on both light and dark themes (the transparent band is what makes
      this work — do not crop it).
- [ ] `README.md` banner `alt` text describes the new render.

## GitHub render notes

The profile README column caps around 1500 CSS px. The source is 2172 px wide,
which covers ~1.4× density — sharp on standard and most HiDPI displays, and well
under GitHub's file-size limits at ~330 KiB.
