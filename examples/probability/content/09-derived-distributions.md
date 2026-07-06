---
slug: 09-derived-distributions
title: Derived Distributions
stage: concept            # tex -> [concept] -> script -> scene -> render
status: reviewed             # draft | reviewed | approved  (human gate)
source: sources/09-derived-distributions.tex
upstream: input/Probability/9Derived_Distributions.tex
source_sha256: d03c9a825989897353ce08652f4168302c607427696d5fc89ae1ef8ffc57cc3e
provenance_stamped: 2026-07-06
framework_commit: 36004fc-dirty
prereqs:
  - 08-continuous-random-variables
audience: undergraduate engineering, first probability course
concepts:
  - id: function-of-rv
    name: A function of a random variable is a random variable
    importance: core
    one_liner: Y = g(X) is itself random; its law comes from the PDF of X and the function g.
  - id: cdf-method
    name: The CDF method
    importance: core
    one_liner: Find F_Y by integrating f_X over the preimage {x : g(x) <= y}, then differentiate.
  - id: monotone-change
    name: Monotone change of variables
    importance: core
    one_liner: When g is strictly monotone and differentiable, f_Y(y) = f_X(x) / |dg/dx|.
  - id: piecewise-sum
    name: Piecewise-monotone functions sum contributions
    importance: highlight
    one_liner: When several x map to one y, add a 1/|dg/dx| term for each branch.
  - id: inverse-transform
    name: Generating random variables
    importance: core
    one_liner: Applying the inverse CDF to a uniform draw produces any desired distribution.
estimated_runtime_sec: 900        # rough target before scripting (~3 section beats)
---

# Derived Distributions — Concept Map

## What
Apply a function `g` to a continuous random variable `X` and you get a new random
variable `Y = g(X)`. This chapter answers one question in several settings: given
the distribution of `X` and the function `g`, what is the distribution of `Y`?
The answers run from a brute-force CDF integral, to a clean change-of-variables
formula for monotone functions, to a sum over branches for piecewise-monotone
functions — and finally to a recipe for generating any distribution from a
uniform draw.

## Why (motivation for the viewer)
We rarely observe the quantity we actually care about directly. We square a
voltage to get energy, take a magnitude to get amplitude, pass a signal through a
nonlinearity. Each transformation reshapes the distribution, and we need to track
exactly how. The same machinery, run in reverse, lets a computer manufacture
samples from any distribution using nothing but a uniform random number
generator — the foundation of simulation.

## How (the spine of the chapter)
1. State the general principle: `Pr(Y in S) = Pr(X in g^{-1}(S))`, so the law of
   `Y` is governed by `g` and the PDF of `X`.
2. The CDF method: write `F_Y(y) = Pr(g(X) <= y)` as an integral of `f_X` over
   the preimage, then differentiate to get the density.
3. Monotone functions: the preimage is an interval, so `F_Y` is `F_X`
   (or `1 - F_X`) composed with the inverse.
4. Differentiable, strictly monotone `g`: differentiate to get the headline
   formula `f_Y(y) = f_X(x) / |dg/dx|`, with `x = g^{-1}(y)`.
5. Piecewise-monotone `g`: sum a `1/|dg/dx|` contribution over every `x` with
   `g(x) = y`.
6. Generating random variables: `F_X(X)` is uniform, so `F_X^{-1}` applied to a
   uniform variable produces a sample with CDF `F_X` (and a case-function does
   the same for discrete targets).

## What else (connections, to seed callbacks in narration)
- The squared Rayleigh is exponential — derived two ways (CDF method and the
  change-of-variables formula) so the two routes can be compared.
- An affine function of a Gaussian is still Gaussian; an affine function of a
  uniform is still uniform — transformations sometimes preserve the family.
- `Y = cos(X)` with `X` uniform on a circle is the canonical piecewise-monotone
  example: two preimages per `y`, giving the arcsine-shaped density.
- The Jacobian factor `|dg/dx|` has a geometric meaning: a flat slope stretches a
  y-interval into a wide x-interval, piling up density.

## Conceptual progression (drives the storyboard)
mapping picture X -> g -> Y  ->  CDF method (preimage integral)  ->  monotone
change of variables with the |dg/dx| stretch  ->  piecewise sum over branches  ->
inverse-CDF sampling: uniform dots pushed through F_X^{-1} into a target shape.

## Visual opportunities
- The three-panel mapping diagram: Omega, then X to the real line, then g to a
  second real line.
- A y-interval of fixed width pulled back through `g` to show how the slope sets
  the width of the matching x-interval (the Jacobian intuition).
- `cos` of a uniform angle: a point sweeping the unit circle while its projection
  traces a density that piles up near plus and minus one.
- Inverse-transform sampling: uniform points on the y-axis fired horizontally
  into the CDF curve and dropping to form the target histogram.

## Deliberately out of scope
- Functions of *several* random variables and joint transformations (later).
- Moment generating functions, which give a different transform-based handle on
  derived distributions (Chapter 10).
- Measure-theoretic care about "almost everywhere"; shown as caveats, not proved.
