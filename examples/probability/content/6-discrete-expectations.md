---
slug: 6-discrete-expectations
title: Discrete Expectations
stage: concept            # tex -> [concept] -> script -> scene -> render
status: reviewed             # draft | reviewed | approved  (human gate)
source: sources/6-discrete-expectations.tex
upstream: input/Probability/6Discrete_Expectations.tex
source_sha256: ce0fa8c8d3731a0b73741f270ec054c5262601f068bb5d1050485218eb3c617f
provenance_stamped: 2026-07-04
framework_commit: 9e207a6-dirty
prereqs:
  - 5-discrete-random-variables
audience: undergraduate engineering, first probability course
concepts:
  - id: expected-value
    name: Expected value
    importance: core
    one_liner: The mean is each value weighted by its probability, summed.
  - id: law-unconscious
    name: Expectation of a function
    importance: core
    one_liner: E[g(X)] sums g(x) against the PMF, with no need to find the distribution of g(X).
  - id: center-of-mass
    name: Mean as center of mass
    importance: highlight        # the visual climax
    one_liner: Place mass p_X(x) at each x; the mean is the balance point.
  - id: variance
    name: Variance and standard deviation
    importance: core
    one_liner: Variance is the expected squared distance from the mean — its spread.
  - id: affine-linearity
    name: Affine rules and linearity
    importance: core
    one_liner: E[aX + b] = aE[X] + b and Var[aX + b] = a^2 Var[X].
  - id: moments
    name: Moments
    importance: optional         # candidate to cut for runtime
    one_liner: The nth moment is E[X^n]; variance is the second moment minus the mean squared.
estimated_runtime_sec: 360         # rough target before scripting
---

# Discrete Expectations — Concept Map

## What
Expectation collapses an entire probability mass function into a few descriptive
numbers. The mean is the probability-weighted average of a random variable; the
variance measures how far it typically strays from that mean; and moments
generalize both. All of these are expectations — sums of some function against
the PMF.

## Why (motivation for the viewer)
A PMF tells you everything, which is often too much. To compare, summarize, or
decide, you want a single representative number and a single measure of spread.
The mean answers "what should I expect on average?" and the variance answers
"how reliable is that average?" These two numbers drive nearly every applied
calculation downstream.

## How (the spine of the chapter)
1. Define the mean as the sum of each value times its probability; compute it for
   a die and for the geometric.
2. Generalize to E[g(X)], summing g(x) against the PMF directly — no derived
   distribution required.
3. Reveal the physical picture: the mean is the center of mass of point masses
   placed at each value.
4. Define the variance as the expected squared deviation from the mean, with the
   standard deviation as its square root.
5. Establish the affine rules and linearity, and the moment formula
   Var[X] = E[X^2] − (E[X])^2.

## What else (connections, to seed callbacks in narration)
- The mean of a Bernoulli is p, of a binomial is np, of a Poisson is lambda, and
  of a geometric is one over p — each tied to its counting story from Chapter 5.
- The expectation of an indicator function of a set equals the probability of
  that set — a bridge back to events.
- For a Poisson, the mean and variance are both lambda; for a Bernoulli the
  variance is p(1−p).
- Linearity (E[ag(X) + h(X)] = aE[g(X)] + E[h(X)]) is the workhorse identity that
  makes expectations easy to manipulate.

## Conceptual progression (drives the storyboard)
PMF bars  ->  weighted-average formula  ->  bars become point masses on a beam
that balances at the mean  ->  variance as the spread around that balance point.

## Visual opportunities
- A die PMF with each bar labeled by k/6, accumulating to the mean of 3.5.
- Point masses sized by probability sitting on a number line, with a fulcrum
  sliding to the balance point — the center-of-mass interpretation.
- A PMF with the mean marked, and shaded squared-deviation rectangles whose
  weighted sum is the variance.
- An affine map aX + b shifting and stretching the masses, the mean tracking by
  aE[X] + b while the spread scales by a.

## Deliberately out of scope
- Skewness and kurtosis — named as higher central moments, not derived.
- Ordinary generating functions (the commented-out section in the source).
- Covariance and joint expectations (Chapter 7, Discrete Vectors).
