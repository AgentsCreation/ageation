---
slug: 11-random-vectors
title: Random Vectors
stage: concept            # tex -> [concept] -> script -> scene -> render
status: reviewed             # draft | reviewed | approved  (human gate)
source: sources/11-random-vectors.tex
upstream: input/Probability/11Random_Vectors.tex
source_sha256: 2d279768cae44138c53a7d9afed4beeae0d15110d271561f26efcbb8295e03fd
provenance_stamped: 2026-06-11
framework_commit: af5d6d4-dirty
prereqs:
  - 10-expectations-and-bounds
audience: undergraduate engineering, first probability course
concepts:
  - id: joint-cdf-pdf
    name: Joint CDF and joint PDF
    importance: core
    one_liner: A pair of continuous RVs is described jointly by a surface over the plane that integrates to one.
  - id: marginals
    name: Marginals from the joint
    importance: core
    one_liner: Sending one variable to infinity (integrating it out) recovers the distribution of the other.
  - id: conditioning
    name: Conditioning on an event or a value
    importance: core
    one_liner: Conditioning reslices and renormalizes the joint density, even on the zero-probability event Y = y.
  - id: independence
    name: Independence as factorization
    importance: core
    one_liner: X and Y are independent exactly when the joint density factors into the two marginals.
  - id: sum-convolution
    name: Sum of independents is a convolution
    importance: highlight        # the visual climax
    one_liner: The density of X + Y is the convolution of the two densities — a sliding-overlap integral.
  - id: gaussian-vectors
    name: Gaussian vectors and affine maps
    importance: optional         # candidate to cut for runtime
    one_liner: An affine transform of a Gaussian vector is again Gaussian, with mean and covariance transformed predictably.
estimated_runtime_sec: 660         # rough target before scripting
---

# Random Vectors — Concept Map

## What
A random vector packages two or more random variables defined on the same
experiment into a single object. For a continuous pair `(X, Y)`, everything is
encoded in the joint CDF `F_{X,Y}(x,y) = Pr(X <= x, Y <= y)` and, when it is
smooth enough, the joint PDF `f_{X,Y}(x,y)` — a nonnegative surface over the
plane that integrates to one. From this single surface we can extract marginals,
condition on events or values, test independence, and find the distribution of
functions of the pair.

## Why (motivation for the viewer)
One variable at a time only takes you so far. Real systems — a signal plus
noise, a position with two coordinates, a measurement and its error — couple
several quantities, and the interesting questions (how does Y inform X? what is
the distribution of their sum?) are precisely the ones a single PDF cannot
answer. This chapter is the continuous, multivariable engine room that powers
estimation, communication, and the limit theorems coming next.

## How (the spine of the chapter)
1. Define the joint CDF, then the joint PDF as its mixed second derivative;
   probability of a region is the volume under the surface over that region.
2. Recover marginals by sending one variable to infinity (integrating it out).
3. Condition: on an event by renormalizing, and on a value `Y = y` by dividing
   the joint slice by the marginal `f_Y(y)` — handling the zero-probability
   subtlety with care.
4. Define independence as factorization of the joint into marginals.
5. Show the distribution of `W = X + Y` for independents is the convolution of
   the two densities — the chapter's unifying tool.

## What else (connections, to seed callbacks in narration)
- Marginalization is the continuous analogue of summing a joint PMF over rows.
- Conditional expectation `E[Y | X = x]` is itself a random variable — a hook
  back to expectations and forward to estimation (the MMSE estimator is just a
  conditional mean).
- Convolution + the moment generating function product `M_W = M_X M_Y` are the
  two ways to add independents; the MGF view makes "Gaussian plus Gaussian is
  Gaussian" almost immediate.
- Affine maps of Gaussian vectors stay Gaussian — the structural fact behind
  much of modern signal processing.

## Conceptual progression (drives the storyboard)
joint surface over the plane  ->  shadow it onto an axis to get a marginal  ->
slice it and renormalize to get a conditional  ->  factor it to test
independence  ->  slide one density past another to add two variables.

## Visual opportunities
- A 3D joint PDF surface (or filled contour) over the xy-plane; shade a region
  and call its volume a probability.
- "Casting a shadow": collapse the surface onto the x-axis to build the marginal
  `f_X`, then onto the y-axis for `f_Y`.
- A vertical slice at `Y = y`, lifted out and rescaled by `1/f_Y(y)` to show
  the conditional density.
- A factorization check: side-by-side `f_{X,Y}` vs `f_X · f_Y`, matching for the
  unit square, mismatching for `(X, X+Y)`.
- The convolution as a sliding overlap: flip one density, slide it across the
  other, and trace the overlap area to draw the triangular density of a sum of
  two uniforms.

## Deliberately out of scope
- The full Jacobian / change-of-variables derivation for general derived
  distributions — stated as a result, motivated by the Gaussian-vector case.
- Contour integration for sums of Cauchy variables (that surfaces in the next
  chapter, and only as a cautionary tale).
- Higher-dimensional covariance algebra beyond the 2x2 illustration.
