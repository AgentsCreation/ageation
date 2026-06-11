# Example project: Undergraduate Probability I

The original worked example this framework was extracted from: 12 chapters of
CC0 LaTeX probability notes taken through the full pipeline. Chapter 5
(`scenes/discrete_random_variables.py` + `content/5-discrete-random-variables*`)
is the fully-built reference implementation — voiceover scenes, bookmark-free
timing, overflow guards, provenance stamps.

This directory is a complete, self-contained project: `course.yaml` (spine +
notation rules), `content/` (concept + script markdown for all 12 chapters),
`sources/` (vendored working copies of the `.tex` notes), `scenes/`, and the
probability `NOTATION.md`. The upstream `input/Probability/` parent notes are
not included (they were gitignored); the vendored `sources/` copies are enough
to build from.

Run the framework tools against it from the repo root:

```
uv run python tools/check_sync.py --project examples/probability
uv run python tools/check_notation.py --project examples/probability
uv run python tools/render.py --project examples/probability -q l
```

`KICKOFF.md` is the historical hand-off prompt from when this was the live
project, kept for reference.
