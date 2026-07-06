---
slug: 05-discrete-random-variables
title: Discrete Random Variables
stage: concept            # tex -> [concept] -> script -> scene -> render
status: approved             # draft | reviewed | approved  (human gate)
source: sources/05-discrete-random-variables.tex
upstream: input/Probability/5Discrete_Random_Variables.tex
source_sha256: 7e9e7474fe3ad6b63e192bdebb7c3aac0776d98f3a7d2b06b7abe215adbe9145
provenance_stamped: 2026-07-06
framework_commit: e248757-dirty
prereqs:
  - 03-basic-concepts
  - 04-conditional-probability
audience: undergraduate engineering, first probability course
concepts:
  - id: rv-as-function
    name: Random variable as a function
    importance: core
    one_liner: A random variable assigns a real number to every outcome.
  - id: pmf
    name: Probability mass function
    importance: core
    one_liner: The PMF gives the probability of each value a discrete RV can take.
  - id: named-distributions
    name: Named discrete distributions
    importance: core
    one_liner: Bernoulli, binomial, Poisson, geometric, and uniform recur everywhere.
  - id: binomial-to-poisson
    name: Binomial-to-Poisson limit
    importance: highlight        # the visual climax
    one_liner: Binomial(n, lambda/n) converges to Poisson(lambda) as n grows.
  - id: functions-of-rvs
    name: Functions of random variables
    importance: optional         # candidate to cut for runtime
    one_liner: Applying g to X yields another random variable Y = g(X).
estimated_runtime_sec: 360         # rough target before scripting
---

# Discrete Random Variables — Concept Map

## What
A discrete random variable is a function from the sample space to the real
numbers whose range is finite or countable. It is fully described by its
probability mass function (PMF), and a handful of named PMFs cover most of the
discrete models an engineer meets.

## Why (motivation for the viewer)
Probability spaces are abstract; real numbers let us *compute*. The moment we
attach a number to each outcome, the whole machinery of sums, expectations, and
limits becomes available. This chapter is the bridge from "events" to
"quantities," so it underpins everything downstream (expectation, variance,
random vectors).

## How (the spine of the chapter)
1. Reframe an outcome-to-number assignment as a *function* `X: Omega -> R`.
2. Define the PMF as the probability of each preimage; note it sums to 1.
3. Tour the named distributions, each tied to a concrete counting story.
4. Show the binomial-to-Poisson limit as the unifying punchline.
5. (Optional) Note that `Y = g(X)` is itself a random variable.

## What else (connections, to seed callbacks in narration)
- Bernoulli is one coin flip; binomial is n of them; geometric counts flips
  until the first success; Poisson is the rare-event limit of the binomial.
- The memoryless property singles out the geometric among discrete RVs.
- Functions of RVs (`g(X)`) foreshadows derived distributions (Chapter 9).

## Conceptual progression (drives the storyboard)
mapping picture  ->  PMF as a bar chart  ->  gallery of named PMFs  ->
binomial bars visibly settling onto the Poisson curve.

## Visual opportunities
- Outcomes (colored balls) in an Omega box, arrows to a number line.
- PMF bar charts on a shared axis so distributions are comparable.
- An animated convergence: redraw binomial bars for n = 5, 15, 25, 35 over a
  faint fixed Poisson reference.

## Deliberately out of scope
- Continuous random variables (Chapter 8).
- Expectation and variance (Chapter 6) — mentioned, not derived.
- Full proof of the Poisson limit — shown as a result, not a derivation.
