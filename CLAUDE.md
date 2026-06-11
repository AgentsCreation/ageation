# CLAUDE.md — Manim Video Pipeline Agent

## Start here (current state)

This project is a generic, file-based pipeline that turns a folder of LaTeX
notes into short, narrated, linked Manim videos. Before doing anything, read
**HISTORY.md** (goal, all design decisions + rationale, reproduce-from-scratch
roadmap) and **PIPELINE.md** (the layered spec). Also: **NOTATION.md** (how
per-project notation rules work) and **course.yaml** (the per-project config +
chapter spine — bootstrap one with `tools/init_course.py` if absent).

The decisions in HISTORY.md marked "do not relitigate" are settled: Python
3.12, bookmark-free sequential voiceover blocks, `_style.fit_to_frame`
overflow guard, expanded-LaTeX notation helpers in `_style.py`, vendored
editable `sources/` copies, and content-hash provenance. Gates: `make check`
(runs `tools/check_sync.py` + `tools/check_notation.py`); re-run
`tools/stamp_provenance.py` after regenerating any layer. All tools take
`--project DIR` (default `.`).

Reference implementation: **`examples/probability/`** — a complete 12-chapter
worked example. Its Chapter 5
(`examples/probability/scenes/discrete_random_variables.py` +
`examples/probability/content/5-*`) is the pattern to copy for new scenes.

The "Mission/Workflow" below is the original single-chapter sketch; the real
process is the multi-stage pipeline in PIPELINE.md.

## Mission

Read a chapter from the project's input folder (`input/<Subject>/`),
understand the content, and produce a Manim animation script that visualizes
the key ideas. Some sources come as a scaffolded pair: a `.tex` (the
authoritative document) plus a sibling pandoc `.md` (a high-level
characterization). When the pair exists, leverage both — the `.md` for intent
and structure, the `.tex` for the precise content.

## Workflow

### Step 1 — Discover the notes

List available chapters:

```bash
ls input/<Subject>/
```

If no chapter is specified by the user, pick the first one alphabetically.
Read the full file (and its companion `.md`, if present) before proceeding.

### Step 2 — Analyze the content

Before writing any code, produce a brief internal plan:

- What is the central concept of this chapter?
- What are the 2–4 most important ideas worth animating?
- What visual representations are natural? (e.g., diagrams, bar charts,
  function plots, trees, convergence plots)
- Are there key theorems or formulas that should appear as LaTeX?

### Step 3 — Write the Manim script

Create `scenes/<chapter_name>.py` with one or more `Scene` subclasses.

**Structure each scene as follows:**

```python
from manim import *

class ChapterOverview(Scene):
    """High-level title card and outline."""
    def construct(self):
        ...

class ConceptOne(Scene):
    """First key concept."""
    def construct(self):
        ...

# Add one Scene per major concept
```

**Guidelines:**

- Use `MathTex` for all formulas — never plain strings for math
- Use `Text` for titles, labels, and prose
- Animate incrementally — reveal formulas line by line with `Write` or
  `TransformMatchingTex`
- Use `Axes` for plots
- Use `VGroup` to organize related objects
- Add `self.wait(1)` between major steps so the viewer can absorb each idea
- Keep each Scene under ~60 seconds of content

### Step 4 — Render a test

Run a low-quality preview of the first scene:

```bash
uv run manim -pql scenes/<chapter_name>.py ChapterOverview
```

Fix any errors before rendering remaining scenes.

### Step 5 — Report

After rendering, print:
- Which scenes were created
- The output video path(s)
- Any concepts from the chapter that were skipped and why

---

## Conventions

- All generated scripts go in `scenes/`
- Do not modify files under `input/` (read-only; edit the vendored copies in
  `sources/` instead — see PIPELINE.md)
- Use `uv run manim` (not bare `manim`) to respect the project venv
- Low quality (`-ql`) for drafts, high quality (`-qh`) for finals

## LaTeX Tips

- Wrap all math in `r"..."` raw strings
- Use `\mid` for conditional bars, never bare `|` in `MathTex`
- **Notation is fixed per project in `course.yaml` (`notation.rules`)** — see
  NOTATION.md for how the system works. Manim cannot see the source notes'
  preamble macros, so use the expanded forms via the `_style.py` helpers
  (e.g. `pr()`, `expectation()`, `variance()`). Run
  `python tools/check_notation.py` to verify.
- Test LaTeX-heavy scenes first; a missing package will fail at render time

## Example Scene Skeleton

```python
from manim import *

class BayesTheorem(Scene):
    def construct(self):
        title = Text("Bayes' Theorem", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        formula = MathTex(
            r"\Pr(A \mid B)",
            r"=",
            r"\frac{\Pr(B \mid A)\, \Pr(A)}{\Pr(B)}"
        )
        self.play(Write(formula))
        self.wait(2)

        intuition = Text("Posterior = Likelihood × Prior / Evidence",
                         font_size=28)
        intuition.next_to(formula, DOWN, buff=0.8)
        self.play(FadeIn(intuition))
        self.wait(2)
```
