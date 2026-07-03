---
slug: 1-mathematical-review
title: Mathematical Review
stage: concept            # tex -> [concept] -> script -> scene -> render
status: reviewed             # draft | reviewed | approved  (human gate)
source: sources/1-mathematical-review.tex
upstream: input/Probability/1Mathematical_Review.tex
source_sha256: debff4497945c67249db18ff907a754446db41d37f3db7cbea5cd1aaddce13a0
provenance_stamped: 2026-07-03
framework_commit: 063f807
# Course start — no prerequisites.
audience: undergraduate engineering, first probability course
concepts:
  - id: sets-and-membership
    name: Sets, elements, and subsets
    importance: core
    one_liner: A set is a collection of objects; membership and containment are the primitives.
  - id: set-operations
    name: Elementary set operations
    importance: core
    one_liner: Union, intersection, complement, and difference build new sets from old.
  - id: algebra-of-sets
    name: Algebra of sets
    importance: core
    one_liner: Distributive laws and De Morgan's laws govern how operations combine.
  - id: cartesian-product
    name: Cartesian products
    importance: highlight
    one_liner: Ordered pairs let us glue two sets into a grid of outcomes.
  - id: functions
    name: Functions, images, and preimages
    importance: core
    one_liner: A function assigns one output to each input; the preimage pulls events back.
  - id: indicator-function
    name: The indicator function
    importance: optional
    one_liner: The indicator of a set reports membership as a zero or a one.
estimated_runtime_sec: 360         # rough target before scripting
---

# Mathematical Review — Concept Map

## What
This chapter is the toolkit. Probability is built on naive set theory, so before
we touch a single coin flip we fix the language: a set is a collection of
objects, elements either belong or they don't, and one set can sit inside
another. From those primitives we build union, intersection, complement, and
difference; we learn the laws that govern them; we glue sets together with the
Cartesian product; and we formalize the idea of a function — including the
all-important preimage, which is how probability later pulls events back to the
sample space.

## Why (motivation for the viewer)
Every later chapter speaks this language. The sample space is a set, an event is
a subset, a random variable is a function, and "the probability that X lands in
a range" is the probability of a preimage. If the set vocabulary is shaky, every
downstream argument feels like guesswork. Nail it once here and the rest of the
course reads cleanly. This is also why the universal set is renamed Omega — it
*is* the sample space we will use for the next eleven chapters.

## How (the spine of the chapter)
1. Sets, elements, membership, and the subset relation; the empty set and the
   universal set Omega.
2. Elementary operations on two sets — union, intersection, complement,
   difference — plus disjointness and partitions.
3. The algebra: distributive laws and De Morgan's laws, including the form for
   arbitrary unions and intersections.
4. The Cartesian product: ordered pairs assemble two sets into a grid.
5. Functions: domain, codomain, image, preimage and the level set; injective,
   surjective, bijective; the indicator function as a probability-flavored
   example.

## What else (connections, to seed callbacks in narration)
- Omega is introduced here as the universal set and is exactly the sample space
  of Chapter 3 — flag the name so the callback lands later.
- The preimage `f^{-1}({y})` is the secret engine behind random variables in
  Chapter 5; an event "X = y" is literally a preimage.
- The Cartesian product previews the counting principle of Chapter 2, where
  |S x T| = |S||T| becomes a rule for counting.
- The indicator function reappears whenever we compute the probability of an
  event by averaging — a quiet thread through the whole course.

## Conceptual progression (drives the storyboard)
labeled balls in a box (a set)  ->  two overlapping circles shaded for each
operation (Venn diagrams)  ->  De Morgan's law shown as a shading identity  ->
two small sets fanning out into a product grid  ->  arrows from a domain to a
codomain, then arrows reversed to show a preimage.

## Visual opportunities
- Colored numbered balls inside a dashed Omega box for "a set and its elements."
- A sweep of Venn diagrams: union, intersection, complement, difference, each
  with the relevant region shaded blue.
- De Morgan animated: shade `(S ∪ T)^c`, then morph it onto `S^c ∩ T^c` to show
  the regions coincide.
- {1,2,3} × {a,b} unfolding into a six-cell grid of paired balls.
- A domain box and codomain line with mapping arrows; then highlight a level set
  by collecting every input that lands on one output.

## Deliberately out of scope
- Axiomatic / ZFC set theory — we stay explicitly naive, as the source does.
- Measure theory, sigma-fields, and cardinality of the uncountable (previewed
  only much later, in Chapter 3).
- Stirling's formula and counting (Chapter 2) — the Cartesian product is shown
  as a construction here, counted there.
