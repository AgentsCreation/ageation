---
slug: 10-expectations-and-bounds
title: Expectations and Bounds
stage: concept            # tex -> [concept] -> script -> scene -> render
status: reviewed             # draft | reviewed | approved  (human gate)
source: sources/10-expectations-and-bounds.tex
upstream: input/Probability/10Expectations_and_Bounds.tex
source_sha256: 527754d62539c3518f08f6a360f9f7e65951a202ce2690fef2c0930a17c0a2a0
provenance_stamped: 2026-06-11
prereqs:
  - 9-derived-distributions
audience: undergraduate engineering, first probability course
concepts:
  - id: mgf
    name: Moment generating function
    importance: core
    one_liner: M_X(s) = E[e^{sX}] packs every moment into one function; differentiate at zero to extract them.
  - id: mgf-affine
    name: MGF of an affine transform
    importance: optional
    one_liner: If Y = aX + b then M_Y(s) = e^{sb} M_X(as), reading off mean and variance painlessly.
  - id: dominating-function
    name: Dominating functions
    importance: core
    one_liner: If g <= h everywhere then E[g(X)] <= E[h(X)] — the engine behind every bound here.
  - id: markov
    name: Markov inequality
    importance: core
    one_liner: For nonnegative X, Pr(X >= a) <= E[X]/a, by dominating an indicator with a line.
  - id: chebyshev
    name: Chebyshev inequality
    importance: highlight
    one_liner: A general bound i_S Pr(X in S) <= E[h(X)] that yields the classic variance bound and Cantelli.
  - id: chernoff
    name: Chernoff bound
    importance: core
    one_liner: Dominate the indicator with an exponential and optimize over s to get an exponentially tight tail bound.
  - id: jensen
    name: Jensen's inequality
    importance: core
    one_liner: For convex g, E[g(X)] >= g(E[X]) — convexity bends the average upward.
estimated_runtime_sec: 600        # rough target before scripting (~2 section beats)
---

# Expectations and Bounds — Concept Map

## What
Expectation summarizes a distribution in a single number, and this chapter pushes
that idea two ways. First, the moment generating function packs *all* the moments
of a random variable into one function. Second, expectations let us bound
probabilities we cannot compute exactly: Markov, Chebyshev, Chernoff, and Jensen
are all expectation inequalities, and the first three flow from one simple idea —
dominating functions.

## Why (motivation for the viewer)
Often the exact probability is hopeless — the integral has no closed form, or the
distribution is only partially known. A good bound is then worth more than an
exact answer we can't reach. These inequalities need only a mean, a variance, or
a moment generating function, yet they pin down how much probability can hide in
a tail. They are the backbone of concentration results and the law of large
numbers downstream.

## How (the spine of the chapter)
1. Define `M_X(s) = E[e^{sX}]`; differentiate `n` times at `s = 0` to pull out
   the `n`-th moment. Work the exponential and Gaussian examples.
2. Note the affine rule `M_Y(s) = e^{sb} M_X(as)` for `Y = aX + b`.
3. State the dominating-function principle: `g <= h` implies
   `E[g(X)] <= E[h(X)]`. Every bound below is an instance.
4. Markov: dominate the indicator of `[a, infinity)` by the line `x/a` to get
   `Pr(X >= a) <= E[X]/a`.
5. Chebyshev: generalize to any nonnegative `h`, giving
   `i_S Pr(X in S) <= E[h(X)]`; specialize to the variance bound and Cantelli.
6. Chernoff: dominate the indicator by `e^{s(x-a)}` and optimize over `s > 0` for
   the sharpest exponential tail bound.
7. Jensen: for convex `g`, the tangent line at the mean lies below `g`, so
   `E[g(X)] >= g(E[X])`.

## What else (connections, to seed callbacks in narration)
- The MGF is a Laplace transform of the density; for integer-valued variables it
  is the ordinary generating function evaluated at `e^s`.
- Markov is the special case of Chebyshev with `h(x) = x`; Chebyshev with
  `h(x) = x^2` gives the familiar variance tail bound.
- The Chernoff bound is Chebyshev with an exponential dominating function — and
  it is exactly where the moment generating function pays off.
- Jensen explains why the mean of a square exceeds the square of the mean, i.e.
  why variance is nonnegative.

## Conceptual progression (drives the storyboard)
MGF as a moment-packing machine  ->  dominating functions (one curve sitting
under another)  ->  Markov's line over an indicator step  ->  Chebyshev's general
template  ->  a family of exponentials over the step, optimized into Chernoff  ->
Jensen's chord-above-curve picture.

## Visual opportunities
- An MGF "machine": differentiate once for the mean, twice for the second
  moment, with the moments dropping out of a turning crank at `s = 0`.
- A step indicator with a straight line `x/a` laid over it — the Markov picture.
- A whole pencil of exponentials `e^{s(x-a)}` sweeping over the same step, the
  best one snapping to the tightest bound — the Chernoff optimization.
- A convex curve with its chord above and its tangent at the mean below,
  illustrating Jensen at a glance.

## Deliberately out of scope
- The law of large numbers and central limit theorem, which these bounds set up
  but which live in a later chapter.
- Convergence-of-MGF uniqueness theorems; the MGF is used, not characterized in
  full.
- Full optimization details of Cantelli and Chernoff beyond stating the optimal
  parameter.
