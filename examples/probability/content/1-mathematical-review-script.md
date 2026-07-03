---
slug: 1-mathematical-review
title: Mathematical Review
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 1-mathematical-review.md
derived_from_sha256: 5f0f719c861289f1c08819ea086860db766667db1c7c7c10647f98bbae24c716
provenance_stamped: 2026-07-03
target_scene_file: scenes/mathematical_review.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing). This is
#             the course opener, so the "recap" is a welcoming orientation.
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
# Neighbour titles for recap/bridge come from project.yaml prereqs + order.
linking:
  objective: "Speak the language of sets and functions that all of probability is built on."
  recap: "Welcome to the course — we start by building the mathematical toolkit everything else rests on."
  key_idea: "Sample spaces are sets, events are subsets, and random variables are functions."
  bridge: "Next: Combinatorics — once outcomes are sets, we learn to count them."

# --- Voice + timing config -------------------------------------------------
voice:
  provider: openai        # gtts (free draft) -> openai/elevenlabs (final)
  model: tts-1
  name: alloy
  rate: 1.0
words_per_minute: 150     # used only for the pre-TTS estimate
target_runtime_sec: 360
tolerance_sec: 30         # build fails review if |actual - target| > tolerance

# --- Estimates vs measured -------------------------------------------------
# est_sec are computed from narration_words / wpm (cheap, pre-render).
# measured_sec is written back by the render stage from tracker.duration.
estimated_runtime_sec: 348
measured_runtime_sec: null

beats:
  - id: sets-intro
    scene_class: SetsAndElements
    narration_words: 120
    est_sec: 48
    measured_sec: null
    sync_points: [show-balls, show-membership, show-subset, show-omega]
  - id: set-operations
    scene_class: ElementarySetOperations
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [union, intersection, disjoint, difference]
  - id: set-algebra
    scene_class: SetAlgebraAndDeMorgan
    narration_words: 130
    est_sec: 52
    measured_sec: null
    sync_points: [distributive, demorgan-shade, demorgan-morph]
  - id: cartesian
    scene_class: CartesianProducts
    narration_words: 95
    est_sec: 38
    measured_sec: null
    sync_points: [show-two-sets, fan-out, count-grid]
  - id: functions
    scene_class: FunctionsAndPreimages
    narration_words: 175
    est_sec: 70
    measured_sec: null
    sync_points: [map-arrows, image, preimage, injective-surjective]
  - id: outro
    scene_class: SetTheoryAndProbability
    narration_words: 80
    est_sec: 32
    measured_sec: null
    sync_points: [callback-omega, bridge]
---

# Video Script — Mathematical Review

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

---

## Beat: sets-intro  (scene: SetsAndElements)

> Welcome to the course. Before we can talk about randomness, we need a shared
> language, and that language is set theory. <bookmark mark="show-balls"/> A set
> is just a collection of objects, which we call its elements. <bookmark
> mark="show-membership"/> If an object x is in a set S, we write x in S; if it
> isn't, we write x not in S. <bookmark mark="show-subset"/> When every element
> of one set also lives in another, the first is a subset of the second. Two
> special sets matter most: the empty set, which contains nothing, and
> <bookmark mark="show-omega"/> the universal set, written capital Omega — the
> collection of everything in play. Keep an eye on Omega: later in the course it
> becomes our sample space.

**Animation cue:** this is the FIRST beat, so it opens with the shared
intro_card stating the objective and the welcoming orientation (recap).

**Cues**
- `show-balls`: fade colored numbered balls into a dashed Omega ellipse.
- `show-membership`: write `x ∈ S` and `x ∉ S` beside one highlighted ball.
- `show-subset`: nest a smaller dashed loop inside, label `S ⊂ T`.
- `show-omega`: outline the whole box, write the symbol Omega in the corner.

---

## Beat: set-operations  (scene: ElementarySetOperations)

> With two sets in hand, we can build new ones. <bookmark mark="union"/> The
> union of S and T is everything in S, or in T, or in both. <bookmark
> mark="intersection"/> The intersection is only what they share — the overlap.
> <bookmark mark="disjoint"/> When two sets share nothing, their intersection is
> empty, and we call them disjoint; a family of disjoint sets that together fill
> S is called a partition of S. <bookmark mark="difference"/> Finally, the
> difference S minus T keeps the elements of S that are not in T. These four
> operations — union, intersection, complement, and difference — are the
> workhorses of everything that follows.

**Cues:** two overlapping circles labeled S and T. At each bookmark, shade the
relevant region blue and morph from the previous shading. For `disjoint`, pull
the circles apart and then show a three-piece partition of one big set.

---

## Beat: set-algebra  (scene: SetAlgebraAndDeMorgan)

> Operations on sets obey their own algebra, much like numbers. <bookmark
> mark="distributive"/> The distributive laws let us factor: R intersect the
> union of S and T equals the union of R-intersect-S and R-intersect-T. The most
> useful identities are De Morgan's laws. <bookmark mark="demorgan-shade"/>
> Shade the complement of the union of S and T — everything outside both
> circles. <bookmark mark="demorgan-morph"/> Now watch: that exact region is the
> intersection of their complements. The complement of a union is the
> intersection of the complements, and the complement of an intersection is the
> union of the complements.

**Cues**
- `distributive`: display the two distributive identities as MathTex, fade in
  line by line.
- `demorgan-shade`: on a Venn pair, shade the region outside both circles.
- `demorgan-morph`: TransformMatchingTex `(S ∪ T)^c` onto `S^c ∩ T^c` while the
  shaded region stays fixed, proving the two describe the same set.

---

## Beat: cartesian  (scene: CartesianProducts)

> There's one more way to make a new set from old ones. <bookmark
> mark="show-two-sets"/> Take a set of numbers, one two three, and a set of
> letters, a and b. <bookmark mark="fan-out"/> The Cartesian product pairs every
> number with every letter, producing ordered pairs like one-a, one-b, two-a,
> and so on. <bookmark mark="count-grid"/> If the first set has three elements
> and the second has two, the product has three times two, six pairs. Hold onto
> that multiplication — it's the seed of the counting principle in the next
> chapter.

**Cues**
- `show-two-sets`: two columns of balls, {1,2,3} and {a,b}.
- `fan-out`: lag-animate arrows that assemble each pair into a 3-by-2 grid.
- `count-grid`: write `|S × T| = |S| · |T| = 6` under the grid.

---

## Beat: functions  (scene: FunctionsAndPreimages)

> The last tool is the function. <bookmark mark="map-arrows"/> A function assigns
> exactly one output to each input. We write f from X to Y, where X is the domain
> — the allowed inputs — and Y is the codomain. <bookmark mark="image"/> The
> image is the set of values f actually hits as the input ranges over the whole
> domain. <bookmark mark="preimage"/> Running the arrows backward gives the
> preimage: for a value y, the preimage is every input that maps to y. That set,
> f-inverse of y, can hold many points, one point, or none — and it's exactly
> how we'll later turn "X equals y" into an event. <bookmark
> mark="injective-surjective"/> If different inputs never collide, the function
> is injective; if it reaches every value in the codomain, it's surjective; if
> both, it's a bijection, and it has a genuine inverse.

**Cues**
- `map-arrows`: domain box on the left, codomain number line on the right, with
  mapping arrows; write `f : X → R`.
- `image`: highlight the subset of the line that gets hit.
- `preimage`: pick one output value, reverse-highlight every input arrow landing
  on it, label the collected inputs as the level set `f^{-1}({y})`.
- `injective-surjective`: brief side-by-side icons for injective, surjective,
  bijective.

---

## Beat: outro  (scene: SetTheoryAndProbability)

> Step back and the payoff is clear. <bookmark mark="callback-omega"/> A sample
> space is a set — that Omega we met at the start. An event is a subset of it.
> And a random variable, which we'll meet later, is simply a function on that
> sample space. Set theory isn't a detour; it's the skeleton of probability.
> <bookmark mark="bridge"/> In the next chapter, Combinatorics, we take these
> sets of outcomes and learn how to count them — because for equally likely
> outcomes, probability is just careful counting.

**Animation cue:** this is the LAST beat, so it closes with the shared
outro_bridge — speak the key_idea on `callback-omega` and the bridge to
"Combinatorics" on `bridge`, with the progress_tag for Chapter 1.

**Cues**
- `callback-omega`: re-summon the Omega box from beat one and overlay the words
  sample space / event / random variable beside set / subset / function.
- `bridge`: fade to the chapter-2 title card.

---

## Cut list (if over budget)
1. Drop the optional `indicator-function` aside from the concept map (already
   omitted from narration).
2. Trim `functions` to domain/codomain/image/preimage; cut the
   injective-surjective-bijective triad.
3. Shorten `set-algebra` to De Morgan only, dropping the distributive laws.
4. Compress the outro callback to key_idea plus bridge, no triple overlay.
