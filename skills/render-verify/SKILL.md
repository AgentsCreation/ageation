---
name: render-verify
description: Draft-render a built chapter, assemble it, check measured runtime against target, and hand the human one reviewable mp4 — layer 5 of the pipeline. Use when a chapter's scenes are built and need a draft render + verification pass.
---

# render-verify — scenes → one assembled draft .mp4 + verified timing

The deliverable of the whole pipeline is **one assembled .mp4 per chapter**;
per-beat clips are iteration artifacts. Drafts are free (render.py forces
gTTS for `-ql`), so render early and often. Final voiced renders cost money
and are the human's call.

Per the user's standing preference, start by printing the layer-flow summary
(source → concept → script → scene → **build**) and the exact deliverable
path: `media/videos/{module}/480p15/_assembled/{slug}.mp4`.

## Preconditions

- Chapter `status: built`; `make check` green.

## Procedure

1. Draft render + assemble (assembly auto-writes measured durations back
   into the script):

   ```
   uv run python tools/render.py --project DIR -q l SLUG --force
   uv run python tools/assemble.py --project DIR -q l SLUG
   ```

   (`--force` is acceptable for *drafts* while the script is `reviewed`;
   the final render still hard-requires `approved`.)
2. Check the timing contract: the assemble step printed the measured total;
   `make status PROJECT=DIR` enforces `target_runtime_sec ± tolerance_sec`
   once the chapter is `rendered`. Over budget → apply the script's Cut
   list (edit the *script*, regenerate the scene, re-stamp).
3. Spot-verify frames: extract one frame per beat with ffmpeg and look at
   it — accent discipline, nothing touching the frame border, captions in
   their lane:

   ```
   ffmpeg -y -ss 5 -i media/videos/{module}/480p15/{SceneClass}.mp4 -frames:v 1 /tmp/frame.png
   ```

4. Fix problems at the right layer: narration → script (then regenerate +
   re-stamp); visuals → scene .py directly (no re-stamp needed); uniform
   idiom fixes → `/scenes/_style.py` in the engine (STYLE_BOOK meta-lesson:
   a per-scene patch of a shared idiom is a bug waiting for the next
   chapter).
5. Hand the human the single assembled draft mp4 path for review. Apply
   their timestamped notes (re-render just the affected scene, verify the
   frame again).

## Finals (human-gated)

When the human approves: script `status: approved`, chapter
`status: rendered`, then hand over the command — do not run paid TTS
without being asked (voice choice is per-video; see project.yaml):

```
make video PROJECT=DIR      # lint-scene + 1080p60 render + assemble + measure
```

Report: scenes rendered, the assembled path, measured vs target runtime,
and anything skipped.
