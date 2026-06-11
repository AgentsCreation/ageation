# NOTATION.md — Notation convention for this project

A single source of truth for mathematical notation, so the book, the scripts,
and the Manim scenes all agree. In academic composition the most common drift is
notation (one author writes $\mathbb{E}$, another $\mathrm{E}$); this file fixes
the choices for *Undergraduate Probability I* and is enforced by
`tools/check_notation.py`.

The conventions below are taken from the source notes' own preamble macros
(e.g. `\newcommand{\Expect}{\mathrm{E}}`), so the generated layers match the
book exactly.

## Important: Manim does not know the book's macros

The LaTeX notes define shortcuts like `\Expect`, `\Var`, `\Prob`, `\RealNumbers`.
Manim's `MathTex` has **no** access to that preamble, so scenes must use the
**expanded** form. The `_style.py` helpers emit the expanded form for you —
prefer them: `pr("X = k")`, `expectation("X")`, `variance("X")`.

## The convention

| Quantity | Source macro | Use in `MathTex` (expanded) | Spoken in narration | Do NOT use |
|---|---|---|---|---|
| Probability | `\Prob` → `\Pr` | `\Pr(A \mid B)` | "the probability of A given B" | `\mathbb{P}`, bare `P` |
| Expectation | `\Expect` → `\mathrm{E}` | `\mathrm{E}[X]` | "the expected value of X" / "E of X" | `\mathbb{E}`, italic `E`, `\operatorname{E}` |
| Variance | `\Var` → `\mathrm{Var}` | `\mathrm{Var}(X)` | "the variance of X" | `\mathbb{V}`, italic `Var` |
| Real numbers | `\RealNumbers` → `\mathbb{R}` | `\mathbb{R}` | "the real numbers" | `\mathbf{R}`, `R` |
| Integers | `\Integers` → `\mathbb{Z}` | `\mathbb{Z}` | "the integers" | `\mathbf{Z}` |
| Indicator | `\IndicatorFcn` → `\mathbf{1}` | `\mathbf{1}\{A\}` | "the indicator of A" | `\mathbb{1}`, `I` |
| Conditional bar | — | `\mid` (not `\|` or `|`) | "given" | `|` in `MathTex` |
| PMF / PDF / CDF | — | `p_X(x)` / `f_X(x)` / `F_X(x)` | "the PMF / density / CDF of X" | mixing cases |

House choices not pinned by a source macro (kept in the `\mathrm` family for
consistency): covariance `\mathrm{Cov}(X,Y)`, correlation `\rho`, standard
deviation `\sigma`.

## How it's enforced

`tools/check_notation.py` scans `content/*.md`, `scenes/*.py`, and the vendored
`sources/*.tex` for the "Do NOT use" forms and fails (nonzero exit) if any
appear. Run it before a render, or wire it into the build gate. To change a
convention, edit the rule list in that script **and** this table together.

When an upstream source violates the convention, fix it on the editable working
copy, never the read-only parent: `tools/normalize_notation.py --write` rewrites
the disallowed forms in `sources/*.tex` (then re-run `tools/stamp_provenance.py`).
This is the reason for vendoring local copies — see PIPELINE.md.

## Why this exists

The very first notation slip in this project was a stale tip in `CLAUDE.md`
suggesting `\mathbb{P}`, which conflicts with the notes' `\Pr`. Centralizing the
convention here — and checking it mechanically — prevents that class of drift
from recurring as more chapters and (eventually) more subjects are added.
