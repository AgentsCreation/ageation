---
name: concept-from-tex
description: Distill a vendored LaTeX chapter into its concept map (content/{slug}.md) — layer 2 of the pipeline. Use when a chapter needs its concept doc written or rewritten from the .tex source.
---

# concept-from-tex — vendored .tex → content/{slug}.md

You are performing the first authored transform of the ageation pipeline:
reading the chapter's vendored LaTeX (and its pandoc `.md` companion when one
exists) and distilling *what is worth animating* into a concept map. The
output is judgment; the file skeleton is not — scaffold it.

Per the user's standing preference, start by printing the layer-flow summary
(source → **concept** → script → scene → build) and the exact path of the
file the human will review at the end (`content/{slug}.md`).

## Inputs

- `sources/{slug}.tex` — the editable vendored copy (run
  `tools/vendor_sources.py --project DIR` first if absent). NEVER read or
  edit the upstream original for content work.
- `sources/{slug}.md` — pandoc companion, when present: use it for intent
  and structure, the `.tex` for precise content.
- `project.yaml` — pedagogy targets, notation rules, prereq chain.

## Procedure

1. `python tools/scaffold.py --layer concept --chapter SLUG --project DIR`
   — emits the front matter (provenance-ready) + the seven sections + the
   source's `\section` outline as a comment.
2. Read the full source (and companion). Fill the seven sections. The
   reference to imitate: `examples/probability/content/5-discrete-random-variables.md`.
3. Fill the `concepts:` ledger — one entry per idea worth a beat, each with
   `importance: core | highlight | optional`. `highlight` marks the visual
   climax; `optional` marks the first runtime cut.
4. **Vertical fidelity**: every claim in the concept must be traceable to
   the source. No fabricated theorems, no invented examples presented as
   the source's.
5. Notation: use the project's expanded forms (`notation.rules` in
   project.yaml; NOTATION.md explains why).

## Exit checklist

```
make stamp PROJECT=DIR
make sync PROJECT=DIR       # local->concept must be in-sync
make notation PROJECT=DIR
```

Status stays `draft` — **this is a human review gate**. Tell the human the
exact file to review and stop; do not proceed to the script layer until the
concept is marked `reviewed`.
