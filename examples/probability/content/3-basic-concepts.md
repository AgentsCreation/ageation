---
slug: 3-basic-concepts
title: Basic Concepts
stage: concept            # tex -> [concept] -> script -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
source: sources/3-basic-concepts.tex
upstream: input/Probability/3Basic_Concepts.tex
source_sha256: 3266eca9580b407bf9003daedd60f5cae4e2b072c7bcfb483e511659d877a79c
provenance_stamped: 2026-06-11
prereqs:
  - 2-combinatorics
audience: undergraduate engineering, first probability course
concepts:
  - id: sample-space-events
    name: Sample spaces and events
    importance: core
    one_liner: An experiment has a sample space of outcomes; an admissible subset is an event.
  - id: probability-axioms
    name: The three axioms of probability
    importance: core
    one_liner: Nonnegativity, normalization, and countable additivity define any probability law.
  - id: derived-properties
    name: Properties derived from the axioms
    importance: highlight
    one_liner: Monotonicity, the union formula, inclusion-exclusion, and the union bound follow.
  - id: finite-equiprobable
    name: Finite and equally likely spaces
    importance: core
    one_liner: On a finite space, summing outcome probabilities gives every event; equal weights give counting.
  - id: countable-models
    name: Countably infinite models
    importance: core
    one_liner: A countable space is still pinned down by outcome probabilities that sum to one.
  - id: uncountable-models
    name: Uncountable models and length
    importance: optional
    one_liner: On the interval, probability becomes length — an integral over the event.
estimated_runtime_sec: 360         # rough target before scripting
---

# Basic Concepts — Concept Map

## What
This chapter makes probability rigorous. A probabilistic model is two things: a
sample space of possible outcomes and a probability law that assigns each event
a number. That law must obey three axioms — nonnegativity, normalization, and
countable additivity — and from those three rules every familiar property of
probability follows. We then specialize to finite, countably infinite, and
uncountable sample spaces, watching how "probability" is computed differently in
each.

## Why (motivation for the viewer)
The previous chapter equated probability with counting, but counting only works
when outcomes are finite and equally likely. Real experiments break both
assumptions: a coin tossed until heads has infinitely many outcomes, and a
spun wheel has uncountably many. The axiomatic approach is the upgrade — it
defines probability for any model at all, and it lets us *derive* results like
the union bound rather than guess them. This is the foundation every later
chapter silently stands on.

## How (the spine of the chapter)
1. Sample space Omega and events; the rules a valid sample space must satisfy —
   distinct, mutually exclusive, collectively exhaustive.
2. The three axioms, stated as the definition of a probability law.
3. Properties derived from the axioms: monotonicity (A ⊂ B implies Pr(A) ≤
   Pr(B)), the two-event union formula, the inclusion-exclusion principle, and
   the union bound (Boole's inequality), proved by induction.
4. Finite spaces: a law is fixed by outcome probabilities; equal weights recover
   Pr(A) = |A|/n, reconnecting to Chapter 2.
5. Countably infinite spaces (coin tossed until heads), where a convergent sum
   pins down the law.
6. Uncountable spaces (the unit interval, the wheel of serendipity), where
   probability becomes length — an integral over the event.

## What else (connections, to seed callbacks in narration)
- "Sample space = a set, event = a subset" is the payoff of Chapter 1's set
  language — call it back at the open.
- Equally likely finite spaces are exactly Chapter 2's counting model, now
  derived as a special case of the axioms rather than assumed.
- The union bound is the practical tool: bound a hard joint probability of rare
  events by the easy sum of individual probabilities.
- The integral-as-probability on [0,1] foreshadows continuous random variables
  and probability density functions later in the course.

## Conceptual progression (drives the storyboard)
outcomes in an Omega box with one event circled  ->  three axiom cards stacking
up  ->  Venn-diagram proofs of monotonicity and the union formula  ->  a finite
bar of outcome weights summing to one  ->  an infinite decaying geometric bar
for the coin experiment  ->  a shaded sub-interval of [0,1] whose length is its
probability.

## Visual opportunities
- The Omega rectangle with seven colored balls; lasso a subset and label it
  "event."
- Three axiom cards animating in: Pr ≥ 0, Pr(Omega) = 1, Pr(A ∪ B) = Pr(A) +
  Pr(B) for disjoint A, B.
- The union formula as overlapping circles: add both, subtract the
  double-counted overlap.
- A geometric bar chart 1/2, 1/4, 1/8, ... with the bars visibly summing to one.
- The unit interval with a shaded sub-interval (a, b); its width *is* Pr((a,b)) =
  b - a; then the spinning wheel of serendipity, with a quadrant = 1/4.

## Deliberately out of scope
- Conditional probability and independence (Chapter 4) — only previewed.
- A rigorous treatment of sigma-fields and measure theory — flagged as the
  starred aside, not developed.
- Random variables and distributions (Chapter 5) — the integral-as-probability
  is shown as a teaser only.
