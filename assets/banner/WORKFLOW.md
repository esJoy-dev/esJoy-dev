# Banner pipeline

The shipped banner is produced from a supplied artwork file by two deterministic
scripts. No generative model is involved in the final output, so the same input
always produces the same `banner.png`.

## Inputs and outputs

| Stage | Script | Input | Output |
| --- | --- | --- | --- |
| 1. Enhance | `enhance.py` | `work/source-new.png` | `work/art-enhanced.png` |
| 2. Fade | `fade_bottom.py` | `work/art-enhanced.png` | `../banner.png` |

Both stages normalise the canvas to 2560 px wide, keeping the aspect ratio. The
`work/` directory holds intermediates and is git-ignored.

## Stage 1 — enhance (`enhance.py`)

Hue-preserving beauty pass at 2560 px wide:

- **Bloom** on bright cores only (`BLOOM 0.17`, threshold `0.55`, ramp `0.25`),
  screened back so flat dark areas stay flat.
- **Clarity** on luminance alone (`CLAR 0.40`, blur `0.0055`), then a gentle
  luminance S-curve (`CURVE 0.05`). Per-pixel channel ratios are preserved, so
  colours are unchanged by construction.
- **Thresholded unsharp** (`radius 1.3`, `percent 35`, `threshold 3`) so linework
  and small text stay crisp without halos on neon edges.

## Stage 2 — fade (`fade_bottom.py`)

Merges the artwork into the page background for any GitHub theme: the last
`110 px` dissolve on an alpha ramp (`EXP 0.65`, hold then fall), and the canvas
extends `40 px` of fully transparent band below the art. Nothing is baked into
pixels — the heading and quote under the image render on the page background.

## Run

```sh
cd assets/banner
mkdir -p work && cp /path/to/artwork.png work/source-new.png
python3 enhance.py
python3 fade_bottom.py          # writes ../banner.png
```

Requires `Pillow` and `numpy`.

## Checklist before swapping the art

- [ ] No readable text baked into the image.
- [ ] Sharp at 100 % zoom.
- [ ] Composes on both light and dark GitHub themes (the transparent band is the
      part that makes this work — do not crop it).
- [ ] `README.md` banner `alt` text describes the new render.

## GitHub render notes

The profile README column caps around 1500 CSS px; at 2× device pixel ratio the
useful ceiling is ~3000 px. 2560 px wide is the sweet spot: sharp on HiDPI and
well under GitHub's file-size limits.
