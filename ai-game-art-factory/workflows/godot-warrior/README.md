# Illustrated warrior playback

Requires Godot 4 and the exported real illustrated sheets in
`exports/warrior_v002/front_left` and `front_right`. The project reads those
persisted PNGs directly; there are no substitute assets or procedural characters.

```sh
python3 scripts/warrior_export.py --sheet assets/characters/warrior_v002/sheet-front_left.png --direction front_left
python3 scripts/warrior_export.py --sheet assets/characters/warrior_v002/sheet-front_right.png --direction front_right
python3 scripts/warrior_export.py --comparison
godot --path workflows/godot-warrior
godot --headless --path workflows/godot-warrior --quit-after 20
godot --path workflows/godot-warrior -- --capture
```

The actual source filenames are recorded in each export's `atlas.json`. Both
directions must be exported before the six-panel scene can start. SPACE pauses,
RIGHT advances 60ms, R restarts. The 256px and 96px displays use exactly those
pixel dimensions. The review automatically repeats one-shot attacks/defense with
a 450ms hold; `atlas.json` still marks them `loop: false` for game integration.

`--capture` requires a real rendering/display backend and saves
`exports/warrior_v002/godot-actual-size.png`. Headless only validates resource
loading; it does not prove appearance. Art approval remains pending.
Capture freezes the real timeline at 400ms so startup speed cannot change the
selected frame. Add `--capture-time-ms=600` to inspect another timeline sample.

Exporter inputs are square, transparent 4×4 sheets: four idle cells, eight attack
cells, four defense cells, in row-major order. It never strips backgrounds or
generates intermediate frames. All cells receive the same scale. Optional
`--offsets-json` accepts explicit per-frame integer translations only, and rejects
translations that crop visible pixels. Per-cell alpha bounds and the 8px safe
margin are reported, independently of manual visual checks.

Generated dimensions such as 1254×1254 are supported: the entire sheet is
resampled to 1024×1024 once, then split into 256px cells. Fractional source cell
bounds and rounded rectangles are both recorded; individual subjects are never
rescaled to fill their own bounding boxes.

If the artist/generator did not respect a regular grid, `--layout-json PATH`
accepts a reviewed layout instead:

```json
{
  "uniform_scale": 0.68,
  "target_foot_anchor": [128, 224],
  "cells": {
    "idle_00": {
      "source_rect": [0, 0, 314, 320],
      "source_foot_anchor": [160, 304]
    }
  }
}
```

The actual file must define all 16 names (`idle_00`–`03`, `attack_00`–`07`,
`defense_00`–`03`). Rectangles are source pixels; foot anchors are local to their
rectangle. One shared affine scale is used for every crop, followed by integer
translation to the common target anchor. These are reviewed image landmarks,
not skeletal measurements. No alpha filtering or per-subject zoom is applied.

QA records both all nonzero-alpha and alpha≥16 bounds, contact with each source
crop boundary, and any alpha lost while placing onto the output canvas. Adding
padding cannot clear a source crop contact error. It also cannot recover content
that was already cut off in the original source.

A corrected group of frames may come from another transparent source image.
Add `"source_file": "correction-strip.png"` and `"uniform_source_scale": 0.5`
to those cells; paths resolve relative to the layout JSON. This source value is
a resolution-normalization factor multiplied by the layout's common scale:
with a global scale of0.60 and source factor0.52, effective pixel scale is0.312.
Every cell referring to that file must use exactly the same scale. The exporter rejects per-frame
zoom and records each input file's dimensions/SHA-256 plus the precise crop,
scale and placement for every exported frame. A base sheet containing replaced
poses is a component source, not the final animation atlas.

Each action also exports a GIF. GIF uses a fixed dark background (`#26313e`), a
single shared 256-color palette across the clip and no dithering. Millisecond
durations are rounded to GIF's 10ms resolution; decoded frame counts/durations
are recorded. The transparent PNG/WebP/APNG assets retain their real alpha.

`--comparison` combines the two saved directions into
`exports/warrior_v002/actions-comparison.gif`: six panels with 256px sprite
canvases, sampled at actual frame-change events over a 2000ms review period.
Idle loops; attack and defense finish once and hold their final pose before the
review restarts. `comparison-gif.json` records that presentation timing and the
decoded GIF duration. It is a review presentation, not a new game animation.

In the current restricted Linux environment, set writable cache directories:

```sh
mkdir -p /tmp/warrior-godot/data /tmp/warrior-godot/config /tmp/warrior-godot/cache
XDG_DATA_HOME=/tmp/warrior-godot/data XDG_CONFIG_HOME=/tmp/warrior-godot/config XDG_CACHE_HOME=/tmp/warrior-godot/cache godot --headless --path workflows/godot-warrior --quit-after 20
```

The existing system Xorg dummy driver and Mesa can provide real rendering if no
display is running. Use an unoccupied display number and a separate process;
never terminate an unrelated display. The project does not install a renderer.
