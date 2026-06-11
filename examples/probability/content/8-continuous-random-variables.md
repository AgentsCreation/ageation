---
slug: 8-continuous-random-variables
title: Continuous Random Variables
stage: concept            # tex -> [concept] -> script -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
source: sources/8-continuous-random-variables.tex
upstream: input/Probability/8Continuous_Random_Variables.tex
source_sha256: fd170dc926eebca1e4f534a38a3b560ce63885fdc8092ecfa2ec21cd4d9ad061
provenance_stamped: 2026-06-11
prereqs:
  - 7-discrete-vectors
audience: undergraduate engineering, first probability course
concepts:
  - id: cdf
    name: Cumulative distribution function
    importance: core
    one_liner: The CDF F_X(x) = Pr(X <= x) describes any random variable, discrete or continuous.
  - id: pdf
    name: Probability density function
    importance: core
    one_liner: The PDF is the derivative of the CDF; it integrates to one and gives probabilities as areas.
  - id: point-mass-zero
    name: Single points carry no probability
    importance: highlight
    one_liner: For a continuous RV, Pr(X = x) = 0; only intervals carry probability.
  - id: continuous-expectation
    name: Expectation as a weighted integral
    importance: core
    one_liner: The discrete sum becomes an integral; E[g(X)] = integral of g(u) f_X(u) du.
  - id: named-continuous
    name: Named continuous distributions
    importance: core
    one_liner: Uniform, Gaussian, and exponential are the workhorses; gamma, Rayleigh, Laplace, Cauchy round out the family.
  - id: geometric-to-exponential
    name: Geometric-to-exponential limit
    importance: highlight
    one_liner: Scaled geometric random variables converge to the exponential, which inherits the memoryless property.
  - id: tail-distributions
    name: Gamma, Rayleigh, Laplace, Cauchy
    importance: optional
    one_liner: A gallery of derived shapes, including a heavy tail with no defined mean.
estimated_runtime_sec: 1500       # rough target before scripting (~5 section beats)
---

# Continuous Random Variables — Concept Map

## What
A continuous random variable ranges over a continuum rather than a countable
list of values. It cannot be described by a probability mass function, so we
introduce two new tools: the cumulative distribution function (CDF), which works
for any random variable, and the probability density function (PDF), the
derivative of the CDF, which plays the role the PMF played in the discrete world.

## Why (motivation for the viewer)
Most engineering quantities — a waiting time, a noise voltage, a signal
amplitude — vary smoothly and take uncountably many values. The discrete
machinery breaks here because the third axiom only covers countable unions, and
a single real value ends up carrying zero probability. The CDF/PDF pair restores
everything we love about the PMF — normalization, expectation, named families —
in a form that handles the continuum.

## How (the spine of the chapter)
1. Define the CDF `F_X(x) = Pr(X <= x)` and read off its three properties:
   it rises from 0 to 1 and never decreases, and interval probabilities are
   differences of CDF values.
2. Call `X` continuous when its CDF is continuous and differentiable; define the
   PDF as `f_X = dF_X/dx`, integrating back to the CDF.
3. Note the headline consequence: `Pr(X = x) = 0`, so endpoints never matter.
4. Re-derive expectation, mean, and variance as integrals; add the tail formula
   `E[X] = integral of Pr(X > x) dx` for nonnegative `X`.
5. Tour the named distributions — uniform, Gaussian (with Phi, erf, Q), and
   exponential — then show scaled geometrics converging to the exponential and
   inheriting memorylessness.
6. (Optional) Survey additional shapes: gamma and its special cases, Rayleigh,
   Laplace, and the heavy-tailed Cauchy.

## What else (connections, to seed callbacks in narration)
- The CDF is the bridge object: a staircase for discrete RVs, a smooth curve for
  continuous ones, and a mixture for mixed RVs.
- The exponential is the continuous cousin of the geometric and is the *only*
  continuous distribution with the memoryless property.
- The Gaussian's normalization uses a polar-coordinate trick; the same trick
  evaluates Gamma(1/2) = sqrt(pi).
- Gamma unifies exponential, chi-square, and Erlang; Rayleigh is the magnitude of
  two independent Gaussians, foreshadowing derived distributions (Chapter 9).

## Conceptual progression (drives the storyboard)
discrete staircase CDF  ->  smooth continuous CDF  ->  PDF as its slope and as
area  ->  expectation as a weighted integral  ->  gallery of named PDFs  ->
binomial-style limit: scaled geometric bars collapsing onto a smooth exponential.

## Visual opportunities
- A staircase CDF morphing into a smooth S-curve to contrast discrete vs.
  continuous.
- A PDF curve with a shaded interval whose area equals Pr(x1 < X < x2), then
  the shaded strip shrinking to a line to show Pr(X = x) = 0.
- Side-by-side parameter sweeps for uniform, Gaussian, and exponential PDFs.
- Scaled geometric bars for n = 5, 20, 50 settling onto a fixed exponential
  reference curve.

## Deliberately out of scope
- Derived distributions Y = g(X) — that is the whole of Chapter 9.
- Moment generating functions and probability bounds (Chapter 10).
- Full proofs beyond the Gaussian normalization sketch; integrals shown as
  results, not worked line by line.
- The heavy gamma/Rayleigh/Laplace/Cauchy gallery is optional and first to be
  cut for runtime.
