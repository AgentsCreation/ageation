# CLAUDE.md — Manim Video Pipeline Agent

## Start here (current state)

This project is a generic, file-based pipeline that turns a folder of LaTeX
notes into short, narrated, linked Manim videos. Before doing anything, read
**HISTORY.md** (goal, all design decisions + rationale, reproduce-from-scratch
roadmap) and **PIPELINE.md** (the layered spec). Also: **NOTATION.md** (how
per-project notation rules work) and **project.yaml** (the per-project config +
chapter spine — bootstrap one with `tools/init_project.py` if absent).

This repo is the **engine**; the content lives in external project
directories driven via `--project DIR`. Preferred posture: a base repo (an
article, a book, a software project) hosts the reserved subdirectory
`ageation/` containing project.yaml + sources/ + content/ + scenes/ +
media/, with `upstream_dir` pointing back into the host (no `input/`).
Standalone projects keep upstream copies under `input/` instead. See
"Consumer projects" in PIPELINE.md.

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
- Avoid `LaggedStartMap` with single-mobject animations (`Create`, `Write`)
  over composite mobjects (arrows with tips, VGroup-of-VGroups): its identity
  arg_creator `*`-unpacks each submobject, so extra parts land in positional
  slots like `lag_ratio` (TypeError at render). Use
  `LaggedStart(*[Create(m) for m in group], lag_ratio=...)` instead.
  (`FadeIn` tolerates it — varargs.)
- `Axes.plot` silently returns a curve with NO points when `x_range` is
  decreasing — any path-based use (e.g. `MoveAlongPath`) then crashes at
  render with "Cannot call Mobject.point_from_proportion". To traverse a
  curve right-to-left, plot the increasing range and call
  `.reverse_points()` on the result.

### Step 4 — Render a test

Run a low-quality preview of the first scene:

```bash
uv run manim -pql scenes/<chapter_name>.py ChapterOverview
```

Fix any errors before rendering remaining scenes.

### Step 5 — Render every beat AND assemble the chapter video

The standard final step of the workflow is **one assembled `.mp4` per
chapter** — that is what the human reviews and comments on. Per-beat clips
stay on disk for cheap iteration, but they are not the deliverable.

```bash
make video-draft     # 480p: render every beat + assemble into one .mp4
make video           # 1080p60 final
# or, equivalently from the shell:
./render_all.sh l    # draft (renders + assembles)
./render_all.sh      # 1080p60 final (renders + assembles)
```

The deliverable lands at
`<project>/media/videos/<module>/<quality>/_assembled/<slug>.mp4`.

### Step 6 — Report

After assembling, print:
- Which scenes were created
- The single assembled `.mp4` path (the reviewable deliverable)
- Any concepts from the chapter that were skipped and why

---

## Conventions

- All generated scripts go in `scenes/`
- Do not modify the upstream files (`input/` or the host repo's own files in
  the embedded posture) — they are read-only; edit the vendored copies in
  `sources/` instead (see PIPELINE.md)
- Use `uv run manim` (not bare `manim`) to respect the project venv
- Low quality (`-ql`) for drafts, high quality (`-qh`) for finals
- The workflow's terminal artifact is **one assembled `.mp4` per chapter**,
  not the per-beat clips. Use `make video` / `make video-draft` (or
  `./render_all.sh`) — they chain render + assemble. The per-beat scene
  files remain on disk for iteration, but the assembled video at
  `media/videos/<module>/<quality>/_assembled/<slug>.mp4` is what you ship
  and what gets reviewed.

## LaTeX Tips

- Wrap all math in `r"..."` raw strings
- Use `\mid` for conditional bars, never bare `|` in `MathTex`
- **Notation is fixed per project in `project.yaml` (`notation.rules`)** — see
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
