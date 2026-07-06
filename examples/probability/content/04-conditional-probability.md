---
slug: 04-conditional-probability
title: Conditional Probability
stage: concept            # tex -> [concept] -> script -> scene -> render
status: approved             # draft | reviewed | approved  (human gate)
source: sources/04-conditional-probability.tex
upstream: input/Probability/4Conditional_Probability.tex
source_sha256: ad6787891068d072eb5d16e0abd90503f0c0280c1968de5df76b3634d1b527cc
provenance_stamped: 2026-07-06
framework_commit: 36004fc-dirty
prereqs:
  - 03-basic-concepts
audience: undergraduate engineering, first probability course
concepts:
  - id: conditioning
    name: Conditioning on events
    importance: core
    one_liner: Side information rescales probabilities to the part of the space still possible.
  - id: cond-def
    name: Definition of conditional probability
    importance: core
    one_liner: Pr(A given B) is Pr(A and B) divided by Pr(B), valid whenever Pr(B) > 0.
  - id: chain-rule
    name: Chain rule
    importance: optional         # candidate to cut for runtime
    one_liner: A long intersection factors into a product of successive conditionals.
  - id: total-probability
    name: Total probability theorem
    importance: core
    one_liner: Split the space into cases, weight each conditional by its case probability, and add.
  - id: bayes
    name: Bayes' rule
    importance: highlight        # the visual climax
    one_liner: Bayes flips a conditional around, turning Pr(B given A) into Pr(A given B).
  - id: independence
    name: Independence
    importance: optional
    one_liner: A and B are independent when knowing one tells you nothing about the other.
estimated_runtime_sec: 360         # rough target before scripting
---

# Conditional Probability — Concept Map

## What
Conditional probability is the machinery for updating likelihoods in the light
of partial information. Given that an event B has occurred, the conditional
probability of A is Pr(A and B) divided by Pr(B). From this single definition
flow the chain rule, the total probability theorem, Bayes' rule, and a precise
notion of independence.

## Why (motivation for the viewer)
Real decisions are made with incomplete knowledge. A test comes back positive, a
packet arrives corrupted, a sensor fires — and we must revise our beliefs.
Conditioning is the formal answer to "what changes once I learn this?" It is the
backbone of inference, communications, and decision-making, and it is the lens
through which every later chapter handles dependence between quantities.

## How (the spine of the chapter)
1. Build intuition from a fair die: learning "the outcome is odd" leaves three
   equally likely faces, so each rises from one-sixth to one-third.
2. Promote that intuition to the definition Pr(A | B) = Pr(A ∩ B) / Pr(B), and
   note it is itself a valid probability law.
3. Partition the sample space, then add the pieces of B across the partition to
   get the total probability theorem.
4. Invert a conditional with Bayes' rule, and apply it to a rare-disease test.
5. (Optional) Define independence as the case where conditioning changes nothing.

## What else (connections, to seed callbacks in narration)
- The frequentist ratio N_AB / N_B is the intuition behind the definition: count
  the trials where both happened, divide by the trials where B happened.
- The chain rule is just the definition applied repeatedly, and it powers the
  "draw three blue balls without replacement" computation.
- Total probability is the engine inside Bayes' denominator.
- Independence (Pr(A ∩ B) = Pr(A)Pr(B)) is the same as "conditioning on B leaves
  Pr(A) untouched"; disjoint non-trivial events are never independent.

## Conceptual progression (drives the storyboard)
die with side information  ->  the definition as a ratio  ->  partition diagram
with B sliced across the cells  ->  Bayes flipping the arrow, then the
counter-intuitive disease-test number.

## Visual opportunities
- Six die faces; the even ones dim out and the odd labels relabel from 1/6 to 1/3.
- A partition of Omega into colored strips with an event B drawn across them,
  highlighting each B ∩ A_k piece.
- Two urns of colored balls for the divide-and-conquer total-probability example.
- Bayes' rule derived from the two ways to expand Pr(A ∩ B), then the disease
  example landing on a surprising 16 percent.

## Deliberately out of scope
- Independence, conditional independence, and the equivalent comma notation —
  mentioned in passing but not animated, to keep the runtime near six minutes.
- The general n-event chain rule beyond the three-ball illustration.
- Random variables (Chapter 5) — conditioning is set up here purely for events.
