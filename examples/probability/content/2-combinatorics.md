---
slug: 2-combinatorics
title: Combinatorics
stage: concept            # tex -> [concept] -> script -> scene -> render
status: reviewed             # draft | reviewed | approved  (human gate)
source: sources/2-combinatorics.tex
upstream: input/Probability/2Combinatorics.tex
source_sha256: 1fe87534736aa916c8599b7b7466c3f5c10aaee210924ae7037518eaf23720eb
provenance_stamped: 2026-06-11
framework_commit: af5d6d4-dirty
prereqs:
  - 1-mathematical-review
audience: undergraduate engineering, first probability course
concepts:
  - id: equally-likely-model
    name: Equally likely outcomes
    importance: core
    one_liner: When outcomes are equally likely, probability is favorable count over total count.
  - id: counting-principle
    name: The counting principle
    importance: core
    one_liner: The product of choices counts the elements of a Cartesian product.
  - id: permutations
    name: Permutations and k-permutations
    importance: core
    one_liner: Ordered arrangements of n items number n factorial; of k items, n!/(n-k)!.
  - id: combinations
    name: Combinations and binomial coefficients
    importance: highlight
    one_liner: Unordered k-subsets number n choose k = n!/(k!(n-k)!).
  - id: partitions-multinomial
    name: Partitions and multinomial coefficients
    importance: core
    one_liner: Splitting n items into labeled groups uses the multinomial coefficient.
  - id: sampling-table
    name: The four sampling modes
    importance: optional
    one_liner: With or without replacement, with or without ordering, gives four counting rules.
estimated_runtime_sec: 360         # rough target before scripting
---

# Combinatorics — Concept Map

## What
For experiments with finitely many equally likely outcomes, computing a
probability reduces to counting: divide the number of outcomes in the event by
the total number of outcomes. This chapter assembles the counting toolkit — the
counting principle, permutations, combinations, and partitions — and ties them
together through the unifying picture of drawing balls from an urn under
different rules.

## Why (motivation for the viewer)
"Count the favorable cases, divide by the total" sounds trivial until the cases
number in the millions. Lotteries, card hands, and rescue-boat assignments all
hinge on counting that's far from obvious by inspection. The binomial and
multinomial coefficients built here are not just counting tools; they reappear
as the backbone of the binomial and multinomial distributions later in the
course. Master counting and the equally likely model becomes a genuine
computational engine.

## How (the spine of the chapter)
1. The counting principle: |S × T| = mn, extended to r sets as a product of
   cardinalities.
2. Permutations: n! orderings of n items; k-permutations give n!/(n-k)!.
   (Stirling's formula as an optional aside on how fast n! grows.)
3. Combinations: choosing an unordered k-subset gives the binomial coefficient
   n choose k = n!/(k!(n-k)!); note the symmetry with n-k.
4. Partitions: splitting into r labeled groups gives the multinomial
   coefficient n!/(n_1! ... n_r!); the stars-and-bars argument counts the
   cardinality assignments themselves.
5. Worked examples: Pick 3 and Mega Millions lotteries, and the sinking-boat
   couples problem.

## What else (connections, to seed callbacks in narration)
- The counting principle is exactly the Cartesian-product cardinality from
  Chapter 1 — call it back explicitly.
- The four classic urn experiments — sampling with/without replacement, with/
  without ordering — map one-to-one onto the four counting formulas, a clean
  organizing table.
- The sum of binomial coefficients over k equals 2^n, the size of the power set:
  counting subsets two different ways.
- Binomial coefficients here become the binomial distribution in Chapter 5;
  multinomial coefficients become the multinomial distribution.

## Conceptual progression (drives the storyboard)
two ball-columns fanning into a product grid (counting principle)  ->  balls
filling ordered slots with a shrinking pool (permutations)  ->  ordered lists
collapsing into unordered loops, divided by k! (combinations)  ->  balls and
divider bars on a line (stars and bars for partitions)  ->  a lottery card lit
up with its odds.

## Visual opportunities
- The {1,2,3} × {a,b} grid reused from Chapter 1, now annotated with "3 × 2 = 6".
- Slot machine of permutation: three slots fill from a pool that shrinks 4, 3, 2.
- Six ordered 2-lists of {1,2,3,4} folding pairwise into three unordered
  subsets, with a "÷ 2!" label appearing.
- Stars-and-bars: five balls and two bars sliding along a line, the arrangement
  reading off the partition (0, 2, 3).
- A Mega Millions card with the odds 1 in 175,711,536 counting up dramatically.

## Deliberately out of scope
- Generating functions and advanced enumerative combinatorics.
- A proof of Stirling's formula — stated as an approximation, not derived.
- The full inclusion-exclusion principle (it belongs to Chapter 3, Basic
  Concepts).
