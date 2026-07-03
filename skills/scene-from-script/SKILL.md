---
name: scene-from-script
description: Generate the Manim scene file (scenes/{module}.py) from an approved-or-reviewed script — layer 4 of the pipeline. Use when a chapter's script is ready and its scenes need building or regenerating.
---

# scene-from-script — content/{slug}-script.md → scenes/{module}.py

You are building the animation layer. The scene file is a **build
artifact**: when narration must change, change the script and regenerate —
never let the .py drift from its script (that is what the sha stamp gates).
Visual-only edits (positions, colors, sizes) are fine directly in the .py
and need no re-stamp.

Per the user's standing preference, start by printing the layer-flow summary
(source → concept → script → **scene** → build) and the file the human will
eventually review (the assembled draft mp4; the code artifact is
`scenes/{module}.py`).

## Preconditions

- Script `status` is `reviewed` or better.

## Procedure

1. `python tools/scaffold.py --layer scene --chapter SLUG --project DIR`
   — emits the sha-stamped skeleton: one `VoiceoverScene` per beat,
   narration already split into sequential voiceover blocks at the
   script's `<bookmark/>` markers, `make_speech_service()` returning
   `speech_service()` (voice comes from project.yaml — never hardcode a
   provider or voice), intro/outro pre-wired from the `linking:` block.
2. Write the animations inside each voiceover block, timed with
   `run_time=tracker.duration`. Reference to imitate:
   `examples/probability/scenes/discrete_random_variables.py`.

## Binding rules (STYLE_BOOK — apply the first time, not on review)

- **One ACCENT at a time**: exactly one thing yellow at any moment.
- **Five font sizes only**: TITLE/SECTION/BODY/SMALL/CAPTION — never a raw
  `font_size=` number off the scale.
- **Everything in frame**: pass composed groups through `fit_to_frame`;
  axis labels via `axis_label_x/y` (safe LABEL_BUFF).
- **Use `_style` helpers, never local copies**: `omega_box`, `ball`,
  `die_face`, `coin`, `make_pmf_chart`, `intro_card`, `outro_bridge`,
  `progress_tag`. A chapter drawing its own glyphs reads as a different
  series.
- **Never `\n` inside a `Text(...)`** — it renders garbled; multi-line
  intro objectives / outro key ideas take a list of lines.
- **One chart on screen at a time**; FadeOut everything at the end of each
  beat.
- **Declare intended overlaps** with `mark_intended_overlap(a, b, ...,
  reason=...)` *before the first play() that shows them* (Venn ellipses,
  crossing arrow fans, bars over ghost bars). Do not write
  `.lint-allow.yaml` sidecars — they are deprecated.
- **Validate parameters before rendering**: probabilities in [0,1]
  (p = λ/n needs n > λ), index ranges shown next to PMFs, conditional vs
  unconditional Pr distinguished.
- Render-time gotchas (CLAUDE.md): no `LaggedStartMap` with
  `Create`/`Write` over composite mobjects (use
  `LaggedStart(*[Create(m) for m in group], ...)`); `Axes.plot` with a
  decreasing `x_range` silently returns an empty curve — plot increasing
  and `.reverse_points()`.

## Exit checklist

```
make stamp PROJECT=DIR
python tools/lint_scene.py --project DIR --chapter SLUG   # 0 violations
make check PROJECT=DIR
```

Set the chapter's project.yaml `status: built`. Then hand off to
render-verify.
