---
slug: 12-empirical-sums
title: Empirical Sums
stage: concept            # tex -> [concept] -> script -> scene -> render
status: reviewed             # draft | reviewed | approved  (human gate)
source: sources/12-empirical-sums.tex
upstream: input/Probability/12Empirical_Sums.tex
source_sha256: 18eb96874b4677789222bc1040bf3f961a906eecfc9888d360d88ebc79b29260
provenance_stamped: 2026-06-11
prereqs:
  - 11-random-vectors
audience: undergraduate engineering, first probability course
concepts:
  - id: types-of-convergence
    name: Types of convergence
    importance: core
    one_liner: Sequences of random variables can converge in probability, in mean square, or in distribution.
  - id: empirical-average
    name: The empirical average
    importance: core
    one_liner: Averaging n i.i.d. draws shrinks the variance like one over n, concentrating the mean.
  - id: law-of-large-numbers
    name: Law of large numbers
    importance: core
    one_liner: The empirical average converges in probability to the true mean.
  - id: central-limit-theorem
    name: Central limit theorem
    importance: highlight        # the visual climax
    one_liner: Standardized sums of i.i.d. variables converge in distribution to the standard normal, whatever the original shape.
  - id: heavy-tails
    name: When the law fails (heavy tails)
    importance: optional         # candidate to cut for runtime
    one_liner: The Cauchy average stays Cauchy — no finite variance, no convergence.
estimated_runtime_sec: 660         # rough target before scripting
---

# Empirical Sums — Concept Map

## What
This chapter studies what happens to sequences of random variables — and in
particular to sums and averages of many independent copies — as their number
grows without bound. Three notions of convergence (in probability, in mean
square, in distribution) give the vocabulary; two headline theorems give the
payoff. The law of large numbers says the empirical average locks onto the true
mean; the central limit theorem says the standardized sum becomes a standard
Gaussian no matter where you started.

## Why (motivation for the viewer)
These are the results that make probability *useful* at scale. Concentration is
why a casino, an insurer, or a communication system can quote a tiny failure
probability and trust it: average enough independent pieces and the randomness
washes out. The CLT is why the bell curve is everywhere and why "plus or minus"
error bars work. As the closing chapter of the course, this is where the whole
toolkit — random variables, expectation, variance, Chebyshev's bound, sums and
convolutions — converges into two unforgettable theorems.

## How (the spine of the chapter)
1. Set up a sequence `X_1, X_2, ...` on one probability space and distinguish
   the three convergence types; note mean-square implies in-probability.
2. Form the empirical average `S_n / n`; compute its mean (stays at `E[X]`) and
   variance (`Var[X] / n`, vanishing).
3. State and prove the law of large numbers via Chebyshev's inequality.
4. State the central limit theorem: standardize the sum and watch its CDF
   approach the standard normal.
5. (Optional) Show the Cauchy counterexample, where infinite variance breaks
   the law.

## What else (connections, to seed callbacks in narration)
- The variance-of-the-average calculation reuses independence and the
  variance-adds rule from random vectors.
- The LLN proof is just Chebyshev's bound (from Expectations and Bounds) applied
  to the empirical average — the same tail bound, one chapter later.
- The CLT explains the Gaussian's privileged status seen throughout the course;
  the warm-up Gaussian example shows the average concentrating while the
  standardized sum holds its shape exactly.
- Heavy tails are the fine print: the LLN needs a finite second moment.

## Conceptual progression (drives the storyboard)
a sequence of distributions in motion  ->  the empirical-average histogram
narrowing onto the mean (LLN)  ->  the standardized-sum histogram, whatever its
source shape, snapping onto the bell curve (CLT)  ->  the Cauchy average that
stubbornly refuses to settle.

## Visual opportunities
- A running die-average meter: as rolls accumulate, the fraction of sixes
  wobbles toward one sixth.
- An LLN panel: redraw the histogram of `S_n / n` for growing n, a faint
  vertical line at the true mean, the spread visibly collapsing.
- A CLT panel: start from a deliberately non-Gaussian source (skewed or
  uniform), standardize the sum, and overlay a fixed standard-normal curve that
  the histogram converges onto as n grows.
- A side-by-side: a well-behaved average concentrating next to a Cauchy average
  that never does — the cautionary climax.

## Deliberately out of scope
- The full MGF / L'Hopital proof of the CLT — shown as a result with intuition,
  not derived line by line.
- Contour integration for the Cauchy convolution — quoted, not carried out.
- Stronger modes (almost-sure convergence, the strong law) beyond the three
  types named here.
