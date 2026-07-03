---
name: script-from-concept
description: Turn a reviewed concept map into a narrated video script (content/{slug}-script.md) with beats, runtime budget, and linking — layer 3 of the pipeline. Use when a chapter's concept is reviewed and needs its script written.
---

# script-from-concept — content/{slug}.md → content/{slug}-script.md

You are writing the narration and beat structure for one chapter video. The
script is the source of truth for everything spoken and for timing; the
scene layer is generated from it.

Per the user's standing preference, start by printing the layer-flow summary
(source → concept → **script** → scene → build) and the review file path
(`content/{slug}-script.md`).

## Preconditions

- The concept (`content/{slug}.md`) exists and its `status` is `reviewed`
  or better. If it is still `draft`, stop and ask for the concept review.

## Procedure

1. `python tools/scaffold.py --layer script --chapter SLUG --project DIR`
   — emits front matter (derived_from + sha, voice/timing contract, one
   beat per concept-ledger entry) and a narration section per beat.
2. Write the narration. Reference to imitate:
   `examples/probability/content/5-discrete-random-variables-script.md`.
   Binding rules (STYLE_BOOK §8):
   - Narration drives animation length, never the reverse.
   - `<bookmark mark="id"/>` markers are *authoring* sync points; the scene
     realizes each chunk as its own sequential voiceover block (no Whisper).
     Put a marker wherever a new element should appear exactly as named —
     per-phrase sub-blocks, not one long paragraph.
   - Numbers and symbols are spoken as words ("lambda over n", not "λ/n").
   - No em-dashes in on-screen captions; drop filler ("So", "again and
     again"); don't promise "coming up" content you may cut.
3. Fill the `linking:` block — objective (intro_card), recap (previous
   chapter), key_idea (outro_bridge), bridge (next chapter). Neighbour
   titles come from project.yaml order; the scaffold pre-fills them.
4. Budget the runtime: `est_sec ≈ narration_words / words_per_minute * 60`
   per beat; fill `narration_words`/`est_sec` and `estimated_runtime_sec`.
   If the estimate exceeds `target_runtime_sec + tolerance_sec`, cut now —
   `optional` concepts first — and record what you'd cut next in the
   **Cut list** section. After render, `make measure` writes the real
   durations back and `check_status` enforces the tolerance.

## Exit checklist

```
make stamp PROJECT=DIR
make check PROJECT=DIR      # sync + notation + status all green
```

Status stays `draft` → human review; rendering hard-requires `approved`
(render.py refuses otherwise, and TTS money is only spent on approved
narration). Tell the human the exact file to review and stop.
