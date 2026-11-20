# Banner pipeline

The shipped banner is produced from a supplied artwork file by two deterministic
scripts. No generative model is involved in the output, so the same input always
produces the same `banner.webp`.

## Inputs and outputs

| Stage | Script | Input | Output |
| --- | --- | --- | --- |
| 1. Enhance (optional) | `enhance.py` | `work/originalbanner.png` | `work/art-enhanced.png` |
| 2. Fade + encode | `fade_bottom.py` | `work/art-enhanced.png` | `../banner.webp` |

Stage 1 is skipped when the delivered art already has the look you want — point
stage 2 straight at the master:

```sh
SRC=work/originalbanner.png python3 fade_bottom.py
```

The canvas stays at the source resolution (1981 px wide). Upscaling a render adds
no detail and only costs bytes. `work/` holds the master and the intermediates
and is git-ignored.

## Stage 1 — enhance (`enhance.py`)

A gentle, hue-preserving pass, deliberately restrained:

- **Bloom** on bright cores only (`BLOOM 0.12`, threshold `0.55`, ramp `0.25`),
  screened back so flat dark areas stay flat.
- **Clarity** on luminance alone (`CLAR 0.18`, blur `0.0055`), then a light
  luminance S-curve (`CURVE 0.03`). Per-pixel channel ratios are preserved, so
  colours are unchanged by construction — nothing pushes saturation.
- **Thresholded unsharp** (`radius 1.2`, `percent 20`, `threshold 3`) so linework
  and small text stay crisp without halos on neon edges.

On the current art this raises the 99th-percentile luminance from 78 to 88 — a
small lift, not a restyle. Stronger settings (the 2026-11-19 pass used
`BLOOM 0.17 / CLAR 0.40 / percent 35`) read as over-processed on the neon arcs.

## Stage 2 — fade + encode (`fade_bottom.py`)

The heading should sit close to the artwork, so the script finds the lowest row
holding coloured content and trims the dead floor below it:

- **Trim** to `content_bottom + 0.80 % of width` — breathing room, nothing more.
- **Fade** the last `5.0 %` of the width on an alpha ramp (`EXP 0.65`, hold then
  fall), starting below the world map so the map stays at full strength.
- **Pad** a final `0.2 %` of fully transparent band.

All three are fractions of the canvas width, so the merge looks the same at any
resolution, and the trim follows the art instead of a hardcoded pixel height.

The band is **transparent, not black**: that is what makes the banner sit
correctly on both the dark and the light GitHub theme. A baked black band would
leave a visible stripe on the light theme.

## Encode

`fade_bottom.py` writes WebP at `quality 95`, `alpha_quality 100`, `method 6`.
At 5× zoom on the hardest regions (the dome glow arc, the dotted mesh, the leaf
detail) this is visually indistinguishable from a lossless encode, at ~210 KiB
instead of ~1 000 KiB lossless or ~2 000 KiB PNG. `alpha_quality 100` keeps the
fade ramp bit-exact.

## Run

```sh
cd assets/banner
mkdir -p work
cp /path/to/artwork.png work/originalbanner.png
python3 enhance.py                              # optional
SRC=work/originalbanner.png python3 fade_bottom.py   # or rely on art-enhanced.png
```

Requires `Pillow` and `numpy`.

## Checklist before swapping the art

- [ ] No readable text baked into the image — identity comes from the heading.
- [ ] Sharp at 100 % zoom.
- [ ] Composes on both light and dark themes (the transparent band is what makes
      this work — do not crop it).
- [ ] `README.md` banner `alt` text describes the new render.

## GitHub render notes

The profile README column caps around 1500 CSS px. The source is 1981 px wide
(~1.3× density) at ~210 KiB — comfortably under every GitHub limit, with room to
go to 3000 px if true 2× density ever matters.
