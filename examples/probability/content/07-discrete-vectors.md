---
slug: 07-discrete-vectors
title: Discrete Vectors
stage: concept            # tex -> [concept] -> script -> scene -> render
status: reviewed             # draft | reviewed | approved  (human gate)
source: sources/07-discrete-vectors.tex
upstream: input/Probability/7Discrete_Vectors.tex
source_sha256: 9a24660296006b721b343e5cbca4814c419e0395b3679cd32da6c97ad3add19d
provenance_stamped: 2026-07-06
framework_commit: 36004fc-dirty
prereqs:
  - 06-discrete-expectations
audience: undergraduate engineering, first probability course
concepts:
  - id: joint-pmf
    name: Joint PMF and marginals
    importance: core
    one_liner: The joint PMF gives Pr(X = x, Y = y); summing out one variable recovers a marginal.
  - id: functions-joint-expect
    name: Functions and joint expectation
    importance: core
    one_liner: V = g(X, Y) is a random variable; its expectation sums g against the joint PMF.
  - id: conditional-pmf
    name: Conditional PMF
    importance: core
    one_liner: p_{Y|X}(y|x) is the joint PMF divided by the marginal of X.
  - id: conditional-expectation
    name: Conditional expectation and the tower rule
    importance: highlight        # the visual climax
    one_liner: E[Y|X] is itself a random variable, and its expectation equals E[Y].
  - id: independence-convolution
    name: Independence and convolution
    importance: core
    one_liner: Independent variables factor the joint PMF; their sum convolves the marginals.
  - id: generating-functions
    name: Generating functions and sums
    importance: optional         # candidate to cut for runtime
    one_liner: The generating function of a sum of independent RVs is the product of theirs.
estimated_runtime_sec: 360         # rough target before scripting
---

# Discrete Vectors — Concept Map

## What
A discrete random vector pairs two random variables, X and Y, on the same
experiment. Their joint behavior lives in a joint PMF; summing one variable out
gives a marginal; dividing the joint by a marginal gives a conditional. From
these come conditional expectation, independence, and the convolution rule for
sums.

## Why (motivation for the viewer)
Single random variables rarely tell the whole story — quantities interact. The
number of corrupted bits and where they fall, the cherry sodas among total sales,
the sum of two dice: each requires reasoning about two variables at once. The
joint PMF is the complete description, and conditioning is how we extract one
variable's behavior given knowledge of the other.

## How (the spine of the chapter)
1. Define the joint PMF Pr(X = x, Y = y) and recover marginals by summing out a
   variable; show that marginals do not determine the joint.
2. Treat V = g(X, Y) as a new random variable and compute its expectation by
   summing g against the joint PMF.
3. Define the conditional PMF as joint over marginal, and read it as the
   distribution of Y once X is pinned to a value.
4. Build the conditional expectation E[Y | X], note it is itself a random
   variable, and prove the tower rule E[E[Y | X]] = E[Y].
5. Define independence as a factoring joint PMF, then derive the convolution
   formula for the PMF of a sum.

## What else (connections, to seed callbacks in narration)
- Conditioning here directly extends the event-conditioning of Chapter 4 to
  random variables.
- For independent variables, E[XY] = E[X]E[Y] and Var[X + Y] = Var[X] + Var[Y];
  in general a cross-term appears.
- The splitting property: thinning a Poisson stream by an independent coin gives
  another Poisson — a clean payoff of conditional PMFs.
- Generating functions turn a convolution into a product, making sums of
  independent Poissons or Bernoullis effortless.

## Conceptual progression (drives the storyboard)
joint PMF as a grid  ->  marginals as row and column sums  ->  a conditional as a
single highlighted slice, renormalized  ->  E[Y|X] as a curve over x, averaging
back to E[Y]  ->  independence factoring, and a sum's PMF as a convolution.

## Visual opportunities
- A joint PMF rendered as a grid or 3D stem plot, with row and column sums
  sliding out to form the marginals.
- A single row of the grid lifting out and renormalizing to show a conditional
  PMF.
- The sum of two dice: the joint grid's anti-diagonals collapsing into the
  triangular PMF of U = X + Y.
- Two independent PMFs sliding past each other as a convolution builds the PMF of
  their sum, term by term.

## Deliberately out of scope
- Ordinary generating functions beyond a one-line mention — the full z-transform
  treatment and the negative-binomial derivation are skipped.
- Numerous random variables and n-fold convolutions (sketched, not animated).
- Continuous joint distributions (Chapter 8, Continuous Random Variables).
