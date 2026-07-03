---
name: animate-chapter
description: Orchestrate one chapter through the full pipeline (concept → script → scene → draft video) with exactly two human gates. Use when asked to "animate chapter X" or take a chapter end-to-end.
argument-hint: <chapter-slug> [--project DIR]
---

# animate-chapter — one slug, end to end, two human touch points

Walk the four processor skills in order for the given chapter slug. You are
the orchestrator: run the gates between stages, refuse to advance past a red
`make check`, and stop at the two human review gates.

Print at the start: the layer-flow summary
(source → concept → script → scene → build), which layers already exist for
this slug (check `content/{slug}.md`, `content/{slug}-script.md`, the scene
file), and where you will therefore resume.

## The walk

0. **Preflight**: `make doctor PROJECT=DIR`; `make check PROJECT=DIR`.
   If sources/{slug}.tex is missing, run `tools/vendor_sources.py` first.
1. **concept-from-tex** (skill) → `content/{slug}.md`, status `draft`.
   → **STOP: human gate 1.** Print the file path; wait for the human to
   mark it `reviewed` (they may edit it first).
2. **script-from-concept** (skill) → `content/{slug}-script.md`, `draft`.
   → **STOP: human gate 2.** Print the file path; wait for `reviewed`
   (drafts may proceed at `reviewed`; the *final* render requires
   `approved`).
3. **scene-from-script** (skill) → `scenes/{module}.py`; lint to 0
   violations; chapter `status: built`.
4. **render-verify** (skill) → assembled 480p draft + measured runtime.
   Hand the human ONE path:
   `media/videos/{module}/480p15/_assembled/{slug}.mp4`.

## Rules

- Never skip a gate; never mark a review status yourself.
- A red `make check` stops the walk — fix it at the layer that broke it,
  re-stamp, re-run.
- Resume idempotently: if a layer's file already exists and is in-sync,
  do not regenerate it; continue from the first missing/stale layer.
- Paid TTS (final voice) is never triggered by this skill; see
  render-verify's Finals section.
