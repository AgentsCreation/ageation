# NOTATION.md — How notation conventions work in this framework

A project's mathematical notation must agree across three places: the source
notes, the narration scripts, and the Manim scenes. In academic composition
the most common drift is notation (one author writes $\mathbb{E}$, another
$\mathrm{E}$), so each project fixes its choices once, as data, and enforces
them mechanically.

## Where the rules live

In the project's `project.yaml`, under `notation.rules`. Each rule is a literal
LaTeX string to avoid, the form to use instead, and a short reason:

```yaml
notation:
  rules:
    - avoid: '\mathbb{P}'
      use: '\Pr'
      reason: probability
```

Derive the rules from the source notes' own preamble macros (e.g.
`\newcommand{\Expect}{\mathrm{E}}`), so the generated layers match the book
exactly. A worked, fully-populated example — including a prose rationale
document — is `examples/probability/` (`project.yaml` + `NOTATION.md` there).

## How it's enforced

- `tools/check_notation.py` scans `content/*.md`, `scenes/*.py`, and the
  vendored `sources/*` for the avoided forms and fails (nonzero exit) if any
  appear. Run it before a render (`make notation`), or wire it into CI.
- Matching is **plain substring**, deliberately aggressive: an avoided form
  inside a comment, docstring, or prose line also fails. This is intentional —
  the layers are narrated and displayed verbatim, so there is no "harmless"
  place for the wrong notation. Rephrase the offending line instead of
  quoting the avoided form.
- When an upstream source violates the convention, fix it on the editable
  working copy, never the read-only parent:
  `tools/normalize_notation.py --write` rewrites the avoided forms in
  `sources/*` (then re-run `tools/stamp_provenance.py`). This is the reason
  for vendoring local copies — see PIPELINE.md.

## Important: Manim does not know the book's macros

Source notes often define shortcuts (`\Expect`, `\Var`, `\Prob`, …). Manim's
`MathTex` has **no** access to that preamble, so scenes must use the
**expanded** forms. Put helper functions for the expanded forms in
`scenes/_style.py` (e.g. `pr()`, `expectation()`, `variance()`) and prefer
them over hand-typed LaTeX in scenes.

## Recommended companion: a prose convention document

Rules-as-data say *what* is enforced; a short per-project notation document
(like `examples/probability/NOTATION.md`) records *why* — which source macros
the choices came from, how each quantity is spoken in narration, and the house
choices not pinned by any macro. Keep it next to `project.yaml` and update both
together when a convention changes.
